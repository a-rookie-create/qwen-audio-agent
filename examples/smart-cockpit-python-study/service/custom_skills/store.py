"""保存自定义技能意味着什么？对应 CustomSkillStore。
技能是工作流说明或事件规则；保存不等于立即执行。
"""


class CustomSkillStore:
    def list(self, cockpit_id):
        return 读取该座舱技能目录(cockpit_id)

    def get(self, cockpit_id, name):
        return 读取完整技能定义(cockpit_id, name)

    def upsert(self, cockpit_id, definition):
        校验工作流或温度事件定义(definition)
        return 保存技能JSON(cockpit_id, definition)
