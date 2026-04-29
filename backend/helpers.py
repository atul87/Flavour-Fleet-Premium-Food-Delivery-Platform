# ============================================
# FLAVOUR FLEET — Shared Helpers & Decorators
# ============================================

import secrets
import os
import jwt
import requests
from functools import wraps
from datetime import datetime, timedelta

from flask import session, jsonify, request
from werkzeug.exceptions import HTTPException

from utils.logger import logger

# JWT verification - JWKS-based (local, no API call per request)
try:
    import jwt

    HAS_JWT = True
except ImportError:
    HAS_JWT = False
    logger.warning("PyJWT not installed. Run: pip install PyJWT")

try:
    from supabase import create_client

    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    logger.warning("Supabase not available")

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
_supabase_client = None

if HAS_SUPABASE and SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")

# JWKS cache (1 hour TTL)
_jwks_cache = {"data": None, "expires_at": None}


def get_jwks():
    """Fetch and cache JWKS from Supabase for local JWT verification."""
    global _jwks_cache
    if _jwks_cache["data"] and _jwks_cache["expires_at"] > datetime.utcnow():
        return _jwks_cache["data"]
    if not SUPABASE_URL:
        return None
    try:
        response = requests.get(
            f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json", timeout=5
        )
        response.raise_for_status()
        jwks = response.json()
        _jwks_cache["data"] = jwks
        _jwks_cache["expires_at"] = datetime.utcnow() + timedelta(hours=1)
        logger.debug("JWKS cached")
        return jwks
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        return None


# ─── JWT Verification (JWKS-based, local, no API call) ────────────────────
def verify_supabase_token(token_string):
    """
    Verify JWT locally using JWKS (fast, no API call per request).
    Returns: (user_id, error_message) tuple
    """
    if not token_string or not HAS_JWT:
        return None, "No token or JWT library unavailable"
    if not SUPABASE_URL:
        return None, "SUPABASE_URL not configured"
    try:
        unverified_header = jwt.get_unverified_header(token_string)
        kid = unverified_header.get("kid")
        if not kid:
            return None, "Token missing key ID"
        jwks = get_jwks()
        if not jwks or "keys" not in jwks:
            return None, "Failed to get JWKS"
        key = next((k for k in jwks["keys"] if k.get("kid") == kid), None)
        if not key:
            return None, "Key not found in JWKS"
        from jwt.algorithms import RSAAlgorithm

        public_key = RSAAlgorithm.from_jwk(key)
        decoded = jwt.decode(
            token_string,
            public_key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}",
        )
        user_id = decoded.get("sub")
        return (user_id, None) if user_id else (None, "Missing user ID in token")
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"
    except Exception as e:
        logger.error(f"JWT verification error: {e}")
        return None, f"Verification failed: {str(e)}"


def extract_token_from_header():
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header[7:]


def get_verified_user_id():
    """
    Get user ID: JWT for authenticated users, session for guests only.
    Returns: (user_id, is_authenticated, error_message)
    """
    token = extract_token_from_header()
    if token:
        user_id, error = verify_supabase_token(token)
        if user_id:
            return user_id, True, None
        return None, False, error or "Invalid token"
    if "guest_id" not in session:
        session["guest_id"] = "guest_" + secrets.token_hex(8)
    return session["guest_id"], False, None


def get_user_id():
    """Get user ID (JWT for auth, guest_id for guests)."""
    user_id, _, _ = get_verified_user_id()
    return user_id


def get_authenticated_user():
    """Get authenticated user ID if logged in (None for guests)."""
    user_id, is_auth, _ = get_verified_user_id()
    return user_id if is_auth and not user_id.startswith("guest_") else None


# ─── Decorators (Authorization) ──────────────────────────────────────────────
def token_required(f):
    """Strict: requires valid JWT. Rejects guests."""

    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, is_authenticated, error = get_verified_user_id()
        if not is_authenticated or not user_id or user_id.startswith("guest_"):
            return (
                jsonify(
                    {"success": False, "message": error or "Authentication required"}
                ),
                401,
            )
        request.user_id = user_id
        return f(*args, **kwargs)

    return decorated


def login_required(f):
    """
    Flexible: works with authenticated users and guests.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, is_authenticated, error = get_verified_user_id()
        if user_id is None:
            return jsonify({"success": False, "message": error or "Unauthorized"}), 401
        request.user_id = user_id
        request.is_authenticated = is_authenticated
        return f(*args, **kwargs)

    return decorated


def role_required(*allowed_roles):
    """Decorator to enforce role-based access control."""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_id, is_authenticated, error = get_verified_user_id()
            if not is_authenticated or not user_id or user_id.startswith("guest_"):
                return jsonify({"success": False, "message": "Login required"}), 401
            user_role = session.get("user_role", "user")
            if user_role not in allowed_roles:
                logger.warning(
                    f"Access denied: user {user_id} role {user_role} attempted {f.__name__}"
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"Requires role: {', '.join(allowed_roles)}",
                        }
                    ),
                    403,
                )
            request.user_id = user_id
            request.user_role = user_role
            return f(*args, **kwargs)

        return decorated

    return decorator


def admin_required(f):
    """Shorthand for @role_required('admin')."""
    return role_required("admin")(f)


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
