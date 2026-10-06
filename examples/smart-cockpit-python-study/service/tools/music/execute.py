"""音乐操作怎样同步到 UI？对应 executeMusicTool。
曲库选择、播放或音量操作都更新 Service 状态。
"""


def execute(name, arguments, state):
    if name == 'music_state_query':
        return state.snapshot()['music']
    changes = 计算音乐状态修改(name, arguments)
    return state.update('music', changes)  # SSE 会把变化送到音乐面板。
