"""Deterministic API smoke test for Flavour Fleet."""
import time
import uuid

import requests

BASE = 'http://localhost:5000/api'


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
    return payload


def main():
    session = requests.Session()
    email = f'apitest_{int(time.time())}_{uuid.uuid4().hex[:6]}@test.com'

    print('\nFlavour Fleet API smoke test\n')

    payload = check('GET /menu', session.get(f'{BASE}/menu'), expect_success=True)
    if payload.get('success'):
        print(f'       items={payload.get("count", 0)}')

    check('GET /menu?category=pizza', session.get(f'{BASE}/menu', params={'category': 'pizza'}), expect_success=True)
    check('GET /menu/p1', session.get(f'{BASE}/menu/p1'), expect_success=True)

    payload = check('GET /restaurants', session.get(f'{BASE}/restaurants'), expect_success=True)
    if payload.get('success'):
        print(f'       restaurants={payload.get("count", 0)}')

    payload = check('GET /offers', session.get(f'{BASE}/offers'), expect_success=True)
    if payload.get('success'):
        print(f'       offers={len(payload.get("offers", []))}')

    check('GET /auth/profile (anon)', session.get(f'{BASE}/auth/profile'), expected_status=200, expect_success=False)
    check('POST /auth/register', session.post(f'{BASE}/auth/register', json={'name': 'API Test User', 'email': email, 'password': 'test1234'}), expected_status=201, expect_success=True)
    check('POST /auth/login', session.post(f'{BASE}/auth/login', json={'email': email, 'password': 'test1234'}), expect_success=True)

    check('GET /cart', session.get(f'{BASE}/cart'), expect_success=True)
    check('POST /cart/add', session.post(f'{BASE}/cart/add', json={
        'id': 'p1',
        'name': 'Margherita Pizza',
        'price': 13.99,
        'image': 'pizza.png',
        'restaurant': 'Pizza Paradise',
        'quantity': 2,
    }), expect_success=True)

    check('POST /offers/validate (valid)', session.post(f'{BASE}/offers/validate', json={'code': 'WELCOME40'}), expect_success=True)
    check('POST /offers/validate (invalid)', session.post(f'{BASE}/offers/validate', json={'code': 'INVALID'}), expected_status=404, expect_success=False)

    print('\nSmoke test complete.\n')


if __name__ == '__main__':
    main()
