"""场景事件怎样影响对话？对应 environment-events 与 assistant/event。
只展示三种行为；事件 Schema、限流、去重省略。
"""


def select_assistant_profile(profile_id):
    校验允许的人设ID(profile_id)
    更新当前实时会话人设(profile_id)  # 同一会话更新，不重新创建一套 Agent。


def navigation_preference_changed(data):
    静默更新前台上下文(data)         # 环境事实不是新的用户话语。


def skill_triggered(data):
    安排一次自然提醒(data)           # 只提醒，不执行提醒文字中的命令。
