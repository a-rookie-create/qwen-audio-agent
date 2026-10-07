"""学习用例评分：比较实际工具调用与状态，不冒充原项目评估算法。"""
from __future__ import annotations


def get_path(value: dict, path: str):
    # 将 vehicle.acTemp 这样的路径逐级取值，便于用例只指定关注的状态字段。
    for key in path.split('.'):
        value = value[key]
    return value


def score_trace(case: dict, calls: list[str], state: dict) -> dict:
    # 调用列表要求顺序与次数都一致；状态只检查用例指定的字段，两项同时正确才通过。
    calls_ok = calls == case['expected_calls']
    state_ok = all(get_path(state, path) == expected for path, expected in case.get('expected_state', {}).items())
    return {'input': case['input'], 'passed': calls_ok and state_ok, 'actual_calls': calls,
            'calls_ok': calls_ok, 'state_ok': state_ok}
