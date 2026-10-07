"""静态导入六个执行器，IDE 可跳转；原 38 个清单决定目录与路由。"""
from __future__ import annotations
import json
import math
from pathlib import Path
from service.tools.vehicle.execute import execute as execute_vehicle
from service.tools.navigation.execute import execute as execute_navigation
from service.tools.music.execute import execute as execute_music
from service.tools.weather.execute import execute as execute_weather
from service.tools.flashbuy.execute import execute as execute_flashbuy
from service.tools.custom_skills.execute import execute as execute_skills
from service.tools.shared import ToolContext
from study_support import ToolDefinition, ToolResult

# 字典的值是已 import 的函数；后续按领域取出函数，再传参数调用。
EXECUTORS = {'vehicle': execute_vehicle, 'navigation': execute_navigation, 'music': execute_music,
             'weather': execute_weather, 'flashbuy': execute_flashbuy, 'custom-skills': execute_skills}
ROOT = Path(__file__).parent


class ToolRegistry:
    def __init__(self) -> None:
        # 路由决定每个领域属于前台还是后台，manifest 提供工具名、说明和参数 Schema。
        self.routing = json.loads((ROOT / 'surface-routing.json').read_text())['domains']
        self.definitions: dict[str, ToolDefinition] = {}
        for domain in EXECUTORS:
            # 目录用下划线，清单领域名用连字符；这里只转换路径，保持领域名不变。
            manifest = json.loads((ROOT / domain.replace('-', '_') / 'manifest.json').read_text())
            for tool in manifest['functions']:
                if tool.get('enabled') is False:
                    continue
                if tool['name'] in self.definitions:
                    # 工具名是全局索引键，重复会导致执行目标不明确，因此启动时直接报错。
                    raise ValueError('工具名重复')
                self.definitions[tool['name']] = ToolDefinition(tool['name'], tool['description'],
                    tool['parameters'], domain, self.routing[domain])

    def definitions_for(self, side: str) -> list[ToolDefinition]:
        # 返回指定工具面的目录；禁用条目在初始化时已经被跳过。
        return [d for d in self.definitions.values() if d.surface == side]

    async def execute(self, name: str, arguments: dict, context: ToolContext) -> ToolResult:
        if name not in self.definitions:
            raise ValueError('未知工具：' + name)
        definition = self.definitions[name]
        # 先校验参数再进入执行器，避免无效输入造成部分业务更新。
        self.validate(definition.input_schema, arguments)
        # 例如 vehicle_temperature_control 的 domain 是 vehicle，调用 execute_vehicle。
        return await EXECUTORS[definition.domain](name, arguments, context)

    @staticmethod
    def validate(schema: dict, args: dict) -> None:
        # staticmethod 不接收 self，这段校验只依赖传入的 Schema 和参数。
        # 学习版实现必填、基本类型与枚举校验，不冒充完整 JSON Schema 引擎。
        for key in schema.get('required', []):
            if key not in args:
                raise ValueError('缺少参数：' + key)
        types = {'string': str, 'number': (int, float), 'integer': int,
                 'boolean': bool, 'array': list, 'object': dict}
        for key, value in args.items():
            spec = schema.get('properties', {}).get(key)
            if not spec:
                raise ValueError('未知参数：' + key)
            expected = types.get(spec.get('type'))
            # Python 的 bool 是 int 子类，需要额外排除，避免 True 被当成温度或数量。
            if expected and (not isinstance(value, expected) or
                    (spec.get('type') in {'number', 'integer'} and isinstance(value, bool))):
                raise ValueError('参数类型不正确：' + key)
            if spec.get('type') in {'number', 'integer'} and not math.isfinite(value):
                # NaN/无穷大虽是浮点数，也不能用于计算和保存业务状态。
                raise ValueError('参数必须是有限数值：' + key)
            if 'enum' in spec and value not in spec['enum']:
                raise ValueError('参数枚举不正确：' + key)
