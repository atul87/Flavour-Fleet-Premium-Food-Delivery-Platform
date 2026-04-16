# ============================================
# FLAVOUR FLEET — Payments Routes Blueprint
# ============================================

from datetime import datetime
from bson import ObjectId
from flask import Blueprint, request, jsonify
from db import payments_col, orders_col
from helpers import login_required, get_user_id, logger

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payments_bp.route('', methods=['GET'])
@login_required
def get_payments():
    """Get payment history for the current user."""
    uid = get_user_id()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    total = payments_col.count_documents({'user_id': uid})
    records = list(
        payments_col.find({'user_id': uid})
        .sort('created_at', -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    for r in records:
        r['_id'] = str(r['_id'])

    return jsonify({
        'success': True,
        'payments': records,
        'total': total,
        'page': page,
        'per_page': per_page
    })


@payments_bp.route('/<order_id>', methods=['GET'])
@login_required
def get_payment_by_order(order_id):
    """Get payment record for a specific order."""
    uid = get_user_id()
    record = payments_col.find_one({'order_id': order_id, 'user_id': uid})
    if not record:
        return jsonify({'success': False, 'message': 'Payment not found'}), 404
    record['_id'] = str(record['_id'])
    return jsonify({'success': True, 'payment': record})


def record_payment(user_id, order_id, amount, method, status='completed'):
    """Record a payment — called internally from the orders blueprint."""
    payment = {
        'user_id': user_id,
        'order_id': order_id,
        'amount': round(amount, 2),
        'method': method,        # "UPI", "Credit Card", "Debit Card", "COD"
        'status': status,        # "completed", "pending", "failed", "refunded"
        'created_at': datetime.utcnow().isoformat(),
    }
    result = payments_col.insert_one(payment)
    payment['_id'] = str(result.inserted_id)
    logger.info('Payment recorded: %s amount=%.2f method=%s', order_id, amount, method)
    return payment
