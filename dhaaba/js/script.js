// DOM Elements
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('.nav-menu');
const searchBtn = document.querySelector('.search-btn');
const searchOverlay = document.querySelector('.search-overlay');
const closeSearch = document.querySelector('.close-search');
const searchInput = document.querySelector('#search-input');
const cartBtn = document.querySelector('.cart-btn');
const cartSidebar = document.querySelector('.cart-sidebar');
const closeCart = document.querySelector('.close-cart');
const filterBtns = document.querySelectorAll('.filter-btn');
const productCards = document.querySelectorAll('.product-card');
const addToCartBtns = document.querySelectorAll('.add-to-cart');
const cartCount = document.querySelector('.cart-count');
const wishlistBtns = document.querySelectorAll('.wishlist-action');
const quickViewBtns = document.querySelectorAll('.quick-view');
const newsletterForm = document.querySelector('.newsletter-form');
const contactForm = document.querySelector('.contact-form');

// Mobile Menu Toggle
menuToggle.addEventListener('click', () => {
    navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
});

// Search Overlay
searchBtn.addEventListener('click', () => {
    searchOverlay.classList.add('active');
    setTimeout(() => {
        searchInput.focus();
    }, 300);
});

closeSearch.addEventListener('click', () => {
    searchOverlay.classList.remove('active');
});

// Close overlays when clicking outside
searchOverlay.addEventListener('click', (e) => {
    if (e.target === searchOverlay) {
        searchOverlay.classList.remove('active');
    }
});

// Cart Sidebar
cartBtn.addEventListener('click', () => {
    cartSidebar.classList.add('active');
});

closeCart.addEventListener('click', () => {
    cartSidebar.classList.remove('active');
});

// Close cart when clicking outside
cartSidebar.addEventListener('click', (e) => {
    if (e.target === cartSidebar) {
        cartSidebar.classList.remove('active');
    }
});

// Product Filtering
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all buttons
        filterBtns.forEach(b => b.classList.remove('active'));
        // Add active class to clicked button
        btn.classList.add('active');
        
        const filter = btn.getAttribute('data-filter');
        
        productCards.forEach(card => {
            if (filter === 'all' || card.getAttribute('data-category') === filter) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// Shopping Cart Functionality
let cartItems = [];
let itemCount = 0;

function updateCartCount() {
    cartCount.textContent = itemCount;
    document.querySelector('.cart-sidebar .cart-count').textContent = itemCount;
}

function updateCartTotal() {
    const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.querySelector('.total-amount').textContent = `₹${total}`;
}

function addToCart(productName, price) {
    // Check if item already exists in cart
    const existingItem = cartItems.find(item => item.name === productName);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cartItems.push({
            name: productName,
            price: price,
            quantity: 1
        });
    }
    
    itemCount++;
    updateCartCount();
    updateCartTotal();
    renderCartItems();
    
    // Show notification
    showNotification(`${productName} added to cart!`);
}

function renderCartItems() {
    const cartItemsContainer = document.querySelector('.cart-items');
    
    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <p>Your cart is empty</p>
            </div>
        `;
        return;
    }
    
    cartItemsContainer.innerHTML = '';
    
    cartItems.forEach(item => {
        const cartItemElement = document.createElement('div');
        cartItemElement.className = 'cart-item';
        cartItemElement.innerHTML = `
            <div class="cart-item-details">
                <h4>${item.name}</h4>
                <p>₹${item.price} × ${item.quantity}</p>
            </div>
            <div class="cart-item-actions">
                <button class="remove-item"><i class="fas fa-trash"></i></button>
            </div>
        `;
        cartItemsContainer.appendChild(cartItemElement);
    });
}

// Add to Cart Buttons
addToCartBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const productCard = e.target.closest('.product-card');
        const productName = productCard.querySelector('h3').textContent;
        const priceText = productCard.querySelector('.price').textContent;
        const price = parseInt(priceText.replace('₹', ''));
        
        addToCart(productName, price);
    });
});

// Wishlist Functionality
wishlistBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const icon = btn.querySelector('i');
        if (icon.classList.contains('far')) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            showNotification('Added to wishlist!');
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            showNotification('Removed from wishlist!');
        }
    });
});

// Quick View Functionality
quickViewBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const productCard = e.target.closest('.product-card');
        const productName = productCard.querySelector('h3').textContent;
        showNotification(`Quick view for ${productName} would open here!`);
    });
});

// Newsletter Form
newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = newsletterForm.querySelector('input[type="email"]').value;
    showNotification(`Thank you for subscribing with ${email}!`);
    newsletterForm.reset();
});

// Contact Form
contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    showNotification('Thank you for your message! We will contact you soon.');
    contactForm.reset();
});

// Notification System
function showNotification(message) {
    // Remove existing notification if any
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        backgroundColor: '#4ECDC4',
        color: 'white',
        padding: '15px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        zIndex: '1300',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });
    
    document.body.appendChild(notification);
    
    // Slide in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Testimonial Slider Auto-scroll
let testimonialIndex = 0;
const testimonialSlider = document.querySelector('.testimonial-slider');

function autoScrollTestimonials() {
    if (window.innerWidth > 768) return; // Only on mobile
    
    testimonialIndex = (testimonialIndex + 1) % (testimonialSlider.children.length);
    testimonialSlider.scrollTo({
        left: testimonialIndex * testimonialSlider.children[0].offsetWidth,
        behavior: 'smooth'
    });
}

setInterval(autoScrollTestimonials, 5000);

// Smooth Scrolling for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Sticky Header
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    } else {
        header.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    updateCartTotal();
    renderCartItems();
    
    // Add animation to hero content
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '0';
        heroContent.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            heroContent.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            heroContent.style.opacity = '1';
            heroContent.style.transform = 'translateY(0)';
        }, 300);
    }
});

// Product Card Animation on Scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.product-card, .about-content, .testimonial-card, .contact-content');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (elementPosition < screenPosition) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// Set initial state for animated elements
document.querySelectorAll('.product-card, .about-content, .testimonial-card, .contact-content').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
});

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);