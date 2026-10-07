"""三个固定工具管理技能，不动态注册新工具；保存后规则立刻刷新。"""
from service.tools.shared import ToolContext
from study_support import ToolResult


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    if name == 'custom_skill_list':
        # 仅查询技能定义，不执行工作流，也不检查温度条件是否命中。
        return ctx.result('已读取技能目录', data={'skills': ctx.skills.list(ctx.cockpit_id)})
    if name == 'custom_skill_create':
        # 先保存并校验定义，再刷新规则基线；创建时温度已满足条件也不会立刻提醒。
        skill = ctx.skills.upsert(ctx.cockpit_id, args)
        ctx.on_skills_changed()
        # 调用 Service 传入的活动回调，通知技能目录变化，不是技能已运行。
        ctx.on_activity({'category': 'custom_skills', 'status': 'skills_changed'})
        return ctx.result('技能已保存，尚未执行', data={'skill': skill})
    if name == 'custom_skill_load':
        # 只返回定义；前台收到 workflow 后将 instructions 规划成已有工具再执行。
        skill = ctx.skills.get(ctx.cockpit_id, args['skill_name'])
        if not skill:
            raise ValueError('找不到技能')
        return ctx.result('已加载技能定义', data={'skill': skill})
    raise ValueError('未知技能工具')
