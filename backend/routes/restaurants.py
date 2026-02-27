# ============================================
# FLAVOUR FLEET — Restaurants Routes Blueprint
# ============================================

from flask import Blueprint, request, jsonify
from db import restaurants_col

restaurants_bp = Blueprint('restaurants', __name__, url_prefix='/api/restaurants')


@restaurants_bp.route('', methods=['GET'])
def get_restaurants():
    category = request.args.get('category')
    query = {'is_deleted': {'$ne': True}}
    if category and category != 'all':
        query['category'] = category

    restaurants = list(restaurants_col.find(query))
    for r in restaurants:
        r['_id'] = str(r['_id'])

    return jsonify({'success': True, 'restaurants': restaurants, 'count': len(restaurants)})


@restaurants_bp.route('/<restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    from bson import ObjectId
    try:
        restaurant = restaurants_col.find_one({'_id': ObjectId(restaurant_id)})
    except Exception:
        restaurant = restaurants_col.find_one({'name': restaurant_id})

    if not restaurant:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404

    restaurant['_id'] = str(restaurant['_id'])
    return jsonify({'success': True, 'restaurant': restaurant})
