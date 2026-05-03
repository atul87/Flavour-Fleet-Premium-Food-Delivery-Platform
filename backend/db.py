# ============================================
# FLAVOUR FLEET — Database Module
# ============================================

import os
from pymongo import MongoClient, ASCENDING, DESCENDING

# ─── MongoDB Connection ──────────────────────────────
database_url = (
    os.getenv("DATABASE_URL")
    or os.getenv("MONGODB_URI")
    or os.getenv("MONGO_URI")
    or "mongodb://localhost:27017/"
)
database_name = os.getenv("DATABASE_NAME", "flavourfleet")
connect_timeout_ms = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "5000"))

client = MongoClient(
    database_url,
    serverSelectionTimeoutMS=connect_timeout_ms,
    connectTimeoutMS=connect_timeout_ms,
)
db = client[database_name]

# ─── Core Collections ────────────────────────────────
users_col = db["users"]
menu_col = db["menu_items"]
restaurants_col = db["restaurants"]
carts_col = db["carts"]
orders_col = db["orders"]
offers_col = db["offers"]
reset_tokens_col = db["password_reset_tokens"]
settings_col = db["settings"]

# ─── Phase 5: New Collections ────────────────────────
addresses_col = db["addresses"]
payments_col = db["payments"]
analytics_col = db["analytics_snapshots"]

# ─── Indexes ─────────────────────────────────────────
# Users
users_col.create_index("email", unique=True)
users_col.create_index([("name", ASCENDING)])  # Admin user search
users_col.create_index([("role", ASCENDING)])  # Filter by role
users_col.create_index([("created_at", DESCENDING)])  # Sort by newest

# Carts
carts_col.create_index("user_id")

# Orders — compound indexes for admin queries
orders_col.create_index("order_id", unique=True)
orders_col.create_index("user_id")
orders_col.create_index([("status", ASCENDING), ("created_at", DESCENDING)])
orders_col.create_index(
    [("user_id", ASCENDING), ("created_at", DESCENDING)]
)  # User order history
orders_col.create_index(
    [("restaurant", ASCENDING), ("created_at", DESCENDING)]
)  # By restaurant
orders_col.create_index([("created_at", DESCENDING)])  # Global sort

# Menu
menu_col.create_index("item_id", unique=True, sparse=True)
menu_col.create_index([("category", ASCENDING)])
menu_col.create_index(
    [("is_deleted", ASCENDING), ("category", ASCENDING)]
)  # Admin filtered view

# Restaurants
restaurants_col.create_index([("is_deleted", ASCENDING), ("rating", DESCENDING)])
restaurants_col.create_index([("category", ASCENDING)])

# Offers
offers_col.create_index("code", unique=True, sparse=True)
offers_col.create_index([("is_deleted", ASCENDING), ("active", ASCENDING)])

# Password reset tokens — TTL index
reset_tokens_col.create_index("expires_at", expireAfterSeconds=0)
reset_tokens_col.create_index("token")

# Addresses
addresses_col.create_index([("user_id", ASCENDING)])
addresses_col.create_index([("user_id", ASCENDING), ("is_default", DESCENDING)])

# Payments
payments_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
payments_col.create_index([("order_id", ASCENDING)])

# Analytics snapshots
analytics_col.create_index([("date", DESCENDING)], unique=True)
