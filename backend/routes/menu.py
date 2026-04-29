# ============================================
# FLAVOUR FLEET — Menu Routes Blueprint
# ============================================

from flask import Blueprint, request, jsonify
from db import menu_col

menu_bp = Blueprint('menu', __name__, url_prefix='/api/menu')

VEG_ITEM_IDS = {
    'p1', 'p4', 'i3', 'i5', 'm3', 'pa2', 'pa3', 'c3',
    'sa2', 'sa3', 'd1', 'd2', 'd3', 'd4',
}

INR_PRICE_BY_ITEM_ID = {
    'p1': 299, 'p2': 349, 'p3': 399, 'p4': 399, 'p5': 349,
    'b1': 199, 'b2': 349, 'b3': 269, 'b4': 299,
    's1': 449, 's2': 349, 's3': 499,
    'i1': 349, 'i2': 449, 'i3': 299, 'i4': 399, 'i5': 249,
    'm1': 199, 'm2': 249, 'm3': 199, 'm4': 199,
    'pa1': 349, 'pa2': 249, 'pa3': 499, 'pa4': 349,
    'c1': 299, 'c2': 399, 'c3': 199,
    'sa1': 199, 'sa2': 249, 'sa3': 199,
    'd1': 149, 'd2': 169, 'd3': 179, 'd4': 119,
}


def build_public_menu_query():
    return {
        'is_deleted': {'$ne': True},
        'active': {'$ne': False},
    }


def infer_is_veg(item):
    explicit = item.get('is_veg')
    if explicit is not None:
        if isinstance(explicit, str):
            return explicit.lower() in {'yes', 'true', 'veg', 'vegan'}
        return bool(explicit)

    if item.get('item_id') in VEG_ITEM_IDS:
        return True

    badge = str(item.get('badge', '')).lower()
    return badge in {'veg', 'vegan'}


def normalize_menu_item(item):
    item_id = item.get('item_id')
    if item_id in INR_PRICE_BY_ITEM_ID:
        item['price'] = INR_PRICE_BY_ITEM_ID[item_id]
    item['is_veg'] = infer_is_veg(item)
    return item


@menu_bp.route('', methods=['GET'])
def get_menu():
    category = request.args.get('category')
    query = build_public_menu_query()
    if category and category != 'all':
        query['category'] = category

    items = list(menu_col.find(query))
    for item in items:
        item['_id'] = str(item['_id'])
        normalize_menu_item(item)

    return jsonify({'success': True, 'items': items, 'count': len(items)})


@menu_bp.route('/<item_id>', methods=['GET'])
def get_menu_item(item_id):
    query = build_public_menu_query()
    query['item_id'] = item_id
    item = menu_col.find_one(query)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    item['_id'] = str(item['_id'])
    normalize_menu_item(item)
    return jsonify({'success': True, 'item': item})
