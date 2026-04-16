# ============================================
# FLAVOUR FLEET — Flask Backend (app.py)
# ============================================
# Slim entry point — all route logic lives in
# routes/<blueprint>.py, shared logic in
# db.py and helpers.py.
# ============================================

import os
import secrets
import sys
import io

from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)


def configure_console_encoding():
    """Force UTF-8 console streams to avoid cp1252 Unicode errors on Windows."""
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        if hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except Exception:
        # Keep startup resilient if streams are redirected/unavailable.
        pass


configure_console_encoding()

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

from helpers import register_error_handlers, logger
from db import db  # Ensures indexes are created on import


def parse_frontend_origins():
    configured = os.environ.get("FRONTEND_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]

    return [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://atul87.github.io",
    ]


# ─── App Setup ────────────────────────────────────────
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), ".."),
    static_url_path="",
)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app_env = os.environ.get("APP_ENV", "development").lower()
frontend_origins = parse_frontend_origins()
CORS(app, supports_credentials=True, origins=frontend_origins)

if app_env == "production":
    # Required for cross-site session cookies when frontend and backend are on different domains.
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
else:
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ─── Socket.IO ───────────────────────────────────────
socketio = SocketIO(
    app,
    cors_allowed_origins=frontend_origins,
    async_mode="threading",
)

# Rate limiter (disabled when TESTING_MODE is set)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
    enabled=not os.environ.get("TESTING_MODE", False),
)

# Register global error handlers
register_error_handlers(app)


# ─── Static File Serving ─────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


# ─── Health Endpoint ─────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "success": True,
            "status": "healthy",
            "service": "Flavour Fleet API",
            "version": "4.0.0",
            "api_versions": ["v1"],
        }
    )


# ─── Register Blueprints ─────────────────────────────
from routes.auth import auth_bp
from routes.menu import menu_bp
from routes.restaurants import restaurants_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.offers import offers_bp
from routes.admin import admin_bp
from routes.addresses import addresses_bp
from routes.payments import payments_bp

app.register_blueprint(auth_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(restaurants_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(offers_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(addresses_bp)
app.register_blueprint(payments_bp)

# ─── API Versioning (v1 aliases) ─────────────────────
# Register all blueprints under /api/v1/ as well for versioned access
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth", name="auth_v1")
app.register_blueprint(menu_bp, url_prefix="/api/v1/menu", name="menu_v1")
app.register_blueprint(
    restaurants_bp, url_prefix="/api/v1/restaurants", name="restaurants_v1"
)
app.register_blueprint(cart_bp, url_prefix="/api/v1/cart", name="cart_v1")
app.register_blueprint(orders_bp, url_prefix="/api/v1/orders", name="orders_v1")
app.register_blueprint(offers_bp, url_prefix="/api/v1/offers", name="offers_v1")
app.register_blueprint(admin_bp, url_prefix="/api/v1/admin", name="admin_v1")
app.register_blueprint(
    addresses_bp, url_prefix="/api/v1/addresses", name="addresses_v1"
)
app.register_blueprint(payments_bp, url_prefix="/api/v1/payments", name="payments_v1")

# Make socketio available to blueprints via app config
app.config["socketio"] = socketio

# ─── Register Socket.IO Events ──────────────────────
from routes.realtime import register_socketio_events

register_socketio_events(socketio)

# ─── Apply Rate Limits ───────────────────────────────
limiter.limit("3/minute")(app.view_functions["auth.register"])
limiter.limit("5/minute")(app.view_functions["auth.login"])
limiter.limit("3/minute")(app.view_functions["auth.forgot_password"])
limiter.limit("5/minute")(app.view_functions["auth.reset_password"])
limiter.limit("10/minute")(app.view_functions["orders.place_order"])

logger.info("9 Blueprints registered (+ v1 versioned aliases, Socket.IO)")

if not os.path.exists(ENV_PATH):
    logger.warning("backend/.env not found; using environment defaults")
if not os.environ.get("SECRET_KEY"):
    logger.warning("SECRET_KEY not set; using an ephemeral development secret")
if not os.environ.get("RESEND_API_KEY"):
    logger.warning("RESEND_API_KEY not set; email delivery is disabled")


def validate_environment():
    if app_env == "production":
        if not os.environ.get("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY is required when APP_ENV=production")
        if not os.environ.get("DATABASE_URL"):
            raise RuntimeError("DATABASE_URL is required when APP_ENV=production")


# ─── Run ─────────────────────────────────────────────
if __name__ == "__main__":
    validate_environment()
    debug_mode = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    logger.info("Flavour Fleet backend running at http://localhost:5000")
    logger.info("Architecture: Flask Blueprints + Socket.IO + API v1")
    socketio.run(
        app,
        debug=debug_mode,
        port=5000,
        host="0.0.0.0",
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
