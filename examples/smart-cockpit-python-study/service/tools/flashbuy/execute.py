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
    if action == 'search':
        query = args.get('query', '')
        results = [p for p in PRODUCTS if query in p['name']]
        changes = {'results': results, 'status': 'searched'}
    elif action in {'add_to_cart', 'update_cart'}:
        item = next((p for p in PRODUCTS if p['id'] == args.get('itemId')), None)
        if item is None:
            raise ValueError('找不到商品')
        quantity = args.get('quantity', 1)
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError('数量必须为正整数')
        cart = [p for p in current['cartItems'] if p['id'] != item['id']]
        cart.append({**item, 'quantity': quantity})
        changes = {'cartItems': cart, 'preview': None, 'status': 'cart'}
    elif action == 'preview_order':
        if not current['cartItems']:
            raise ValueError('购物车为空')
        preview = {'items': deepcopy(current['cartItems']),
                   'total': sum(p['price'] * p['quantity'] for p in current['cartItems']),
                   'address': args.get('address', '演示车位'), 'source': 'offline-demo'}
        changes = {'preview': preview, 'status': 'preview'}
    elif action == 'confirm_order':
        if current['order']:
            return ctx.result('订单已存在，未重复下单', data={'order': current['order'], 'duplicate': True})
        if not current['preview']:
            raise ValueError('请先预览订单')
        if args.get('confirmed') is not True:
            return ctx.result('需要用户明确确认', data={'requireConfirm': True, 'preview': current['preview']})
        changes = {'order': {'id': 'DEMO-' + uuid4().hex[:8], **current['preview']},
                   'cartItems': [], 'preview': None, 'status': 'completed'}
    elif action == 'cancel_order':
        changes = {'order': None, 'cartItems': [], 'preview': None, 'status': 'cancelled'}
    else:
        raise ValueError('未知闪购操作')
    after = ctx.update('flashbuy', changes)
    text = '已生成演示订单' if action == 'confirm_order' else '闪购步骤完成：' + action
    return ctx.result(text, ['flashbuy'], {'flashbuy': after['flashbuy']})
