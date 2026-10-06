"""投影和事件队列是什么？对应 projections/cockpit-state、environment-events。
投影整理数据，队列暂存待发事件；二者不执行车辆业务。
"""


def apply_cockpit_state_update(previous, event):
    return event['state']  # 原版还保留未变化领域的对象引用。


def skill_triggered_event(activity):
    return 将温度触发活动整理成客户端事件(activity)


class CockpitEnvironmentOutbox:
    def enqueue(self, event):
        有界保存待发送事件(event)       # 原版最多 16 条。

    def flush(self, gateway):
        丢弃超过30秒的旧提醒()
        将待发事件交给Gateway(gateway)

    def restore_context(self):
        恢复最新环境事实()             # 重连不重放过期提醒。
