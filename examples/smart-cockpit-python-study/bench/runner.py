"""评估流程是什么？原 bench 的多种 runner 在此教学归纳。
文本模型、受控实时模型、完整 Gateway 系统需要分别评估。
"""


def run_cases(cases, path):
    scores = []
    for case in cases:
        重置场景和对话()
        trace = 按选定路径执行并记录(case, path)
        scores.append(score_trace(case, trace))
    return 汇总分数并记录评估范围(scores)
