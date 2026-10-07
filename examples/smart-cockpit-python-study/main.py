"""项目执行入口：python3 main.py --demo --trace。"""
from __future__ import annotations
import argparse
import asyncio
from overview import run_demo
from bench.runner import run_cases
from bootstrap.start import build_study_runtime


async def interactive() -> None:
    runtime = await build_study_runtime()
    # 保存打印函数为消息回调；前台回复和异步后台结果都会通过此回调展示。
    runtime.app.voice.on_message = lambda event: print('助手：' + event['text'])
    print('离线学习模式，可输入：你好、空调调到24度、播放晴天、帮我买杯咖啡；exit 退出。')
    try:
        while True:
            try:
                # input 会阻塞线程；移到工作线程后，事件循环仍能处理后台任务和提醒。
                text = await asyncio.to_thread(input, '你：')
            except EOFError:
                break
            if text.strip().lower() in {'exit', 'quit'}:
                break
            await runtime.app.send(text)
    finally:
        # 正常退出、输入结束或执行报错都要关闭订阅和未完成任务。
        await runtime.close()


async def async_main() -> None:
    parser = argparse.ArgumentParser(description='智能座舱 Python 学习版，默认完全离线')
    group = parser.add_mutually_exclusive_group()
    # 三种模式互斥；没有选择时走最后的演示分支。
    group.add_argument('--demo', action='store_true', help='运行完整演示（默认）')
    group.add_argument('--interactive', action='store_true', help='交互式文字输入')
    group.add_argument('--benchmark', action='store_true', help='运行四个学习回归用例')
    parser.add_argument('--trace', action='store_true', help='显示演示调用链')
    args = parser.parse_args()
    if args.interactive:
        await interactive()
    elif args.benchmark:
        scores = await run_cases()
        for score in scores:
            print(('PASS' if score['passed'] else 'FAIL'), score)
        if not all(score['passed'] for score in scores):
            # 非零退出码让命令行/自动检查能识别评估失败。
            raise SystemExit(1)
    else:
        await run_demo(args.trace)


def main() -> None:
    # 同步入口创建事件循环，驱动所有 async 方法和后台 Task；结束时关闭循环。
    asyncio.run(async_main())


if __name__ == '__main__':
    # 直接运行本文件才启动程序，其他模块 import main 不会自动运行演示。
    main()
