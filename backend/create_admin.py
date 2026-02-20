from pymongo import MongoClient
import bcrypt
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['flavourfleet']
users_col = db['users']

def create_admin_user():
    email = 'admin@flavourfleet.com'
    password = 'admin123'
    name = 'Admin User'
    
    # Check if admin already exists
    if users_col.find_one({'email': email}):
        print(f"⚠️ Admin user '{email}' already exists.")
        return

    # Hash password using bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    admin_user = {
        'name': name,
        'email': email,
        'password_hash': password_hash,
        'phone': '123-456-7890',
        'address': 'Admin HQ',
        'role': 'admin',
        'created_at': datetime.utcnow().isoformat(),
        'avatar': 'assets/images/default.png'
    }

    users_col.insert_one(admin_user)
    print(f"✅ Admin user created successfully!")
    print(f"   Email: {email}")
    print(f"   Password: {password}")

if __name__ == '__main__':
    create_admin_user()
