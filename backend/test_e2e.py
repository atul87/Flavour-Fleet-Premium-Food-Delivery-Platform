"""
Flavour Fleet — Comprehensive End-to-End API Test Suite
Tests all 18 backend endpoints systematically.
"""
import requests
import json

BASE = 'http://localhost:5000'
s = requests.Session()
passed = 0
failed = 0
errors = []

def test(name, condition, detail=''):
    global passed, failed, errors
    if condition:
        passed += 1
        print(f'  PASS: {name}')
    else:
        failed += 1
        errors.append(f'{name}: {detail}')
        print(f'  FAIL: {name} -> {detail}')

print('=' * 60)
print('PHASE 1: BACKEND API TESTING (18 endpoints)')
print('=' * 60)

# ──── AUTH ────
print('\n--- AUTH API (8 endpoints) ---')

r = s.post(f'{BASE}/api/auth/register', json={'name': 'E2E Tester', 'email': 'e2e_final@test.com', 'password': 'test1234'})
d = r.json()
test('1. Register new user', d.get('success') == True, str(d))

r2 = s.post(f'{BASE}/api/auth/register', json={'name': 'E2E Tester', 'email': 'e2e_final@test.com', 'password': 'test1234'})
d2 = r2.json()
test('2. Duplicate register blocked', d2.get('success') == False, str(d2))

r = s.post(f'{BASE}/api/auth/logout')
d = r.json()
test('3. Logout', d.get('success') == True, str(d))

r = s.post(f'{BASE}/api/auth/login', json={'email': 'e2e_final@test.com', 'password': 'test1234'})
d = r.json()
test('4. Login', d.get('success') == True, str(d))

s_bad = requests.Session()
r = s_bad.post(f'{BASE}/api/auth/login', json={'email': 'e2e_final@test.com', 'password': 'wrongpass'})
d = r.json()
test('5. Wrong password rejected', d.get('success') == False, str(d))

r = s.get(f'{BASE}/api/auth/profile')
d = r.json()
test('6. Get profile', d.get('success') == True and d.get('logged_in') == True, str(d))
test('7. Profile has avatar field', 'avatar' in d.get('user', {}), str(d.get('user', {})))

r = s.put(f'{BASE}/api/auth/profile', json={'name': 'E2E Updated', 'phone': '9876543210', 'address': '456 Test Blvd'})
d = r.json()
test('8. Update profile', d.get('success') == True, str(d))

r = s.get(f'{BASE}/api/auth/profile')
d = r.json()
test('9. Verify name updated', d['user']['name'] == 'E2E Updated', d['user']['name'])
test('10. Verify phone updated', d['user']['phone'] == '9876543210', d['user']['phone'])

r = s.post(f'{BASE}/api/auth/forgot-password', json={'email': 'e2e_final@test.com'})
d = r.json()
test('11. Forgot password', d.get('success') == True and d.get('token') is not None, str(d))
token = d.get('token', '')
code = d.get('code', '')

r = s.post(f'{BASE}/api/auth/reset-password', json={'token': token, 'code': code, 'new_password': 'newpass1234'})
d = r.json()
test('12. Reset password', d.get('success') == True, str(d))

s_new = requests.Session()
r = s_new.post(f'{BASE}/api/auth/login', json={'email': 'e2e_final@test.com', 'password': 'newpass1234'})
d = r.json()
test('13. Login with new password', d.get('success') == True, str(d))

r = s.post(f'{BASE}/api/auth/reset-password', json={'token': 'bad', 'code': 'bad', 'new_password': 'whatever'})
d = r.json()
test('14. Invalid reset rejected', d.get('success') == False, str(d))

# ──── MENU ────
print('\n--- MENU API (2 endpoints) ---')

r = s.get(f'{BASE}/api/menu')
d = r.json()
menu_count = d.get('count', 0)
test('15. Get all menu items', d.get('success') == True and menu_count > 0, f'count={menu_count}')

r = s.get(f'{BASE}/api/menu?category=pizza')
d = r.json()
pizza_count = d.get('count', 0)
test('16. Filter by pizza', d.get('success') == True and pizza_count > 0, f'count={pizza_count}')

items = d.get('items', [])
if items:
    item_id = items[0].get('item_id', '')
    r = s.get(f'{BASE}/api/menu/{item_id}')
    d2 = r.json()
    test('17. Get menu item by ID', d2.get('success') == True, str(d2)[:100])
else:
    test('17. Get menu item by ID', False, 'No items found')

# ──── RESTAURANTS ────
print('\n--- RESTAURANTS API (2 endpoints) ---')

r = s.get(f'{BASE}/api/restaurants')
d = r.json()
rest_count = d.get('count', 0)
test('18. Get all restaurants', d.get('success') == True and rest_count > 0, f'count={rest_count}')

r = s.get(f'{BASE}/api/restaurants?category=italian')
d = r.json()
test('19. Filter restaurants', d.get('success') == True, f'count={d.get("count", 0)}')

rests = s.get(f'{BASE}/api/restaurants').json().get('restaurants', [])
if rests:
    rid = str(rests[0].get('_id', ''))
    r = s.get(f'{BASE}/api/restaurants/{rid}')
    d2 = r.json()
    test('20. Get restaurant by ID', d2.get('success') == True, str(d2)[:100])
else:
    test('20. Get restaurant by ID', False, 'No restaurants')

# ──── CART ────
print('\n--- CART API (5 endpoints) ---')

r = s.delete(f'{BASE}/api/cart/clear')
test('21. Clear cart', r.json().get('success') == True, str(r.json()))

r = s.post(f'{BASE}/api/cart/add', json={
    'id': 'pizza-1', 'name': 'Pepperoni Pizza', 'price': 12.99,
    'image': 'pizza.png', 'restaurant': 'Pizza Palace', 'quantity': 1
})
d = r.json()
test('22. Add item to cart', d.get('success') == True, str(d))

r = s.post(f'{BASE}/api/cart/add', json={
    'id': 'burger-1', 'name': 'Cheeseburger', 'price': 10.99,
    'image': 'burger.png', 'restaurant': 'Burger Joint', 'quantity': 2
})
d = r.json()
test('23. Add second item', d.get('success') == True and len(d.get('items', [])) == 2, f'items={len(d.get("items", []))}')

r = s.get(f'{BASE}/api/cart')
d = r.json()
test('24. Get cart (2 items)', d.get('success') == True and len(d.get('items', [])) == 2, f'items={len(d.get("items", []))}')

r = s.put(f'{BASE}/api/cart/update', json={'id': 'pizza-1', 'quantity': 3})
d = r.json()
test('25. Update quantity', d.get('success') == True, str(d)[:80])
pizza = next((i for i in d.get('items', []) if i['id'] == 'pizza-1'), None)
test('26. Verify qty=3', pizza and pizza.get('quantity') == 3, str(pizza))

r = s.delete(f'{BASE}/api/cart/remove/burger-1')
d = r.json()
test('27. Remove item', d.get('success') == True and len(d.get('items', [])) == 1, f'items={len(d.get("items", []))}')

# ──── ORDERS ────
print('\n--- ORDERS API (3 endpoints) ---')

r = s.post(f'{BASE}/api/orders', json={
    'name': 'E2E Tester', 'address': '456 Test Blvd',
    'phone': '9876543210', 'city': 'Test City', 'zip': '12345',
    'payment_method': 'Credit Card'
})
d = r.json()
test('28. Place order', d.get('success') == True, str(d)[:100])
order_id = d.get('order', {}).get('order_id', '')
test('29. Order has ID', len(order_id) > 0, order_id)

r = s.get(f'{BASE}/api/cart')
d = r.json()
test('30. Cart cleared after order', len(d.get('items', [])) == 0, f'items={len(d.get("items", []))}')

r = s.get(f'{BASE}/api/orders')
d = r.json()
test('31. Get order history', d.get('success') == True and len(d.get('orders', [])) > 0, f'orders={len(d.get("orders", []))}')

r = s.get(f'{BASE}/api/orders/{order_id}')
d = r.json()
test('32. Get order by ID', d.get('success') == True and d.get('order', {}).get('order_id') == order_id, str(d)[:100])

# ──── OFFERS ────
print('\n--- OFFERS API (2 endpoints) ---')

r = s.get(f'{BASE}/api/offers')
d = r.json()
offer_count = len(d.get('offers', []))
test('33. Get all offers', d.get('success') == True and offer_count > 0, f'offers={offer_count}')

# Add cart items for promo test
s.post(f'{BASE}/api/cart/add', json={
    'id': 'test-promo', 'name': 'Test Item', 'price': 50.00,
    'image': '', 'restaurant': 'Test', 'quantity': 1
})
r = s.post(f'{BASE}/api/offers/validate', json={'code': 'WELCOME50'})
d = r.json()
test('34. Validate promo WELCOME50', d.get('success') == True, str(d))

r = s.post(f'{BASE}/api/offers/validate', json={'code': 'INVALIDCODE'})
d = r.json()
test('35. Invalid promo rejected', d.get('success') == False, str(d))

# Empty cart test
s.delete(f'{BASE}/api/cart/clear')
r = s.post(f'{BASE}/api/orders', json={'name': 'Test', 'address': 'x'})
d = r.json()
test('36. Empty cart order rejected', d.get('success') == False, str(d))

# ──── SUMMARY ────
print('\n' + '=' * 60)
print(f'RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests')
print('=' * 60)
if errors:
    print('\nFAILURES:')
    for e in errors:
        print(f'  X {e}')
else:
    print('\nALL TESTS PASSED!')
