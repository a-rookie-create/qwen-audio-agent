"""温度提醒为什么不需要后台持续轮询？对应 TemperatureSkillRules。
Service 观察权威状态变化，满足进入条件时发布事件。
"""


def normalize_temperature_trigger(trigger):
    return 校验温区与温度范围(trigger)


class TemperatureSkillRules:
    def prepare(self, store, skills):
        self.rules = 从技能中取出温度规则(skills)
        self.previous = store.snapshot()  # 建立基线，加载规则不立即提醒。
        订阅状态变化(store, self.observe)

    def observe(self, new_state):
        for rule in self.rules:
            if 条件外进入条件内(rule, self.previous, new_state):
                发布温度触发活动(rule, new_state)
        self.previous = new_state
        # 活动经 SSE → 客户端 → GCP → 前台提醒，持续在范围内不重复触发。
