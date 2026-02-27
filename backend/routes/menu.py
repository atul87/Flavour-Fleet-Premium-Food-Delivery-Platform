# ============================================
# FLAVOUR FLEET — Menu Routes Blueprint
# ============================================

from flask import Blueprint, request, jsonify
from db import menu_col

menu_bp = Blueprint('menu', __name__, url_prefix='/api/menu')


@menu_bp.route('', methods=['GET'])
def get_menu():
    category = request.args.get('category')
    query = {'is_deleted': {'$ne': True}}
    if category and category != 'all':
        query['category'] = category

    items = list(menu_col.find(query))
    for item in items:
        item['_id'] = str(item['_id'])

    return jsonify({'success': True, 'items': items, 'count': len(items)})


@menu_bp.route('/<item_id>', methods=['GET'])
def get_menu_item(item_id):
    item = menu_col.find_one({'item_id': item_id})
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    item['_id'] = str(item['_id'])
    return jsonify({'success': True, 'item': item})
