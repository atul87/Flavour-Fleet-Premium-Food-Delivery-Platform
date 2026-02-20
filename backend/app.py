# ============================================
# FLAVOUR FLEET — Flask Backend (app.py)
# ============================================

import os
import base64
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt

# ─── App Setup ────────────────────────────────────────
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..'), static_url_path='')
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True)

# Upload folder for avatars
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'assets', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── MongoDB Connection ──────────────────────────────
client = MongoClient('mongodb://localhost:27017/')
db = client['flavourfleet']

# Collections
users_col = db['users']
menu_col = db['menu_items']
restaurants_col = db['restaurants']
carts_col = db['carts']
orders_col = db['orders']
offers_col = db['offers']
reset_tokens_col = db['password_reset_tokens']
settings_col = db['settings']

# Ensure indexes
users_col.create_index('email', unique=True)
carts_col.create_index('user_id')
orders_col.create_index('user_id')
orders_col.create_index('order_id', unique=True)
reset_tokens_col.create_index('expires_at', expireAfterSeconds=0)


# ─── Helpers ──────────────────────────────────────────
def get_user_id():
    """Get user ID from session, or generate a guest ID."""
    if 'user_id' in session:
        return session['user_id']
    if 'guest_id' not in session:
        session['guest_id'] = 'guest_' + secrets.token_hex(8)
    return session['guest_id']


def login_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        if session.get('user_role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    return doc


# ─── Static File Serving ─────────────────────────────
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


# ════════════════════════════════════════════════════
#  AUTH API
# ════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    # Check if email exists
    if users_col.find_one({'email': email}):
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = {
        'name': name,
        'email': email,
        'password_hash': password_hash,
        'phone': '',
        'address': '',
        'role': 'user',
        'created_at': datetime.utcnow().isoformat(),
    }
    result = users_col.insert_one(user)
    user_id = str(result.inserted_id)

    # Transfer guest cart to user
    guest_id = session.get('guest_id')
    if guest_id:
        guest_cart = carts_col.find_one({'user_id': guest_id})
        if guest_cart and guest_cart.get('items'):
            carts_col.update_one(
                {'user_id': user_id},
                {'$set': {'user_id': user_id, 'items': guest_cart['items']}},
                upsert=True
            )
            carts_col.delete_one({'user_id': guest_id})

    # Set session
    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    session['user_role'] = 'user'
    session.pop('guest_id', None)

    return jsonify({
        'success': True,
        'message': 'Account created successfully!',
        'user': {'id': user_id, 'name': name, 'email': email}
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = users_col.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    user_id = str(user['_id'])

    # Transfer guest cart to user
    guest_id = session.get('guest_id')
    if guest_id:
        guest_cart = carts_col.find_one({'user_id': guest_id})
        if guest_cart and guest_cart.get('items'):
            # Merge with existing user cart
            user_cart = carts_col.find_one({'user_id': user_id})
            if user_cart and user_cart.get('items'):
                existing_ids = {item['id'] for item in user_cart['items']}
                for item in guest_cart['items']:
                    if item['id'] not in existing_ids:
                        user_cart['items'].append(item)
                    else:
                        # Update quantity
                        for existing in user_cart['items']:
                            if existing['id'] == item['id']:
                                existing['quantity'] += item['quantity']
                carts_col.update_one({'user_id': user_id}, {'$set': {'items': user_cart['items']}})
            else:
                carts_col.update_one(
                    {'user_id': user_id},
                    {'$set': {'user_id': user_id, 'items': guest_cart['items']}},
                    upsert=True
                )
            carts_col.delete_one({'user_id': guest_id})

    session['user_id'] = user_id
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['user_role'] = user.get('role', 'user')
    session.pop('guest_id', None)

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {'id': user_id, 'name': user['name'], 'email': user['email']}
    })


@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'logged_in': False, 'message': 'Not logged in'}), 200

    from bson import ObjectId
    user = users_col.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'logged_in': True,
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'address': user.get('address', ''),
            'avatar': user.get('avatar', ''),
            'role': user.get('role', 'user'),
            'created_at': user.get('created_at', ''),
        }
    })


@app.route('/api/auth/profile', methods=['PUT'])
@login_required
def update_profile():
    from bson import ObjectId
    data = request.get_json()
    allowed_fields = ['name', 'phone', 'address']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({'success': False, 'message': 'No valid fields to update'}), 400

    users_col.update_one({'_id': ObjectId(session['user_id'])}, {'$set': update_data})

    if 'name' in update_data:
        session['user_name'] = update_data['name']

    return jsonify({'success': True, 'message': 'Profile updated successfully'})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


# ─── Password Reset ──────────────────────────────────
@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    user = users_col.find_one({'email': email})
    # Always return success to prevent email enumeration
    if not user:
        return jsonify({'success': True, 'message': 'If an account exists, a reset code has been generated.', 'token': None})

    # Generate a 6-digit reset code
    reset_code = f'{secrets.randbelow(1000000):06d}'
    token = secrets.token_hex(16)

    # Store reset token (expires in 15 minutes)
    reset_tokens_col.delete_many({'email': email})  # Remove old tokens
    reset_tokens_col.insert_one({
        'email': email,
        'token': token,
        'code': reset_code,
        'expires_at': datetime.utcnow() + timedelta(minutes=15),
        'created_at': datetime.utcnow().isoformat()
    })

    # In production, send email. For demo, return the code directly.
    return jsonify({
        'success': True,
        'message': 'Reset code generated! (In production, this would be emailed)',
        'token': token,
        'code': reset_code  # Remove in production — only for demo
    })


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token', '')
    code = data.get('code', '')
    new_password = data.get('new_password', '')

    if not token or not code or not new_password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    reset_doc = reset_tokens_col.find_one({'token': token, 'code': code})
    if not reset_doc:
        return jsonify({'success': False, 'message': 'Invalid or expired reset code'}), 400

    if datetime.utcnow() > reset_doc['expires_at']:
        reset_tokens_col.delete_one({'_id': reset_doc['_id']})
        return jsonify({'success': False, 'message': 'Reset code has expired'}), 400

    # Update password
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users_col.update_one({'email': reset_doc['email']}, {'$set': {'password_hash': password_hash}})

    # Clean up token
    reset_tokens_col.delete_many({'email': reset_doc['email']})

    return jsonify({'success': True, 'message': 'Password reset successfully! You can now login.'})


# ─── Avatar Upload ───────────────────────────────────
@app.route('/api/auth/avatar', methods=['POST'])
@login_required
def upload_avatar():
    from bson import ObjectId
    data = request.get_json()
    image_data = data.get('image', '')  # base64 data URL

    if not image_data:
        return jsonify({'success': False, 'message': 'No image provided'}), 400

    # Parse base64 data URL
    try:
        if ',' in image_data:
            header, encoded = image_data.split(',', 1)
        else:
            encoded = image_data

        # Determine file extension
        ext = 'png'
        if 'jpeg' in image_data or 'jpg' in image_data:
            ext = 'jpg'
        elif 'webp' in image_data:
            ext = 'webp'

        filename = f'avatar_{session["user_id"]}.{ext}'
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Decode and save
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(encoded))

        # Update user record
        avatar_url = f'/assets/uploads/{filename}'
        users_col.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'avatar': avatar_url}}
        )

        return jsonify({'success': True, 'message': 'Avatar updated!', 'avatar_url': avatar_url})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500


# ════════════════════════════════════════════════════
#  MENU API
# ════════════════════════════════════════════════════

@app.route('/api/menu', methods=['GET'])
def get_menu():
    category = request.args.get('category')
    query = {}
    if category and category != 'all':
        query['category'] = category

    items = list(menu_col.find(query))
    for item in items:
        item['_id'] = str(item['_id'])

    return jsonify({'success': True, 'items': items, 'count': len(items)})


@app.route('/api/menu/<item_id>', methods=['GET'])
def get_menu_item(item_id):
    item = menu_col.find_one({'item_id': item_id})
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    item['_id'] = str(item['_id'])
    return jsonify({'success': True, 'item': item})


# ════════════════════════════════════════════════════
#  RESTAURANTS API
# ════════════════════════════════════════════════════

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    category = request.args.get('category')
    query = {}
    if category and category != 'all':
        query['category'] = category

    restaurants = list(restaurants_col.find(query))
    for r in restaurants:
        r['_id'] = str(r['_id'])

    return jsonify({'success': True, 'restaurants': restaurants, 'count': len(restaurants)})


@app.route('/api/restaurants/<restaurant_id>', methods=['GET'])
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


# ════════════════════════════════════════════════════
#  CART API
# ════════════════════════════════════════════════════

@app.route('/api/cart', methods=['GET'])
def get_cart():
    uid = get_user_id()
    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart and 'items' in cart else []
    return jsonify({'success': True, 'items': items})


@app.route('/api/cart/add', methods=['POST'])
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
        # Check if item exists
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


@app.route('/api/cart/update', methods=['PUT'])
def update_cart_item():
    uid = get_user_id()
    data = request.get_json()
    item_id = data.get('id')
    quantity = int(data.get('quantity', 1))

    if quantity <= 0:
        # Remove item
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


@app.route('/api/cart/remove/<item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    uid = get_user_id()
    carts_col.update_one(
        {'user_id': uid},
        {'$pull': {'items': {'id': item_id}}}
    )
    cart = carts_col.find_one({'user_id': uid})
    items = cart['items'] if cart else []
    return jsonify({'success': True, 'message': 'Item removed', 'items': items})


@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    uid = get_user_id()
    carts_col.update_one({'user_id': uid}, {'$set': {'items': []}})
    return jsonify({'success': True, 'message': 'Cart cleared'})


# ════════════════════════════════════════════════════
#  ORDERS API
# ════════════════════════════════════════════════════

@app.route('/api/orders', methods=['POST'])
def place_order():
    uid = get_user_id()
    data = request.get_json()

    # Get cart items
    cart = carts_col.find_one({'user_id': uid})
    if not cart or not cart.get('items'):
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    items = cart['items']
    subtotal = sum(i['price'] * i['quantity'] for i in items)
    delivery_fee = 0 if subtotal > 30 else 4.99
    tax = round(subtotal * 0.08, 2)
    discount = float(data.get('discount', 0))
    total = round(subtotal + delivery_fee + tax - discount, 2)

    order_id = 'ORD-' + secrets.token_hex(4).upper()

    order = {
        'order_id': order_id,
        'user_id': uid,
        'items': items,
        'items_summary': ', '.join(i['name'] for i in items),
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'tax': tax,
        'discount': discount,
        'total': total,
        'status': 'preparing',
        'address': data.get('address', ''),
        'phone': data.get('phone', ''),
        'name': data.get('name', ''),
        'city': data.get('city', ''),
        'zip': data.get('zip', ''),
        'instructions': data.get('instructions', ''),
        'payment_method': data.get('payment_method', 'Credit Card'),
        'restaurant': items[0].get('restaurant', 'Mixed'),
        'created_at': datetime.utcnow().isoformat(),
    }

    orders_col.insert_one(order)

    # Clear cart
    carts_col.update_one({'user_id': uid}, {'$set': {'items': []}})

    # Return order (without _id for clean JSON)
    order.pop('_id', None)

    return jsonify({
        'success': True,
        'message': 'Order placed successfully! 🎉',
        'order': order
    }), 201


@app.route('/api/orders', methods=['GET'])
def get_orders():
    uid = get_user_id()
    orders = list(orders_col.find({'user_id': uid}).sort('created_at', -1))
    for o in orders:
        o['_id'] = str(o['_id'])
    return jsonify({'success': True, 'orders': orders})


@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_col.find_one({'order_id': order_id})
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    order['_id'] = str(order['_id'])
    return jsonify({'success': True, 'order': order})


# ════════════════════════════════════════════════════
#  OFFERS API
# ════════════════════════════════════════════════════

@app.route('/api/offers', methods=['GET'])
def get_offers():
    offers = list(offers_col.find())
    for o in offers:
        o['_id'] = str(o['_id'])
    return jsonify({'success': True, 'offers': offers})


@app.route('/api/offers/validate', methods=['POST'])
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


# ════════════════════════════════════════════════════
#  ADMIN APIs
# ════════════════════════════════════════════════════

# ─── Admin: Stats ────────────────────────────────────
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    total_orders = orders_col.count_documents({})
    total_users = users_col.count_documents({})
    total_menu = menu_col.count_documents({})
    total_restaurants = restaurants_col.count_documents({})

    # Revenue
    pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$total'}}}]
    rev_result = list(orders_col.aggregate(pipeline))
    total_revenue = round(rev_result[0]['total'], 2) if rev_result else 0

    # Recent orders
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


# ─── Admin: Orders ───────────────────────────────────
@app.route('/api/admin/orders', methods=['GET'])
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


@app.route('/api/admin/orders/<order_id>', methods=['PUT'])
@admin_required
def admin_update_order(order_id):
    data = request.get_json()
    new_status = data.get('status')
    allowed = ['placed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled']
    if new_status not in allowed:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    result = orders_col.update_one({'order_id': order_id}, {'$set': {'status': new_status}})
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Order not found'}), 404

    return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})


# ─── Admin: Menu ─────────────────────────────────────
@app.route('/api/admin/menu', methods=['GET'])
@admin_required
def admin_get_menu():
    items = list(menu_col.find())
    for item in items:
        item['_id'] = str(item['_id'])
    return jsonify({'success': True, 'items': items, 'count': len(items)})


@app.route('/api/admin/menu', methods=['POST'])
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


@app.route('/api/admin/menu/<item_id>', methods=['PUT'])
@admin_required
def admin_update_menu_item(item_id):
    from bson import ObjectId
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


@app.route('/api/admin/menu/<item_id>', methods=['DELETE'])
@admin_required
def admin_delete_menu_item(item_id):
    from bson import ObjectId
    try:
        result = menu_col.delete_one({'_id': ObjectId(item_id)})
    except Exception:
        result = menu_col.delete_one({'item_id': item_id})
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    return jsonify({'success': True, 'message': 'Menu item deleted'})


# ─── Admin: Restaurants ──────────────────────────────
@app.route('/api/admin/restaurants', methods=['GET'])
@admin_required
def admin_get_restaurants():
    restaurants = list(restaurants_col.find())
    for r in restaurants:
        r['_id'] = str(r['_id'])
    return jsonify({'success': True, 'restaurants': restaurants, 'count': len(restaurants)})


@app.route('/api/admin/restaurants', methods=['POST'])
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


@app.route('/api/admin/restaurants/<restaurant_id>', methods=['PUT'])
@admin_required
def admin_update_restaurant(restaurant_id):
    from bson import ObjectId
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


@app.route('/api/admin/restaurants/<restaurant_id>', methods=['DELETE'])
@admin_required
def admin_delete_restaurant(restaurant_id):
    from bson import ObjectId
    try:
        result = restaurants_col.delete_one({'_id': ObjectId(restaurant_id)})
    except Exception:
        result = restaurants_col.delete_one({'name': restaurant_id})
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404
    return jsonify({'success': True, 'message': 'Restaurant deleted'})


# ─── Admin: Offers ───────────────────────────────────
@app.route('/api/admin/offers', methods=['GET'])
@admin_required
def admin_get_offers():
    offers = list(offers_col.find())
    for o in offers:
        o['_id'] = str(o['_id'])
    return jsonify({'success': True, 'offers': offers, 'count': len(offers)})


@app.route('/api/admin/offers', methods=['POST'])
@admin_required
def admin_add_offer():
    data = request.get_json()
    if not data.get('code') or not data.get('title'):
        return jsonify({'success': False, 'message': 'Code and title are required'}), 400

    # Check for duplicate code
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


@app.route('/api/admin/offers/<offer_id>', methods=['PUT'])
@admin_required
def admin_update_offer(offer_id):
    from bson import ObjectId
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


@app.route('/api/admin/offers/<offer_id>', methods=['DELETE'])
@admin_required
def admin_delete_offer(offer_id):
    from bson import ObjectId
    try:
        result = offers_col.delete_one({'_id': ObjectId(offer_id)})
    except Exception:
        result = offers_col.delete_one({'code': offer_id})
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Offer not found'}), 404
    return jsonify({'success': True, 'message': 'Offer deleted'})


# ─── Admin: Users ────────────────────────────────────
@app.route('/api/admin/users', methods=['GET'])
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

    # Get order counts per user
    for u in users:
        uid = str(u['_id'])
        u['_id'] = uid
        u['order_count'] = orders_col.count_documents({'user_id': uid})

    return jsonify({'success': True, 'users': users, 'total': total, 'page': page})


@app.route('/api/admin/users/<user_id>/role', methods=['PUT'])
@admin_required
def admin_update_user_role(user_id):
    from bson import ObjectId
    data = request.get_json()
    new_role = data.get('role')
    if new_role not in ['user', 'admin']:
        return jsonify({'success': False, 'message': 'Invalid role'}), 400

    result = users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})
    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'message': f'User role updated to {new_role}'})


# ─── Admin: Analytics ───────────────────────────────
@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def admin_analytics():
    from datetime import timezone
    # Last 14 days daily revenue and orders
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

    # Orders by status
    status_pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
    status_data = {doc['_id']: doc['count'] for doc in orders_col.aggregate(status_pipeline)}

    # Top menu items (by cart orders, simplified)
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


# ─── Admin: Settings ────────────────────────────────
settings_col = db['settings']

@app.route('/api/admin/settings', methods=['GET'])
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


@app.route('/api/admin/settings', methods=['PUT'])
@admin_required
def admin_update_settings():
    data = request.get_json()
    allowed = ['platform_name', 'delivery_fee', 'free_delivery_threshold', 'tax_percent', 'contact_email']
    update_data = {k: v for k, v in data.items() if k in allowed}

    settings_col.update_one({'key': 'platform'}, {'$set': {**update_data, 'key': 'platform'}}, upsert=True)
    return jsonify({'success': True, 'message': 'Settings saved'})


# ════════════════════════════════════════════════════
#  RUN
# ════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n🔥 Flavour Fleet Backend Running!")
    print("   → http://localhost:5000\n")
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)
