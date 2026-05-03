import os
from pymongo import MongoClient
import bcrypt
from datetime import datetime

from utils.logger import logger

# Connect to MongoDB
client = MongoClient(
    os.getenv("DATABASE_URL")
    or os.getenv("MONGODB_URI")
    or os.getenv("MONGO_URI")
    or "mongodb://localhost:27017/"
)
db = client[os.getenv("DATABASE_NAME", "flavourfleet")]
users_col = db["users"]


def create_admin_user():
    email = "admin@flavourfleet.com"
    password = "admin123"
    name = "Admin User"

    # Check if admin already exists
    if users_col.find_one({"email": email}):
        logger.warning("Admin user '%s' already exists", email)
        return

    # Hash password using bcrypt
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    admin_user = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "phone": "123-456-7890",
        "address": "Admin HQ",
        "role": "admin",
        "created_at": datetime.utcnow().isoformat(),
        "avatar": "assets/images/default.png",
    }

    users_col.insert_one(admin_user)
    logger.info("Admin user created successfully")
    logger.info("Admin email: %s", email)
    logger.info("Admin password: %s", password)


if __name__ == "__main__":
    create_admin_user()
