"""可选环境加载，不默认读取原项目密钥文件。"""
from __future__ import annotations
import os
from pathlib import Path


def load_cockpit_environment(env: dict | None = None, files: tuple[Path, ...] = ()) -> dict:
    # 先复制传入配置或进程环境，后续补值不会修改调用方字典或 os.environ。
    values = dict(os.environ if env is None else env)
    for path in files:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or '=' not in stripped:
                continue
            # 只按第一个等号分割，值本身可以含等号；这里仅支持简单 KEY=VALUE。
            key, value = stripped.split('=', 1)
            # setdefault 不覆盖已存在的值：环境配置优先，其次是更早读取的文件。
            values.setdefault(key.strip(), value.strip().strip(chr(34)).strip(chr(39)))
    return values
