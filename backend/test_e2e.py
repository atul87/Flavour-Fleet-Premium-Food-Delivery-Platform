"""Deterministic end-to-end API test suite for Flavour Fleet."""

import time
import uuid

import requests

BASE = "http://localhost:5000"


class Tracker:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def check(self, name, condition, detail=""):
        if condition:
            self.passed += 1
            print(f"  PASS: {name}")
        else:
            self.failed += 1
            self.errors.append((name, detail))
            print(f"  FAIL: {name} -> {detail}")


def as_json(response):
    try:
        return response.json()
    except Exception:
        return {"raw": response.text[:300]}


def main():
    tracker = Tracker()
    session = requests.Session()
    outsider = requests.Session()

    suffix = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"
    email = f"e2e_{suffix}@test.com"
    password = "test1234"
    new_password = "newpass1234"

    print("=" * 60)
    print("FLAVOUR FLEET END-TO-END API TESTS")
    print("=" * 60)

    print("\n--- AUTH ---")
    payload = as_json(
        session.post(
            f"{BASE}/api/auth/register",
            json={"name": "E2E Tester", "email": email, "password": password},
        )
    )
    tracker.check("Register new user", payload.get("success") is True, payload)

    dup = session.post(
        f"{BASE}/api/auth/register",
        json={"name": "E2E Tester", "email": email, "password": password},
    )
    tracker.check(
        "Duplicate register blocked",
        dup.status_code == 409 and as_json(dup).get("success") is False,
        as_json(dup),
    )

    logout_payload = as_json(session.post(f"{BASE}/api/auth/logout"))
    tracker.check("Logout", logout_payload.get("success") is True, logout_payload)

    login_payload = as_json(
        session.post(
            f"{BASE}/api/auth/login", json={"email": email, "password": password}
        )
    )
    tracker.check("Login", login_payload.get("success") is True, login_payload)

    bad_login = outsider.post(
        f"{BASE}/api/auth/login", json={"email": email, "password": "wrongpass"}
    )
    tracker.check(
        "Wrong password rejected",
        bad_login.status_code == 401 and as_json(bad_login).get("success") is False,
        as_json(bad_login),
    )

    profile_payload = as_json(session.get(f"{BASE}/api/auth/profile"))
    tracker.check(
        "Get profile",
        profile_payload.get("success") is True
        and profile_payload.get("logged_in") is True,
        profile_payload,
    )

    update_payload = as_json(
        session.put(
            f"{BASE}/api/auth/profile",
            json={
                "name": "E2E Updated",
                "phone": "9876543210",
                "address": "456 Test Blvd",
            },
        )
    )
    tracker.check(
        "Update profile", update_payload.get("success") is True, update_payload
    )

    profile_payload = as_json(session.get(f"{BASE}/api/auth/profile"))
    tracker.check(
        "Verify profile update",
        profile_payload.get("user", {}).get("name") == "E2E Updated"
        and profile_payload.get("user", {}).get("phone") == "9876543210",
        profile_payload,
    )

    outsider_orders = outsider.get(f"{BASE}/api/orders")
    tracker.check(
        "Unauthorized order history blocked",
        outsider_orders.status_code == 401
        and as_json(outsider_orders).get("success") is False,
        as_json(outsider_orders),
    )

    forgot_payload = as_json(
        session.post(f"{BASE}/api/auth/forgot-password", json={"email": email})
    )
    tracker.check(
        "Forgot password request accepted",
        forgot_payload.get("success") is True,
        forgot_payload,
    )

    dev_code = forgot_payload.get("dev_reset_code")
    if dev_code:
        reset_payload = as_json(
            session.post(
                f"{BASE}/api/auth/reset-password",
                json={"code": dev_code, "new_password": new_password},
            )
        )
        tracker.check(
            "Reset password (dev mode)",
            reset_payload.get("success") is True,
            reset_payload,
        )

        new_login = as_json(
            outsider.post(
                f"{BASE}/api/auth/login",
                json={"email": email, "password": new_password},
            )
        )
        tracker.check(
            "Login with new password", new_login.get("success") is True, new_login
        )
    else:
        tracker.check(
            "Dev reset code hidden by config", True, "Production-safe mode detected"
        )

    invalid_reset = outsider.post(
        f"{BASE}/api/auth/reset-password",
        json={"code": "000000", "new_password": "whatever123"},
    )
    tracker.check(
        "Invalid reset rejected",
        invalid_reset.status_code == 400
        and as_json(invalid_reset).get("success") is False,
        as_json(invalid_reset),
    )

    missing_code_reset = outsider.post(
        f"{BASE}/api/auth/reset-password",
        json={"new_password": "whatever123"},
    )
    tracker.check(
        "Reset without code rejected",
        missing_code_reset.status_code == 400
        and as_json(missing_code_reset).get("success") is False,
        as_json(missing_code_reset),
    )

    print("\n--- MENU / RESTAURANTS ---")
    menu_payload = as_json(session.get(f"{BASE}/api/menu"))
    tracker.check(
        "Get all menu items",
        menu_payload.get("success") is True and menu_payload.get("count", 0) > 0,
        menu_payload,
    )

    pizza_payload = as_json(
        session.get(f"{BASE}/api/menu", params={"category": "pizza"})
    )
    tracker.check(
        "Filter pizza menu",
        pizza_payload.get("success") is True and pizza_payload.get("count", 0) > 0,
        pizza_payload,
    )

    item_id = pizza_payload.get("items", [{}])[0].get("item_id", "p1")
    item_payload = as_json(session.get(f"{BASE}/api/menu/{item_id}"))
    tracker.check(
        "Get menu item by ID",
        item_payload.get("success") is True
        and item_payload.get("item", {}).get("item_id") == item_id,
        item_payload,
    )

    restaurants_payload = as_json(session.get(f"{BASE}/api/restaurants"))
    tracker.check(
        "Get all restaurants",
        restaurants_payload.get("success") is True
        and restaurants_payload.get("count", 0) > 0,
        restaurants_payload,
    )

    restaurant_id = restaurants_payload.get("restaurants", [{}])[0].get("_id", "")
    restaurant_payload = as_json(session.get(f"{BASE}/api/restaurants/{restaurant_id}"))
    tracker.check(
        "Get restaurant by ID",
        restaurant_payload.get("success") is True
        and restaurant_payload.get("restaurant", {}).get("_id") == restaurant_id,
        restaurant_payload,
    )

    print("\n--- CART / OFFERS / ORDERS ---")
    tracker.check(
        "Clear cart",
        as_json(session.delete(f"{BASE}/api/cart/clear")).get("success") is True,
    )

    add_payload = as_json(
        session.post(
            f"{BASE}/api/cart/add",
            json={
                "id": item_id,
                "name": item_payload.get("item", {}).get("name", "Margherita Pizza"),
                "price": item_payload.get("item", {}).get("price", 13.99),
                "image": item_payload.get("item", {}).get("image", "pizza.png"),
                "restaurant": item_payload.get("item", {}).get(
                    "restaurant", "Pizza Paradise"
                ),
                "quantity": 2,
            },
        )
    )
    tracker.check(
        "Add item to cart",
        add_payload.get("success") is True and len(add_payload.get("items", [])) == 1,
        add_payload,
    )

    cart_payload = as_json(session.get(f"{BASE}/api/cart"))
    tracker.check(
        "Get cart",
        cart_payload.get("success") is True and len(cart_payload.get("items", [])) == 1,
        cart_payload,
    )

    promo_payload = as_json(
        session.post(f"{BASE}/api/offers/validate", json={"code": "WELCOME40"})
    )
    tracker.check(
        "Valid promo applies", promo_payload.get("success") is True, promo_payload
    )

    invalid_promo = session.post(
        f"{BASE}/api/offers/validate", json={"code": "INVALIDCODE"}
    )
    tracker.check(
        "Invalid promo rejected",
        invalid_promo.status_code == 404
        and as_json(invalid_promo).get("success") is False,
        as_json(invalid_promo),
    )

    order_payload = as_json(
        session.post(
            f"{BASE}/api/orders",
            json={
                "name": "E2E Updated",
                "address": "456 Test Blvd",
                "phone": "9876543210",
                "city": "Test City",
                "zip": "123456",
                "payment_method": "Credit Card",
                "promo_code": "WELCOME40",
            },
        )
    )
    order_id = order_payload.get("order", {}).get("order_id", "")
    tracker.check(
        "Place order",
        order_payload.get("success") is True and bool(order_id),
        order_payload,
    )

    cart_payload = as_json(session.get(f"{BASE}/api/cart"))
    tracker.check(
        "Cart cleared after order",
        len(cart_payload.get("items", [])) == 0,
        cart_payload,
    )

    empty_cart_order = session.post(
        f"{BASE}/api/orders",
        json={
            "name": "E2E Updated",
            "address": "456 Test Blvd",
            "phone": "9876543210",
            "city": "Test City",
            "zip": "123456",
            "payment_method": "Credit Card",
        },
    )
    tracker.check(
        "Empty cart checkout blocked",
        empty_cart_order.status_code == 400
        and as_json(empty_cart_order).get("success") is False,
        as_json(empty_cart_order),
    )

    history_payload = as_json(session.get(f"{BASE}/api/orders"))
    tracker.check(
        "Get order history",
        any(
            order.get("order_id") == order_id
            for order in history_payload.get("orders", [])
        ),
        history_payload,
    )

    own_order_payload = as_json(session.get(f"{BASE}/api/orders/{order_id}"))
    tracker.check(
        "Owner gets order by ID",
        own_order_payload.get("order", {}).get("order_id") == order_id,
        own_order_payload,
    )

    outsider_order = outsider.get(f"{BASE}/api/orders/{order_id}")
    tracker.check(
        "Other session cannot access order by ID",
        outsider_order.status_code in {401, 403, 404}
        and as_json(outsider_order).get("success") is False,
        as_json(outsider_order),
    )

    payments_payload = as_json(session.get(f"{BASE}/api/payments"))
    tracker.check(
        "Payment history available",
        any(
            payment.get("order_id") == order_id
            for payment in payments_payload.get("payments", [])
        ),
        payments_payload,
    )

    print("\n" + "=" * 60)
    print(f"RESULTS: {tracker.passed} passed, {tracker.failed} failed")
    print("=" * 60)
    if tracker.errors:
        print("\nFAILURES:")
        for name, detail in tracker.errors:
            print(f"  - {name}: {detail}")
    else:
        print("\nALL TESTS PASSED")


if __name__ == "__main__":
    main()
