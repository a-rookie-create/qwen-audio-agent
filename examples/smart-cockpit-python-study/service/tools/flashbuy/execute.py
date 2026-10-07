"""搜索→加购→预览→明确确认；所有商品和订单均为本地演示数据。"""
from __future__ import annotations
from copy import deepcopy
from uuid import uuid4
from service.tools.shared import ToolContext
from study_support import ToolResult

PRODUCTS = [{'id': 'latte', 'name': '拿铁咖啡', 'price': 18},
            {'id': 'tea', 'name': '奶茶', 'price': 12}, {'id': 'meal', 'name': '演示套餐', 'price': 25}]


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    current = ctx.snapshot()['flashbuy']
    action = args['action']
    changes: dict = {}
    # 按 action 推进购物状态，先生成 changes，最后统一提交到 flashbuy 领域。
    if action == 'search':
        query = args.get('query', '')
        results = [p for p in PRODUCTS if query in p['name']]
        changes = {'results': results, 'status': 'searched'}
    elif action in {'add_to_cart', 'update_cart'}:
        # 从固定商品目录取可信价格，不使用调用方自己提供的商品价格。
        item = next((p for p in PRODUCTS if p['id'] == args.get('itemId')), None)
        if item is None:
            raise ValueError('找不到商品')
        quantity = args.get('quantity', 1)
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError('数量必须为正整数')
        # 先移除同商品旧项再追加新数量，表示替换数量而非重复累加同一项。
        cart = [p for p in current['cartItems'] if p['id'] != item['id']]
        cart.append({**item, 'quantity': quantity})
        # 购物车一旦变化，原预览失效，必须重新预览后才能确认订单。
        changes = {'cartItems': cart, 'preview': None, 'status': 'cart'}
    elif action == 'preview_order':
        # 预览只快照商品和计算总价，不创建 order；深拷贝避免后续购物车变化影响预览。
        if not current['cartItems']:
            raise ValueError('购物车为空')
        preview = {'items': deepcopy(current['cartItems']),
                   'total': sum(p['price'] * p['quantity'] for p in current['cartItems']),
                   'address': args.get('address', '演示车位'), 'source': 'offline-demo'}
        changes = {'preview': preview, 'status': 'preview'}
    elif action == 'confirm_order':
        if current['order']:
            # 已有订单时返回原订单，重复确认不会生成第二个演示订单。
            return ctx.result('订单已存在，未重复下单', data={'order': current['order'], 'duplicate': True})
        if not current['preview']:
            raise ValueError('请先预览订单')
        if args.get('confirmed') is not True:
            # 缺少明确确认只返回提示，不调用 ctx.update，也不消耗原预览。
            return ctx.result('需要用户明确确认', data={'requireConfirm': True, 'preview': current['preview']})
        # 只有预览存在且明确确认才创建订单，随后清空购物车和预览。
        changes = {'order': {'id': 'DEMO-' + uuid4().hex[:8], **current['preview']},
                   'cartItems': [], 'preview': None, 'status': 'completed'}
    elif action == 'cancel_order':
        # 清理本地演示购物状态，没有外部商家请求或支付流程。
        changes = {'order': None, 'cartItems': [], 'preview': None, 'status': 'cancelled'}
    else:
        raise ValueError('未知闪购操作')
    # 保存后把新状态作为工具结果交回模型，下一轮模型据此选择下一步动作。
    after = ctx.update('flashbuy', changes)
    text = '已生成演示订单' if action == 'confirm_order' else '闪购步骤完成：' + action
    return ctx.result(text, ['flashbuy'], {'flashbuy': after['flashbuy']})
