"""场景事件的实际校验和投递；人设、静默事实、温度提醒各有明确路径。"""
from pathlib import Path
from dataclasses import dataclass

PROFILE_IDS = {'healer', 'action', 'sharp'}


@dataclass
class AgentDelivery:
    mode: str
    text: str
    name: str = ''
    data: dict | None = None
    profile_id: str = ''


def load_profile(profile_id: str) -> str:
    if profile_id not in PROFILE_IDS:
        raise ValueError('未知人设 ID')
    return (Path(__file__).parent / 'assistant' / (profile_id + '.md')).read_text()


def select_assistant_profile(event: dict) -> AgentDelivery:
    profile_id = event['data']['profile']
    return AgentDelivery('handle', load_profile(profile_id), profile_id=profile_id)


def navigation_preference_changed(event: dict) -> AgentDelivery:
    data = event['data']
    if data.get('strategy') not in {0, 13, 5, 4, 11, 14, 2}:
        raise ValueError('未知导航偏好')
    return AgentDelivery('context', '已更新路线偏好', event['name'], data)


def skill_triggered(event: dict) -> AgentDelivery:
    data = event['data']
    trigger = data['trigger']
    matches = lambda t: trigger.get('min', 16) <= t <= trigger.get('max', 32)
    if matches(data['previousTemperature']) or not matches(data['temperature']):
        raise ValueError('没有观察到进入温度条件的变化')
    return AgentDelivery('respond', '温度提醒：' + data['reminder'], event['name'], data)
    # 只是提醒内容，不把提醒字符串解析成新的工具指令。


CLIENT_EVENT_DEFINITIONS = {
    'cockpit.assistant_profile.selected': select_assistant_profile,
    'cockpit.navigation.preference_changed': navigation_preference_changed,
    'cockpit.skill.triggered': skill_triggered,
}
