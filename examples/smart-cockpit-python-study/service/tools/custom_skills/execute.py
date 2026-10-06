"""技能工具只管理定义，对应 executeCustomSkillTool。
工作流加载后由 Agent 按工具权限执行；温度规则由 Service 观察状态触发。
"""


def execute(name, arguments, state):
    if name == 'custom_skill_create':
        skill = 保存技能定义(arguments)
        刷新温度规则()
        return skill                     # 保存完成，不立即执行步骤。
    if name == 'custom_skill_load':
        return 加载完整定义(arguments['skill_name'])
    return 列出已保存技能()
