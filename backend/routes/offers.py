# ============================================
# FLAVOUR FLEET — Offers Routes Blueprint
# ============================================

from flask import Blueprint, request, jsonify
from db import offers_col, carts_col
from helpers import get_user_id

offers_bp = Blueprint('offers', __name__, url_prefix='/api/offers')


def get_public_offer(code):
    return offers_col.find_one({
        'code': code.upper(),
        'is_deleted': {'$ne': True},
        'active': {'$ne': False},
    })


def validate_offer_for_subtotal(code, subtotal, delivery_fee=49):
    offer = get_public_offer(code)
    if not offer:
        return None, 'Invalid or inactive promo code', 404

    min_order = float(offer.get('min_order', 0) or 0)
    if subtotal < min_order:
        return None, f'Minimum order for this promo is INR {min_order:.2f}', 400

    return offer, None, None


def calculate_offer_discount(offer, subtotal, delivery_fee=49):
    discount_amount = 0
    dtype = offer.get('discount_type', 'percent')
    dval = float(offer.get('discount_value', 0) or 0)

    if dtype == 'percent':
        discount_amount = round(subtotal * dval / 100, 2)
    elif dtype == 'flat':
        discount_amount = dval
    elif dtype == 'delivery':
        discount_amount = delivery_fee

    return round(max(0, min(discount_amount, subtotal + delivery_fee)), 2)


@offers_bp.route('', methods=['GET'])
def get_offers():
    offers = list(offers_col.find({
        'is_deleted': {'$ne': True},
        'active': {'$ne': False},
    }))
    for o in offers:
        o['_id'] = str(o['_id'])
    return jsonify({'success': True, 'offers': offers})


@offers_bp.route('/validate', methods=['POST'])
def validate_offer():
    data = request.get_json()
    code = data.get('code', '').upper().strip()

    uid = get_user_id()
    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart and 'items' in cart else []
    subtotal = sum(i['price'] * i['quantity'] for i in items)
    delivery_fee = 0 if subtotal > 499 else 49

    offer, error_message, error_status = validate_offer_for_subtotal(code, subtotal, delivery_fee)
    if error_message:
        return jsonify({'success': False, 'message': error_message}), error_status

    discount_amount = calculate_offer_discount(offer, subtotal, delivery_fee)
    dtype = offer.get('discount_type', 'percent')
    dval = float(offer.get('discount_value', 0) or 0)

    return jsonify({
        'success': True,
        'message': f"Promo applied: {offer['title']}",
        'code': code,
        'discount_type': dtype,
        'discount_value': dval,
        'discount_amount': discount_amount,
        'label': offer.get('title', '')
    })
