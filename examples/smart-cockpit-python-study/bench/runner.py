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
        runtime = await build_study_runtime()
        try:
            reply = await runtime.app.send(case['input'])
            for task_id in reply['task_ids']:
                await runtime.app.wait_for_task(task_id)
            calls = [detail for component, action, detail in runtime.trace.entries
                     if component == 'Service' and action == 'execute']
            scores.append(score_trace(case, calls, runtime.service.service.snapshot()))
        finally:
            await runtime.close()
    return scores
