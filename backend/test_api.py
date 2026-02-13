"""Quick test script for Flavour Fleet API endpoints"""
import urllib.request
import json

BASE = 'http://localhost:5000/api'

def test(name, url, method='GET', data=None):
    try:
        if data:
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method=method)
        else:
            req = urllib.request.Request(url, method=method)
        r = urllib.request.urlopen(req)
        d = json.loads(r.read())
        print(f'  ✅ {name}: {json.dumps({k:v for k,v in d.items() if k != "items" and k != "offers" and k != "restaurants" and k != "orders"}, default=str)}')
        return d
    except Exception as e:
        print(f'  ❌ {name}: {e}')
        return None

print('\n🧪 Testing Flavour Fleet API\n')

# Menu
print('── Menu ──')
d = test('GET /api/menu', f'{BASE}/menu')
if d: print(f'     → {d["count"]} items')
test('GET /api/menu?category=pizza', f'{BASE}/menu?category=pizza')
test('GET /api/menu/p1', f'{BASE}/menu/p1')

# Restaurants
print('\n── Restaurants ──')
d = test('GET /api/restaurants', f'{BASE}/restaurants')
if d: print(f'     → {d["count"]} restaurants')

# Offers
print('\n── Offers ──')
d = test('GET /api/offers', f'{BASE}/offers')
if d: print(f'     → {len(d["offers"])} offers')

# Auth
print('\n── Auth ──')
test('GET /api/auth/profile (no session)', f'{BASE}/auth/profile')
test('POST /api/auth/register', f'{BASE}/auth/register', 'POST', {
    'name': 'Test User', 'email': 'apitest@test.com', 'password': 'test123'
})
test('POST /api/auth/login', f'{BASE}/auth/login', 'POST', {
    'email': 'apitest@test.com', 'password': 'test123'
})

# Cart (uses session cookies, so will test basic responses)
print('\n── Cart ──')
test('GET /api/cart', f'{BASE}/cart')
test('POST /api/cart/add', f'{BASE}/cart/add', 'POST', {
    'id': 'p1', 'name': 'Margherita Pizza', 'price': 13.99, 'image': 'pizza.png', 'restaurant': 'Pizza Paradise', 'quantity': 2
})

# Offers validation
print('\n── Offers Validation ──')
test('POST /api/offers/validate (WELCOME40)', f'{BASE}/offers/validate', 'POST', {'code': 'WELCOME40'})
test('POST /api/offers/validate (INVALID)', f'{BASE}/offers/validate', 'POST', {'code': 'INVALID'})

print('\n✅ All tests completed!\n')
