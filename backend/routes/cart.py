# ============================================
# FLAVOUR FLEET — Cart Routes Blueprint
# ============================================

from flask import Blueprint, request, jsonify
from db import carts_col
from helpers import get_user_id

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@cart_bp.route('', methods=['GET'])
def get_cart():
    uid = get_user_id()
    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart and 'items' in cart else []
    return jsonify({'success': True, 'items': items})


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    uid = get_user_id()
    data = request.get_json()

    item = {
        'id': data['id'],
        'name': data['name'],
        'price': float(data['price']),
        'image': data.get('image', ''),
        'restaurant': data.get('restaurant', ''),
        'quantity': int(data.get('quantity', 1))
    }

    cart = carts_col.find_one({'user_id': uid})
    if not cart:
        carts_col.insert_one({'user_id': uid, 'items': [item]})
    else:
        existing = next((i for i in cart['items'] if i['id'] == item['id']), None)
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
    return jsonify({
        'success': True,
        'message': f"{item['name']} added to cart!",
        'items': updated['items']
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
    return jsonify({'success': True, 'message': 'Item removed', 'items': items})


@cart_bp.route('/clear', methods=['DELETE'])
def clear_cart():
    uid = get_user_id()
    carts_col.update_one({'user_id': uid}, {'$set': {'items': []}})
    return jsonify({'success': True, 'message': 'Cart cleared'})
