"""可运行的场景配置；默认只返回对象，可选择导出 JSON 便于观察。"""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from gateway.environment_events import load_profile
from study_support import ToolDefinition


@dataclass
class GatewayConfig:
    profile_id: str = 'healer'
    profile_text: str = ''
    frontend_tools: list[str] | None = None


def create_cockpit_frontend_mcp_configuration(tools: list[ToolDefinition]) -> dict:
    # 将工具对象投影为可观察的目录配置，不在这里调用工具或创建业务状态。
    return {'transport': 'in-process', 'surface': 'frontend', 'tools': [tool.name for tool in tools]}


def write_cockpit_frontend_profile_bundle(tools: list[ToolDefinition], root: Path | None = None) -> GatewayConfig:
    # 默认人设从 Markdown 读取，工具名来自 Service 的前台目录。
    config = GatewayConfig('healer', load_profile('healer'), [tool.name for tool in tools])
    if root:
        # 只有传入输出目录才落盘；默认装配只返回内存中的配置对象。
        root.mkdir(parents=True, exist_ok=True)
        (root / 'profile.json').write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2))
    return config
