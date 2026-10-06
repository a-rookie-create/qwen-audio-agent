"""可直接运行的总览：真实调用各模块，观察聊天、前台工具与后台任务。"""
from __future__ import annotations
import asyncio
from bootstrap.start import build_study_runtime


async def run_demo(show_trace: bool = False) -> None:
    # 从这个函数向下跳转，就能看到四个角色如何装配。
    runtime = await build_study_runtime()
    app = runtime.app
    try:
        print('1. 普通聊天：', (await app.send('你好'))['text'])
        print('2. 前台工具：', (await app.send('空调调到24度，播放晴天'))['text'])
        print('   Service 权威温度：', runtime.service.service.snapshot()['vehicle']['acTemp'])
        print('   客户端同步温度：', app.cockpit.state['vehicle']['acTemp'])

        # 收到回执时后台还在执行，立即继续发一条普通聊天消息。
        receipt = await app.send('帮我买杯咖啡')
        print('3. 后台回执：', receipt['text'])
        print('   执行期间聊天：', (await app.send('你好'))['text'])
        task = await app.wait_for_task(receipt['task_ids'][0])
        print('   后台结果：', task.result.content)
        print('   执行状态 / 通知状态：', task.status, '/', task.notification)

        # 预览不会自动下单，只有明确确认后才生成演示订单。
        confirm = await app.send('确认下单')
        await app.wait_for_task(confirm['task_ids'][0])
        print('   本地演示订单：', runtime.service.service.snapshot()['flashbuy']['order']['id'])

        # 保存提醒后，真实温度变化触发 Service→客户端→Gateway 的事件链。
        await app.cockpit.execute('custom_skill_create', {
            'name': '降温提醒', 'description': '演示事件链', 'kind': 'event',
            'trigger': {'type': 'vehicle_temperature', 'max': 20}, 'reminder': '温度较低，请注意保暖'})
        await app.send('空调调到19度')
        await app.voice.flush()
        reminders = [message['text'] for message in app.voice.messages if message.get('origin') == 'environment']
        print('4. 环境提醒：', reminders[-1])
        if show_trace:
            print('\n调用链：')
            for component, action, detail in runtime.trace.entries:
                print(f'  {component:14} {action:27} {detail}')
    finally:
        await runtime.close()


if __name__ == '__main__':
    asyncio.run(run_demo())
