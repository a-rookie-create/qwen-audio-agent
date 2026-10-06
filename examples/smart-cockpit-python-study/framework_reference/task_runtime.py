"""为什么后台执行时还能聊天？对应 TaskManager、TaskOperations、SessionTaskCoordinator。

任务记录用字典简写；owner/session 隔离、持久化、恢复和取消机制省略。
后台异步执行() 表示排队调度，无需学习 asyncio 或线程实现。
"""


class TaskManager:
    def create(self, objective, runner):
        task = {'id': 生成任务ID(), 'objective': objective, 'status': 'queued'}
        保存任务记录(task)
        后台异步执行(self.execute, task, runner)
        return task                         # 立即返回，执行尚未完成。

    def execute(self, task, runner):
        task['status'] = 'running'
        try:
            result = runner(task)
            task.update(status='completed', result=result)
        except Exception as error:
            task.update(status='failed', result=str(error))
        保存任务记录(task)
        发布待通知事件(task)                 # 不在这里直接控制音频播放。


class TaskOperations:
    def __init__(self, tasks, backend):
        self.tasks, self.backend = tasks, backend

    def submit(self, objective):
        # 将“何时执行”交给 TaskManager，将“怎样联系后台”交给 backend。
        return self.tasks.create(
            objective, runner=lambda task: self.backend.run(task),
        )


class SessionTaskCoordinator:
    def __init__(self, tasks, session):
        self.session = session
        订阅此用户会话的任务通知(tasks, self.on_result)

    def on_result(self, task):
        self.session.on_background_result(task['result'])
        # 真实框架继续跟踪播报回执；送入模型不等于用户已听完。
