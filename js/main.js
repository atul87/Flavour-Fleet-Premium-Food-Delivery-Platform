// ============================================
// FLAVOUR FLEET — Main JS (Shared Logic)
// ============================================

// ---------- Toast Notification System ----------
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const icons = { success: '✅', error: '❌', info: '🔔' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
    <span class="toast-icon">${icons[type] || '🔔'}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">✕</button>`;
    toast.style.animation = 'slideInRight 0.4s ease';
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ---------- Navbar Scroll Effect ----------
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
    // Hamburger toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
        document.addEventListener('click', (e) => {
            if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }
}

// ---------- Dark/Light Mode Toggle ----------
function initTheme() {
    const toggle = document.querySelector('.theme-toggle');
    const saved = localStorage.getItem('flavourfleet_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);

    if (toggle) {
        toggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('flavourfleet_theme', next);
            updateThemeIcon(next);
        });
    }
}

function updateThemeIcon(theme) {
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) toggle.innerHTML = theme === 'dark' ? '☀️' : '🌙';
}

// ---------- Scroll Animations (Intersection Observer) ----------
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    if (!elements.length) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    elements.forEach(el => observer.observe(el));
}

// ---------- 3D Tilt Effect ----------
function initTiltEffect() {
    document.querySelectorAll('.tilt-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / centerY * -8;
            const rotateY = (x - centerX) / centerX * 8;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

// ---------- Shared Filter State ----------
const _filterState = { search: '', category: 'all', vegOnly: false };

function applyAllFilters() {
    const cards = document.querySelectorAll('.food-card[data-category]');
    let visibleCount = 0;
    cards.forEach(card => {
        let show = true;
        // Category filter
        if (_filterState.category !== 'all' && card.dataset.category !== _filterState.category) show = false;
        // Veg filter
        if (_filterState.vegOnly && card.dataset.veg === 'no') show = false;
        // Search filter
        if (_filterState.search && !card.textContent.toLowerCase().includes(_filterState.search)) show = false;
        card.style.display = show ? '' : 'none';
        if (show) visibleCount++;
    });
    // Also filter restaurant cards by search
    document.querySelectorAll('.restaurant-card').forEach(card => {
        card.style.display = (!_filterState.search || card.textContent.toLowerCase().includes(_filterState.search)) ? '' : 'none';
    });
    // Empty state
    let emptyEl = document.getElementById('filter-empty-state');
    const grid = document.getElementById('food-grid');
    if (grid) {
        if (visibleCount === 0) {
            if (!emptyEl) {
                emptyEl = document.createElement('div');
                emptyEl.id = 'filter-empty-state';
                emptyEl.style.cssText = 'grid-column:1/-1;text-align:center;padding:3rem 1rem;color:var(--text-muted)';
                grid.parentNode.insertBefore(emptyEl, grid.nextSibling);
            }
            emptyEl.innerHTML = `<div style="font-size:3rem;margin-bottom:0.5rem">😕</div><h3 style="margin-bottom:0.5rem">No items found</h3><p>Try a different search or filter.</p><button class="btn btn-outline" style="margin-top:1rem" onclick="clearAllFilters()">Clear Filters</button>`;
            emptyEl.style.display = 'block';
        } else if (emptyEl) {
            emptyEl.style.display = 'none';
        }
    }
}

function clearAllFilters() {
    _filterState.search = '';
    _filterState.category = 'all';
    _filterState.vegOnly = false;
    const searchInput = document.querySelector('.nav-search input') || document.getElementById('search-input');
    if (searchInput) searchInput.value = '';
    const vegToggle = document.getElementById('veg-toggle');
    if (vegToggle) vegToggle.checked = false;
    document.querySelectorAll('.pill[data-category]').forEach(p => {
        p.classList.toggle('active', p.dataset.category === 'all');
    });
    applyAllFilters();
}

// ---------- Search Filter ----------
function initSearch() {
    const searchInput = document.querySelector('.nav-search input');
    if (!searchInput) return;
    searchInput.addEventListener('input', (e) => {
        _filterState.search = e.target.value.toLowerCase();
        applyAllFilters();
    });
}

// ---------- Category Filter ----------
function initCategoryFilter() {
    const pills = document.querySelectorAll('.pill[data-category]');
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            _filterState.category = pill.dataset.category;
            applyAllFilters();
        });
    });
}

// ---------- Favorites ----------
function toggleFavorite(btn) {
    btn.classList.toggle('active');
    const icon = btn.classList.contains('active') ? '❤️' : '🤍';
    btn.textContent = icon;
    const msg = btn.classList.contains('active') ? 'Added to favorites!' : 'Removed from favorites';
    showToast(msg, btn.classList.contains('active') ? 'success' : 'info');
}

// ---------- Page Loader ----------
function hideLoader() {
    const loader = document.querySelector('.page-loader');
    if (loader) {
        setTimeout(() => loader.classList.add('hidden'), 600);
    }
}

// ---------- Skeleton Loader Helper ----------
function showSkeletons(container, count = 3) {
    if (!container) return;
    let html = '';
    for (let i = 0; i < count; i++) {
        html += `
        <div class="skeleton-card">
            <div class="skeleton-img"></div>
            <div class="skeleton-body">
                <div class="skeleton-line" style="width:80%"></div>
                <div class="skeleton-line" style="width:60%"></div>
                <div class="skeleton-line" style="width:40%"></div>
            </div>
        </div>`;
    }
    container.innerHTML = html;
}

// ---------- Sort Restaurants ----------
function initSort() {
    const sortSelect = document.getElementById('sort-select');
    if (!sortSelect) return;
    sortSelect.addEventListener('change', () => {
        const container = document.querySelector('.restaurants-grid');
        if (!container) return;
        const cards = [...container.querySelectorAll('.restaurant-card')];
        const sortBy = sortSelect.value;
        cards.sort((a, b) => {
            if (sortBy === 'rating') {
                return parseFloat(b.dataset.rating) - parseFloat(a.dataset.rating);
            } else if (sortBy === 'time') {
                return parseInt(a.dataset.time) - parseInt(b.dataset.time);
            } else if (sortBy === 'name') {
                return a.dataset.name.localeCompare(b.dataset.name);
            }
            return 0;
        });
        cards.forEach(card => container.appendChild(card));
    });
}

// ---------- Floating Active Order Pill ----------
function initOrderPill() {
    // Don't show pill on the tracking page itself
    if (window.location.pathname.includes('tracking')) return;

    const statusConfig = {
        'Placed': { text: 'Your order has been placed', dot: 'dot-blue', progress: 10 },
        'Preparing': { text: 'Kitchen is preparing your meal', dot: 'dot-green', progress: 40 },
        'Out for Delivery': { text: 'Driver is on the way 🚴', dot: 'dot-orange', progress: 75 },
    };

    // Create pill element
    const pill = document.createElement('a');
    pill.id = 'active-order-pill';
    pill.href = 'tracking.html';
    pill.className = 'pill-hidden';
    pill.innerHTML = `
        <span class="pill-status-dot"></span>
        <span class="pill-text"></span>
        <span class="pill-track-arrow">Track →</span>
        <div class="pill-progress"><div class="pill-progress-fill" style="width:0%"></div></div>`;
    document.body.appendChild(pill);

    const dot = pill.querySelector('.pill-status-dot');
    const text = pill.querySelector('.pill-text');
    const progressFill = pill.querySelector('.pill-progress-fill');

    function updatePill() {
        const status = localStorage.getItem('flavourfleet_order_status');
        const config = statusConfig[status];

        if (!config) {
            // No active order or Delivered/Cancelled — hide
            pill.classList.add('pill-hidden');
            return;
        }

        // Show pill with correct content
        pill.classList.remove('pill-hidden');
        text.textContent = config.text;
        dot.className = 'pill-status-dot ' + config.dot;
        progressFill.style.width = config.progress + '%';
    }

    // Initial check
    updatePill();

    // Poll localStorage every 3s for cross-tab/status sync
    setInterval(updatePill, 3000);
}

// ---------- Initialize Everything ----------
document.addEventListener('DOMContentLoaded', () => {
    hideLoader();
    initNavbar();
    initTheme();
    initScrollAnimations();
    initTiltEffect();
    initSearch();
    initCategoryFilter();
    initSort();
    initOrderPill();
    // Update cart badge
    if (typeof Cart !== 'undefined') Cart.updateCartBadge();
    if (typeof updateAuthUI !== 'undefined') updateAuthUI();
});
