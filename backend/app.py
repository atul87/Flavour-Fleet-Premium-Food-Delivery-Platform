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
#  RUN
# ════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n🔥 Flavour Fleet Backend Running!")
    print("   → http://localhost:5000\n")
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)
