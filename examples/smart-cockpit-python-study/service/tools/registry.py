"""怎样从工具名找到业务函数？对应 registry 与 surface-routing。
manifest 是工具说明/参数，execute 是实现；路由决定谁能调用。
"""


class ToolRegistry:
    def __init__(self):
        self.functions = 从六组清单建立工具名到执行函数的映射()
        self.routing = 读取前后台领域路由()

    def definitions_for(self, side):
        return 取出属于该侧的工具定义(self.routing, side)
        # 默认前台 37 个，后台 1 个 flashbuy。

    def execute(self, name, arguments, state):
        function = self.functions[name]
        return function(name, arguments, state)
