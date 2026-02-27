# ============================================
# FLAVOUR FLEET — Addresses Routes Blueprint
# ============================================

from datetime import datetime
from bson import ObjectId
from flask import Blueprint, request, jsonify, session
from db import addresses_col
from helpers import login_required, get_user_id, logger

addresses_bp = Blueprint('addresses', __name__, url_prefix='/api/addresses')


@addresses_bp.route('', methods=['GET'])
@login_required
def get_addresses():
    uid = get_user_id()
    addrs = list(addresses_col.find({'user_id': uid}).sort('is_default', -1))
    for a in addrs:
        a['_id'] = str(a['_id'])
    return jsonify({'success': True, 'addresses': addrs})


@addresses_bp.route('', methods=['POST'])
@login_required
def add_address():
    uid = get_user_id()
    data = request.get_json()

    required = ['label', 'address_line', 'city', 'zip']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400

    # If this is the first address or marked as default, set it
    is_default = data.get('is_default', False)
    if is_default or addresses_col.count_documents({'user_id': uid}) == 0:
        addresses_col.update_many({'user_id': uid}, {'$set': {'is_default': False}})
        is_default = True

    address = {
        'user_id': uid,
        'label': data['label'],           # "Home", "Work", "Other"
        'address_line': data['address_line'],
        'city': data['city'],
        'state': data.get('state', ''),
        'zip': data['zip'],
        'phone': data.get('phone', ''),
        'instructions': data.get('instructions', ''),
        'is_default': is_default,
        'created_at': datetime.utcnow().isoformat(),
    }
    result = addresses_col.insert_one(address)
    address['_id'] = str(result.inserted_id)

    logger.info(f'Address added for user {uid}: {data["label"]}')
    return jsonify({'success': True, 'message': 'Address saved', 'address': address}), 201


@addresses_bp.route('/<address_id>', methods=['PUT'])
@login_required
def update_address(address_id):
    uid = get_user_id()
    data = request.get_json()
    allowed = ['label', 'address_line', 'city', 'state', 'zip', 'phone', 'instructions', 'is_default']
    update_data = {k: v for k, v in data.items() if k in allowed}

    if update_data.get('is_default'):
        addresses_col.update_many({'user_id': uid}, {'$set': {'is_default': False}})

    result = addresses_col.update_one(
        {'_id': ObjectId(address_id), 'user_id': uid},
        {'$set': update_data}
    )
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Address not found'}), 404
    return jsonify({'success': True, 'message': 'Address updated'})


@addresses_bp.route('/<address_id>', methods=['DELETE'])
@login_required
def delete_address(address_id):
    uid = get_user_id()
    result = addresses_col.delete_one({'_id': ObjectId(address_id), 'user_id': uid})
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Address not found'}), 404
    return jsonify({'success': True, 'message': 'Address deleted'})
