"""A teaching model for the guide, not a port of qwen-audio-agent.

Python 3.10+, standard library only. No network, file writes or configuration.
This deliberately omits providers, permissions, persistence and delegation.
"""

import asyncio
import time
from dataclasses import dataclass


@dataclass
class Work:
    id: str
    objective: str
    status: str = "queued"
    notification: str = "none"
    result: str = ""


class TeachingRuntime:
    def __init__(self) -> None:
        self.started_at = time.monotonic()
        self.work_queue: asyncio.Queue[Work] = asyncio.Queue()
        self.notification_queue: asyncio.Queue[Work] = asyncio.Queue()
        self.voice_idle = asyncio.Event()
        self.next_number = 1

    def log(self, message: str) -> None:
        elapsed = time.monotonic() - self.started_at
        print(f"{elapsed:5.2f}s  {message}")

    def submit(self, objective: str) -> Work:
        work = Work(id=f"task_{self.next_number}", objective=objective)
        self.next_number += 1
        self.work_queue.put_nowait(work)
        self.log(f"受理回执 accepted: {work.id}；尚未等待后台结果")
        return work

    async def execute_work(self) -> None:
        while True:
            work = await self.work_queue.get()
            try:
                work.status = "running"
                self.log(f"后台开始工作: {work.objective}")
                await asyncio.sleep(0.20)  # Simulated external work.
                work.result = "已找到测试失败的原因"
                work.status = "completed"
                work.notification = "pending"
                self.log("工作 completed；通知 pending，用户还可以继续说话")
                self.notification_queue.put_nowait(work)
            finally:
                self.work_queue.task_done()

    async def deliver_results(self) -> None:
        while True:
            work = await self.notification_queue.get()
            try:
                await self.voice_idle.wait()
                work.notification = "delivering"
                self.log("当前窗口空闲，领取通知并请求结果播报")
                await asyncio.sleep(0.03)  # Simulated model generation.
                self.log("模型 response.done；通知仍 delivering")
                await asyncio.sleep(0.05)  # Simulated audio scheduling.
                work.notification = "delivered"
                self.log(f"客户端 playback.started；通知 delivered: {work.result}")
            finally:
                self.notification_queue.task_done()

    async def continue_conversation(self) -> None:
        for number in range(1, 5):
            await asyncio.sleep(0.08)
            self.log(f"用户继续对话，第 {number} 段；后台没有堵住这个协程")
        self.voice_idle.set()


async def main() -> None:
    runtime = TeachingRuntime()
    work = runtime.submit("检查项目为什么测试失败")
    background = [
        asyncio.create_task(runtime.execute_work()),
        asyncio.create_task(runtime.deliver_results()),
    ]
    try:
        await runtime.continue_conversation()
        await runtime.work_queue.join()
        await runtime.notification_queue.join()
        runtime.log(f"最终两条状态轴: status={work.status}, notification={work.notification}")
    finally:
        for task in background:
            task.cancel()
        await asyncio.gather(*background, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
