# ============================================
# FLAVOUR FLEET — Offers Routes Blueprint
# ============================================

from flask import Blueprint, request, jsonify
from db import offers_col, carts_col
from helpers import get_user_id

offers_bp = Blueprint('offers', __name__, url_prefix='/api/offers')


@offers_bp.route('', methods=['GET'])
def get_offers():
    offers = list(offers_col.find({'is_deleted': {'$ne': True}}))
    for o in offers:
        o['_id'] = str(o['_id'])
    return jsonify({'success': True, 'offers': offers})


@offers_bp.route('/validate', methods=['POST'])
def validate_offer():
    data = request.get_json()
    code = data.get('code', '').upper().strip()

    offer = offers_col.find_one({'code': code})
    if not offer:
        return jsonify({'success': False, 'message': 'Invalid promo code'}), 404

    # Calculate discount
    uid = get_user_id()
    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart and 'items' in cart else []
    subtotal = sum(i['price'] * i['quantity'] for i in items)

    discount_amount = 0
    dtype = offer.get('discount_type', 'percent')
    dval = offer.get('discount_value', 0)

    if dtype == 'percent':
        discount_amount = round(subtotal * dval / 100, 2)
    elif dtype == 'flat':
        discount_amount = dval
    elif dtype == 'delivery':
        discount_amount = 4.99 if subtotal <= 30 else 0

    return jsonify({
        'success': True,
        'message': f"Promo applied: {offer['title']}",
        'code': code,
        'discount_type': dtype,
        'discount_value': dval,
        'discount_amount': discount_amount,
        'label': offer.get('title', '')
    })
