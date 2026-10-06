"""三个固定工具管理技能，不动态注册新工具；保存后规则立刻刷新。"""
from service.tools.shared import ToolContext
from study_support import ToolResult


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    if name == 'custom_skill_list':
        return ctx.result('已读取技能目录', data={'skills': ctx.skills.list(ctx.cockpit_id)})
    if name == 'custom_skill_create':
        skill = ctx.skills.upsert(ctx.cockpit_id, args)
        ctx.on_skills_changed()
        ctx.on_activity({'category': 'custom_skills', 'status': 'skills_changed'})
        return ctx.result('技能已保存，尚未执行', data={'skill': skill})
    if name == 'custom_skill_load':
        skill = ctx.skills.get(ctx.cockpit_id, args['skill_name'])
        if not skill:
            raise ValueError('找不到技能')
        return ctx.result('已加载技能定义', data={'skill': skill})
    raise ValueError('未知技能工具')
