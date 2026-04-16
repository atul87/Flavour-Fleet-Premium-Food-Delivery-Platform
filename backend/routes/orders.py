# ============================================
# FLAVOUR FLEET — Orders Routes Blueprint
# ============================================

import secrets
import threading
from datetime import datetime

from flask import Blueprint, request, jsonify, session
from db import carts_col, orders_col, users_col
from helpers import get_user_id, logger, login_required
from routes.offers import calculate_offer_discount, validate_offer_for_subtotal

from utils.email_service import send_email
from utils.email_templates import order_confirmation_template

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


def sanitize_order(order):
    """Return an API-safe order payload without sensitive PII fields."""
    clean = dict(order)
    clean.pop("user_id", None)
    clean.pop("phone", None)
    clean.pop("address", None)
    clean.pop("city", None)
    clean.pop("zip", None)
    clean.pop("name", None)
    clean.pop("instructions", None)
    if "_id" in clean:
        clean["_id"] = str(clean["_id"])
    return clean


@orders_bp.route("", methods=["POST"])
def place_order():
    uid = get_user_id()
    data = request.get_json()

    # Get cart items
    cart = carts_col.find_one({"user_id": uid})
    if not cart or not cart.get("items"):
        return jsonify({"success": False, "message": "Cart is empty"}), 400

    items = cart["items"]
    subtotal = sum(i["price"] * i["quantity"] for i in items)
    delivery_fee = 0 if subtotal > 30 else 4.99
    tax = round(subtotal * 0.08, 2)

    # Server-side promo code re-validation (never trust client discount)
    promo_code = data.get("promo_code", "").upper().strip()
    discount = 0
    if promo_code:
        offer, error_message, error_status = validate_offer_for_subtotal(
            promo_code, subtotal, delivery_fee
        )
        if error_message:
            return jsonify({"success": False, "message": error_message}), error_status
        discount = calculate_offer_discount(offer, subtotal, delivery_fee)

    total = round(subtotal + delivery_fee + tax - discount, 2)

    order_id = "ORD-" + secrets.token_hex(4).upper()

    order = {
        "order_id": order_id,
        "user_id": uid,
        "items": [{**i, "item_id": i.get("id", "")} for i in items],
        "items_summary": ", ".join(i["name"] for i in items),
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "tax": tax,
        "discount": discount,
        "promo_code": promo_code if promo_code else None,
        "total": total,
        "status": "preparing",
        "status_history": [
            {"status": "preparing", "timestamp": datetime.utcnow().isoformat()}
        ],
        "address": data.get("address", ""),
        "phone": data.get("phone", ""),
        "name": data.get("name", ""),
        "city": data.get("city", ""),
        "zip": data.get("zip", ""),
        "instructions": data.get("instructions", ""),
        "payment_method": data.get("payment_method", "Credit Card"),
        "restaurant": items[0].get("restaurant", "Mixed"),
        "created_at": datetime.utcnow().isoformat(),
    }

    orders_col.insert_one(order)

    # Clear cart
    carts_col.update_one({"user_id": uid}, {"$set": {"items": []}})

    # Record payment
    from routes.payments import record_payment

    record_payment(uid, order_id, total, data.get("payment_method", "Credit Card"))

    # Send order confirmation email (non-blocking)
    user = (
        users_col.find_one({"_id": session.get("user_id")})
        if session.get("user_id")
        else None
    )
    if not user:
        from bson import ObjectId

        user = (
            users_col.find_one({"_id": ObjectId(uid)})
            if ObjectId.is_valid(uid)
            else None
        )
    if user and user.get("email"):
        html = order_confirmation_template(
            user_name=user.get("name", "Customer"),
            order_id=order_id,
            items_summary=order["items_summary"],
            total=total,
        )
        threading.Thread(
            target=send_email, args=(user["email"], "Your Order is Confirmed 🍔", html)
        ).start()

    # Return a sanitized order payload
    order = sanitize_order(order)

    logger.info(f"Order placed: {order_id} by user {uid}")

    return (
        jsonify(
            {
                "success": True,
                "message": "Order placed successfully! 🎉",
                "order": order,
            }
        ),
        201,
    )


@orders_bp.route("", methods=["GET"])
@login_required
def get_orders():
    uid = get_user_id()
    orders = list(orders_col.find({"user_id": uid}).sort("created_at", -1))
    orders = [sanitize_order(o) for o in orders]
    return jsonify({"success": True, "orders": orders})


@orders_bp.route("/<order_id>", methods=["GET"])
@login_required
def get_order(order_id):
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    order = orders_col.find_one({"order_id": order_id})
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    is_admin = session.get("user_role") == "admin"
    if not is_admin and order.get("user_id") != current_user_id:
        return jsonify({"success": False, "message": "Forbidden"}), 403

    order = sanitize_order(order)
    return jsonify({"success": True, "order": order})
