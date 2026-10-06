"""天气查询经可替换的 ScenarioServices；默认结果明确属于离线演示。"""
from service.tools.shared import ToolContext
from study_support import ToolResult


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    weather = ctx.services.weather(args.get('city') or '杭州')
    ctx.update('weather', weather)
    return ctx.result(f"{weather['city']}：{weather['temperature']} 度，{weather['condition']}",
                      ['weather'], {'weather': weather})
