# ============================================
# FLAVOUR FLEET — Auth Routes Blueprint
# ============================================

import os
import base64
import secrets
import threading
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, session
import bcrypt

from db import users_col, carts_col, reset_tokens_col
from helpers import get_user_id, login_required, logger

from utils.email_service import send_email
from utils.email_templates import password_reset_template

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Upload folder for avatars
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─── Register ────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    if users_col.find_one({'email': email}):
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

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

    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    session['user_role'] = 'user'
    session.pop('guest_id', None)

    logger.info(f'New user registered: {email}')

    return jsonify({
        'success': True,
        'message': 'Account created successfully!',
        'user': {'id': user_id, 'name': name, 'email': email}
    }), 201


# ─── Login ───────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
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
            user_cart = carts_col.find_one({'user_id': user_id})
            if user_cart and user_cart.get('items'):
                existing_ids = {item['id'] for item in user_cart['items']}
                for item in guest_cart['items']:
                    if item['id'] not in existing_ids:
                        user_cart['items'].append(item)
                    else:
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

    logger.info(f'User logged in: {email}')

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {'id': user_id, 'name': user['name'], 'email': user['email']}
    })


# ─── Profile ────────────────────────────────────────
@auth_bp.route('/profile', methods=['GET'])
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


@auth_bp.route('/profile', methods=['PUT'])
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


# ─── Logout ──────────────────────────────────────────
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


# ─── Password Reset ──────────────────────────────────
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    user = users_col.find_one({'email': email})
    if not user:
        return jsonify({'success': True, 'message': 'If an account exists, a reset code has been generated.', 'token': None})

    reset_code = f'{secrets.randbelow(1000000):06d}'
    token = secrets.token_hex(16)

    reset_tokens_col.delete_many({'email': email})
    reset_tokens_col.insert_one({
        'email': email,
        'token': token,
        'code': reset_code,
        'expires_at': datetime.utcnow() + timedelta(minutes=15),
        'created_at': datetime.utcnow().isoformat()
    })

    html = password_reset_template(
        user_name=user.get('name', 'User'),
        reset_code=reset_code
    )
    threading.Thread(
        target=send_email,
        args=(user['email'], 'Password Reset Code 🔐', html)
    ).start()

    logger.info(f'Password reset requested for: {email}')

    return jsonify({
        'success': True,
        'message': 'Reset code sent to your email!',
        'token': token,
        'code': reset_code  # Remove in production — only for demo
    })


@auth_bp.route('/reset-password', methods=['POST'])
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

    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users_col.update_one({'email': reset_doc['email']}, {'$set': {'password_hash': password_hash}})
    reset_tokens_col.delete_many({'email': reset_doc['email']})

    return jsonify({'success': True, 'message': 'Password reset successfully! You can now login.'})


# ─── Avatar Upload ───────────────────────────────────
@auth_bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    from bson import ObjectId
    data = request.get_json()
    image_data = data.get('image', '')

    if not image_data:
        return jsonify({'success': False, 'message': 'No image provided'}), 400

    try:
        if ',' in image_data:
            header, encoded = image_data.split(',', 1)
        else:
            encoded = image_data

        ext = 'png'
        if 'jpeg' in image_data or 'jpg' in image_data:
            ext = 'jpg'
        elif 'webp' in image_data:
            ext = 'webp'

        filename = f'avatar_{session["user_id"]}.{ext}'
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(encoded))

        avatar_url = f'/assets/uploads/{filename}'
        users_col.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'avatar': avatar_url}}
        )

        return jsonify({'success': True, 'message': 'Avatar updated!', 'avatar_url': avatar_url})
    except Exception as e:
        logger.error(f'Avatar upload failed: {e}')
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500
