"""实际导入所有学习模块，检查语法之外的导入和依赖引用。"""
from pathlib import Path
import importlib
import unittest


class ImportTests(unittest.TestCase):
    def test_all_application_modules_import(self):
        root = Path(__file__).resolve().parents[1]
        for path in sorted(root.rglob('*.py')):
            relative = path.relative_to(root)
            if relative.parts[0] == 'tests' or path.name == '__init__.py':
                continue
            # 将 agent/model.py 转成 agent.model，实际 import 验证模块间引用可解析。
            name = '.'.join(relative.with_suffix('').parts)
            with self.subTest(module=name):
                self.assertIsNotNone(importlib.import_module(name))


if __name__ == '__main__':
    unittest.main()
