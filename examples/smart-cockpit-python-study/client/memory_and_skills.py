"""记忆和技能分别从哪里读？对应 useGatewayMemory、useCockpitSkills。
记忆属于 Gateway；座舱自定义技能属于 Service。
"""


class GatewayMemoryController:
    def load(self):
        return 向Gateway发送HTTP_GET('/api/memory')

    def remove(self, item):
        向Gateway发送HTTP_PATCH('/api/memory', 生成带版本的删除操作(item))
        # 原版处理版本冲突并刷新列表，本页省略。


class CockpitSkillsController:
    def list(self):
        return 向Service发送HTTP_GET('/api/cockpit/skills')

    def load(self, skill_id):
        return 向Service发送HTTP_GET('/api/cockpit/skills/' + skill_id)

    def remove(self, skill_id):
        向Service发送HTTP_DELETE('/api/cockpit/skills/' + skill_id)
