# ============================================
# FLAVOUR FLEET — Cart Routes Blueprint
# ============================================

from flask import Blueprint, request, jsonify
from db import carts_col, menu_col
from helpers import get_user_id
from routes.menu import normalize_menu_item

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


def _get_menu_item(item_id):
    return menu_col.find_one({
        'item_id': item_id,
        'is_deleted': {'$ne': True},
        'active': {'$ne': False},
    })


def _canonicalize_cart_item(data):
    item_id = str(data.get('id') or data.get('item_id') or '').strip()
    if not item_id:
        raise ValueError('Missing item id')

    quantity = max(1, int(data.get('quantity', 1) or 1))
    menu_item = _get_menu_item(item_id)
    if menu_item:
        menu_item = normalize_menu_item(dict(menu_item))
        return {
            'id': menu_item.get('item_id', item_id),
            'name': menu_item.get('name', data.get('name', 'Menu item')),
            'price': float(menu_item.get('price', 0)),
            'image': menu_item.get('image', data.get('image', '')),
            'restaurant': menu_item.get('restaurant', data.get('restaurant', '')),
            'quantity': quantity,
        }

    return {
        'id': item_id,
        'name': data.get('name', 'Menu item'),
        'price': float(data.get('price', 0)),
        'image': data.get('image', ''),
        'restaurant': data.get('restaurant', ''),
        'quantity': quantity,
    }


def _sync_cart_items(uid, items):
    canonical_items = []
    changed = False

    for item in items:
        try:
            canonical = _canonicalize_cart_item(item)
        except (TypeError, ValueError):
            changed = True
            continue

        if canonical != item:
            changed = True
        canonical_items.append(canonical)

    if changed:
        carts_col.update_one(
            {'user_id': uid},
            {'$set': {'items': canonical_items}},
            upsert=True,
        )

    return canonical_items


@cart_bp.route('', methods=['GET'])
def get_cart():
    uid = get_user_id()
    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart and 'items' in cart else []
    items = _sync_cart_items(uid, items)
    return jsonify({'success': True, 'items': items})


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    uid = get_user_id()
    data = request.get_json() or {}
    try:
        item = _canonicalize_cart_item(data)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid cart item'}), 400

    cart = carts_col.find_one({'user_id': uid})
    if not cart:
        carts_col.insert_one({'user_id': uid, 'items': [item]})
    else:
        items = _sync_cart_items(uid, cart.get('items', []))
        existing = next((i for i in items if i['id'] == item['id']), None)
        if existing:
            carts_col.update_one(
                {'user_id': uid, 'items.id': item['id']},
                {'$inc': {'items.$.quantity': item['quantity']}}
            )
        else:
            carts_col.update_one(
                {'user_id': uid},
                {'$push': {'items': item}}
            )

    updated = carts_col.find_one({'user_id': uid})
    items = _sync_cart_items(uid, updated.get('items', []) if updated else [])
    return jsonify({
        'success': True,
        'message': f"{item['name']} added to cart!",
        'items': items,
    })


@cart_bp.route('/update', methods=['PUT'])
def update_cart_item():
    uid = get_user_id()
    data = request.get_json()
    item_id = data.get('id')
    quantity = int(data.get('quantity', 1))

    if quantity <= 0:
        carts_col.update_one(
            {'user_id': uid},
            {'$pull': {'items': {'id': item_id}}}
        )
    else:
        carts_col.update_one(
            {'user_id': uid, 'items.id': item_id},
            {'$set': {'items.$.quantity': quantity}}
        )

    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart else []
    items = _sync_cart_items(uid, items)
    return jsonify({'success': True, 'items': items})


@cart_bp.route('/remove/<item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    uid = get_user_id()
    carts_col.update_one(
        {'user_id': uid},
        {'$pull': {'items': {'id': item_id}}}
    )
    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart else []
    items = _sync_cart_items(uid, items)
    return jsonify({'success': True, 'message': 'Item removed', 'items': items})


@cart_bp.route('/clear', methods=['DELETE'])
def clear_cart():
    uid = get_user_id()
    carts_col.update_one({'user_id': uid}, {'$set': {'items': []}})
    return jsonify({'success': True, 'message': 'Cart cleared'})
