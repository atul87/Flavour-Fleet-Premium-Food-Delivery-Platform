# ============================================
# FLAVOUR FLEET — MongoDB Seed Script
# ============================================

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['flavourfleet']


def seed_menu_items():
    """Seed all menu items matching the frontend."""
    db.menu_items.drop()
    items = [
        # ── Pizza ──
        {'item_id': 'p1', 'name': 'Margherita Pizza', 'price': 13.99, 'category': 'pizza',
         'image': 'assets/images/pizza.png', 'restaurant': 'Pizza Paradise',
         'rating': 4.9, 'badge': 'Bestseller', 'description': 'Fresh mozzarella, basil, tomato sauce on hand-tossed dough'},
        {'item_id': 'p2', 'name': 'Pepperoni Pizza', 'price': 15.99, 'category': 'pizza',
         'image': 'assets/images/pizza.png', 'restaurant': 'Pizza Paradise',
         'rating': 4.8, 'badge': 'Popular', 'description': 'Loaded with spicy pepperoni and extra mozzarella cheese'},
        {'item_id': 'p3', 'name': 'BBQ Chicken Pizza', 'price': 16.99, 'category': 'pizza',
         'image': 'assets/images/pizza.png', 'restaurant': 'Pizza Paradise',
         'rating': 4.7, 'badge': '', 'description': 'Smoky BBQ sauce, grilled chicken, red onion, cilantro'},
        {'item_id': 'p4', 'name': 'Four Cheese Pizza', 'price': 17.49, 'category': 'pizza',
         'image': 'assets/images/pizza.png', 'restaurant': 'Pizza Paradise',
         'rating': 4.8, 'badge': 'New', 'description': 'Mozzarella, parmesan, gorgonzola, and ricotta blend'},

        # ── Burgers ──
        {'item_id': 'b1', 'name': 'Classic Cheeseburger', 'price': 11.99, 'category': 'burger',
         'image': 'assets/images/burger.png', 'restaurant': 'Burger Palace',
         'rating': 4.8, 'badge': 'Bestseller', 'description': 'Angus beef patty, cheddar, lettuce, tomato, special sauce'},
        {'item_id': 'b2', 'name': 'BBQ Bacon Burger', 'price': 14.99, 'category': 'burger',
         'image': 'assets/images/burger.png', 'restaurant': 'Burger Palace',
         'rating': 4.9, 'badge': 'Popular', 'description': 'Double patty, crispy bacon, onion rings, smoky BBQ sauce'},
        {'item_id': 'b3', 'name': 'Mushroom Swiss Burger', 'price': 13.49, 'category': 'burger',
         'image': 'assets/images/burger.png', 'restaurant': 'Burger Palace',
         'rating': 4.7, 'badge': 'Chef Pick', 'description': 'Sautéed mushrooms, Swiss cheese, garlic aioli, brioche bun'},

        # ── Sushi ──
        {'item_id': 's1', 'name': 'Dragon Roll', 'price': 18.99, 'category': 'sushi',
         'image': 'assets/images/sushi.png', 'restaurant': 'Tokyo Bites',
         'rating': 4.9, 'badge': 'Chef Special', 'description': 'Shrimp tempura, avocado, eel sauce, tobiko on top'},
        {'item_id': 's2', 'name': 'Salmon Nigiri', 'price': 14.99, 'category': 'sushi',
         'image': 'assets/images/sushi.png', 'restaurant': 'Tokyo Bites',
         'rating': 4.8, 'badge': 'Popular', 'description': 'Fresh Atlantic salmon over seasoned sushi rice, wasabi'},
        {'item_id': 's3', 'name': 'Rainbow Roll', 'price': 19.99, 'category': 'sushi',
         'image': 'assets/images/sushi.png', 'restaurant': 'Tokyo Bites',
         'rating': 4.9, 'badge': '', 'description': 'California roll topped with assorted sashimi and avocado'},

        # ── Indian ──
        {'item_id': 'i1', 'name': 'Butter Chicken', 'price': 15.99, 'category': 'indian',
         'image': 'assets/images/curry.png', 'restaurant': 'Spice Garden',
         'rating': 4.9, 'badge': 'Bestseller', 'description': 'Creamy tomato-based curry with tender tikka chicken, served with naan'},
        {'item_id': 'i2', 'name': 'Lamb Biryani', 'price': 17.99, 'category': 'indian',
         'image': 'assets/images/curry.png', 'restaurant': 'Spice Garden',
         'rating': 4.8, 'badge': 'Popular', 'description': 'Fragrant basmati rice layered with spiced lamb and saffron'},
        {'item_id': 'i3', 'name': 'Paneer Tikka Masala', 'price': 14.49, 'category': 'indian',
         'image': 'assets/images/curry.png', 'restaurant': 'Spice Garden',
         'rating': 4.7, 'badge': 'Veg', 'description': 'Grilled paneer cubes in rich, creamy masala gravy with bell peppers'},
        {'item_id': 'i4', 'name': 'Chicken Tandoori', 'price': 16.49, 'category': 'indian',
         'image': 'assets/images/curry.png', 'restaurant': 'Tandoori Nights',
         'rating': 4.8, 'badge': '', 'description': 'Spiced clay-oven roasted chicken with mint chutney'},

        # ── Mexican ──
        {'item_id': 'm1', 'name': 'Street Tacos', 'price': 11.49, 'category': 'mexican',
         'image': 'assets/images/tacos.png', 'restaurant': 'El Fuego Cantina',
         'rating': 4.8, 'badge': 'Bestseller', 'description': 'Carne asada, onion, cilantro, lime on corn tortillas'},
        {'item_id': 'm2', 'name': 'Loaded Burrito', 'price': 12.99, 'category': 'mexican',
         'image': 'assets/images/tacos.png', 'restaurant': 'El Fuego Cantina',
         'rating': 4.7, 'badge': 'Popular', 'description': 'Chicken, rice, beans, cheese, sour cream, guacamole wrapped'},
        {'item_id': 'm3', 'name': 'Nachos Supreme', 'price': 10.99, 'category': 'mexican',
         'image': 'assets/images/tacos.png', 'restaurant': 'El Fuego Cantina',
         'rating': 4.6, 'badge': '', 'description': 'Loaded tortilla chips with jalapeños, cheese, salsa, and guac'},

        # ── Pasta ──
        {'item_id': 'pa1', 'name': 'Classic Carbonara', 'price': 14.99, 'category': 'pasta',
         'image': 'assets/images/pasta.png', 'restaurant': 'Bella Cucina',
         'rating': 4.9, 'badge': 'Chef Pick', 'description': 'Spaghetti, pancetta, egg, parmesan — creamy Roman style'},
        {'item_id': 'pa2', 'name': 'Penne Arrabbiata', 'price': 12.99, 'category': 'pasta',
         'image': 'assets/images/pasta.png', 'restaurant': 'Bella Cucina',
         'rating': 4.6, 'badge': 'Spicy', 'description': 'Penne in fiery tomato sauce with garlic and chili flakes'},
        {'item_id': 'pa3', 'name': 'Truffle Mushroom Pasta', 'price': 19.99, 'category': 'pasta',
         'image': 'assets/images/pasta.png', 'restaurant': 'Bella Cucina',
         'rating': 4.9, 'badge': 'Premium', 'description': 'Tagliatelle with wild mushrooms, truffle oil, and parmesan shavings'},

        # ── Salad / Healthy ──
        {'item_id': 'sa1', 'name': 'Caesar Salad', 'price': 10.99, 'category': 'salad',
         'image': 'assets/images/salad.png', 'restaurant': 'Green Bowl Co.',
         'rating': 4.7, 'badge': 'Healthy', 'description': 'Romaine, parmesan, croutons, grilled chicken, classic dressing'},
        {'item_id': 'sa2', 'name': 'Quinoa Power Bowl', 'price': 12.49, 'category': 'salad',
         'image': 'assets/images/salad.png', 'restaurant': 'Green Bowl Co.',
         'rating': 4.8, 'badge': 'Vegan', 'description': 'Quinoa, roasted veggies, avocado, tahini lemon dressing'},

        # ── Chinese ──
        {'item_id': 'c1', 'name': 'Kung Pao Chicken', 'price': 14.99, 'category': 'chinese',
         'image': 'assets/images/chinese.png', 'restaurant': 'Golden Dragon',
         'rating': 4.8, 'badge': 'Bestseller', 'description': 'Spicy stir-fried chicken with peanuts, vegetables, chili peppers'},
        {'item_id': 'c2', 'name': 'Dim Sum Platter', 'price': 16.99, 'category': 'chinese',
         'image': 'assets/images/chinese.png', 'restaurant': 'Golden Dragon',
         'rating': 4.7, 'badge': 'Popular', 'description': 'Assorted steamed dumplings — har gow, siu mai, char siu bao'},
        {'item_id': 'c3', 'name': 'Vegetable Chow Mein', 'price': 11.99, 'category': 'chinese',
         'image': 'assets/images/chinese.png', 'restaurant': 'Wok This Way',
         'rating': 4.6, 'badge': 'Veg', 'description': 'Stir-fried noodles with mixed vegetables and soy sauce'},

        # ── Dessert ──
        {'item_id': 'd1', 'name': 'Chocolate Lava Cake', 'price': 8.99, 'category': 'dessert',
         'image': 'assets/images/dessert.png', 'restaurant': 'Sweet Tooth Bakery',
         'rating': 4.9, 'badge': 'Must Try', 'description': 'Warm, gooey chocolate center with vanilla ice cream'},
        {'item_id': 'd2', 'name': 'Tiramisu', 'price': 9.49, 'category': 'dessert',
         'image': 'assets/images/dessert.png', 'restaurant': 'Sweet Tooth Bakery',
         'rating': 4.8, 'badge': 'Classic', 'description': 'Layers of espresso-soaked ladyfingers, mascarpone, cocoa'},
        {'item_id': 'd3', 'name': 'New York Cheesecake', 'price': 8.49, 'category': 'dessert',
         'image': 'assets/images/dessert.png', 'restaurant': 'Sweet Tooth Bakery',
         'rating': 4.7, 'badge': 'Popular', 'description': 'Classic creamy cheesecake with graham cracker crust'},
        {'item_id': 'd4', 'name': 'Gulab Jamun', 'price': 6.99, 'category': 'dessert',
         'image': 'assets/images/dessert.png', 'restaurant': 'Sweet Tooth Bakery',
         'rating': 4.8, 'badge': '', 'description': 'Deep-fried milk dumplings soaked in rose-scented sugar syrup'},
    ]
    db.menu_items.insert_many(items)
    print(f"  ✅ Seeded {len(items)} menu items")


def seed_restaurants():
    """Seed all restaurants."""
    db.restaurants.drop()
    restaurants = [
        {'name': 'Pizza Paradise', 'category': 'pizza', 'rating': 4.8,
         'delivery_time': '25-35', 'image': 'assets/images/pizza.png', 'price_range': '$$',
         'description': 'Authentic Italian pizzas made with love and fresh ingredients'},
        {'name': 'Burger Palace', 'category': 'burger', 'rating': 4.7,
         'delivery_time': '20-30', 'image': 'assets/images/burger.png', 'price_range': '$$',
         'description': 'Gourmet burgers with premium Angus beef and house-made sauces'},
        {'name': 'Tokyo Bites', 'category': 'sushi', 'rating': 4.9,
         'delivery_time': '30-40', 'image': 'assets/images/sushi.png', 'price_range': '$$$',
         'description': 'Premium Japanese sushi and sashimi crafted by master chefs'},
        {'name': 'Spice Garden', 'category': 'indian', 'rating': 4.8,
         'delivery_time': '25-35', 'image': 'assets/images/curry.png', 'price_range': '$$',
         'description': 'Traditional North Indian cuisine with rich, aromatic flavors'},
        {'name': 'Tandoori Nights', 'category': 'indian', 'rating': 4.6,
         'delivery_time': '30-40', 'image': 'assets/images/curry.png', 'price_range': '$$',
         'description': 'Authentic tandoor-cooked dishes and kebabs'},
        {'name': 'El Fuego Cantina', 'category': 'mexican', 'rating': 4.7,
         'delivery_time': '20-30', 'image': 'assets/images/tacos.png', 'price_range': '$$',
         'description': 'Authentic Mexican street food — tacos, burritos, and more'},
        {'name': 'Bella Cucina', 'category': 'pasta', 'rating': 4.8,
         'delivery_time': '25-35', 'image': 'assets/images/pasta.png', 'price_range': '$$$',
         'description': 'Fine Italian pasta prepared with imported ingredients'},
        {'name': 'Green Bowl Co.', 'category': 'salad', 'rating': 4.6,
         'delivery_time': '15-25', 'image': 'assets/images/salad.png', 'price_range': '$$',
         'description': 'Fresh, healthy bowls and salads made daily'},
        {'name': 'Golden Dragon', 'category': 'chinese', 'rating': 4.7,
         'delivery_time': '20-30', 'image': 'assets/images/chinese.png', 'price_range': '$$',
         'description': 'Traditional Cantonese and Sichuan dishes'},
        {'name': 'Wok This Way', 'category': 'chinese', 'rating': 4.5,
         'delivery_time': '15-25', 'image': 'assets/images/chinese.png', 'price_range': '$',
         'description': 'Quick and delicious wok-fired Chinese favorites'},
        {'name': 'Sweet Tooth Bakery', 'category': 'dessert', 'rating': 4.9,
         'delivery_time': '20-35', 'image': 'assets/images/dessert.png', 'price_range': '$$',
         'description': 'Artisan cakes, pastries, and decadent desserts'},
    ]
    db.restaurants.insert_many(restaurants)
    print(f"  ✅ Seeded {len(restaurants)} restaurants")


def seed_offers():
    """Seed all offers and promo codes."""
    db.offers.drop()
    offers = [
        {'code': 'WELCOME40', 'title': 'First Order Special', 'description': 'Get 40% off on your very first order. Valid on all restaurants and cuisines!',
         'discount_type': 'percent', 'discount_value': 40, 'icon': '🍕', 'color': 'orange',
         'valid_till': 'Mar 31', 'tag': 'Popular'},
        {'code': 'FREEDEL', 'title': 'Free Delivery All Week', 'description': 'No delivery fee on orders above $15. Save your money for more food!',
         'discount_type': 'delivery', 'discount_value': 4.99, 'icon': '🚚', 'color': 'teal',
         'valid_till': 'No expiry', 'tag': ''},
        {'code': 'BOGO2026', 'title': 'Buy 1 Get 1 Free', 'description': 'Order any burger or pizza, get the second one absolutely free. Weekends only!',
         'discount_type': 'percent', 'discount_value': 50, 'icon': '🍔', 'color': 'purple',
         'valid_till': 'Weekends Only', 'tag': 'Hot'},
        {'code': 'NIGHT30', 'title': 'Late Night Cravings', 'description': '30% discount on all orders placed between 10 PM and 2 AM. Night owls rejoice!',
         'discount_type': 'percent', 'discount_value': 30, 'icon': '🌙', 'color': 'pink',
         'valid_till': '10PM – 2AM', 'tag': ''},
        {'code': 'FAMILY10', 'title': 'Family Feast', 'description': 'Flat $10 off on family-sized orders above $40. Feed the whole gang for less!',
         'discount_type': 'flat', 'discount_value': 10, 'icon': '👨‍👩‍👧‍👦', 'color': 'gold',
         'valid_till': 'Apr 30', 'tag': ''},
        {'code': 'HEALTHY25', 'title': 'Healthy Eats Week', 'description': '25% off on all salads, smoothie bowls, and healthy menu items. Eat clean, save green!',
         'discount_type': 'percent', 'discount_value': 25, 'icon': '🥗', 'color': 'blue',
         'valid_till': 'This week only', 'tag': 'New'},
        {'code': 'BREKKY99', 'title': 'Breakfast Combo', 'description': 'Any breakfast item + coffee for just ₹99. Available 7 AM – 11 AM daily.',
         'discount_type': 'flat', 'discount_value': 5, 'icon': '☕', 'color': 'orange',
         'valid_till': '7AM – 11AM', 'tag': ''},
        {'code': 'ONLINE15', 'title': 'Pay Online & Save', 'description': 'Extra 15% off (up to $8) when you pay via UPI, cards, or wallet.',
         'discount_type': 'percent', 'discount_value': 15, 'icon': '💳', 'color': 'teal',
         'valid_till': 'All payment modes', 'tag': ''},
        {'code': 'BDAY2026', 'title': 'Birthday Surprise', 'description': "It's your birthday? Get a free chocolate lava cake with any order over $20!",
         'discount_type': 'flat', 'discount_value': 8.99, 'icon': '🎂', 'color': 'purple',
         'valid_till': 'Your B-day month', 'tag': ''},
        {'code': 'FIRST50', 'title': '50% Off First Order', 'description': 'New to Flavour Fleet? Enjoy a massive 50% discount on your first order (up to $25).',
         'discount_type': 'percent', 'discount_value': 50, 'icon': '🔥', 'color': 'orange',
         'valid_till': 'First order only', 'tag': 'Mega Deal'},
        {'code': 'WELCOME10', 'title': 'Welcome 10% Off', 'description': '10% off your first order. No minimum order required.',
         'discount_type': 'percent', 'discount_value': 10, 'icon': '👋', 'color': 'teal',
         'valid_till': 'No expiry', 'tag': ''},
        {'code': 'SAVE5', 'title': '$5 Off Any Order', 'description': 'Flat $5 off on any order. No minimum required.',
         'discount_type': 'flat', 'discount_value': 5, 'icon': '💰', 'color': 'gold',
         'valid_till': 'No expiry', 'tag': ''},
        {'code': 'LUNCH99', 'title': 'Lunch Combo Deal', 'description': 'Any main + drink + dessert at just ₹99. 11AM–3PM only.',
         'discount_type': 'flat', 'discount_value': 7, 'icon': '🍱', 'color': 'orange',
         'valid_till': '11AM – 3PM', 'tag': ''},
    ]
    db.offers.insert_many(offers)
    print(f"  ✅ Seeded {len(offers)} offers/promo codes")


if __name__ == '__main__':
    print("\n🌱 Seeding Flavour Fleet Database...")
    seed_menu_items()
    seed_restaurants()
    seed_offers()
    print("\n✅ Database seeded successfully!\n")
