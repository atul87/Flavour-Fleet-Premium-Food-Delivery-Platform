// Zomato Pizza Website JavaScript Functions

// Shopping Cart System
let cart = [];
let cartCount = 0;

// Product Data
const products = [
  { id: 1, name: "Bacon Cheese Burger", category: "Burger", price: 6.00, image: "image/p-1.png" },
  { id: 2, name: "Beef Burger", category: "Burger", price: 6.00, image: "image/p-2.png" },
  { id: 3, name: "Chicken Burger", category: "Burger", price: 6.00, image: "image/p-3.png" },
  { id: 4, name: "Veggie Burger", category: "Burger", price: 6.00, image: "image/p-4.png" },
  { id: 5, name: "Double Cheese Burger", category: "Burger", price: 6.00, image: "image/p-5.png" },
  { id: 6, name: "Spicy Burger", category: "Burger", price: 6.00, image: "image/p-6.png" },
  { id: 7, name: "Mushroom Burger", category: "Burger", price: 6.00, image: "image/p-7.png" },
  { id: 8, name: "BBQ Burger", category: "Burger", price: 6.00, image: "image/p-8.png" }
];

// Custom Pizza Options
const pizzaSizes = [
  { name: "Small", price: 8.00 },
  { name: "Medium", price: 12.00 },
  { name: "Large", price: 16.00 }
];

const pizzaToppings = [
  { name: "Pepperoni", price: 1.50 },
  { name: "Mushrooms", price: 1.00 },
  { name: "Extra Cheese", price: 2.00 },
  { name: "Olives", price: 1.25 },
  { name: "Onions", price: 0.75 },
  { name: "Bell Peppers", price: 0.75 },
  { name: "Ham", price: 1.75 },
  { name: "Pineapple", price: 1.00 }
];

// User Data
let users = JSON.parse(localStorage.getItem('users')) || [];
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;
let userOrders = JSON.parse(localStorage.getItem('userOrders')) || {};

// Initialize the website
document.addEventListener('DOMContentLoaded', function() {
  initializeWebsite();
  setupEventListeners();
});

// Initialize website components
function initializeWebsite() {
  updateCartCount();
  loadCartFromLocalStorage();
  loadProducts();
  setupLanguageToggle();
  setupAccessibilityFeatures();
  
  // Load user data if exists
  if (currentUser) {
    updateUIForLoggedInUser();
  }
}

// Set up event listeners
function setupEventListeners() {
  // Cart buttons
  document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function() {
      const productId = parseInt(this.dataset.productId);
      addToCart(productId);
    });
  });
  
  // Search functionality
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', filterProducts);
  }
  
  // Category filters
  document.querySelectorAll('.category-filter').forEach(filter => {
    filter.addEventListener('click', function() {
      const category = this.dataset.category;
      filterByCategory(category);
      
      // Update active state
      document.querySelectorAll('.category-filter').forEach(btn => {
        btn.classList.remove('active');
      });
      this.classList.add('active');
    });
  });
  
  // Language toggle
  const languageToggle = document.getElementById('language-toggle');
  if (languageToggle) {
    languageToggle.addEventListener('change', toggleLanguage);
  }
  
  // Pizza builder events
  setupPizzaBuilderEvents();
  
  // Customization options for products
  setupProductCustomization();
}

// Shopping Cart Functions
function addToCart(productId) {
  const product = products.find(p => p.id === productId);
  if (product) {
    cart.push({ ...product, customizations: [] });
    cartCount++;
    updateCartCount();
    saveCartToLocalStorage();
    showNotification(`${product.name} added to cart!`);
  }
}

function addToCartWithCustomizations(productId, customizations) {
  const product = products.find(p => p.id === productId);
  if (product) {
    cart.push({ ...product, customizations: customizations });
    cartCount++;
    updateCartCount();
    saveCartToLocalStorage();
    showNotification(`${product.name} with customizations added to cart!`);
  }
}

function updateCartCount() {
  const cartCountElement = document.getElementById('cart-count');
  if (cartCountElement) {
    cartCountElement.textContent = cartCount;
  }
}

function showCart() {
  // This would show a modal with cart contents
  if (cart.length === 0) {
    showNotification("Your cart is empty!");
    return;
  }
  
  let cartContent = "Items in your cart:\n\n";
  let total = 0;
  
  cart.forEach((item, index) => {
    cartContent += `${index + 1}. ${item.name} - $${item.price.toFixed(2)}\n`;
    
    // Add customizations if any
    if (item.customizations && item.customizations.length > 0) {
      cartContent += "   Customizations: ";
      item.customizations.forEach((custom, i) => {
        cartContent += `${custom.name} (+$${custom.price.toFixed(2)})`;
        if (i < item.customizations.length - 1) cartContent += ", ";
      });
      cartContent += "\n";
    }
    
    let itemTotal = item.price;
    if (item.customizations) {
      item.customizations.forEach(custom => {
        itemTotal += custom.price;
      });
    }
    
    cartContent += `   Item Total: $${itemTotal.toFixed(2)}\n\n`;
    total += itemTotal;
  });
  
  // Add loyalty points information
  if (currentUser) {
    const loyaltyInfo = checkLoyaltyRewards(currentUser.id);
    if (loyaltyInfo) {
      cartContent += `Loyalty Points: ${loyaltyInfo.points}\n`;
      cartContent += `Points earned with this order: ${Math.floor(total * loyaltyProgram.pointsPerDollar)}\n`;
      if (loyaltyInfo.rewardsAvailable > 0) {
        cartContent += `${loyaltyInfo.rewardsAvailable} free items available for redemption!\n`;
      }
    }
  }
  
  cartContent += `Overall Total: $${total.toFixed(2)}\n\n`;
  cartContent += "Press OK to proceed to checkout";
  
  if (confirm(cartContent)) {
    checkoutCart(total);
  }
}

function checkoutCart(total) {
  // Simulate checkout process
  showNotification("Processing your order...");
  
  // Simulate delay
  setTimeout(() => {
    // Add loyalty points for this order
    if (currentUser) {
      addLoyaltyPoints(currentUser.id, total);
      
      // Save order to user's history
      if (!userOrders[currentUser.id]) {
        userOrders[currentUser.id] = [];
      }
      
      userOrders[currentUser.id].push({
        id: Math.floor(Math.random() * 100000),
        date: new Date().toISOString(),
        total: total,
        status: "Order Placed"
      });
      
      localStorage.setItem('userOrders', JSON.stringify(userOrders));
    }
    
    // Clear cart
    cart = [];
    cartCount = 0;
    updateCartCount();
    saveCartToLocalStorage();
    
    showNotification("Order placed successfully! Thank you for your purchase.");
  }, 2000);
}

function saveCartToLocalStorage() {
  localStorage.setItem('cart', JSON.stringify(cart));
  localStorage.setItem('cartCount', cartCount);
}

function loadCartFromLocalStorage() {
  const savedCart = localStorage.getItem('cart');
  const savedCartCount = localStorage.getItem('cartCount');
  
  if (savedCart) {
    cart = JSON.parse(savedCart);
  }
  
  if (savedCartCount) {
    cartCount = parseInt(savedCartCount);
  }
}

// Product Display Functions
function loadProducts() {
  // In a real application, this would load products from a database
  console.log("Products loaded:", products);
}

function filterProducts() {
  const searchTerm = document.getElementById('search-input').value.toLowerCase();
  
  // Get all product elements
  const productElements = document.querySelectorAll('.famous-product');
  
  productElements.forEach((productElement, index) => {
    const productName = productElement.querySelector('h3').textContent.toLowerCase();
    const productCategory = products[index] ? products[index].category.toLowerCase() : "";
    
    // Check if product matches search term
    if (searchTerm === '' || productName.includes(searchTerm) || productCategory.includes(searchTerm)) {
      productElement.style.display = 'block';
    } else {
      productElement.style.display = 'none';
    }
  });
  
  if (searchTerm) {
    showNotification(`Showing results for: ${searchTerm}`);
  }
}

function filterByCategory(category) {
  // Get all product elements
  const productElements = document.querySelectorAll('.famous-product');
  
  if (category === 'all') {
    // Show all products
    productElements.forEach(productElement => {
      productElement.style.display = 'block';
    });
    showNotification("Showing all products");
  } else {
    // Filter by category
    productElements.forEach((productElement, index) => {
      const productCategory = products[index] ? products[index].category.toLowerCase() : "";
      
      // Check if product matches category
      if (productCategory === category.toLowerCase()) {
        productElement.style.display = 'block';
      } else {
        productElement.style.display = 'none';
      }
    });
    showNotification(`Showing ${category} products`);
  }
}

// Product Customization Functions
function setupProductCustomization() {
  // Add customization buttons to products
  document.querySelectorAll('.famous-product').forEach((productElement, index) => {
    const productId = index + 1;
    const customizeButton = document.createElement('button');
    customizeButton.className = 'btn btn-outline-danger mt-2';
    customizeButton.textContent = 'Customize';
    customizeButton.onclick = () => showProductCustomization(productId);
    
    const priceDiv = productElement.querySelector('.price');
    if (priceDiv) {
      // Check if button already exists to avoid duplicates
      if (!priceDiv.querySelector('.btn-outline-danger')) {
        priceDiv.appendChild(customizeButton);
      }
    }
  });
}

function showProductCustomization(productId) {
  const product = products.find(p => p.id === productId);
  if (!product) return;
  
  // Create customization modal
  const modalHtml = `
    <div class="modal fade" id="customizationModal" tabindex="-1" aria-labelledby="customizationModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="customizationModalLabel">Customize ${product.name}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="container-fluid">
              <div class="row">
                <div class="col-12">
                  <h6>Select Add-ons:</h6>
                  <div id="addons-list">
                    <!-- Addons will be populated here -->
                  </div>
                </div>
              </div>
              <div class="row mt-3">
                <div class="col-12">
                  <h6>Special Instructions:</h6>
                  <textarea id="special-instructions" class="form-control" rows="3" placeholder="Any special requests?"></textarea>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" onclick="applyCustomizations(${productId})">Add to Cart</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to body if it doesn't exist
  if (!document.getElementById('customizationModal')) {
    document.body.insertAdjacentHTML('beforeend', modalHtml);
  }
  
  // Populate addons list
  const addonsList = document.getElementById('addons-list');
  if (addonsList) {
    addonsList.innerHTML = '';
    pizzaToppings.forEach((topping, index) => {
      const addonDiv = document.createElement('div');
      addonDiv.className = 'form-check';
      addonDiv.innerHTML = `
        <input class="form-check-input" type="checkbox" id="addon-${index}" data-name="${topping.name}" data-price="${topping.price}">
        <label class="form-check-label" for="addon-${index}">
          ${topping.name} (+$${topping.price.toFixed(2)})
        </label>
      `;
      addonsList.appendChild(addonDiv);
    });
  }
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('customizationModal'));
  modal.show();
}

function applyCustomizations(productId) {
  const selectedAddons = [];
  document.querySelectorAll('#addons-list input:checked').forEach(checkbox => {
    selectedAddons.push({
      name: checkbox.dataset.name,
      price: parseFloat(checkbox.dataset.price)
    });
  });
  
  const specialInstructions = document.getElementById('special-instructions').value;
  
  // Add to cart with customizations
  const customizations = [...selectedAddons];
  if (specialInstructions) {
    customizations.push({
      name: "Special Instructions",
      price: 0,
      details: specialInstructions
    });
  }
  
  addToCartWithCustomizations(productId, customizations);
  
  // Close modal
  const modal = bootstrap.Modal.getInstance(document.getElementById('customizationModal'));
  if (modal) {
    modal.hide();
  }
  
  // Remove modal from DOM to avoid duplicates
  setTimeout(() => {
    const modalElement = document.getElementById('customizationModal');
    if (modalElement) {
      modalElement.remove();
    }
  }, 500);
}

// Pizza Builder Functions
function setupPizzaBuilderEvents() {
  // Size selection
  document.querySelectorAll('input[name="size"]').forEach(radio => {
    radio.addEventListener('change', updatePizzaPreview);
  });
  
  // Toppings selection
  document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', updatePizzaPreview);
  });
}

function updatePizzaPreview() {
  // Get selected size
  const size = document.querySelector('input[name="size"]:checked').value;
  
  // Get selected toppings
  const toppings = [];
  document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
    toppings.push(checkbox.value);
  });
  
  // Update description
  const descriptionElement = document.getElementById('pizza-description');
  if (descriptionElement) {
    const toppingsText = toppings.length > 0 ? `with ${toppings.join(', ')}` : 'with no toppings';
    descriptionElement.textContent = `${size.charAt(0).toUpperCase() + size.slice(1)} pizza ${toppingsText}`;
  }
  
  // Update price
  let price = 8.00; // Base price for small
  if (size === 'medium') price = 12.00;
  if (size === 'large') price = 16.00;
  
  // Add topping prices
  toppings.forEach(topping => {
    if (topping === 'pepperoni') price += 1.50;
    if (topping === 'mushrooms') price += 1.00;
    if (topping === 'cheese') price += 2.00;
    if (topping === 'olives') price += 1.25;
    if (topping === 'onions') price += 0.75;
    if (topping === 'bellpeppers') price += 0.75;
    if (topping === 'ham') price += 1.75;
    if (topping === 'pineapple') price += 1.00;
  });
  
  const priceElement = document.getElementById('pizza-price');
  if (priceElement) {
    priceElement.textContent = `$${price.toFixed(2)}`;
  }
}

function addToCartCustomPizza() {
  // Add custom pizza to cart
  const size = document.querySelector('input[name="size"]:checked').value;
  const pizzaName = `${size.charAt(0).toUpperCase() + size.slice(1)} Custom Pizza`;
  const priceElement = document.getElementById('pizza-price');
  const price = priceElement ? parseFloat(priceElement.textContent.replace('$', '')) : 10.00;
  
  // Get selected toppings
  const toppings = [];
  document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
    toppings.push({
      name: checkbox.value,
      price: parseFloat(checkbox.dataset.price || 
        (checkbox.value === 'pepperoni' ? 1.50 :
         checkbox.value === 'mushrooms' ? 1.00 :
         checkbox.value === 'cheese' ? 2.00 :
         checkbox.value === 'olives' ? 1.25 :
         checkbox.value === 'onions' ? 0.75 :
         checkbox.value === 'bellpeppers' ? 0.75 :
         checkbox.value === 'ham' ? 1.75 :
         checkbox.value === 'pineapple' ? 1.00 : 0)
      )
    });
  });
  
  const customPizza = {
    id: Date.now(), // Unique ID
    name: pizzaName,
    category: "Custom Pizza",
    price: price,
    image: "image/pizza-preview.png",
    customizations: toppings
  };
  
  cart.push(customPizza);
  cartCount++;
  updateCartCount();
  saveCartToLocalStorage();
  showNotification(`${pizzaName} added to cart!`);
  
  // Close modal
  const modal = bootstrap.Modal.getInstance(document.getElementById('pizzaBuilderModal'));
  if (modal) {
    modal.hide();
  }
}

// User Authentication (Simplified)
function registerUser() {
  const name = document.getElementById('register-name').value;
  const email = document.getElementById('register-email').value;
  const password = document.getElementById('register-password').value;
  
  if (name && email && password) {
    const user = registerUserInternal(name, email, password);
    if (user) {
      // Clear form fields
      document.getElementById('register-name').value = '';
      document.getElementById('register-email').value = '';
      document.getElementById('register-password').value = '';
      
      // Switch to login tab
      const loginTab = document.getElementById('login-tab');
      const registerTab = document.getElementById('register-tab');
      if (loginTab && registerTab) {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        
        const loginPane = document.getElementById('login');
        const registerPane = document.getElementById('register');
        if (loginPane && registerPane) {
          loginPane.classList.add('show', 'active');
          registerPane.classList.remove('show', 'active');
        }
      }
    }
  } else {
    showNotification("Please fill in all fields");
  }
}

function registerUserInternal(name, email, password) {
  // Check if user already exists
  const existingUser = users.find(u => u.email === email);
  if (existingUser) {
    showNotification("User with this email already exists!");
    return null;
  }
  
  const user = { 
    id: Date.now(), 
    name, 
    email, 
    password, // In a real app, this should be hashed
    joinDate: new Date().toISOString(),
    loyaltyPoints: 0
  };
  
  users.push(user);
  localStorage.setItem('users', JSON.stringify(users));
  showNotification("Registration successful!");
  return user;
}

function loginUser() {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  
  if (email && password) {
    const user = users.find(u => u.email === email && u.password === password);
    if (user) {
      currentUser = user;
      localStorage.setItem('currentUser', JSON.stringify(user));
      updateUIForLoggedInUser();
      showNotification(`Welcome back, ${user.name}!`);
      
      // Load user's order history
      loadUserOrders();
      
      // Close modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('authModal'));
      if (modal) {
        modal.hide();
      }
      
      // Clear form fields
      document.getElementById('login-email').value = '';
      document.getElementById('login-password').value = '';
      
      return true;
    } else {
      showNotification("Invalid credentials!");
      return false;
    }
  } else {
    showNotification("Please enter both email and password");
    return false;
  }
}

function logoutUser() {
  currentUser = null;
  localStorage.removeItem('currentUser');
  updateUIForLoggedOutUser();
  showNotification("You have been logged out.");
}

function updateUIForLoggedInUser() {
  // Update UI to show logged in state
  const userIcon = document.querySelector('.fa-user');
  if (userIcon) {
    userIcon.classList.remove('fa-user');
    userIcon.classList.add('fa-sign-out');
    userIcon.parentElement.setAttribute('onclick', 'showUserProfile()');
    userIcon.parentElement.setAttribute('aria-label', 'User Profile');
  }
  
  // Update user name in navbar if element exists
  const userNameElement = document.getElementById('user-name');
  if (userNameElement && currentUser) {
    userNameElement.textContent = currentUser.name;
  }
}

function updateUIForLoggedOutUser() {
  // Update UI to show logged out state
  const userIcon = document.querySelector('.fa-sign-out');
  if (userIcon) {
    userIcon.classList.remove('fa-sign-out');
    userIcon.classList.add('fa-user');
    userIcon.parentElement.setAttribute('onclick', 'showAuthModal()');
    userIcon.parentElement.setAttribute('aria-label', 'Login');
  }
  
  // Clear user name in navbar if element exists
  const userNameElement = document.getElementById('user-name');
  if (userNameElement) {
    userNameElement.textContent = '';
  }
}

function showAuthModal() {
  const authModal = new bootstrap.Modal(document.getElementById('authModal'));
  authModal.show();
}

function showUserProfile() {
  if (!currentUser) {
    showAuthModal();
    return;
  }
  
  // Create or update profile modal
  const modalHtml = `
    <div class="modal fade" id="profileModal" tabindex="-1" aria-labelledby="profileModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="profileModalLabel">User Profile</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="container-fluid">
              <div class="row">
                <div class="col-12">
                  <h6>Welcome, ${currentUser.name}!</h6>
                  <p>Email: ${currentUser.email}</p>
                  <p>Member since: ${new Date(currentUser.joinDate).toLocaleDateString()}</p>
                  <p>Loyalty Points: ${currentUser.loyaltyPoints || 0}</p>
                </div>
              </div>
              <div class="row mt-3">
                <div class="col-12">
                  <h6>Order History</h6>
                  <div id="order-history">
                    <!-- Order history will be populated here -->
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" onclick="logoutUser()">Logout</button>
            <button type="button" class="btn btn-danger" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to body if it doesn't exist
  if (!document.getElementById('profileModal')) {
    document.body.insertAdjacentHTML('beforeend', modalHtml);
  }
  
  // Populate order history
  populateOrderHistory();
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('profileModal'));
  modal.show();
}

function populateOrderHistory() {
  const orderHistoryElement = document.getElementById('order-history');
  if (!orderHistoryElement) return;
  
  const userOrdersList = userOrders[currentUser.id] || [];
  
  if (userOrdersList.length === 0) {
    orderHistoryElement.innerHTML = '<p>No orders yet.</p>';
    return;
  }
  
  let orderHistoryHtml = '<ul class="list-group">';
  userOrdersList.forEach(order => {
    orderHistoryHtml += `
      <li class="list-group-item">
        <div class="d-flex justify-content-between">
          <span>Order #${order.id}</span>
          <span>$${order.total.toFixed(2)}</span>
        </div>
        <div class="d-flex justify-content-between">
          <small>${new Date(order.date).toLocaleDateString()}</small>
          <small>${order.status}</small>
        </div>
      </li>
    `;
  });
  orderHistoryHtml += '</ul>';
  
  orderHistoryElement.innerHTML = orderHistoryHtml;
}

function loadUserOrders() {
  // In a real app, this would load from a database
  // For now, we'll simulate some order history for demo purposes
  if (!userOrders[currentUser.id]) {
    userOrders[currentUser.id] = [
      {
        id: Math.floor(Math.random() * 10000),
        date: new Date(Date.now() - 86400000).toISOString(), // Yesterday
        total: 24.50,
        status: "Delivered"
      },
      {
        id: Math.floor(Math.random() * 10000),
        date: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
        total: 32.75,
        status: "Delivered"
      }
    ];
    localStorage.setItem('userOrders', JSON.stringify(userOrders));
  }
}

// Loyalty Program
const loyaltyProgram = {
  pointsPerDollar: 10, // 10 points per $1 spent
  pointsForFreeItem: 1000, // 1000 points for a free item
  referralPoints: 500 // 500 points for each referral
};

function addLoyaltyPoints(userId, amount) {
  const user = users.find(u => u.id === userId);
  if (user) {
    const pointsEarned = Math.floor(amount * loyaltyProgram.pointsPerDollar);
    user.loyaltyPoints = (user.loyaltyPoints || 0) + pointsEarned;
    
    // Update in localStorage
    localStorage.setItem('users', JSON.stringify(users));
    
    // Update current user if this is the current user
    if (currentUser && currentUser.id === userId) {
      currentUser.loyaltyPoints = user.loyaltyPoints;
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
    }
    
    showNotification(`You earned ${pointsEarned} loyalty points!`);
    return pointsEarned;
  }
  return 0;
}

function redeemLoyaltyPoints(userId, pointsToRedeem) {
  const user = users.find(u => u.id === userId);
  if (user && user.loyaltyPoints >= pointsToRedeem) {
    user.loyaltyPoints -= pointsToRedeem;
    
    // Update in localStorage
    localStorage.setItem('users', JSON.stringify(users));
    
    // Update current user if this is the current user
    if (currentUser && currentUser.id === userId) {
      currentUser.loyaltyPoints = user.loyaltyPoints;
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
    }
    
    showNotification(`You've redeemed ${pointsToRedeem} points!`);
    return true;
  }
  
  showNotification("Not enough loyalty points to redeem");
  return false;
}

function checkLoyaltyRewards(userId) {
  const user = users.find(u => u.id === userId);
  if (user) {
    const points = user.loyaltyPoints || 0;
    const rewardsAvailable = Math.floor(points / loyaltyProgram.pointsForFreeItem);
    return {
      points: points,
      rewardsAvailable: rewardsAvailable,
      pointsNeededForNextReward: loyaltyProgram.pointsForFreeItem - (points % loyaltyProgram.pointsForFreeItem)
    };
  }
  return null;
}

// (Enhanced cart functions merged above — duplicates removed)

function showNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'notification';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 3000);
}

function trackOrderById() {
  const orderId = document.getElementById('order-id').value;
  if (!orderId) {
    showNotification("Please enter an Order ID");
    return;
  }
  
  const trackingInfo = document.getElementById('tracking-info');
  if (trackingInfo) {
    trackingInfo.classList.remove('d-none');
    
    // Simulate tracking progress
    const statuses = ['Preparing', 'On the Way', 'Delivered'];
    let statusIndex = 0;
    
    const statusElement = document.getElementById('order-status');
    const progressBar = document.querySelector('.progress-bar');
    
    if (statusElement && progressBar) {
      statusElement.textContent = statuses[statusIndex];
      progressBar.style.width = '33%';
      progressBar.textContent = '33%';
      
      const interval = setInterval(() => {
        statusIndex++;
        if (statusIndex >= statuses.length) {
          clearInterval(interval);
          return;
        }
        
        statusElement.textContent = statuses[statusIndex];
        const progress = ((statusIndex + 1) / statuses.length) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${Math.round(progress)}%`;
        
      }, 2000);
    }
  }
}

function setupAccessibilityFeatures() {
  document.querySelectorAll('a, button, input').forEach(el => {
    if (!el.getAttribute('aria-label') && !el.textContent.trim()) {
       if (el.tagName === 'A' && el.querySelector('i')) {
           let iconClass = el.querySelector('i').className;
           el.setAttribute('aria-label', iconClass.replace('fa fa-', ''));
       }
    }
  });
}

// Export functions for use in other scripts
window.zomato = {
  cart,
  products,
  addToCart,
  showCart,
  trackOrder,
  registerUser,
  loginUser,
  logoutUser,
  showAuthModal,
  showProductCustomization,
  applyCustomizations,
  showOrderTracker,
  trackOrderById,
  addLoyaltyPoints,
  redeemLoyaltyPoints,
  checkLoyaltyRewards
};

// Additional utility functions
window.showOrderTracker = function() {
  const orderTrackerModal = new bootstrap.Modal(document.getElementById('orderTrackerModal'));
  orderTrackerModal.show();
};

window.showPizzaBuilder = function() {
  const pizzaBuilderModal = new bootstrap.Modal(document.getElementById('pizzaBuilderModal'));
  pizzaBuilderModal.show();
};

window.trackOrder = function() {
  trackOrderById();
};

// Language translations
const translations = {
  en: {
    bestChoice: "Best Choice",
    italianPizza: "ITALIAN PIZZA",
    orderNow: "Order Now",
    fullMenu: "Full Menu",
    buildYourOwn: "Build Your Own Pizza",
    save: "SAVE",
    hamburgerCombo: "Hamburger's Combo",
    burgerCombo: "Burg's Combo",
    pizzaCombo: "Pizza's Combo",
    bestRestaurant: "We Make The Best Restaurant!",
    whyTaste: "Why Taste Our Best Pizza Now?",
    burger: "Burger",
    shakes: "Shakes",
    pasta: "Pasta",
    pizza: "Pizza",
    topSell: "Our Top Sell",
    checkoutBurgers: "Checkout Our Top Sell Burger",
    beef: "BEEF",
    baconCheese: "Bacon Cheese Burger",
    addToCart: "Add",
    fastestDelivery: "Fastest Delivery",
    onTheWay: "Your Favorite Pizza, <br> on the Way!",
    delivery30: "Delivery in 30 minutes.",
    realTime: "Real-time tracking",
    satisfaction: "100% satisfaction",
    trackOrder: "Track Your Order",
    testimonials: "Our Testimonials",
    whatClients: "What Our Client Say's",
    moments: "A Moments Of Delivered <br> On Right Time & Place",
    ourCompany: "Our Company",
    openingHours: "Opening Hours",
    contactUs: "Contact Us",
    home: "Home",
    menu: "Menu",
    services: "Our Services",
    testimonial: "Testimonial",
    searchPlaceholder: "Search for pizza, burgers, etc..."
  },
  hi: {
    bestChoice: "सर्वश्रेष्ठ विकल्प",
    italianPizza: "इटैलियन पिज्जा",
    orderNow: "आज ही ऑर्डर करें",
    fullMenu: "पूरा मेनू",
    buildYourOwn: "अपनी पिज्जा बनाएं",
    save: "बचाएं",
    hamburgerCombo: "हैमबर्गर कॉम्बो",
    burgerCombo: "बर्गर कॉम्बो",
    pizzaCombo: "पिज्जा कॉम्बो",
    bestRestaurant: "हम सबसे अच्छा रेस्तरां बनाते हैं!",
    whyTaste: "अब हमारी सबसे अच्छी पिज्जा क्यों टेस्ट करें?",
    burger: "बर्गर",
    shakes: "शेक",
    pasta: "पास्ता",
    pizza: "पिज्जा",
    topSell: "हमारी शीर्ष बिक्री",
    checkoutBurgers: "हमारे शीर्ष बिकने वाले बर्गर की जाँच करें",
    beef: "बीफ",
    baconCheese: "बेकन चीज़ बर्गर",
    addToCart: "जोड़ें",
    fastestDelivery: "सबसे तेज़ डिलीवरी",
    onTheWay: "आपकी पसंदीदा पिज्जा, <br> रास्ते में है!",
    delivery30: "30 मिनट में डिलीवरी।",
    realTime: "वास्तविक समय ट्रैकिंग",
    satisfaction: "100% संतुष्टि",
    trackOrder: "अपने ऑर्डर को ट्रैक करें",
    testimonials: "हमारी प्रशंसापत्र",
    whatClients: "हमारे ग्राहक क्या कहते हैं",
    moments: "सही समय और स्थान पर <br> वितरित के क्षण",
    ourCompany: "हमारी कंपनी",
    openingHours: "खुलने का समय",
    contactUs: "संपर्क करें",
    home: "होम",
    menu: "मेनू",
    services: "हमारी सेवाएँ",
    testimonial: "प्रशंसापत्र",
    searchPlaceholder: "पिज्जा, बर्गर आदि के लिए खोजें..."
  }
};

// Language Functions
function setupLanguageToggle() {
  // Set up language toggle functionality
  const languageToggle = document.getElementById('language-toggle');
  if (languageToggle) {
    languageToggle.addEventListener('change', toggleLanguage);
  }
}

function toggleLanguage() {
  const toggle = document.getElementById('language-toggle');
  const currentLang = toggle && toggle.checked ? 'hi' : 'en';
  
  // Update all translatable elements
  updateTranslations(currentLang);
  
  // Update search placeholder
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.placeholder = translations[currentLang].searchPlaceholder;
  }
  
  // Update category filter buttons
  const categoryButtons = document.querySelectorAll('.category-filter');
  if (currentLang === 'hi') {
    if (categoryButtons.length > 0) categoryButtons[0].textContent = 'सभी';
    if (categoryButtons.length > 1) categoryButtons[1].textContent = 'पिज्जा';
    if (categoryButtons.length > 2) categoryButtons[2].textContent = 'बर्गर';
    if (categoryButtons.length > 3) categoryButtons[3].textContent = 'पास्ता';
    if (categoryButtons.length > 4) categoryButtons[4].textContent = 'शेक';
  } else {
    if (categoryButtons.length > 0) categoryButtons[0].textContent = 'All';
    if (categoryButtons.length > 1) categoryButtons[1].textContent = 'Pizza';
    if (categoryButtons.length > 2) categoryButtons[2].textContent = 'Burgers';
    if (categoryButtons.length > 3) categoryButtons[3].textContent = 'Pasta';
    if (categoryButtons.length > 4) categoryButtons[4].textContent = 'Shakes';
  }
  
  // Show notification
  const message = currentLang === 'hi' ? "भाषा हिंदी में बदल गई" : "Language changed to English";
  showNotification(message);
}

function updateTranslations(lang) {
  const t = translations[lang];
  
  // Update banner text
  const bestChoice = document.querySelector('.banner-detail h5');
  if (bestChoice) bestChoice.innerHTML = t.bestChoice;
  
  const italianPizza = document.querySelector('.banner-detail h1');
  if (italianPizza) italianPizza.innerHTML = t.italianPizza;
  
  // Update banner paragraph
  const bannerParagraph = document.querySelector('.banner-detail p');
  if (bannerParagraph) {
    bannerParagraph.textContent = lang === 'hi' ? 
      "सही पिज्जा के लिए लालायित? हमारे हाथ से बने पिज्जा ताज़ा सामग्री और प्रामाणिक इटैलियन तकनीकों के साथ बनाए जाते हैं।" :
      "Craving the perfect slice? Our handcrafted pizzas are made with fresh ingredients and authentic Italian techniques.";
  }
  
  // Update button text
  const orderNowBtn = document.querySelector('.button-1');
  if (orderNowBtn) orderNowBtn.textContent = t.orderNow;
  
  const fullMenuBtn = document.querySelector('.button-2');
  if (fullMenuBtn) fullMenuBtn.textContent = t.fullMenu;
  
  const buildPizzaBtn = document.querySelector('.btn.btn-outline-light');
  if (buildPizzaBtn) buildPizzaBtn.textContent = t.buildYourOwn;
  
  // Update banner section text
  const bannerHeaders = document.querySelectorAll('.top-banner h2');
  bannerHeaders.forEach(h2 => {
    if (h2.textContent.includes("SAVE") || h2.textContent.includes("बचाएं")) {
      h2.innerHTML = t.save + " 30%";
    }
  });
  
  // Update specific banner headings and paragraphs
  const topBanners = document.querySelectorAll('.top-banner');
  if (topBanners.length >= 5) {
    // First banner
    const h3_1 = topBanners[0].querySelector('h3');
    const p_1 = topBanners[0].querySelector('p');
    if (h3_1) h3_1.innerHTML = t.hamburgerCombo;
    if (p_1) p_1.textContent = lang === 'hi' ? 
      "एक विशेष मूल्य पर फ्राइस और पेय के साथ स्वादिष्ट हैमबर्गर!" :
      "Delicious hamburger with fries and drink combo at a special price!";
    
    // Second banner
    const h3_2 = topBanners[1].querySelector('h3');
    const p_2 = topBanners[1].querySelector('p');
    if (h3_2) h3_2.innerHTML = t.burgerCombo;
    if (p_2) p_2.textContent = lang === 'hi' ? 
      "क्रिस्पी फ्राइस और ताज़ा पेय के साथ हमारा हस्ताक्षरित बर्गर!" :
      "Our signature burger with crispy fries and refreshing drink!";
    
    // Third banner
    const h3_3 = topBanners[2].querySelector('h3');
    const p_3 = topBanners[2].querySelector('p');
    if (h3_3) h3_3.innerHTML = t.pizzaCombo;
    if (p_3) p_3.textContent = lang === 'hi' ? 
      "पूरे परिवार के लिए गारलिक ब्रेड और 2 पेय के साथ बड़ा पिज्जा!" :
      "Large pizza with garlic bread and 2 drinks for the whole family!";
    
    // Fourth banner
    const h3_4 = topBanners[3].querySelector('h3');
    const p_4 = topBanners[3].querySelector('p');
    if (h3_4) h3_4.innerHTML = t.bestRestaurant;
    if (p_4) p_4.textContent = lang === 'hi' ? 
      "हमारे शेफ केवल ताज़ा सामग्री का उपयोग करते हैं जो आपकी भूख को संतुष्ट करने के लिए मोहक व्यंजन बनाते हैं।" :
      "Our chefs use only the freshest ingredients to create mouthwatering dishes that will satisfy your cravings.";
    
    // Fifth banner
    const h3_5 = topBanners[4].querySelector('h3');
    const p_5 = topBanners[4].querySelector('p');
    if (h3_5) h3_5.innerHTML = t.whyTaste;
    if (p_5) p_5.textContent = lang === 'hi' ? 
      "प्रामाणिक इटैलियन व्यंजन, ताज़ा डॉय रोज़ बनाई जाती है, और प्रीमियम टॉपिंग के साथ सही पिज्जा का अनुभव।" :
      "Authentic Italian recipes, fresh dough made daily, and premium toppings for the perfect pizza experience.";
  }
  
  // Update category list
  const categoryLists = document.querySelectorAll('.category-list');
  categoryLists.forEach((categoryList, index) => {
    const h2 = categoryList.querySelector('h2');
    const p = categoryList.querySelector('p');
    if (h2 && p) {
      switch(index) {
        case 0:
        case 1:
        case 3:
        case 5:
        case 6:
        case 7:
          h2.textContent = t.burger;
          p.textContent = lang === 'hi' ? "19 रेस्तरां उत्पाद" : "19 Restaurants Products";
          break;
        case 2:
          h2.textContent = t.shakes;
          p.textContent = lang === 'hi' ? "9 रेस्तरां उत्पाद" : "9 Restaurants Products";
          break;
        case 4:
          h2.textContent = t.pasta;
          p.textContent = lang === 'hi' ? "44 रेस्तरां उत्पाद" : "44 Restaurants Products";
          break;
      }
    }
  });
  
  // Update product section
  const headingSections = document.querySelectorAll('.heading-section');
  if (headingSections.length >= 2) {
    const topSellHeading = headingSections[0].querySelector('h3');
    const checkoutHeading = headingSections[0].querySelector('h2');
    if (topSellHeading) topSellHeading.textContent = t.topSell;
    if (checkoutHeading) checkoutHeading.innerHTML = t.checkoutBurgers;
  }
  
  // Update product names
  const productHeaders = document.querySelectorAll('.famous-product h2');
  productHeaders.forEach(h2 => {
    h2.textContent = t.beef;
  });
  
  const productNames = document.querySelectorAll('.famous-product h3');
  productNames.forEach(h3 => {
    h3.textContent = t.baconCheese;
  });
  
  const productCalories = document.querySelectorAll('.famous-product .price p');
  productCalories.forEach(p => {
    p.textContent = lang === 'hi' ? "220ग्रा/600कैल" : "220gr/600cal";
  });
  
  // Update add to cart buttons
  const addToCartButtons = document.querySelectorAll('.add-to-cart');
  addToCartButtons.forEach(button => {
    const icon = button.querySelector('i');
    button.innerHTML = '';
    if (icon) button.appendChild(icon);
    button.insertAdjacentHTML('beforeend', ' ' + t.addToCart);
  });
  
  // Update delivery section
  const fastestDelivery = document.querySelector('.adv-right h2');
  if (fastestDelivery) fastestDelivery.textContent = t.fastestDelivery;
  
  const onTheWay = document.querySelector('.adv-right h3');
  if (onTheWay) onTheWay.innerHTML = t.onTheWay;
  
  const deliveryTexts = document.querySelectorAll('.about-div p');
  if (deliveryTexts.length > 0) deliveryTexts[0].textContent = t.delivery30;
  if (deliveryTexts.length > 1) deliveryTexts[1].textContent = t.realTime;
  if (deliveryTexts.length > 2) deliveryTexts[2].textContent = t.satisfaction;
  
  const trackOrderBtn = document.querySelector('.adv-right .btn');
  if (trackOrderBtn) trackOrderBtn.textContent = t.trackOrder;
  
  // Update delivery paragraph
  const deliveryParagraph = document.querySelector('.adv-right p');
  if (deliveryParagraph) {
    deliveryParagraph.textContent = lang === 'hi' ? 
      "हमारी सबसे तेज़ डिलीवरी सेवा का आनंद लें जिसमें वास्तविक समय ट्रैकिंग है। आपका ऑर्डर 30 मिनट या उससे कम समय में गर्म और ताज़ा पहुंचेगा!" :
      "Enjoy our fastest delivery service with real-time tracking. Your order will arrive hot and fresh in 30 minutes or less!";
  }
  
  // Update testimonials section
  if (headingSections.length >= 2) {
    const testimonialsHeading = headingSections[1].querySelector('h3');
    const whatClientsHeading = headingSections[1].querySelector('h2');
    if (testimonialsHeading) testimonialsHeading.textContent = t.testimonials;
    if (whatClientsHeading) whatClientsHeading.innerHTML = t.whatClients;
  }
  
  // Update testimonial texts
  const testimonials = document.querySelectorAll('.testimonial p');
  if (lang === 'hi') {
    if (testimonials.length > 0) testimonials[0].textContent = "सबसे अच्छा पिज्जा जो मैंने कभी टेस्ट किया है! डिलीवरी सुपर तेज़ थी और पिज्जा गर्म और ताज़ा पहुंचा। फिर से ऑर्डर करूंगा!";
    if (testimonials.length > 1) testimonials[1].textContent = "उनका कस्टम पिज्जा बिल्डर शानदार है! मैंने वास्तव में जो चाहा वह बना पाया। लॉयल्टी प्रोग्राम भी महान पुरस्कार देता है!";
    if (testimonials.length > 2) testimonials[2].textContent = "वास्तविक समय के ऑर्डर ट्रैकिंग सुविधा बहुत सहायक है। मुझे पता है कि मेरा खाना कब पहुंचेगा। महान सेवा!";
    if (testimonials.length > 3) testimonials[3].textContent = "उनकी बहुभाषी समर्थन ने ऑर्डरिंग को आसान बना दिया। पिज्जा स्वादिष्ट था और डिलीवरी तेज़ थी। अत्यधिक अनुशंसित!";
  } else {
    if (testimonials.length > 0) testimonials[0].textContent = "The best pizza I've ever tasted! The delivery was super fast and the pizza arrived hot and fresh. Will definitely order again!";
    if (testimonials.length > 1) testimonials[1].textContent = "Their custom pizza builder is amazing! I was able to create exactly what I wanted. The loyalty program gives great rewards too!";
    if (testimonials.length > 2) testimonials[2].textContent = "The real-time order tracking feature is so helpful. I love knowing exactly when my food will arrive. Great service!";
    if (testimonials.length > 3) testimonials[3].textContent = "Their multi-language support made ordering so easy. The pizza was delicious and delivery was quick. Highly recommended!";
  }
  
  // Update testimonial user names and titles
  const testimonialUsers = document.querySelectorAll('.testimonial-user h5');
  const testimonialTitles = document.querySelectorAll('.testimonial-user h6');
  if (lang === 'hi') {
    if (testimonialUsers.length > 0) testimonialUsers[0].textContent = "नैंसी बेयर्स";
    if (testimonialTitles.length > 0) testimonialTitles[0].textContent = " संस्थापक एवं सीईओ डेज़वेन";
    if (testimonialUsers.length > 1) testimonialUsers[1].textContent = "राजेश कुमार";
    if (testimonialTitles.length > 1) testimonialTitles[1].textContent = " पिज्जा प्रेमी";
    if (testimonialUsers.length > 2) testimonialUsers[2].textContent = "प्रिया शर्मा";
    if (testimonialTitles.length > 2) testimonialTitles[2].textContent = " नियमित आदेशकर्ता";
    if (testimonialUsers.length > 3) testimonialUsers[3].textContent = "अमित पटेल";
    if (testimonialTitles.length > 3) testimonialTitles[3].textContent = " नया ग्राहक";
  } else {
    if (testimonialUsers.length > 0) testimonialUsers[0].textContent = "Nancy Bayers";
    if (testimonialTitles.length > 0) testimonialTitles[0].textContent = " Founder & CEO At Dezven";
    if (testimonialUsers.length > 1) testimonialUsers[1].textContent = "Rajesh Kumar";
    if (testimonialTitles.length > 1) testimonialTitles[1].textContent = " Pizza Enthusiast";
    if (testimonialUsers.length > 2) testimonialUsers[2].textContent = "Priya Sharma";
    if (testimonialTitles.length > 2) testimonialTitles[2].textContent = " Frequent Orderer";
    if (testimonialUsers.length > 3) testimonialUsers[3].textContent = "Amit Patel";
    if (testimonialTitles.length > 3) testimonialTitles[3].textContent = " New Customer";
  }
  
  // Update footer
  const moments = document.querySelector('.footer-top h2');
  if (moments) moments.innerHTML = t.moments;
  
  const footerHeadings = document.querySelectorAll('h4');
  if (footerHeadings.length >= 3) {
    footerHeadings[0].textContent = t.ourCompany;
    footerHeadings[1].textContent = t.openingHours;
    footerHeadings[2].textContent = t.contactUs;
  }
  
  // Update footer menu items
  const footerMenuItems = document.querySelectorAll('.footer-menu li');
  if (lang === 'hi') {
    if (footerMenuItems.length > 0) footerMenuItems[0].textContent = "होम";
    if (footerMenuItems.length > 1) footerMenuItems[1].textContent = "मेनू";
    if (footerMenuItems.length > 2) footerMenuItems[2].textContent = "हमारे बारे में";
    if (footerMenuItems.length > 3) footerMenuItems[3].textContent = "रेस्तरां";
    if (footerMenuItems.length > 4) footerMenuItems[4].textContent = "त्वरित आदेश";
    if (footerMenuItems.length > 5) footerMenuItems[5].textContent = "फास्ट फूड";
    if (footerMenuItems.length > 6) footerMenuItems[6].textContent = "ब्लॉगिंग";
    if (footerMenuItems.length > 7) footerMenuItems[7].textContent = "संपर्क करें";
  } else {
    if (footerMenuItems.length > 0) footerMenuItems[0].textContent = "Home";
    if (footerMenuItems.length > 1) footerMenuItems[1].textContent = "Menu";
    if (footerMenuItems.length > 2) footerMenuItems[2].textContent = "About us";
    if (footerMenuItems.length > 3) footerMenuItems[3].textContent = "restaurant";
    if (footerMenuItems.length > 4) footerMenuItems[4].textContent = "Quick Order";
    if (footerMenuItems.length > 5) footerMenuItems[5].textContent = "Fast Food";
    if (footerMenuItems.length > 6) footerMenuItems[6].textContent = "Blogging";
    if (footerMenuItems.length > 7) footerMenuItems[7].textContent = "Contact Us";
  }
  
  // Update opening hours table
  const tableRows = document.querySelectorAll('table tr');
  if (tableRows.length >= 3) {
    const td1 = tableRows[0].querySelectorAll('td');
    const td2 = tableRows[1].querySelectorAll('td');
    const td3 = tableRows[2].querySelectorAll('td');
    
    if (td1.length >= 2) td1[1].textContent = lang === 'hi' ? "8:00 पूर्वाह्न-12:00 अपराह्न" : "8:00 am-12:00 pm";
    if (td2.length >= 2) td2[1].textContent = lang === 'hi' ? "8:00 पूर्वाह्न-12:00 अपराह्न" : "8:00 am-12:00 pm";
    if (td3.length >= 2) td3[1].textContent = lang === 'hi' ? "बंद" : "Closed";
  }
  
  // Update contact info
  const contactParagraphs = document.querySelectorAll('.contact-info p');
  if (contactParagraphs.length >= 3) {
    contactParagraphs[2].innerHTML = lang === 'hi' ? 
      `<span><i class="fa fa-envelope"></i></span> info@zomatopizza.com` :
      `<span><i class="fa fa-envelope"></i></span> info@zomatopizza.com`;
  }
  
  // Update copyright
  const copyrightText = document.querySelector('.copyright p');
  if (copyrightText) {
    copyrightText.textContent = lang === 'hi' ? 
      "@ 2023 सभी अधिकार ज़ोमैटो पिज्जा द्वारा सुरक्षित" :
      "@ 2023 All Rights Reserved By Zomato Pizza";
  }
  
  // Update copyright links
  const copyrightLinks = document.querySelectorAll('.copyright a');
  if (lang === 'hi') {
    if (copyrightLinks.length > 0) copyrightLinks[0].textContent = "सेवा";
    if (copyrightLinks.length > 1) copyrightLinks[1].textContent = "ब्लॉग";
    if (copyrightLinks.length > 2) copyrightLinks[2].textContent = "संपर्क";
    if (copyrightLinks.length > 3) copyrightLinks[3].textContent = "गोपनीयता नीति";
  } else {
    if (copyrightLinks.length > 0) copyrightLinks[0].textContent = "Service";
    if (copyrightLinks.length > 1) copyrightLinks[1].textContent = "Blog";
    if (copyrightLinks.length > 2) copyrightLinks[2].textContent = "Contact";
    if (copyrightLinks.length > 3) copyrightLinks[3].textContent = "Privacy Policy";
  }
  
  // Update navigation (only main navbar links, not modal tabs)
  const navLinks = document.querySelectorAll('nav .navbar-nav .nav-link');
  if (navLinks.length >= 6) {
    navLinks[0].textContent = t.home;
    navLinks[1].textContent = lang === 'hi' ? "श्रेणी" : "Category";
    navLinks[2].textContent = t.menu;
    navLinks[3].textContent = t.services;
    navLinks[4].textContent = t.testimonial;
    navLinks[5].textContent = t.contactUs;
  }
}
