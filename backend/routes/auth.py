# ============================================
# FLAVOUR FLEET — Supabase Auth Routes
# ============================================

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session

from db import carts_col
from helpers import logger

# Import limiter from app (configured globally)
def get_limiter():
    """Get rate limiter instance from Flask app."""
    from flask import current_app
    return current_app.limiter

try:
    from supabase import create_client, Client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not installed. Run: pip install supabase")

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = None
if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    logger.info("Supabase initialized successfully")
else:
    logger.warning(
        "Supabase not configured. Check SUPABASE_URL and SUPABASE_SERVICE_KEY"
    )

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")



def get_supabase():
    """Get Supabase client or return None if not configured."""
    return supabase


def serialize_user(user_data):
    """Convert Supabase user data to frontend format."""
    if not user_data:
        return None
    return {
        "id": str(user_data.get("id", "")),
        "name": user_data.get("name", ""),
        "email": user_data.get("email", ""),
        "phone": user_data.get("phone", ""),
        "address": user_data.get("address", ""),
        "avatar_url": user_data.get("avatar_url", ""),
        "role": user_data.get("role", "user"),
        "created_at": user_data.get("created_at", ""),
    }


# ─── Register (Create User in Supabase Auth + Users Table) ────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    # Note: Rate limiting applied via app.py limiter configuration
    """Register new user with Supabase Auth."""
    try:
        sb = get_supabase()
        if not sb:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Authentication service not configured",
                    }
                ),
                503,
            )

        data = request.get_json() or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # Validation
        if not name or not email or not password:
            return (
                jsonify(
                    {"success": False, "message": "All fields are required"}
                ),
                400,
            )

        if len(password) < 6:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Password must be at least 6 characters",
                    }
                ),
                400,
            )

        # Register user in Supabase Auth
        try:
            auth_response = sb.auth.sign_up(
                {"email": email, "password": password}
            )
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Email already registered",
                        }
                    ),
                    409,
                )
            return (
                jsonify({"success": False, "message": f"Registration failed: {error_msg}"}),
                400,
            )

        user_id = auth_response.user.id if auth_response.user else None
        if not user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to create user account",
                    }
                ),
                400,
            )

        # Create user profile in public.users table
        try:
            user_profile = {
                "id": user_id,
                "email": email,
                "name": name,
                "role": "user",
                "created_at": datetime.utcnow().isoformat(),
            }
            sb.table("users").insert(user_profile).execute()
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            # User created in auth but profile failed - still return success

        # Store session info
        session["user_id"] = user_id
        session["email"] = email

        # Transfer guest cart to user
        guest_id = session.get("guest_id")
        if guest_id:
            guest_cart = carts_col.find_one({"user_id": guest_id})
            if guest_cart and guest_cart.get("items"):
                carts_col.update_one(
                    {"user_id": user_id},
                    {"$set": {"user_id": user_id, "items": guest_cart["items"]}},
                    upsert=True,
                )
                carts_col.delete_one({"user_id": guest_id})

        logger.info(f"User registered: {email}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Registration successful!",
                    "user": {
                        "id": user_id,
                        "email": email,
                        "name": name,
                        "role": "user",
                    },
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return (
            jsonify({"success": False, "message": "Registration failed"}),
            500,
        )


# ─── Login ────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    # Note: Rate limiting applied via app.py limiter configuration
    """Login user with Supabase Auth."""
    try:
        sb = get_supabase()
        if not sb:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Authentication service not configured",
                    }
                ),
                503,
            )

        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return (
                jsonify(
                    {"success": False, "message": "Email and password required"}
                ),
                400,
            )

        # Authenticate with Supabase
        try:
            auth_response = sb.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid credentials" in error_msg or "invalid login" in error_msg:
                return (
                    jsonify(
                        {"success": False, "message": "Invalid email or password"}
                    ),
                    401,
                )
            return (
                jsonify({"success": False, "message": "Login failed"}),
                400,
            )

        if not auth_response.user:
            return (
                jsonify({"success": False, "message": "Login failed"}),
                401,
            )

        user_id = auth_response.user.id
        access_token = auth_response.session.access_token if auth_response.session else None

        # Get user profile from public.users table
        try:
            user_response = sb.table("users").select("*").eq("id", user_id).execute()
            user_profile = (
                user_response.data[0] if user_response.data else {}
            )
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {e}")
            user_profile = {"id": user_id, "email": email}

        # Store session info
        session["user_id"] = user_id
        session["email"] = email
        session["access_token"] = access_token

        logger.info(f"User logged in: {email}")

        return jsonify(
            {
                "success": True,
                "message": "Login successful!",
                "user": serialize_user(user_profile),
                "access_token": access_token,
            }
        )

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"success": False, "message": "Login failed"}), 500


# ─── Logout ────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout user from Supabase."""
    try:
        sb = get_supabase()
        
        # Clear session
        user_id = session.pop("user_id", None)
        session.pop("email", None)
        session.pop("access_token", None)
        
        # Sign out from Supabase (server-side)
        if sb and user_id:
            try:
                sb.auth.sign_out()
            except Exception as e:
                logger.warning(f"Supabase sign out error: {e}")

        logger.info(f"User logged out: {user_id}")

        return jsonify(
            {
                "success": True,
                "message": "Logged out successfully",
            }
        )

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"success": False, "message": "Logout failed"}), 500


# ─── Get Profile (Current User) ────────────────────────────────
@auth_bp.route("/profile", methods=["GET"])
def get_profile():
    """Get current user profile from Supabase."""
    try:
        sb = get_supabase()
        if not sb:
            return jsonify({"success": False, "logged_in": False})

        user_id = session.get("user_id")
        
        if not user_id:
            return jsonify({"success": False, "logged_in": False})

        # Fetch user profile
        try:
            user_response = sb.table("users").select("*").eq("id", user_id).execute()
            if not user_response.data:
                return jsonify({"success": False, "logged_in": False})
            
            user_profile = user_response.data[0]
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {e}")
            return jsonify({"success": False, "logged_in": False})

        return jsonify(
            {
                "success": True,
                "logged_in": True,
                "user": serialize_user(user_profile),
            }
        )

    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        return jsonify({"success": False, "logged_in": False}), 500


# ─── Update Profile ────────────────────────────────
@auth_bp.route("/profile", methods=["PUT"])
def update_profile():
    """Update current user profile."""
    try:
        sb = get_supabase()
        if not sb:
            return jsonify({"success": False, "message": "Not authenticated"}), 401

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "Not authenticated"}), 401

        data = request.get_json() or {}
        
        # Allowed fields to update
        update_data = {}
        for field in ["name", "phone", "address", "avatar_url"]:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({"success": False, "message": "No data to update"}), 400

        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update user profile
        try:
            sb.table("users").update(update_data).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return jsonify({"success": False, "message": "Update failed"}), 400

        # Fetch updated profile
        try:
            user_response = sb.table("users").select("*").eq("id", user_id).execute()
            updated_user = user_response.data[0] if user_response.data else {}
        except Exception as e:
            logger.error(f"Failed to fetch updated profile: {e}")
            updated_user = {}

        logger.info(f"User profile updated: {user_id}")

        return jsonify(
            {
                "success": True,
                "message": "Profile updated successfully",
                "user": serialize_user(updated_user),
            }
        )

    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({"success": False, "message": "Update failed"}), 500


# ─── Password Reset (Supabase Email Link) ────────────────────────────────
@auth_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    # Note: Rate limiting applied via app.py limiter configuration
    """Request password reset email from Supabase."""
    try:
        sb = get_supabase()
        if not sb:
            return jsonify({"success": False, "message": "Service not configured"}), 503

        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()

        if not email:
            return (
                jsonify({"success": False, "message": "Email required"}),
                400,
            )

        # Request password reset
        try:
            sb.auth.reset_password_email(email)
        except Exception as e:
            logger.error(f"Password reset request error: {e}")
            # Don't expose whether email exists
            pass

        return jsonify(
            {
                "success": True,
                "message": "If email is registered, password reset link will be sent",
            }
        )

    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        return jsonify({"success": False, "message": "Request failed"}), 500
            "created_at": datetime.utcnow().isoformat(),
        }
    )
    session["password_reset_token"] = token
    session["password_reset_email"] = email

    html = password_reset_template(
        user_name=user.get("name", "User"), reset_code=reset_code
    )
    if is_email_configured():
        threading.Thread(
            target=send_email, args=(user["email"], "Password Reset Code 🔐", html)
        ).start()

    logger.info(f"Password reset requested for: {email}")

    response = {
        "success": True,
        "message": "If an account exists, a reset code has been sent.",
    }
    if should_expose_dev_reset_details():
        response["dev_reset_code"] = reset_code
    return jsonify(response)


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token") or session.get("password_reset_token", "")
    code = data.get("code", "")
    new_password = data.get("new_password", "")

    if not code or not new_password:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Reset code and new password are required",
                }
            ),
            400,
        )
    if not token:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Reset session expired. Please request a new code.",
                }
            ),
            400,
        )

    if len(new_password) < 6:
        return (
            jsonify(
                {"success": False, "message": "Password must be at least 6 characters"}
            ),
            400,
        )

    reset_doc = reset_tokens_col.find_one({"token": token, "code": code})
    if not reset_doc:
        return (
            jsonify({"success": False, "message": "Invalid or expired reset code"}),
            400,
        )

    if datetime.utcnow() > reset_doc["expires_at"]:
        reset_tokens_col.delete_one({"_id": reset_doc["_id"]})
        return jsonify({"success": False, "message": "Reset code has expired"}), 400

    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    users_col.update_one(
        {"email": reset_doc["email"]}, {"$set": {"password_hash": password_hash}}
    )
    reset_tokens_col.delete_many({"email": reset_doc["email"]})
    session.pop("password_reset_token", None)
    session.pop("password_reset_email", None)

    return jsonify(
        {"success": True, "message": "Password reset successfully! You can now login."}
    )


# ─── Avatar Upload ───────────────────────────────────
@auth_bp.route("/avatar", methods=["POST"])
@login_required
def upload_avatar():
    from bson import ObjectId

    data = request.get_json()
    image_data = data.get("image", "")

    if not image_data:
        return jsonify({"success": False, "message": "No image provided"}), 400

    try:
        if "," in image_data:
            header, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        ext = "png"
        if "jpeg" in image_data or "jpg" in image_data:
            ext = "jpg"
        elif "webp" in image_data:
            ext = "webp"

        filename = f'avatar_{session["user_id"]}.{ext}'
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(base64.b64decode(encoded))

        avatar_url = f"/assets/uploads/{filename}"
        users_col.update_one(
            {"_id": ObjectId(session["user_id"])}, {"$set": {"avatar": avatar_url}}
        )

        return jsonify(
            {"success": True, "message": "Avatar updated!", "avatar_url": avatar_url}
        )
    except Exception as e:
        logger.error(f"Avatar upload failed: {e}")
        return jsonify({"success": False, "message": f"Upload failed: {str(e)}"}), 500
