"""闪购为什么有多步？对应 executeFlashbuyTool。
原版是 Demo 商品与订单状态；这里不涉及真实交易。
"""


def execute(name, arguments, state):
    if arguments['action'] == 'confirm_order':
        if 已存在订单(state):
            return '避免重复下单'
        if not 已有订单预览(state):
            return '先预览订单'
        if arguments.get('confirmed') is not True:
            return '需要用户明确确认'
        return 创建Demo订单并更新状态(state)
    return 搜索加购或预览等操作(arguments, state)
