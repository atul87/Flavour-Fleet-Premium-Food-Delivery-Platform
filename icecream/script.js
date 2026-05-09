// Product data
const products = [
    {
        id: 1,
        name: "Classic Vanilla Cone",
        price: 25,
        image: "https://kwalitywalls-cascaron-9c3e15.netlify.app/assets/img/download%20(3).jpeg",
        category: "Cones",
        description: "Rich and creamy vanilla ice cream in a crispy cone"
    },
    {
        id: 2,
        name: "Chocolate Fudge Sundae",
        price: 85,
        image: "https://kwalitywalls-cascaron-9c3e15.netlify.app/assets/img/download%20(6).jpeg",
        category: "Sundaes",
        description: "Decadent chocolate ice cream topped with fudge sauce and nuts"
    },
    {
        id: 3,
        name: "Strawberry Delight Cake",
        price: 450,
        image: "https://kwalitywalls-cascaron-9c3e15.netlify.app/assets/img/download%20(7).jpeg",
        category: "Cakes",
        description: "Fresh strawberry ice cream layered in a delicious cake"
    },
    {
        id: 4,
        name: "Mango Mania Ice Cream",
        price: 65,
        image: "https://kwalitywalls-cascaron-9c3e15.netlify.app/assets/img/images.jpeg",
        category: "Ice Creams",
        description: "Refreshing mango flavor with real fruit pieces"
    },
    {
        id: 5,
        name: "Butterscotch Ripple",
        price: 75,
        image: "https://kwalitywalls-cascaron-9c3e15.netlify.app/assets/img/344519-6.webp",
        category: "Ice Creams",
        description: "Creamy butterscotch with delicious ripple swirls"
    },
    {
        id: 6,
        name: "Rainbow Sprinkle Cone",
        price: 35,
        image: "https://kwalitywalls-cascaron-9c3e15.netlify.app/assets/img/download%20(8).jpeg",
        category: "Cones",
        description: "Vanilla ice cream with colorful sprinkles in a waffle cone"
    }
];

// Cart array to store items
let cart = [];

// Current testimonial index
let currentTestimonial = 0;

// Product detail metadata for the modal
const productDetails = {
    1: {
        ingredients: 'Milk, sugar, cream, vanilla extract, biscuit cone.',
        nutrition: 'Energy 180 kcal - Protein 3 g - Carbs 22 g.',
        reviews: [
            'Classic vanilla with a crisp cone bite.',
            'Light, creamy, and easy to finish in one go.'
        ]
    },
    2: {
        ingredients: 'Milk, cocoa, fudge sauce, roasted nuts, stabilizers.',
        nutrition: 'Energy 320 kcal - Protein 5 g - Carbs 31 g.',
        reviews: [
            'Rich chocolate flavor with a proper fudge hit.',
            'A dessert-style treat that feels premium.'
        ]
    },
    3: {
        ingredients: 'Milk, strawberry puree, sponge cake, cream, sugar.',
        nutrition: 'Energy 410 kcal - Protein 6 g - Carbs 42 g.',
        reviews: [
            'Sweet, fruity, and great for celebrations.',
            'Looks as good as it tastes.'
        ]
    },
    4: {
        ingredients: 'Milk, mango pulp, cream, fruit pieces, sugar.',
        nutrition: 'Energy 210 kcal - Protein 4 g - Carbs 26 g.',
        reviews: [
            'Bright mango flavor that feels refreshing.',
            'A solid summer pick with real fruit notes.'
        ]
    },
    5: {
        ingredients: 'Milk, butterscotch swirl, caramel notes, cream.',
        nutrition: 'Energy 230 kcal - Protein 4 g - Carbs 24 g.',
        reviews: [
            'The caramel swirl is the best part.',
            'Balanced sweetness and a smooth finish.'
        ]
    },
    6: {
        ingredients: 'Milk, sugar, cream, rainbow sprinkles, waffle cone.',
        nutrition: 'Energy 190 kcal - Protein 3 g - Carbs 23 g.',
        reviews: [
            'The sprinkles make it feel fun immediately.',
            'Simple, nostalgic, and very shareable.'
        ]
    }
};

let currentCategoryFilter = 'all';

function debounce(fn, delay = 300) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

function normalizeText(value) {
    return value ? value.toString().trim() : '';
}

function escapeHtml(value) {
    return normalizeText(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function setFieldState(element, isValid) {
    if (!element) return;
    element.classList.remove('is-invalid', 'is-valid');
    element.classList.add(isValid ? 'is-valid' : 'is-invalid');
}

function clearFieldStates(elements) {
    elements.forEach(element => {
        if (element) {
            element.classList.remove('is-invalid', 'is-valid');
        }
    });
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function getProductDetails(productId) {
    return productDetails[productId] || {
        ingredients: 'Milk, cream, sugar, and signature flavor blend.',
        nutrition: 'Energy 200 kcal - Protein 4 g - Carbs 24 g.',
        reviews: ['Creamy texture with a clean finish.', 'A dependable crowd-pleaser.']
    };
}

// DOM Elements
document.addEventListener('DOMContentLoaded', function () {
    // Hide loading screen
    setTimeout(() => {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.classList.add('fade-out');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }
    }, 1500);

    // Initialize the page
    initPage();

    // Add event listeners
    setupEventListeners();

    // Load cart from localStorage
    loadCart();

    // Animate elements when they come into view
    setupScrollAnimations();
});

// Initialize the page
function initPage() {
    // Render products
    renderProducts(products);

    // Initialize carousel
    initializeCarousel();

    // Animate stats counter
    animateStats();

    // Set active testimonial
    showTestimonial(currentTestimonial);
}

// Set up event listeners
function setupEventListeners() {
    // Login button
    const loginButton = document.getElementById('loginButton');
    if (loginButton) {
        loginButton.addEventListener('click', function () {
            const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
            loginModal.show();
        });
    }

    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        // Password visibility toggle
        document.getElementById('toggleLoginPassword')?.addEventListener('click', function () {
            const input = document.getElementById('password');
            const icon = document.getElementById('toggleLoginIcon');
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            icon.className = isHidden ? 'bi bi-eye-slash' : 'bi bi-eye';
        });

        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            let valid = true;

            // Reset states
            clearFieldStates([emailInput, passwordInput]);

            if (!isValidEmail(email)) {
                setFieldState(emailInput, false);
                valid = false;
            } else {
                setFieldState(emailInput, true);
            }

            if (password.length < 6) {
                setFieldState(passwordInput, false);
                valid = false;
            } else {
                setFieldState(passwordInput, true);
            }

            if (!valid) {
                showToast('Use a valid email and a password with at least 6 characters.', 'Login failed', 'error');
                return;
            }

            showToast('Login successful! Welcome back 🍦');
            loginForm.reset();
            clearFieldStates([emailInput, passwordInput]);
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            loginModal.hide();

            // Update UI to show user is logged in
            const loginButton = document.getElementById('loginButton');
            if (loginButton) {
                loginButton.textContent = 'My Account';
                loginButton.onclick = function () {
                    showToast('Welcome to your account!', 'My Account', 'info');
                };
            }
        });
    }

    // Signup form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        // Password visibility toggle
        document.getElementById('toggleSignupPassword')?.addEventListener('click', function () {
            const input = document.getElementById('signupPassword');
            const icon = document.getElementById('toggleSignupIcon');
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            icon.className = isHidden ? 'bi bi-eye-slash' : 'bi bi-eye';
        });

        // Password strength meter
        document.getElementById('signupPassword')?.addEventListener('input', function () {
            const val = this.value;
            const container = document.getElementById('passwordStrengthContainer');
            const bar = document.getElementById('passwordStrengthBar');
            const label = document.getElementById('passwordStrengthLabel');

            if (val.length === 0) {
                container.style.display = 'none';
                return;
            }
            container.style.display = 'block';

            let score = 0;
            if (val.length >= 6) score++;
            if (val.length >= 10) score++;
            if (/[A-Z]/.test(val)) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;

            const levels = [
                { label: 'Very Weak', color: '#dc3545', width: '15%' },
                { label: 'Weak', color: '#fd7e14', width: '30%' },
                { label: 'Fair', color: '#ffc107', width: '55%' },
                { label: 'Good', color: '#20c997', width: '80%' },
                { label: 'Strong', color: '#198754', width: '100%' },
            ];
            const level = levels[Math.min(score, 4)];
            bar.style.width = level.width;
            bar.style.backgroundColor = level.color;
            label.textContent = level.label;
            label.style.color = level.color;
        });

        signupForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const nameInput = document.getElementById('signupName');
            const emailInput = document.getElementById('signupEmail');
            const passInput = document.getElementById('signupPassword');
            const confirmInput = document.getElementById('signupConfirmPassword');
            let valid = true;

            // Reset all
            clearFieldStates([nameInput, emailInput, passInput, confirmInput]);

            if (!nameInput.value.trim()) {
                setFieldState(nameInput, false);
                valid = false;
            } else {
                setFieldState(nameInput, true);
            }

            if (!isValidEmail(emailInput.value.trim())) {
                setFieldState(emailInput, false);
                valid = false;
            } else {
                setFieldState(emailInput, true);
            }

            if (passInput.value.length < 6) {
                setFieldState(passInput, false);
                valid = false;
            } else {
                setFieldState(passInput, true);
            }

            if (confirmInput.value !== passInput.value || !confirmInput.value) {
                setFieldState(confirmInput, false);
                valid = false;
            } else {
                setFieldState(confirmInput, true);
            }

            if (!valid) {
                showToast('Check your name, email, password, and confirmation fields.', 'Signup failed', 'error');
                return;
            }

            showToast('Account created successfully! Welcome 🎉');
            signupForm.reset();
            clearFieldStates([nameInput, emailInput, passInput, confirmInput]);
            document.getElementById('passwordStrengthContainer').style.display = 'none';
            const signupModal = bootstrap.Modal.getInstance(document.getElementById('signupModal'));
            signupModal.hide();

            // Update UI to show user is logged in
            const loginButton = document.getElementById('loginButton');
            if (loginButton) {
                loginButton.textContent = 'My Account';
                loginButton.onclick = function () {
                    showToast('Welcome to your account!', 'My Account', 'info');
                };
            }
        });
    }

    // Show signup modal from login modal
    const showSignup = document.getElementById('showSignup');
    if (showSignup) {
        showSignup.addEventListener('click', function (e) {
            e.preventDefault();
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            loginModal.hide();

            setTimeout(() => {
                const signupModal = new bootstrap.Modal(document.getElementById('signupModal'));
                signupModal.show();
            }, 300);
        });
    }

    // Show login modal from signup modal
    const showLogin = document.getElementById('showLogin');
    if (showLogin) {
        showLogin.addEventListener('click', function (e) {
            e.preventDefault();
            const signupModal = bootstrap.Modal.getInstance(document.getElementById('signupModal'));
            signupModal.hide();

            setTimeout(() => {
                const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            }, 300);
        });
    }

    // Cart button
    const cartButton = document.getElementById('cartButton');
    if (cartButton) {
        cartButton.addEventListener('click', function (e) {
            e.preventDefault();
            const cartOffcanvas = new bootstrap.Offcanvas(document.getElementById('cartOffcanvas'));
            cartOffcanvas.show();
            renderCart();
        });
    }

    // Checkout button
    const checkoutButton = document.getElementById('checkoutButton');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', function () {
            if (cart.length > 0) {
                showToast('Order placed successfully! Thank you for your purchase.');
                cart = [];
                updateCartCount();
                renderCart();
                const cartOffcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('cartOffcanvas'));
                if (cartOffcanvas) cartOffcanvas.hide();
            } else {
                showToast('Your cart is empty!', 'Error', 'error');
            }
        });
    }

    // Newsletter form
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const emailInput = document.getElementById('newsletterEmail');
            const email = emailInput.value.trim();
            if (isValidEmail(email)) {
                showToast('Thanks for subscribing to our newsletter!');
                newsletterForm.reset();
            } else {
                showToast('Enter a valid email address to subscribe.', 'Subscription failed', 'error');
            }
        });
    }

    // Contact form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const name = normalizeText(document.getElementById('contactName').value);
            const email = normalizeText(document.getElementById('contactEmail').value);
            const subject = normalizeText(document.getElementById('contactSubject').value);
            const message = normalizeText(document.getElementById('contactMessage').value);

            if (name && isValidEmail(email) && subject && message) {
                const messageDiv = document.getElementById('contactFormMessage');
                if (messageDiv) messageDiv.innerHTML = '';
                showToast('Thank you for your message! We will get back to you soon.');
                contactForm.reset();
            } else {
                showToast('Please complete the contact form with a valid email.', 'Message not sent', 'error');
            }
        });
    }

    // Testimonial navigation
    const prevTestimonial = document.getElementById('prevTestimonial');
    const nextTestimonial = document.getElementById('nextTestimonial');
    const addTestimonial = document.getElementById('addTestimonial');

    if (prevTestimonial) {
        prevTestimonial.addEventListener('click', function () {
            currentTestimonial = (currentTestimonial - 1 + 3) % 3;
            showTestimonial(currentTestimonial);
        });
    }

    if (nextTestimonial) {
        nextTestimonial.addEventListener('click', function () {
            currentTestimonial = (currentTestimonial + 1) % 3;
            showTestimonial(currentTestimonial);
        });
    }

    if (addTestimonial) {
        addTestimonial.addEventListener('click', function () {
            const testimonialModal = new bootstrap.Modal(document.getElementById('testimonialModal'));
            testimonialModal.show();
        });
    }

    // Testimonial form
    const testimonialForm = document.getElementById('testimonialForm');
    if (testimonialForm) {
        testimonialForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const name = document.getElementById('testimonialName').value;
            const text = document.getElementById('testimonialText').value;
            const rating = document.getElementById('testimonialRating').value;

            if (name && text && rating) {
                showToast('Thank you for your review!');
                const testimonialModal = bootstrap.Modal.getInstance(document.getElementById('testimonialModal'));
                testimonialModal.hide();
                testimonialForm.reset();
            }
        });
    }

    // Category Filters and Debounced Search
    const filterProducts = () => {
        const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
        const filtered = products.filter(product => {
            const matchesSearch = product.name.toLowerCase().includes(searchTerm) ||
                product.description.toLowerCase().includes(searchTerm);
            const matchesCategory = currentCategoryFilter === 'all' || product.category === currentCategoryFilter;
            return matchesSearch && matchesCategory;
        });
        renderProducts(filtered);
    };

    const debouncedFilterProducts = debounce(filterProducts, 300);

    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            filterBtns.forEach(b => {
                b.classList.remove('btn-danger', 'active');
                b.classList.add('btn-outline-danger');
            });
            this.classList.remove('btn-outline-danger');
            this.classList.add('btn-danger', 'active');

            currentCategoryFilter = this.getAttribute('data-filter');
            filterProducts();
        });
    });

    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            debouncedFilterProducts();
        });
    }
}

// Render products
function renderProducts(productsToRender) {
    const productsContainer = document.getElementById('productsContainer');
    if (!productsContainer) return;

    if (productsToRender.length === 0) {
        productsContainer.innerHTML = `
            <div class="col-12">
                <div class="empty-products-state text-center p-5 rounded-4">
                    <div class="empty-products-icon mb-3">🍦</div>
                    <h4 class="fw-bold mb-2">No products match your search.</h4>
                    <p class="text-muted mb-4">Try a different search term or reset the category filters to keep browsing.</p>
                    <button class="btn btn-danger rounded-pill px-4" id="resetProductFilters">Start Exploring</button>
                </div>
            </div>
        `;
        document.getElementById('resetProductFilters')?.addEventListener('click', function () {
            currentCategoryFilter = 'all';
            const searchInput = document.getElementById('searchInput');
            if (searchInput) searchInput.value = '';
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('btn-danger', 'active');
                btn.classList.add('btn-outline-danger');
            });
            const defaultFilter = document.querySelector('.filter-btn[data-filter="all"]');
            if (defaultFilter) {
                defaultFilter.classList.remove('btn-outline-danger');
                defaultFilter.classList.add('btn-danger', 'active');
            }
            renderProducts(products);
            document.getElementById('products')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
        return;
    }

    let productsHTML = '';
    productsToRender.forEach(product => {
        productsHTML += `
            <div class="col-12 col-md-6 col-lg-4">
                <div class="card product-item h-100" style="cursor: pointer;" data-id="${product.id}">
                    <img src="${product.image}" class="card-img-top product-card-image" alt="${product.name}" data-product-open="true">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title product-card-title" data-product-open="true">${product.name}</h5>
                        <p class="card-text flex-grow-1">${product.description}</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="fw-bold fs-5 text-danger">₹${product.price}</span>
                            <button class="btn btn-danger btn-sm add-to-cart rounded-pill px-3" data-id="${product.id}">
                                <i class="bi bi-cart-plus"></i> Add
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    productsContainer.innerHTML = productsHTML;

    // Add event listeners to product cards to open modal
    document.querySelectorAll('.product-item').forEach(item => {
        item.addEventListener('click', function () {
            const productId = parseInt(this.getAttribute('data-id'));
            openProductModal(productId);
        });
    });

    document.querySelectorAll('[data-product-open="true"]').forEach(element => {
        element.addEventListener('click', function (e) {
            e.stopPropagation();
            const productItem = this.closest('.product-item');
            const productId = parseInt(productItem?.getAttribute('data-id'));
            openProductModal(productId);
        });
    });

    // Add event listeners to "Add to Cart" buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation(); // Prevent opening the modal when clicking the button
            const productId = parseInt(this.getAttribute('data-id'));
            addToCart(productId, this);
        });
    });
}

// Open Product Modal
function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    const details = getProductDetails(productId);

    document.getElementById('modalProductImage').src = product.image;
    document.getElementById('modalProductName').textContent = product.name;
    document.getElementById('modalProductCategory').textContent = product.category;
    document.getElementById('modalProductPrice').textContent = product.price;
    document.getElementById('modalProductDesc').textContent = product.description;
    document.getElementById('modalProductIngredients').textContent = details.ingredients;
    document.getElementById('modalProductNutrition').textContent = details.nutrition;
    document.getElementById('modalProductReviews').innerHTML = details.reviews.map(review => `<div class="product-review">${escapeHtml(review)}</div>`).join('');

    const addToCartBtn = document.getElementById('modalAddToCartButton');
    // Remove old event listeners
    const newBtn = addToCartBtn.cloneNode(true);
    addToCartBtn.parentNode.replaceChild(newBtn, addToCartBtn);

    newBtn.addEventListener('click', function () {
        addToCart(product.id, newBtn);
        const modal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
        if (modal) modal.hide();
    });

    const productModal = new bootstrap.Modal(document.getElementById('productModal'));
    productModal.show();
}

// Add to cart function
function addToCart(productId, originElement) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    // Check if product is already in cart
    const existingItem = cart.find(item => item.id === productId);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            image: product.image,
            quantity: 1
        });
    }

    // Update cart count with bounce micro-interaction
    updateCartCount();
    bounceCartIcon();
    animateAddToCart(product, originElement);

    // Save to localStorage
    localStorage.setItem('cart', JSON.stringify(cart));

    // Show confirmation
    showToast(`${product.name} added to cart!`);
}

// Update cart count
function updateCartCount() {
    const cartCount = document.getElementById('cartCount');
    if (cartCount) {
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        cartCount.textContent = totalItems;
    }
}

// Render cart
function renderCart() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    const emptyCartMessage = document.getElementById('emptyCartMessage');

    if (!cartItems || !cartTotal) return;

    if (cart.length === 0) {
        if (emptyCartMessage) {
            emptyCartMessage.style.display = 'block';
            emptyCartMessage.innerHTML = `
                <div class="empty-cart-illustration mb-3">🍦</div>
                <h6 class="fw-bold mb-2">Your cart is empty</h6>
                <p class="text-muted mb-3">Start exploring the menu and add a few sweet treats.</p>
                <button class="btn btn-danger rounded-pill px-4" id="startExploringFromCart">Start Exploring</button>
            `;
        }
        cartItems.innerHTML = '';
        cartTotal.textContent = '0';
        document.getElementById('startExploringFromCart')?.addEventListener('click', function () {
            const offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('cartOffcanvas'));
            if (offcanvas) offcanvas.hide();
            document.getElementById('products')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
        return;
    }

    if (emptyCartMessage) emptyCartMessage.style.display = 'none';

    let cartHTML = '';
    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        cartHTML += `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}">
                <div class="cart-item-details">
                    <h6>${item.name}</h6>
                    <p class="cart-item-price">₹${item.price} × ${item.quantity}</p>
                </div>
                <div class="cart-item-total">₹${itemTotal}</div>
                <button class="cart-item-remove" data-id="${item.id}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
    });

    cartItems.innerHTML = cartHTML;
    cartTotal.textContent = total;

    // Add event listeners to remove buttons
    document.querySelectorAll('.cart-item-remove').forEach(button => {
        button.addEventListener('click', function () {
            const productId = parseInt(this.getAttribute('data-id'));
            removeFromCart(productId);
        });
    });
}

// Remove from cart
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartCount();
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart();
}

// Load cart from localStorage
function loadCart() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        updateCartCount();
    }
}

// Initialize carousel
function initializeCarousel() {
    // Carousel is handled by Bootstrap
}

// Show testimonial
function showTestimonial(index) {
    const testimonials = document.querySelectorAll('.testimonial-card');
    testimonials.forEach((testimonial, i) => {
        if (i === index) {
            testimonial.classList.add('active');
        } else {
            testimonial.classList.remove('active');
        }
    });
}

// Animate stats counter
function animateStats() {
    const counters = document.querySelectorAll('.stats-counter');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // ms
        const increment = target / (duration / 16); // 16ms per frame

        let current = 0;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    });
}

// Set up scroll animations
function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, {
        threshold: 0.1
    });

    // Observe elements that should be animated
    document.querySelectorAll('.fade-in, .about-content, .about-image, .stats-counter, .category-tile').forEach(el => {
        observer.observe(el);
    });
}

// Handle scroll events
window.addEventListener('scroll', function () {
    // Add scrolled class to header
    const header = document.querySelector('.kw-header');
    if (header) {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }

    // Animate elements when they come into view
    setupScrollAnimations();
});

// Show Toast Notification
function showToast(message, title = "Kwality Wall's", type = "success") {
    const toastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastTitle = document.getElementById('toastTitle');
    const toastIcon = document.getElementById('toastIcon');

    if (!toastEl) return;

    toastMessage.textContent = message;
    if (toastTitle) toastTitle.textContent = title;

    if (type === "success") {
        toastEl.className = "toast align-items-center text-bg-success border-0 shadow-lg rounded-4";
        if (toastIcon) toastIcon.className = "bi bi-check-circle-fill fs-5 me-2";
    } else if (type === "error") {
        toastEl.className = "toast align-items-center text-bg-danger border-0 shadow-lg rounded-4";
        if (toastIcon) toastIcon.className = "bi bi-exclamation-circle-fill fs-5 me-2";
    } else {
        toastEl.className = "toast align-items-center text-bg-primary border-0 shadow-lg rounded-4";
        if (toastIcon) toastIcon.className = "bi bi-info-circle-fill fs-5 me-2";
    }

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// Cart icon bounce micro-interaction
function bounceCartIcon() {
    const cartBtn = document.getElementById('cartButton');
    if (!cartBtn) return;
    cartBtn.classList.remove('cart-bounce');
    // Force reflow to restart animation
    void cartBtn.offsetWidth;
    cartBtn.classList.add('cart-bounce');
    cartBtn.addEventListener('animationend', () => {
        cartBtn.classList.remove('cart-bounce');
    }, { once: true });
}

function animateAddToCart(product, originElement) {
    const cartButton = document.getElementById('cartButton');
    if (!cartButton) return;

    const sourceImage = originElement?.closest('.card')?.querySelector('img')
        || originElement?.querySelector?.('img')
        || document.getElementById('modalProductImage');

    if (!sourceImage) return;

    const sourceRect = sourceImage.getBoundingClientRect();
    const cartRect = cartButton.getBoundingClientRect();
    const flyingImage = document.createElement('img');
    flyingImage.src = product.image;
    flyingImage.alt = product.name;
    flyingImage.className = 'cart-flight-item';
    flyingImage.style.left = `${sourceRect.left}px`;
    flyingImage.style.top = `${sourceRect.top}px`;
    flyingImage.style.width = `${sourceRect.width}px`;
    flyingImage.style.height = `${sourceRect.height}px`;
    document.body.appendChild(flyingImage);

    requestAnimationFrame(() => {
        const translateX = cartRect.left + cartRect.width / 2 - (sourceRect.left + sourceRect.width / 2);
        const translateY = cartRect.top + cartRect.height / 2 - (sourceRect.top + sourceRect.height / 2);
        flyingImage.style.transform = `translate(${translateX}px, ${translateY}px) scale(0.15)`;
        flyingImage.style.opacity = '0';
    });

    flyingImage.addEventListener('transitionend', () => flyingImage.remove(), { once: true });
    setTimeout(() => flyingImage.remove(), 900);

    if (originElement) {
        originElement.classList.remove('button-ripple');
        void originElement.offsetWidth;
        originElement.classList.add('button-ripple');
        originElement.addEventListener('animationend', () => originElement.classList.remove('button-ripple'), { once: true });
    }
}