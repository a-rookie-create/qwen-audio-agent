"""真正执行学习用例、记录链路并评分；仅评估本地规则模型的回归行为。"""
from bootstrap.start import build_study_runtime
from bench.evaluator import score_trace

CASES = [
    {'input': '你好', 'expected_calls': []},
    {'input': '空调调到24度', 'expected_calls': ['vehicle_temperature_control'], 'expected_state': {'vehicle.acTemp': 24}},
    {'input': '导航到西湖', 'expected_calls': ['navigation_start'], 'expected_state': {'navigation.destination': '西湖'}},
    {'input': '帮我买杯咖啡', 'expected_calls': ['flashbuy', 'flashbuy', 'flashbuy'], 'expected_state': {'flashbuy.status': 'preview'}},
]


async def run_cases(cases: list[dict] | None = None) -> list[dict]:
    scores = []
    for case in CASES if cases is None else cases:
        # 每个用例创建全新运行时，防止上一个用例的业务状态、历史或任务影响结果。
        runtime = await build_study_runtime()
        try:
            reply = await runtime.app.send(case['input'])
            # 有后台任务时必须等它结束，再检查状态；接受回执不代表工具已执行完。
            for task_id in reply['task_ids']:
                await runtime.app.wait_for_task(task_id)
            # 只取 Service 真正执行过的工具，不能用模型计划或回复文本冒充实际调用。
            calls = [detail for component, action, detail in runtime.trace.entries
                     if component == 'Service' and action == 'execute']
            scores.append(score_trace(case, calls, runtime.service.service.snapshot()))
        finally:
            # 评分或执行失败也清理任务/订阅，使下一个用例独立启动。
            await runtime.close()
    return scores
