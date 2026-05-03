# ============================================
# FLAVOUR FLEET — Shared Helpers & Decorators
# ============================================

import secrets
from functools import wraps

from flask import session, jsonify, request
from werkzeug.exceptions import HTTPException

from utils.logger import logger


# ─── Helpers ──────────────────────────────────────────
def get_user_id():
    """Get user ID from session, or generate a guest ID."""
    if "user_id" in session:
        return session["user_id"]
    if "guest_id" not in session:
        session["guest_id"] = "guest_" + secrets.token_hex(8)
    return session["guest_id"]


def login_required(f):
    """Decorator to require authentication."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first"}), 401
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Decorator to require admin role."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first"}), 401
        if session.get("user_role") != "admin":
            return jsonify({"success": False, "message": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated

token_required = login_required

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def error_response(message, code=400):
    """Standardized error response."""
    return jsonify({"success": False, "message": message}), code


def success_response(message="OK", data=None, code=200):
    """Standardized success response."""
    resp = {"success": True, "message": message}
    if data:
        resp.update(data)
    return jsonify(resp), code


# ─── Global Error Handlers ───────────────────────────
def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"404: {request.path}")
        return jsonify({"success": False, "message": "Endpoint not found"}), 404

    @app.errorhandler(429)
    def rate_limited(e):
        logger.warning(f"Rate limited: {request.remote_addr} on {request.path}")
        return (
            jsonify(
                {"success": False, "message": "Too many requests. Please slow down."}
            ),
            429,
        )

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 error: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def unhandled_error(e):
        if isinstance(e, HTTPException):
            return jsonify({"success": False, "message": e.description}), e.code
        logger.error("Unhandled exception: %s", e, exc_info=True)
        return jsonify({"success": False, "message": "Internal Server Error"}), 500
