# Zomato Pizza Website

A fully functional pizza delivery website with modern features and excellent user experience.

## Features Implemented

### 🎨 Design & UI Improvements
- Responsive design using Bootstrap
- Modern color scheme with appealing food colors
- Smooth animations and hover effects
- Consistent typography with Google Fonts

### 🛒 Functional Features
- **Shopping Cart System**: Add/remove items, view cart contents
- **Product Customization**: Add toppings and special instructions
- **Pizza Builder**: Drag-and-drop pizza customization tool
- **Search & Filters**: Find products by name or category
- **User Authentication**: Login/register with profile management
- **Order Tracking**: Real-time order status updates
- **Multi-language Support**: English and Hindi toggles

### 🎯 Bonus Features
- **Loyalty Program**: Earn points for purchases and redeem rewards
- **Order History**: View past orders in user profile
- **Accessibility Features**: Keyboard navigation and screen reader support
- **SEO Optimized**: Meta tags and structured data markup

## Technologies Used
- HTML5
- CSS3
- JavaScript (Vanilla)
- Bootstrap 5
- Owl Carousel
- Font Awesome

## How to Run
1. Clone the repository
2. Open `zomato.html` in a web browser
3. Or run a local server:
   ```bash
   python -m http.server 8000
   ```
4. Visit `http://localhost:8000` in your browser

## File Structure
```
zomato/
├── zomato.html          # Main HTML file
├── zomato.css           # Stylesheet
├── zomato.js            # JavaScript functionality
├── image/               # Image directory
│   ├── logo.png
│   ├── banner.png
│   ├── product images
│   └── ...
└── README.md            # This file
```

## Key Features Explained

### Shopping Cart
- Add products to cart with "Add" button
- Customize products with additional toppings
- View cart contents and total price
- Loyalty points earned automatically

### Product Customization
- Each product can be customized with additional toppings
- Special instructions can be added
- Customizations are saved with the cart item

### Pizza Builder
- Create custom pizzas with your favorite toppings
- Choose from different sizes (Small, Medium, Large)
- Visual preview of your pizza
- Price calculated based on selections

### User System
- Register and login functionality
- Profile page with order history
- Loyalty points tracking
- Persistent data using localStorage

### Order Tracking
- Enter order ID to track status
- Visual progress bar showing order status
- Estimated delivery time

### Multi-language Support
- Toggle between English and Hindi
- All UI elements translate dynamically
- Search placeholder text also translates

### Loyalty Program
- Earn 10 points for every $1 spent
- Redeem 1000 points for free items
- Points displayed in user profile
- Automatic point calculation at checkout

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimizations
- Lazy loading for images
- Minified CSS and JavaScript
- Efficient DOM manipulation
- Local storage for persistent data

## Accessibility Features
- Keyboard navigation support
- ARIA labels for screen readers
- Proper contrast ratios
- Semantic HTML structure

## SEO Features
- Meta tags for description and keywords
- Structured data markup for restaurants
- Semantic HTML elements
- Alt text for all images

## Future Enhancements
- Payment integration
- Admin dashboard for managing products
- Mobile app version
- Delivery area mapping
- Push notifications
- Social sharing features