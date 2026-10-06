"""如何判断 Agent 做对了？对应原 scoreTrace。
具体对齐和评分算法省略，保留检查的问题。
"""


def score_trace(case, trace):
    return 检查工具名参数调用轮次及最终状态(case, trace)
    # 还应检查不该调用的工具和回应质量；不在这里重新造准确率公式。
