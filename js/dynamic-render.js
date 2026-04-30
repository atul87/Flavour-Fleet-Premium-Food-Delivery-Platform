/* ====================================================
   FLAVOUR FLEET — Dynamic Page Renderer
   Fetches data from backend APIs and renders cards
   for Menu, Restaurants, and Offers pages.
   ==================================================== */

const DynamicRender = (() => {
    const API_BASE = '';
    const VEG_ITEM_IDS = new Set([
        'p1', 'p4', 'i3', 'i5', 'm3', 'pa2', 'pa3', 'c3',
        'sa2', 'sa3', 'd1', 'd2', 'd3', 'd4'
    ]);

    function inferIsVeg(item) {
        const explicit = item.is_veg;
        if (explicit === true || explicit === 'yes' || explicit === 'true' || explicit === 1) return true;
        if (explicit === false || explicit === 'no' || explicit === 'false' || explicit === 0) return false;

        const itemId = String(item.item_id || item.id || '').toLowerCase();
        if (VEG_ITEM_IDS.has(itemId)) return true;

        const badge = String(item.badge || '').toLowerCase();
        if (badge === 'veg' || badge === 'vegan') return true;

        return false;
    }

    // ─── Menu Page ──────────────────────────────────
    async function renderMenu(gridId) {
        const grid = document.getElementById(gridId);
        if (!grid) return;

        // Show skeleton while loading
        grid.innerHTML = Array(8).fill(0).map(() => `
            <div class="food-card skeleton-card" style="min-height:300px">
                <div class="food-image" style="background:var(--bg-tertiary);height:180px;border-radius:var(--radius-md)"></div>
                <div class="food-body"><div style="height:16px;width:70%;background:var(--bg-tertiary);border-radius:4px;margin-bottom:8px"></div><div style="height:12px;width:90%;background:var(--bg-tertiary);border-radius:4px"></div></div>
            </div>
        `).join('');

        try {
            const res = await fetch(`${API_BASE}/api/menu`);
            const data = await res.json();
            if (!data.success || !data.items.length) {
                grid.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:2rem">No menu items found.</p>';
                return;
            }

            grid.innerHTML = data.items.map(item => {
                const isVeg = inferIsVeg(item);
                const vegClass = isVeg ? 'veg' : 'non-veg';
                const vegLabel = isVeg ? 'Veg' : 'Non-Veg';
                const badge = item.badge ? `<span class="food-badge">${item.badge}</span>` : '';
                const price = Math.round(item.price);
                const rating = (Number(item.rating) || 4.5).toFixed(1);
                const imgSrc = item.image || 'assets/images/default.png';
                const category = (item.category || '').toLowerCase();

                return `
                <div class="food-card tilt-card animate-on-scroll" data-category="${category}" data-veg="${isVeg ? 'yes' : 'no'}">
                    <div class="food-image"><img loading="lazy" src="${imgSrc}" alt="${item.name}">${badge}</div>
                    <div class="food-body">
                        <h4>${item.name} <span class="veg-indicator ${vegClass}">${vegLabel}</span></h4>
                        <p class="food-desc">${item.description || ''}</p>
                    </div>
                    <div class="food-footer"><span class="food-price">₹${price}</span><span class="food-rating">⭐ ${rating}</span>
                        <div class="cart-actions" data-id="${item.item_id}" data-name="${item.name}" data-price="${price}" data-image="${imgSrc}" data-restaurant="${item.restaurant || ''}">
                            <button class="add-to-cart-btn" onclick="addItem(this)">+</button>
                        </div>
                    </div>
                </div>`;
            }).join('');

            // Restore cart qty selectors for items already in cart
            if (typeof Cart !== 'undefined') {
                const cartItems = Cart.getCart();
                cartItems.forEach(ci => {
                    const wrapper = document.querySelector(`.cart-actions[data-id="${ci.id}"]`);
                    if (wrapper && typeof updateQtyUI === 'function') updateQtyUI(wrapper, ci.id);
                });
            }

            // Re-init scroll animations
            if (typeof initScrollAnimations === 'function') initScrollAnimations();

        } catch (err) {
            console.error('Menu fetch failed:', err);
            grid.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:2rem">Failed to load menu. Please try again.</p>';
        }
    }


    // ─── Restaurants Page ───────────────────────────
    async function renderRestaurants(gridSelector) {
        const grid = document.querySelector(gridSelector);
        if (!grid) return;

        grid.innerHTML = Array(6).fill(0).map(() => `
            <div class="restaurant-card skeleton-card" style="min-height:260px">
                <div class="card-image" style="background:var(--bg-tertiary);height:160px;border-radius:var(--radius-md)"></div>
                <div class="card-body"><div style="height:16px;width:60%;background:var(--bg-tertiary);border-radius:4px;margin:12px 0"></div></div>
            </div>
        `).join('');

        try {
            const res = await fetch(`${API_BASE}/api/restaurants`);
            const data = await res.json();
            if (!data.success || !data.restaurants.length) {
                grid.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:2rem">No restaurants found.</p>';
                return;
            }

            grid.innerHTML = data.restaurants.map(r => {
                const imgSrc = r.image || 'assets/images/default.png';
                const rating = (r.rating || 4.5).toFixed(1);
                const deliveryTime = r.delivery_time || '30-40';
                const category = (r.category || '').toLowerCase();
                const cuisine = r.description || r.category || '';
                const parsedTime = parseInt(String(deliveryTime).split('-')[0], 10) || 0;
                const name = r.name || '';
                const priceRange = r.price_range || '$$';
                const priceLevel = (String(priceRange).match(/\$/g) || []).length || 0;

                return `
                <a href="menu.html" class="restaurant-card tilt-card animate-on-scroll" data-category="${category}" data-rating="${rating}" data-time="${parsedTime}" data-name="${name.toLowerCase()}" data-price-level="${priceLevel}">
                    <div class="card-image">
                        <img loading="lazy" src="${imgSrc}" alt="${r.name}">
                        <span class="delivery-badge">• ${deliveryTime} min</span>
                        <button class="fav-btn" onclick="event.preventDefault()"><i class="far fa-heart"></i></button>
                    </div>
                    <div class="card-body">
                        <h3>${r.name}</h3>
                        <p class="cuisine">${cuisine}</p>
                        <div class="card-meta">
                            <span class="rating">⭐ ${rating}</span>
                            <span class="delivery-time">${r.price_range || '$$'}</span>
                        </div>
                    </div>
                </a>`;
            }).join('');

            if (typeof initScrollAnimations === 'function') initScrollAnimations();

        } catch (err) {
            console.error('Restaurants fetch failed:', err);
            grid.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:2rem">Failed to load restaurants. Please try again.</p>';
        }
    }


    // ─── Offers Page ────────────────────────────────
    async function renderOffers(gridSelector) {
        const grid = document.querySelector(gridSelector);
        if (!grid) return;

        grid.innerHTML = Array(4).fill(0).map(() => `
            <div class="offer-card skeleton-card" style="min-height:200px">
                <div style="padding:24px"><div style="height:56px;width:56px;background:var(--bg-tertiary);border-radius:12px;margin-bottom:16px"></div><div style="height:16px;width:60%;background:var(--bg-tertiary);border-radius:4px;margin-bottom:8px"></div><div style="height:12px;width:80%;background:var(--bg-tertiary);border-radius:4px"></div></div>
            </div>
        `).join('');

        try {
            const res = await fetch(`${API_BASE}/api/offers`);
            const data = await res.json();
            if (!data.success || !data.offers.length) {
                grid.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:2rem">No offers available right now.</p>';
                return;
            }

            grid.innerHTML = data.offers.map(offer => {
                const color = offer.color || 'orange';
                const icon = offer.icon || '🎟';
                const discountLabel = offer.discount_type === 'percent'
                    ? `${offer.discount_value}%`
                    : offer.discount_type === 'flat'
                        ? `₹${offer.discount_value}`
                        : 'FREE';

                return `
                <div class="offer-card animate-on-scroll">
                    <div class="offer-header">
                        <div class="offer-icon ${color}">${icon}</div>
                        <div class="offer-pct">${discountLabel}</div>
                    </div>
                    <div class="offer-body" style="padding:0 var(--space-xl) var(--space-xl)">
                        <h3 style="margin-bottom:var(--space-xs)">${offer.title}</h3>
                        <p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:var(--space-md)">${offer.description || ''}</p>
                        <div class="mega-code" style="display:inline-flex;align-items:center;gap:var(--space-md);padding:0.5rem 1rem;border:2px dashed var(--primary);border-radius:var(--radius-md);font-weight:800;color:var(--primary);letter-spacing:2px;font-size:1rem">
                            ${offer.code}
                            <button onclick="navigator.clipboard.writeText('${offer.code}');showToast('Code copied!','success')" style="background:var(--primary);color:#fff;border:none;padding:0.25rem 0.6rem;border-radius:var(--radius-sm);font-size:0.7rem;font-weight:600;cursor:pointer">COPY</button>
                        </div>
                        ${offer.tag ? `<span style="display:inline-block;margin-left:8px;padding:0.2rem 0.6rem;background:rgba(255,107,53,0.12);border-radius:var(--radius-sm);font-size:0.7rem;font-weight:600;color:var(--primary)">${offer.tag}</span>` : ''}
                        <p style="color:var(--text-muted);font-size:0.75rem;margin-top:var(--space-sm)">${offer.valid_till ? 'Valid till: ' + offer.valid_till : ''}</p>
                    </div>
                </div>`;
            }).join('');

            if (typeof initScrollAnimations === 'function') initScrollAnimations();

        } catch (err) {
            console.error('Offers fetch failed:', err);
            grid.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:2rem">Failed to load offers. Please try again.</p>';
        }
    }

    return { renderMenu, renderRestaurants, renderOffers };
})();
