"""可选环境加载，不默认读取原项目密钥文件。"""
from __future__ import annotations
import os
from pathlib import Path


def load_cockpit_environment(env: dict | None = None, files: tuple[Path, ...] = ()) -> dict:
    values = dict(os.environ if env is None else env)
    for path in files:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or '=' not in stripped:
                continue
            key, value = stripped.split('=', 1)
            values.setdefault(key.strip(), value.strip().strip(chr(34)).strip(chr(39)))
    return values
