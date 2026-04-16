"""ASCII-only admin API verification for Flavour Fleet."""
import time
import uuid

import requests

BASE = 'http://localhost:5000'


def check(name, response, expected_status=200, expect_success=None):
    try:
        payload = response.json()
    except Exception:
        payload = {'raw': response.text[:200]}

    ok = response.status_code == expected_status
    if expect_success is not None:
        ok = ok and payload.get('success') is expect_success

    status = 'PASS' if ok else 'FAIL'
    print(f'[{status}] {name} -> HTTP {response.status_code}')
    if not ok:
        print(f'       {payload}')
    return ok, payload


def main():
    session = requests.Session()
    suffix = uuid.uuid4().hex[:6]

    print('\nAdmin API verification\n')

    check('Login as admin', session.post(f'{BASE}/api/auth/login', json={
        'email': 'admin@flavourfleet.com',
        'password': 'admin123',
    }), expect_success=True)

    check('Profile check', session.get(f'{BASE}/api/auth/profile'), expect_success=True)
    check('GET /api/admin/stats', session.get(f'{BASE}/api/admin/stats'), expect_success=True)
    check('GET /api/admin/orders', session.get(f'{BASE}/api/admin/orders', params={'page': 1, 'per_page': 5}), expect_success=True)
    check('GET /api/admin/menu', session.get(f'{BASE}/api/admin/menu'), expect_success=True)

    menu_name = f'TEST_MENU_{suffix}'
    ok, payload = check('POST /api/admin/menu', session.post(f'{BASE}/api/admin/menu', json={
        'name': menu_name,
        'price': 8.99,
        'category': 'mexican',
        'restaurant': 'Test Restaurant',
        'description': 'Test item',
        'rating': 4.2,
    }), expected_status=201, expect_success=True)
    menu_id = payload.get('item', {}).get('_id') if ok else None
    if menu_id:
        check('PUT /api/admin/menu/<id>', session.put(f'{BASE}/api/admin/menu/{menu_id}', json={'name': f'{menu_name}_UPDATED', 'price': 9.49}), expect_success=True)
        check('DELETE /api/admin/menu/<id>', session.delete(f'{BASE}/api/admin/menu/{menu_id}'), expect_success=True)

    restaurant_name = f'TEST_RESTAURANT_{suffix}'
    ok, payload = check('POST /api/admin/restaurants', session.post(f'{BASE}/api/admin/restaurants', json={
        'name': restaurant_name,
        'category': 'italian',
        'rating': 4.5,
        'delivery_time': '25-35',
        'price_range': '$$',
        'address': '123 Test St',
    }), expected_status=201, expect_success=True)
    restaurant_id = payload.get('restaurant', {}).get('_id') if ok else None
    if restaurant_id:
        check('PUT /api/admin/restaurants/<id>', session.put(f'{BASE}/api/admin/restaurants/{restaurant_id}', json={'name': f'{restaurant_name}_UPDATED'}), expect_success=True)
        check('DELETE /api/admin/restaurants/<id>', session.delete(f'{BASE}/api/admin/restaurants/{restaurant_id}'), expect_success=True)

    offer_code = f'TEST{suffix}'.upper()
    ok, payload = check('POST /api/admin/offers', session.post(f'{BASE}/api/admin/offers', json={
        'code': offer_code,
        'title': 'Test Offer',
        'description': '50 percent off',
        'discount_type': 'percent',
        'discount_value': 50,
        'min_order': 10,
        'valid_till': 'Dec 31',
        'icon': 'tag',
    }), expected_status=201, expect_success=True)
    offer_id = payload.get('offer', {}).get('_id') if ok else None
    if offer_id:
        check('PUT /api/admin/offers/<id>', session.put(f'{BASE}/api/admin/offers/{offer_id}', json={'title': 'Updated Test Offer'}), expect_success=True)
        check('DELETE /api/admin/offers/<id>', session.delete(f'{BASE}/api/admin/offers/{offer_id}'), expect_success=True)

    check('GET /api/admin/users', session.get(f'{BASE}/api/admin/users', params={'page': 1, 'per_page': 10}), expect_success=True)
    check('GET /api/admin/analytics', session.get(f'{BASE}/api/admin/analytics'), expect_success=True)
    check('GET /api/admin/settings', session.get(f'{BASE}/api/admin/settings'), expect_success=True)
    check('PUT /api/admin/settings', session.put(f'{BASE}/api/admin/settings', json={
        'platform_name': 'Flavour Fleet',
        'delivery_fee': 3.99,
        'free_delivery_threshold': 25,
        'tax_percent': 8.5,
        'contact_email': 'admin@test.com',
    }), expect_success=True)

    session.post(f'{BASE}/api/auth/logout')
    check('Unauthenticated admin stats blocked', session.get(f'{BASE}/api/admin/stats'), expected_status=401, expect_success=False)

    user_email = f'testuser_{int(time.time())}_{suffix}@test.com'
    regular = requests.Session()
    regular.post(f'{BASE}/api/auth/register', json={'name': 'Test User', 'email': user_email, 'password': 'pass1234'})
    regular.post(f'{BASE}/api/auth/login', json={'email': user_email, 'password': 'pass1234'})
    check('Regular user admin stats blocked', regular.get(f'{BASE}/api/admin/stats'), expected_status=403, expect_success=False)

    print('\nAdmin verification complete.\n')


if __name__ == '__main__':
    main()
