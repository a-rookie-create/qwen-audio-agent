"""天气查询经可替换的 ScenarioServices；默认结果明确属于离线演示。"""
from service.tools.shared import ToolContext
from study_support import ToolResult


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    # 未指定城市使用杭州；天气数据来自注入的业务适配对象。
    weather = ctx.services.weather(args.get('city') or '杭州')
    ctx.update('weather', weather)  # 查询结果也保存进状态，供客户端面板同步显示。
    return ctx.result(f"{weather['city']}：{weather['temperature']} 度，{weather['condition']}",
                      ['weather'], {'weather': weather})
