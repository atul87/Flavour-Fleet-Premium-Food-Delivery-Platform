# ============================================
# FLAVOUR FLEET — Create Admin User Script
# ============================================
# Run once: python backend/seed_admin.py
# Admin credentials:
#   Email: admin@flavourfleet.com
#   Password: admin123

import bcrypt
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['flavourfleet']
users_col = db['users']

ADMIN_EMAIL = 'admin@flavourfleet.com'
ADMIN_PASSWORD = 'admin123'
ADMIN_NAME = 'Admin'

# Remove existing admin if present
users_col.delete_one({'email': ADMIN_EMAIL})

password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

admin_user = {
    'name': ADMIN_NAME,
    'email': ADMIN_EMAIL,
    'password_hash': password_hash,
    'phone': '',
    'address': '',
    'role': 'admin',
    'created_at': datetime.utcnow().isoformat(),
}

users_col.insert_one(admin_user)
print('\n✅ Admin user created!')
print(f'   Email   : {ADMIN_EMAIL}')
print(f'   Password: {ADMIN_PASSWORD}')
print(f'   Role    : admin\n')
