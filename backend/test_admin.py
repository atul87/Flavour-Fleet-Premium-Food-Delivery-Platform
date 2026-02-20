"""
End-to-end test for ALL Admin Dashboard API endpoints.
"""
import requests, json, sys

BASE = 'http://localhost:5000'
s = requests.Session()

PASS = 0
FAIL = 0

def test(name, response, expect_success=True, expect_status=200):
    global PASS, FAIL
    ok = response.status_code == expect_status
    data = None
    try:
        data = response.json()
        if expect_success and not data.get('success'):
            ok = False
    except:
        if expect_status == 200:
            ok = False

    if ok:
        PASS += 1
        print(f'  ✅ {name} — HTTP {response.status_code}')
    else:
        FAIL += 1
        print(f'  ❌ {name} — HTTP {response.status_code}')
        if data:
            print(f'     Response: {json.dumps(data, indent=2)[:200]}')
    return data

# ════════════════════════════════════════════
print('\n🔐 TEST 1: Admin Login')
# ════════════════════════════════════════════
data = test('Login as admin', s.post(f'{BASE}/api/auth/login', json={
    'email': 'admin@flavourfleet.com', 'password': 'admin123'
}))

# ════════════════════════════════════════════
print('\n👤 TEST 2: Profile (role = admin)')
# ════════════════════════════════════════════
data = test('Profile check', s.get(f'{BASE}/api/auth/profile'))
if data and data.get('user', {}).get('role') == 'admin':
    print(f'     → role = admin ✅')
else:
    print(f'     → role check FAILED ❌')

# ════════════════════════════════════════════
print('\n📊 TEST 3: Admin Stats')
# ════════════════════════════════════════════
data = test('GET /api/admin/stats', s.get(f'{BASE}/api/admin/stats'))
if data:
    st = data.get('stats', {})
    print(f'     → orders={st.get("total_orders")}, revenue=${st.get("total_revenue")}, '
          f'users={st.get("total_users")}, menu={st.get("total_menu_items")}, restaurants={st.get("total_restaurants")}')

# ════════════════════════════════════════════
print('\n📦 TEST 4: Admin Orders')
# ════════════════════════════════════════════
data = test('GET /api/admin/orders', s.get(f'{BASE}/api/admin/orders', params={'page': 1, 'per_page': 5}))
if data:
    print(f'     → total={data.get("total")}, page={data.get("page")}')

# ════════════════════════════════════════════
print('\n🍔 TEST 5: Menu CRUD')
# ════════════════════════════════════════════
# GET
data = test('GET /api/admin/menu', s.get(f'{BASE}/api/admin/menu'))
if data:
    print(f'     → {data.get("count")} menu items')

# POST - add new item
data = test('POST /api/admin/menu', s.post(f'{BASE}/api/admin/menu', json={
    'name': 'TEST_Spicy Taco', 'price': 8.99, 'category': 'mexican',
    'restaurant': 'Test Restaurant', 'description': 'Test item', 'rating': 4.2
}))
new_menu_id = None
if data:
    new_menu_id = data.get('item_id') or data.get('id')
    print(f'     → created item id: {new_menu_id}')

# To get the id, fetch the list again
data = test('GET menu to find test item', s.get(f'{BASE}/api/admin/menu'))
if data:
    for item in data.get('items', []):
        if item.get('name') == 'TEST_Spicy Taco':
            new_menu_id = item.get('_id')
            print(f'     → found test item _id: {new_menu_id}')
            break

# PUT - update
if new_menu_id:
    data = test('PUT /api/admin/menu/<id>', s.put(f'{BASE}/api/admin/menu/{new_menu_id}', json={
        'name': 'TEST_Updated Taco', 'price': 9.49
    }))

# DELETE
if new_menu_id:
    data = test('DELETE /api/admin/menu/<id>', s.delete(f'{BASE}/api/admin/menu/{new_menu_id}'))

# ════════════════════════════════════════════
print('\n🏪 TEST 6: Restaurants CRUD')
# ════════════════════════════════════════════
data = test('GET /api/admin/restaurants', s.get(f'{BASE}/api/admin/restaurants'))
if data:
    print(f'     → {len(data.get("restaurants", []))} restaurants')

# POST
data = test('POST /api/admin/restaurants', s.post(f'{BASE}/api/admin/restaurants', json={
    'name': 'TEST_Bistro', 'category': 'italian', 'rating': 4.5,
    'delivery_time': '25-35', 'price_range': '$$', 'address': '123 Test St'
}))

# Find the new restaurant
data = test('GET restaurants to find test', s.get(f'{BASE}/api/admin/restaurants'))
new_rest_id = None
if data:
    for r in data.get('restaurants', []):
        if r.get('name') == 'TEST_Bistro':
            new_rest_id = r.get('_id')
            print(f'     → found test restaurant _id: {new_rest_id}')
            break

# PUT
if new_rest_id:
    data = test('PUT /api/admin/restaurants/<id>', s.put(f'{BASE}/api/admin/restaurants/{new_rest_id}', json={
        'name': 'TEST_Updated Bistro', 'rating': 4.8
    }))

# DELETE
if new_rest_id:
    data = test('DELETE /api/admin/restaurants/<id>', s.delete(f'{BASE}/api/admin/restaurants/{new_rest_id}'))

# ════════════════════════════════════════════
print('\n🎟 TEST 7: Offers CRUD')
# ════════════════════════════════════════════
data = test('GET /api/admin/offers', s.get(f'{BASE}/api/admin/offers'))
if data:
    print(f'     → {len(data.get("offers", []))} offers')

# POST
data = test('POST /api/admin/offers', s.post(f'{BASE}/api/admin/offers', json={
    'code': 'TESTCODE50', 'title': 'Test Offer', 'description': '50% off test',
    'discount_type': 'percent', 'discount_value': 50, 'min_order': 10,
    'valid_till': 'Dec 31', 'icon': '🎉'
}))

# Find offer
data = test('GET offers to find test', s.get(f'{BASE}/api/admin/offers'))
new_offer_id = None
if data:
    for o in data.get('offers', []):
        if o.get('code') == 'TESTCODE50':
            new_offer_id = o.get('_id')
            print(f'     → found test offer _id: {new_offer_id}')
            break

# PUT
if new_offer_id:
    data = test('PUT /api/admin/offers/<id>', s.put(f'{BASE}/api/admin/offers/{new_offer_id}', json={
        'title': 'Updated Test Offer', 'discount_value': 40
    }))

# DELETE
if new_offer_id:
    data = test('DELETE /api/admin/offers/<id>', s.delete(f'{BASE}/api/admin/offers/{new_offer_id}'))

# ════════════════════════════════════════════
print('\n👥 TEST 8: Users')
# ════════════════════════════════════════════
data = test('GET /api/admin/users', s.get(f'{BASE}/api/admin/users', params={'page': 1, 'per_page': 10}))
if data:
    print(f'     → {data.get("total")} users total')

# ════════════════════════════════════════════
print('\n📊 TEST 9: Analytics')
# ════════════════════════════════════════════
data = test('GET /api/admin/analytics', s.get(f'{BASE}/api/admin/analytics'))
if data:
    print(f'     → daily_data days: {len(data.get("daily_data",[]))}')
    print(f'     → status_breakdown: {data.get("status_breakdown",{})}')
    print(f'     → top_items: {len(data.get("top_items",[]))}')

# ════════════════════════════════════════════
print('\n⚙ TEST 10: Settings')
# ════════════════════════════════════════════
data = test('GET /api/admin/settings', s.get(f'{BASE}/api/admin/settings'))
if data:
    print(f'     → settings: {data.get("settings")}')

# PUT settings
data = test('PUT /api/admin/settings', s.put(f'{BASE}/api/admin/settings', json={
    'platform_name': 'Flavour Fleet', 'delivery_fee': 3.99,
    'free_delivery_threshold': 25, 'tax_percent': 8.5, 'contact_email': 'admin@test.com'
}))

# ════════════════════════════════════════════
print('\n🚫 TEST 11: Non-Admin Redirect Check')
# ════════════════════════════════════════════
# Logout
s.post(f'{BASE}/api/auth/logout')
data = test('Unauthenticated /api/admin/stats → 401',
    s.get(f'{BASE}/api/admin/stats'), expect_success=False, expect_status=401)

# Login as regular user (register first)
s2 = requests.Session()
reg = s2.post(f'{BASE}/api/auth/register', json={
    'name': 'TestUser', 'email': 'testuser99@test.com', 'password': 'pass123'
})
# If already exists, login
s2.post(f'{BASE}/api/auth/login', json={'email': 'testuser99@test.com', 'password': 'pass123'})
data = test('Regular user /api/admin/stats → 403',
    s2.get(f'{BASE}/api/admin/stats'), expect_success=False, expect_status=403)

# ════════════════════════════════════════════
print(f'\n{"="*50}')
print(f'🏁 RESULTS: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests')
if FAIL == 0:
    print('🎉 ALL TESTS PASSED!')
else:
    print('⚠️  Some tests failed — check output above')
print(f'{"="*50}\n')
