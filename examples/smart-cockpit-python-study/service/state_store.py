"""谁保存业务状态？对应原 CockpitStateStore。

只展示读取、更新、发布三步。原版还按 cockpitId 隔离状态并维护版本。
"""


class CockpitStateStore:
    def __init__(self):
        self.state = {'vehicle': {}, 'navigation': {}, 'music': {}, 'weather': {}, 'flashbuy': {}}

    def snapshot(self):
        return 复制当前状态(self.state)    # 调用方读取快照，不能偷偷改权威状态。

    def update(self, domain, changes):
        self.state[domain].update(changes)
        更新状态版本()
        发布状态变化(self.snapshot())      # UI 订阅、温度规则观察都由这一步驱动。
        return self.snapshot()
