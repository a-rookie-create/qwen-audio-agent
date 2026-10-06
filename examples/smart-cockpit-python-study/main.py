"""项目执行入口：python3 main.py --demo --trace。"""
from __future__ import annotations
import argparse
import asyncio
from overview import run_demo
from bench.runner import run_cases
from bootstrap.start import build_study_runtime


async def interactive() -> None:
    runtime = await build_study_runtime()
    runtime.app.voice.on_message = lambda event: print('助手：' + event['text'])
    print('离线学习模式，可输入：你好、空调调到24度、播放晴天、帮我买杯咖啡；exit 退出。')
    try:
        while True:
            try:
                text = await asyncio.to_thread(input, '你：')
            except EOFError:
                break
            if text.strip().lower() in {'exit', 'quit'}:
                break
            await runtime.app.send(text)
    finally:
        await runtime.close()


async def async_main() -> None:
    parser = argparse.ArgumentParser(description='智能座舱 Python 学习版，默认完全离线')
    group = parser.add_mutually_exclusive_group()
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
            raise SystemExit(1)
    else:
        await run_demo(args.trace)


def main() -> None:
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
