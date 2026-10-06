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

EXECUTORS = {'vehicle': execute_vehicle, 'navigation': execute_navigation, 'music': execute_music,
             'weather': execute_weather, 'flashbuy': execute_flashbuy, 'custom-skills': execute_skills}
ROOT = Path(__file__).parent


class ToolRegistry:
    def __init__(self) -> None:
        self.routing = json.loads((ROOT / 'surface-routing.json').read_text())['domains']
        self.definitions: dict[str, ToolDefinition] = {}
        for domain in EXECUTORS:
            manifest = json.loads((ROOT / domain.replace('-', '_') / 'manifest.json').read_text())
            for tool in manifest['functions']:
                if tool.get('enabled') is False:
                    continue
                if tool['name'] in self.definitions:
                    raise ValueError('工具名重复')
                self.definitions[tool['name']] = ToolDefinition(tool['name'], tool['description'],
                    tool['parameters'], domain, self.routing[domain])

    def definitions_for(self, side: str) -> list[ToolDefinition]:
        return [d for d in self.definitions.values() if d.surface == side]

    async def execute(self, name: str, arguments: dict, context: ToolContext) -> ToolResult:
        if name not in self.definitions:
            raise ValueError('未知工具：' + name)
        definition = self.definitions[name]
        self.validate(definition.input_schema, arguments)
        return await EXECUTORS[definition.domain](name, arguments, context)

    @staticmethod
    def validate(schema: dict, args: dict) -> None:
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
            if expected and (not isinstance(value, expected) or
                    (spec.get('type') in {'number', 'integer'} and isinstance(value, bool))):
                raise ValueError('参数类型不正确：' + key)
            if spec.get('type') in {'number', 'integer'} and not math.isfinite(value):
                raise ValueError('参数必须是有限数值：' + key)
            if 'enum' in spec and value not in spec['enum']:
                raise ValueError('参数枚举不正确：' + key)
