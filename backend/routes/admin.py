# ============================================
# FLAVOUR FLEET — Admin Routes Blueprint
# ============================================

import secrets
import threading
from datetime import datetime, timedelta

from bson import ObjectId
from flask import Blueprint, request, jsonify, session

from db import (
    users_col, menu_col, restaurants_col,
    orders_col, offers_col, settings_col
)
from helpers import admin_required, logger

from utils.email_service import send_email
from utils.email_templates import order_delivered_template

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ─── Stats ───────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
@admin_required
def admin_stats():
    total_orders = orders_col.count_documents({})
    total_users = users_col.count_documents({})
    total_menu = menu_col.count_documents({})
    total_restaurants = restaurants_col.count_documents({})

    pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$total'}}}]
    rev_result = list(orders_col.aggregate(pipeline))
    total_revenue = round(rev_result[0]['total'], 2) if rev_result else 0

    recent_orders = list(orders_col.find().sort('created_at', -1).limit(5))
    for o in recent_orders:
        o['_id'] = str(o['_id'])

    return jsonify({
        'success': True,
        'stats': {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_users': total_users,
            'total_menu_items': total_menu,
            'total_restaurants': total_restaurants,
        },
        'recent_orders': recent_orders
    })


# ─── Orders ──────────────────────────────────────────
@admin_bp.route('/orders', methods=['GET'])
@admin_required
def admin_get_orders():
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = {}
    if status_filter and status_filter != 'all':
        query['status'] = status_filter
    if search:
        query['order_id'] = {'$regex': search, '$options': 'i'}

    total = orders_col.count_documents(query)
    orders = list(orders_col.find(query).sort('created_at', -1).skip((page - 1) * per_page).limit(per_page))
    for o in orders:
        o['_id'] = str(o['_id'])

    return jsonify({'success': True, 'orders': orders, 'total': total, 'page': page, 'per_page': per_page})


@admin_bp.route('/orders/<order_id>', methods=['PUT'])
@admin_required
def admin_update_order(order_id):
    data = request.get_json()
    new_status = data.get('status')
    allowed = ['placed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled']
    if new_status not in allowed:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    result = orders_col.update_one(
        {'order_id': order_id},
        {
            '$set': {'status': new_status},
            '$push': {'status_history': {'status': new_status, 'changed_by': session.get('user_id', 'system'), 'timestamp': datetime.utcnow().isoformat()}}
        }
    )
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Order not found'}), 404

    # Emit real-time update to tracking clients
    from flask import current_app
    sio = current_app.config.get('socketio')
    if sio:
        from routes.realtime import emit_order_update
        eta_map = {'placed': '30 min', 'preparing': '20 min', 'out_for_delivery': '10 min', 'delivered': 'Delivered!', 'cancelled': 'Cancelled'}
        emit_order_update(sio, order_id, new_status, eta_map.get(new_status))

    if new_status == 'delivered':
        order = orders_col.find_one({'order_id': order_id})
        if order:
            user = users_col.find_one({'_id': ObjectId(order['user_id'])}) if ObjectId.is_valid(order.get('user_id', '')) else None
            if user and user.get('email'):
                html = order_delivered_template(
                    user_name=user.get('name', 'Customer'),
                    order_id=order_id
                )
                threading.Thread(
                    target=send_email,
                    args=(user['email'], 'Order Delivered 🎉', html)
                ).start()

    return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})


# ─── Menu ────────────────────────────────────────────
@admin_bp.route('/menu', methods=['GET'])
@admin_required
def admin_get_menu():
    items = list(menu_col.find())
    for item in items:
        item['_id'] = str(item['_id'])
    return jsonify({'success': True, 'items': items, 'count': len(items)})


@admin_bp.route('/menu', methods=['POST'])
@admin_required
def admin_add_menu_item():
    data = request.get_json()
    required = ['name', 'price', 'category']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400

    item = {
        'item_id': 'item_' + secrets.token_hex(4),
        'name': data['name'],
        'price': float(data['price']),
        'category': data['category'],
        'description': data.get('description', ''),
        'image': data.get('image', 'assets/images/default.png'),
        'restaurant': data.get('restaurant', ''),
        'rating': float(data.get('rating', 4.5)),
        'badge': data.get('badge', ''),
        'active': data.get('active', True),
        'created_at': datetime.utcnow().isoformat(),
    }
    result = menu_col.insert_one(item)
    item['_id'] = str(result.inserted_id)
    return jsonify({'success': True, 'message': 'Menu item added', 'item': item}), 201


@admin_bp.route('/menu/<item_id>', methods=['PUT'])
@admin_required
def admin_update_menu_item(item_id):
    data = request.get_json()
    allowed = ['name', 'price', 'category', 'description', 'image', 'restaurant', 'rating', 'badge', 'active']
    update_data = {k: v for k, v in data.items() if k in allowed}
    if 'price' in update_data:
        update_data['price'] = float(update_data['price'])
    if 'rating' in update_data:
        update_data['rating'] = float(update_data['rating'])

    try:
        result = menu_col.update_one({'_id': ObjectId(item_id)}, {'$set': update_data})
    except Exception:
        result = menu_col.update_one({'item_id': item_id}, {'$set': update_data})

    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    return jsonify({'success': True, 'message': 'Menu item updated'})


@admin_bp.route('/menu/<item_id>', methods=['DELETE'])
@admin_required
def admin_delete_menu_item(item_id):
    soft_delete = {'$set': {'is_deleted': True, 'deleted_at': datetime.utcnow().isoformat()}}
    try:
        result = menu_col.update_one({'_id': ObjectId(item_id)}, soft_delete)
    except Exception:
        result = menu_col.update_one({'item_id': item_id}, soft_delete)
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    return jsonify({'success': True, 'message': 'Menu item deleted'})


# ─── Restaurants ─────────────────────────────────────
@admin_bp.route('/restaurants', methods=['GET'])
@admin_required
def admin_get_restaurants():
    restaurants = list(restaurants_col.find())
    for r in restaurants:
        r['_id'] = str(r['_id'])
    return jsonify({'success': True, 'restaurants': restaurants, 'count': len(restaurants)})


@admin_bp.route('/restaurants', methods=['POST'])
@admin_required
def admin_add_restaurant():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Name is required'}), 400

    restaurant = {
        'name': data['name'],
        'category': data.get('category', ''),
        'description': data.get('description', ''),
        'rating': float(data.get('rating', 4.5)),
        'delivery_time': data.get('delivery_time', '30-40'),
        'price_range': data.get('price_range', '$$'),
        'image': data.get('image', 'assets/images/default.png'),
        'address': data.get('address', ''),
        'active': data.get('active', True),
        'created_at': datetime.utcnow().isoformat(),
    }
    result = restaurants_col.insert_one(restaurant)
    restaurant['_id'] = str(result.inserted_id)
    return jsonify({'success': True, 'message': 'Restaurant added', 'restaurant': restaurant}), 201


@admin_bp.route('/restaurants/<restaurant_id>', methods=['PUT'])
@admin_required
def admin_update_restaurant(restaurant_id):
    data = request.get_json()
    allowed = ['name', 'category', 'description', 'rating', 'delivery_time', 'price_range', 'image', 'address', 'active']
    update_data = {k: v for k, v in data.items() if k in allowed}
    if 'rating' in update_data:
        update_data['rating'] = float(update_data['rating'])

    try:
        result = restaurants_col.update_one({'_id': ObjectId(restaurant_id)}, {'$set': update_data})
    except Exception:
        result = restaurants_col.update_one({'name': restaurant_id}, {'$set': update_data})

    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404
    return jsonify({'success': True, 'message': 'Restaurant updated'})


@admin_bp.route('/restaurants/<restaurant_id>', methods=['DELETE'])
@admin_required
def admin_delete_restaurant(restaurant_id):
    soft_delete = {'$set': {'is_deleted': True, 'deleted_at': datetime.utcnow().isoformat()}}
    try:
        result = restaurants_col.update_one({'_id': ObjectId(restaurant_id)}, soft_delete)
    except Exception:
        result = restaurants_col.update_one({'name': restaurant_id}, soft_delete)
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404
    return jsonify({'success': True, 'message': 'Restaurant deleted'})


# ─── Offers ──────────────────────────────────────────
@admin_bp.route('/offers', methods=['GET'])
@admin_required
def admin_get_offers():
    offers = list(offers_col.find())
    for o in offers:
        o['_id'] = str(o['_id'])
    return jsonify({'success': True, 'offers': offers, 'count': len(offers)})


@admin_bp.route('/offers', methods=['POST'])
@admin_required
def admin_add_offer():
    data = request.get_json()
    if not data.get('code') or not data.get('title'):
        return jsonify({'success': False, 'message': 'Code and title are required'}), 400

    if offers_col.find_one({'code': data['code'].upper()}):
        return jsonify({'success': False, 'message': 'Promo code already exists'}), 409

    offer = {
        'code': data['code'].upper(),
        'title': data['title'],
        'description': data.get('description', ''),
        'discount_type': data.get('discount_type', 'percent'),
        'discount_value': float(data.get('discount_value', 0)),
        'icon': data.get('icon', '🎟'),
        'color': data.get('color', 'orange'),
        'valid_till': data.get('valid_till', 'No expiry'),
        'tag': data.get('tag', ''),
        'min_order': float(data.get('min_order', 0)),
        'active': data.get('active', True),
        'created_at': datetime.utcnow().isoformat(),
    }
    result = offers_col.insert_one(offer)
    offer['_id'] = str(result.inserted_id)
    return jsonify({'success': True, 'message': 'Offer created', 'offer': offer}), 201


@admin_bp.route('/offers/<offer_id>', methods=['PUT'])
@admin_required
def admin_update_offer(offer_id):
    data = request.get_json()
    allowed = ['title', 'description', 'discount_type', 'discount_value', 'icon', 'color', 'valid_till', 'tag', 'min_order', 'active']
    update_data = {k: v for k, v in data.items() if k in allowed}
    if 'discount_value' in update_data:
        update_data['discount_value'] = float(update_data['discount_value'])

    try:
        result = offers_col.update_one({'_id': ObjectId(offer_id)}, {'$set': update_data})
    except Exception:
        result = offers_col.update_one({'code': offer_id}, {'$set': update_data})

    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Offer not found'}), 404
    return jsonify({'success': True, 'message': 'Offer updated'})


@admin_bp.route('/offers/<offer_id>', methods=['DELETE'])
@admin_required
def admin_delete_offer(offer_id):
    soft_delete = {'$set': {'is_deleted': True, 'deleted_at': datetime.utcnow().isoformat()}}
    try:
        result = offers_col.update_one({'_id': ObjectId(offer_id)}, soft_delete)
    except Exception:
        result = offers_col.update_one({'code': offer_id}, soft_delete)
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Offer not found'}), 404
    return jsonify({'success': True, 'message': 'Offer deleted'})


# ─── Users ───────────────────────────────────────────
@admin_bp.route('/users', methods=['GET'])
@admin_required
def admin_get_users():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search', '')

    query = {}
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'email': {'$regex': search, '$options': 'i'}}
        ]

    total = users_col.count_documents(query)
    users = list(users_col.find(query, {'password_hash': 0}).sort('created_at', -1).skip((page - 1) * per_page).limit(per_page))

    for u in users:
        uid = str(u['_id'])
        u['_id'] = uid
        u['order_count'] = orders_col.count_documents({'user_id': uid})

    return jsonify({'success': True, 'users': users, 'total': total, 'page': page})


@admin_bp.route('/users/<user_id>/role', methods=['PUT'])
@admin_required
def admin_update_user_role(user_id):
    data = request.get_json()
    new_role = data.get('role')
    if new_role not in ['user', 'admin']:
        return jsonify({'success': False, 'message': 'Invalid role'}), 400

    result = users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'message': f'User role updated to {new_role}'})


# ─── Analytics ───────────────────────────────────────
@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def admin_analytics():
    days = 14
    daily_data = []

    for i in range(days - 1, -1, -1):
        day_start = (datetime.utcnow() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        day_orders = list(orders_col.find({
            'created_at': {'$gte': day_start.isoformat(), '$lt': day_end.isoformat()}
        }))

        daily_data.append({
            'date': day_start.strftime('%b %d'),
            'orders': len(day_orders),
            'revenue': round(sum(o.get('total', 0) for o in day_orders), 2)
        })

    status_pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
    status_data = {doc['_id']: doc['count'] for doc in orders_col.aggregate(status_pipeline)}

    top_pipeline = [
        {'$unwind': '$items'},
        {'$group': {'_id': '$items.name', 'count': {'$sum': '$items.quantity'}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]
    top_items = [{'name': doc['_id'], 'count': doc['count']} for doc in orders_col.aggregate(top_pipeline)]

    return jsonify({
        'success': True,
        'daily_data': daily_data,
        'status_breakdown': status_data,
        'top_items': top_items
    })


# ─── Settings ────────────────────────────────────────
@admin_bp.route('/settings', methods=['GET'])
@admin_required
def admin_get_settings():
    settings = settings_col.find_one({'key': 'platform'})
    if settings:
        settings['_id'] = str(settings['_id'])
    else:
        settings = {
            'platform_name': 'Flavour Fleet',
            'delivery_fee': 4.99,
            'free_delivery_threshold': 30,
            'tax_percent': 8,
            'contact_email': 'support@flavourfleet.com',
        }
    return jsonify({'success': True, 'settings': settings})


@admin_bp.route('/settings', methods=['PUT'])
@admin_required
def admin_update_settings():
    data = request.get_json()
    allowed = ['platform_name', 'delivery_fee', 'free_delivery_threshold', 'tax_percent', 'contact_email']
    update_data = {k: v for k, v in data.items() if k in allowed}

    settings_col.update_one({'key': 'platform'}, {'$set': {**update_data, 'key': 'platform'}}, upsert=True)
    return jsonify({'success': True, 'message': 'Settings saved'})


# ─── Materialized Analytics Snapshots ────────────────
@admin_bp.route('/analytics/snapshot', methods=['POST'])
@admin_required
def build_analytics_snapshot():
    """Build and store a materialized analytics snapshot for today."""
    from db import analytics_col

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today + timedelta(days=1)

    # Revenue totals
    revenue_pipeline = [
        {'$match': {'created_at': {'$gte': today.isoformat(), '$lt': today_end.isoformat()}}},
        {'$group': {'_id': None, 'revenue': {'$sum': '$total'}, 'count': {'$sum': 1}}}
    ]
    rev = list(orders_col.aggregate(revenue_pipeline))
    daily_revenue = round(rev[0]['revenue'], 2) if rev else 0
    daily_orders = rev[0]['count'] if rev else 0

    # Top 10 items (all time)
    top_pipeline = [
        {'$unwind': '$items'},
        {'$group': {'_id': '$items.name', 'count': {'$sum': '$items.quantity'}, 'revenue': {'$sum': {'$multiply': ['$items.price', '$items.quantity']}}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    top_items = [{'name': d['_id'], 'count': d['count'], 'revenue': round(d['revenue'], 2)} for d in orders_col.aggregate(top_pipeline)]

    # Status breakdown
    status_pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
    status_data = {d['_id']: d['count'] for d in orders_col.aggregate(status_pipeline)}

    # Top restaurants by order count
    rest_pipeline = [
        {'$group': {'_id': '$restaurant', 'orders': {'$sum': 1}, 'revenue': {'$sum': '$total'}}},
        {'$sort': {'orders': -1}},
        {'$limit': 10}
    ]
    top_restaurants = [{'name': d['_id'], 'orders': d['orders'], 'revenue': round(d['revenue'], 2)} for d in orders_col.aggregate(rest_pipeline)]

    snapshot = {
        'date': today.strftime('%Y-%m-%d'),
        'daily_revenue': daily_revenue,
        'daily_orders': daily_orders,
        'total_orders': orders_col.count_documents({}),
        'total_users': users_col.count_documents({}),
        'total_revenue': round(sum(o.get('total', 0) for o in orders_col.find({}, {'total': 1})), 2),
        'status_breakdown': status_data,
        'top_items': top_items,
        'top_restaurants': top_restaurants,
        'computed_at': datetime.utcnow().isoformat(),
    }

    analytics_col.update_one(
        {'date': snapshot['date']},
        {'$set': snapshot},
        upsert=True
    )

    logger.info(f'Analytics snapshot built for {snapshot["date"]}')
    return jsonify({'success': True, 'message': 'Snapshot built', 'snapshot': snapshot}), 201


@admin_bp.route('/analytics/snapshots', methods=['GET'])
@admin_required
def get_analytics_snapshots():
    """Get cached analytics snapshots (fast dashboard loading)."""
    from db import analytics_col

    days = int(request.args.get('days', 14))
    snapshots = list(analytics_col.find().sort('date', -1).limit(days))
    for s in snapshots:
        s['_id'] = str(s['_id'])
    return jsonify({'success': True, 'snapshots': snapshots})

