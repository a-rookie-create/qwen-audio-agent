"""验证真实调用、状态归属、异步执行与错误路径。默认全部离线。"""
from __future__ import annotations
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from agent.model import DemoChatModel
from bench.runner import run_cases
from bootstrap.start import build_study_runtime
from client.app import CockpitApp
from client.projections import CockpitEnvironmentOutbox
from framework_reference.extension_ports import MemoryConflictError, MemoryProvider
from service.custom_skills.store import CustomSkillStore


class BrokenModel:
    async def complete(self, messages, tools):
        raise RuntimeError('演示模型故障')


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    # 每个测试使用独立事件循环与运行时，避免业务记录和待执行 Task 跨用例残留。
    async def asyncSetUp(self):
        self.runtime = await build_study_runtime(model=DemoChatModel(delay=0.001))
        self.app = self.runtime.app
        self.service = self.runtime.service.service

    async def asyncTearDown(self):
        await self.runtime.close()
        # 回调异常也必须检查，避免观察链静默失败。
        self.assertEqual(self.service.store.events.errors, [])
        self.assertEqual(self.service.activity.errors, [])
        self.assertEqual(self.runtime.gateway.tasks.events.errors, [])
        self.assertEqual(self.runtime.agent.executor.executions, {})

    async def create_task(self, text='帮我买杯咖啡'):
        # 前台只返回接受回执，这个辅助函数取出任务记录，故意不等待其完成。
        reply = await self.app.send(text)
        return self.runtime.gateway.tasks.get(reply['task_ids'][0], 'demo-user')

    async def set_temperature(self, temperature):
        return await self.service.execute('vehicle_temperature_control',
                                         {'action': 'set', 'temperature': temperature})

    async def test_chat_does_not_create_task_or_change_business_state(self):
        state = self.service.snapshot()
        reply = await self.app.send('你好')
        self.assertIn('学习助手', reply['text'])
        self.assertEqual(reply['task_ids'], [])
        self.assertEqual(self.runtime.gateway.tasks.tasks, {})
        self.assertEqual(self.service.snapshot(), state)

    async def test_foreground_changes_state_and_updates_client(self):
        reply = await self.app.send('空调调到24度，播放晴天')
        self.assertEqual(reply['task_ids'], [])
        state = self.service.snapshot()
        self.assertEqual(state['vehicle']['acTemp'], 24)
        self.assertTrue(state['music']['playing'])
        self.assertEqual(self.app.cockpit.state, state)

    async def test_original_tool_surfaces_are_preserved(self):
        frontend = self.runtime.service.mcp('frontend')
        backend = self.runtime.service.mcp('backend')
        self.assertEqual(len(frontend.list_tools()), 37)
        self.assertEqual([t.name for t in backend.list_tools()], ['flashbuy'])
        self.assertTrue((await frontend.call_tool('flashbuy', {'action': 'search'})).is_error)
        self.assertTrue((await backend.call_tool('vehicle_state_query', {})).is_error)

    async def test_invalid_parameters_do_not_change_state(self):
        state = self.service.snapshot()
        for temperature in (99, True, float('nan'), float('inf'), '24'):
            with self.subTest(temperature=temperature):
                self.assertTrue((await self.set_temperature(temperature)).is_error)
                self.assertEqual(self.service.snapshot(), state)
        result = await self.service.execute('vehicle_temperature_control', {'action': 'set'})
        self.assertTrue(result.is_error)
        self.assertEqual(self.service.snapshot(), state)

    async def test_unknown_tool_is_an_error(self):
        result = await self.service.execute('missing_tool', {})
        self.assertTrue(result.is_error)
        self.assertIn('未知工具', result.content)

    async def test_every_manifest_tool_has_a_working_execution_path(self):
        # 按业务顺序调用，检查全部工具确实能到达业务实现。
        # 收藏后才能导航到收藏，搜索商品后才能加购；这些前置状态来自真实执行。
        steps = [
            ('vehicle_location_query', {}), ('vehicle_state_query', {}),
            ('vehicle_climate_control', {'action': 'open'}),
            ('vehicle_temperature_control', {'action': 'set', 'temperature': 24}),
            ('vehicle_window_control', {'action': 'vent'}),
            ('vehicle_sunroof_control', {'action': 'open'}),
            ('vehicle_closure_control', {'target': 'trunk', 'action': 'open'}),
            ('vehicle_comfort_control', {'target': 'seat_heater', 'action': 'open'}),
            ('vehicle_light_control', {'action': 'flash'}),
            ('vehicle_sound_control', {'action': 'honk'}),
            ('vehicle_charging_control', {'action': 'set_limit', 'limitPercent': 85}),
            ('navigation_search_place', {'query': '西湖'}),
            ('navigation_set_favorite', {'favoriteType': 'home', 'address': '杭州'}),
            ('navigation_to_favorite', {'favoriteType': 'home'}),
            ('navigation_start', {'destination': '西湖'}),
            ('navigation_add_waypoint', {'waypoint': '博物馆'}),
            ('navigation_route_query', {}), ('navigation_remove_waypoint', {'index': 0}),
            ('navigation_change_destination', {'destination': '公园'}),
            ('navigation_set_route_strategy', {'strategy': 13}),
            ('navigation_set_voice', {'mute': True}),
            ('navigation_set_view', {'viewMode': 'overview'}), ('navigation_stop', {}),
            ('music_search', {'query': '晴天'}), ('music_play', {'query': '晴天'}),
            ('music_state_query', {}), ('music_pause', {}), ('music_toggle_playback', {}),
            ('music_next', {}), ('music_previous', {}),
            ('music_volume_control', {'action': 'set', 'volume': 7}),
            ('music_source_control', {'source': 'radio'}),
            ('music_favorite_control', {'action': 'add'}), ('weather', {'city': '杭州'}),
            ('flashbuy', {'action': 'search', 'query': '咖啡'}),
            ('flashbuy', {'action': 'add_to_cart', 'itemId': 'latte'}),
            ('flashbuy', {'action': 'preview_order'}),
            ('custom_skill_create', {'name': '上车', 'description': '准备', 'instructions': '空调调到24度'}),
            ('custom_skill_list', {}), ('custom_skill_load', {'skill_name': '上车'}),
        ]
        self.assertEqual({name for name, _ in steps}, set(self.service.registry.definitions))
        for name, arguments in steps:
            with self.subTest(tool=name):
                result = await self.service.execute(name, arguments)
                self.assertFalse(result.is_error, result.content)
        await self.app.voice.flush()
        self.assertEqual(self.service.snapshot()['vehicle']['chargeLimit'], 85)
        self.assertEqual(self.service.snapshot()['music']['volume'], 7)
        self.assertIsNotNone(self.service.snapshot()['flashbuy']['preview'])

    async def test_ui_commands_share_the_same_state_as_model_tools(self):
        await self.app.cockpit.execute('vehicle_temperature_control', {'action': 'set', 'temperature': 23})
        reply = await self.app.send('当前空调多少度')
        self.assertIn('23', reply['text'])
        self.assertEqual(self.app.cockpit.state['vehicle']['acTemp'], 23)

    async def test_navigation_and_weather_use_explicit_demo_adapters(self):
        await self.app.send('导航到西湖，查一下天气')
        state = self.service.snapshot()
        self.assertEqual(state['navigation']['destination'], '西湖')
        self.assertEqual(state['navigation']['route']['source'], 'offline-demo')
        self.assertEqual(state['weather']['source'], 'offline-demo')
        await self.app.voice.flush()
        self.assertIn('cockpit.navigation.preference_changed', self.app.voice.client.session.model.environment)

    async def test_mixed_input_splits_foreground_and_background(self):
        task = await self.create_task('空调调到24度，帮我买杯咖啡')
        self.assertEqual(self.service.snapshot()['vehicle']['acTemp'], 24)
        self.assertEqual(task.objective, '帮我买杯咖啡')
        await self.app.wait_for_task(task.id)

    async def test_background_receipt_is_immediate_and_chat_can_continue(self):
        task = await self.create_task()
        self.assertEqual(task.status, 'queued')
        reply = await self.app.send('你好')
        self.assertIn('学习助手', reply['text'])
        self.assertNotEqual(task.status, 'completed')
        await self.app.wait_for_task(task.id)
        self.assertEqual(task.status, 'completed')
        self.assertEqual(task.notification, 'delivered')
        self.assertTrue(any(m.get('task_id') == task.id for m in self.app.voice.messages))

    async def test_preview_does_not_order_until_explicit_confirmation(self):
        task = await self.create_task()
        await self.app.wait_for_task(task.id)
        self.assertIsNotNone(self.service.snapshot()['flashbuy']['preview'])
        self.assertIsNone(self.service.snapshot()['flashbuy']['order'])
        rejected = await self.service.execute('flashbuy', {'action': 'confirm_order'})
        self.assertTrue(rejected.data['requireConfirm'])
        self.assertIsNone(self.service.snapshot()['flashbuy']['order'])
        confirmation = await self.create_task('确认下单')
        await self.app.wait_for_task(confirmation.id)
        order_id = self.service.snapshot()['flashbuy']['order']['id']
        self.assertTrue(order_id.startswith('DEMO-'))
        duplicate = await self.service.execute('flashbuy', {'action': 'confirm_order', 'confirmed': True})
        self.assertTrue(duplicate.data['duplicate'])
        self.assertEqual(self.service.snapshot()['flashbuy']['order']['id'], order_id)

    async def test_muted_completion_waits_for_unmute(self):
        # 执行完成与播报分离：静音不阻止工具执行，但结果要等取消静音后才投递。
        await self.app.voice.mute(True)
        task = await self.create_task()
        await self.app.wait_for_task(task.id)
        self.assertEqual(task.notification, 'pending')
        self.assertFalse(any(m.get('task_id') == task.id for m in self.app.voice.messages))
        await self.app.voice.mute(False)
        await self.app.voice.client.session.coordinator.flush()
        self.assertEqual(task.notification, 'delivered')

    async def test_delivery_requires_playback_ack(self):
        # 关闭自动确认，区分“回复已发出”与“客户端报告播放完成”两个阶段。
        self.app.voice.auto_play = False
        task = await self.create_task()
        await self.app.wait_for_task(task.id)
        self.assertEqual(task.status, 'completed')
        self.assertEqual(task.notification, 'delivering')
        self.app.voice.client.playback_ack(task.id)
        self.assertEqual(task.notification, 'delivered')

    async def test_queued_task_can_be_cancelled_before_execution(self):
        # 不先让出事件循环，验证 create_task 安排的协程还没开始也能正确取消。
        task = await self.create_task()
        await self.app.voice.client.request('task.cancel', {'task_id': task.id})
        self.assertEqual(task.status, 'cancelled')
        self.assertTrue(task.finished.is_set())
        self.assertIsNone(self.service.snapshot()['flashbuy']['preview'])

    async def test_running_task_can_be_cancelled(self):
        self.runtime.agent.executor.model = DemoChatModel(delay=0.1)
        task = await self.create_task()
        # 让事件循环启动后台工作；较慢模型保证取消时它仍处于运行阶段。
        await asyncio.sleep(0.01)
        self.assertEqual(task.status, 'running')
        await self.app.voice.client.request('task.cancel', {'task_id': task.id})
        self.assertEqual(task.status, 'cancelled')
        self.assertEqual(self.runtime.agent.executor.executions, {})

    async def test_backend_error_becomes_failed_task_and_returns_to_chat(self):
        self.runtime.agent.executor.model = BrokenModel()
        task = await self.create_task()
        await self.app.wait_for_task(task.id)
        self.assertEqual(task.status, 'failed')
        self.assertTrue(task.result.is_error)
        self.assertIn('模型故障', task.result.content)
        self.assertEqual(task.notification, 'delivered')

    async def test_task_access_is_scoped_to_owner(self):
        task = await self.create_task()
        with self.assertRaises(PermissionError):
            self.runtime.gateway.tasks.get(task.id, 'other-user')
        with self.assertRaises(PermissionError):
            await self.runtime.gateway.tasks.cancel(task.id, 'other-user')
        await self.app.wait_for_task(task.id)

    async def test_closing_session_does_not_cancel_accepted_work(self):
        task = await self.create_task()
        await self.app.close()
        await self.runtime.gateway.tasks.wait(task.id, 'demo-user')
        self.assertEqual(task.status, 'completed')
        self.assertEqual(task.notification, 'pending')

    async def test_workflow_creation_saves_definition_without_executing(self):
        result = await self.service.execute('custom_skill_create', {
            'name': '上车准备', 'description': '准备工作流', 'kind': 'workflow',
            'instructions': '空调调到25度，播放晴天'})
        self.assertFalse(result.is_error)
        self.assertEqual(self.service.snapshot()['vehicle']['acTemp'], 22)
        reply = await self.app.send('运行上车准备技能')
        self.assertEqual(reply['task_ids'], [])
        self.assertEqual(self.service.snapshot()['vehicle']['acTemp'], 25)
        self.assertTrue(self.service.snapshot()['music']['playing'])

    async def test_event_skill_only_triggers_on_transition(self):
        result = await self.service.execute('custom_skill_create', {
            'name': '低温提醒', 'description': '低温时提醒', 'kind': 'event',
            'trigger': {'type': 'vehicle_temperature', 'max': 20}, 'reminder': '注意保暖'})
        self.assertFalse(result.is_error)
        await self.app.voice.flush()
        self.assertEqual(len(self.app.voice.messages), 0)
        # 22->19 首次进入条件，19->18 不重复；离开到 25 后再次进入 19 才第二次提醒。
        for temperature in (19, 18, 25, 19):
            await self.set_temperature(temperature)
            await self.app.voice.flush()
        reminders = [m for m in self.app.voice.messages if m.get('origin') == 'environment']
        self.assertEqual(len(reminders), 2)
        self.assertIn('注意保暖', reminders[0]['text'])
        self.assertEqual(self.runtime.gateway.tasks.tasks, {})

    async def test_loading_an_already_matching_event_skill_does_not_trigger(self):
        await self.set_temperature(19)
        result = await self.service.execute('custom_skill_create', {
            'name': '低温提醒', 'description': '低温时提醒', 'kind': 'event',
            'trigger': {'type': 'vehicle_temperature', 'max': 20}, 'reminder': '注意保暖'})
        self.assertFalse(result.is_error)
        await self.app.voice.flush()
        self.assertEqual(self.app.voice.messages, [])

    async def test_skills_ui_reads_and_deletes_same_definitions(self):
        result = await self.service.execute('custom_skill_create', {
            'name': '测试', 'description': '测试技能', 'instructions': '空调调到25度'})
        skill = result.data['skill']
        self.assertEqual(await self.app.skills.load(skill['id']), skill)
        self.assertEqual(len(await self.app.skills.list()), 1)
        await self.app.skills.remove(skill['id'])
        self.assertEqual(await self.app.skills.list(), [])

    async def test_memory_save_delete_and_owner_isolation(self):
        await self.app.send('记住我喜欢晴天')
        documents = await self.app.memory.load()
        self.assertEqual(documents[0]['text'], '我喜欢晴天')
        self.assertEqual(self.runtime.gateway.memory.list('other-user'), [])
        with self.assertRaises(MemoryConflictError):
            await self.app.memory.remove({**documents[0], 'version': 99})
        self.assertEqual(await self.app.memory.remove(documents[0]), [])

    async def test_cockpit_state_isolation_and_snapshot_is_a_copy(self):
        # 第二个客户端绑定不同车机；同时检查 ID 隔离与深拷贝对内部数据的保护。
        other = CockpitApp(self.runtime.gateway, self.runtime.service, 'other', 'other', 'other')
        other.start()
        try:
            await other.send('空调调到26度')
            self.assertEqual(self.service.snapshot('other')['vehicle']['acTemp'], 26)
            self.assertEqual(self.service.snapshot()['vehicle']['acTemp'], 22)
            copy = self.service.snapshot()
            copy['vehicle']['acTemp'] = 99
            self.assertEqual(self.service.snapshot()['vehicle']['acTemp'], 22)
        finally:
            await other.close()

    async def test_persona_selection_changes_foreground_profile(self):
        await self.app.voice.select_persona('action')
        self.assertEqual(self.app.voice.client.session.model.profile_id, 'action')
        with self.assertRaises(ValueError):
            await self.app.voice.select_persona('unknown')

    async def test_web_task_keeps_citations_and_demo_label(self):
        task = await self.create_task('研究一下智能座舱')
        await self.app.wait_for_task(task.id)
        self.assertEqual(task.status, 'completed')
        self.assertEqual(task.result.data['sources'][0]['url'], 'https://example.test/study')
        self.assertTrue(task.result.data['sources'][0]['read'])
        self.assertIn('离线演示', task.result.content)

    async def test_benchmark_runs_actual_calls(self):
        scores = await run_cases()
        self.assertEqual(len(scores), 4)
        self.assertTrue(all(score['passed'] for score in scores), scores)


class SupportingTests(unittest.IsolatedAsyncioTestCase):
    async def test_expired_reminder_is_dropped_but_latest_context_is_kept(self):
        clock = [0.0]
        # 注入可控制的时钟模拟过期，无需真实等待三十秒。
        outbox = CockpitEnvironmentOutbox(ttl=30, now=lambda: clock[0])
        outbox.enqueue({'name': 'reminder', 'event_id': 'r1', 'delivery_hint': 'respond'})
        outbox.enqueue({'name': 'context', 'delivery_hint': 'context', 'data': {'strategy': 0}})
        outbox.enqueue({'name': 'context', 'delivery_hint': 'context', 'data': {'strategy': 2}})
        clock[0] = 31
        delivered = []
        async def send(event):
            delivered.append(event)
            return {'accepted': True}
        await outbox.flush(send, lambda: True)
        self.assertEqual(len(delivered), 1)
        self.assertEqual(delivered[0]['data']['strategy'], 2)

    async def test_optional_skill_persistence_round_trip(self):
        # 创建新 Store 重新读同一临时目录，验证数据来自文件而不是旧对象内存。
        with TemporaryDirectory() as directory:
            store = CustomSkillStore(Path(directory))
            skill = store.upsert('../cockpit', {'name': '上车', 'instructions': '空调调到24度'})
            reloaded = CustomSkillStore(Path(directory))
            self.assertEqual(reloaded.get('../cockpit', skill['id']), skill)
            self.assertEqual(len(list(Path(directory).glob('*.json'))), 1)

    async def test_memory_conflict_is_atomic(self):
        # 一批变更先添加、后删除冲突；两者都不能提交，验证副本上的整批修改策略。
        provider = MemoryProvider()
        documents = provider.apply('user', [{'operation': 'add', 'text': '原记忆'}])
        with self.assertRaises(MemoryConflictError):
            provider.apply('user', [{'operation': 'add', 'text': '不能部分提交'},
                {'operation': 'remove', 'id': documents[0]['id'], 'version': 2}])
        self.assertEqual(provider.list('user'), documents)


if __name__ == '__main__':
    unittest.main()
