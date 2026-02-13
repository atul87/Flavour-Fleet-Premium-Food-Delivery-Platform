// ============================================
// FLAVOUR FLEET — Cart Module (API-powered)
// ============================================

const Cart = {
    _items: [],   // local cache for synchronous access

    // ── Sync from server ──
    async syncFromServer() {
        const result = await API.get('/cart');
        if (result.success) {
            this._items = result.items || [];
        }
        this.updateCartBadge();
        return this._items;
    },

    // ── Get cached items (synchronous) ──
    getCart() {
        return this._items;
    },

    // ── Add to cart ──
    async addToCart(item) {
        const result = await API.post('/cart/add', item);
        if (result.success) {
            this._items = result.items || [];
            this.updateCartBadge();
            window.dispatchEvent(new Event('cartUpdated'));
            showToast(result.message || `${item.name} added to cart!`, 'success');
        } else {
            showToast(result.message || 'Failed to add item', 'error');
        }
        return result;
    },

    // ── Remove from cart ──
    async removeFromCart(id) {
        const result = await API.delete('/cart/remove/' + id);
        if (result.success) {
            this._items = result.items || [];
            this.updateCartBadge();
            window.dispatchEvent(new Event('cartUpdated'));
        }
        return result;
    },

    // ── Update quantity ──
    async updateQuantity(id, qty) {
        const result = await API.put('/cart/update', { id, quantity: qty });
        if (result.success) {
            this._items = result.items || [];
            this.updateCartBadge();
            window.dispatchEvent(new Event('cartUpdated'));
        }
        return result;
    },

    // ── Clear cart ──
    async clearCart() {
        const result = await API.delete('/cart/clear');
        if (result.success) {
            this._items = [];
            this.updateCartBadge();
            window.dispatchEvent(new Event('cartUpdated'));
        }
        return result;
    },

    // ── Computed values (use cached items) ──
    getItemCount() {
        return this._items.reduce((sum, i) => sum + i.quantity, 0);
    },

    getSubtotal() {
        return this._items.reduce((sum, i) => sum + (i.price * i.quantity), 0);
    },

    getDeliveryFee() {
        const subtotal = this.getSubtotal();
        return subtotal > 0 ? (subtotal > 30 ? 0 : 4.99) : 0;
    },

    getTax() {
        return +(this.getSubtotal() * 0.08).toFixed(2);
    },

    getTotal(discount = 0) {
        return +(this.getSubtotal() + this.getDeliveryFee() + this.getTax() - discount).toFixed(2);
    },

    // ── Promo code validation ──
    async applyPromo(code) {
        const result = await API.post('/offers/validate', { code });
        if (result.success) {
            return {
                discount: result.discount_value,
                type: result.discount_type,
                label: result.label || result.message,
                discountAmount: result.discount_amount
            };
        }
        return null;
    },

    // ── Badge update (synchronous) ──
    updateCartBadge() {
        const badges = document.querySelectorAll('.cart-count');
        const count = this.getItemCount();
        badges.forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        });
    },
};


// ─── Cart Page Rendering ─────────────────────────────

async function renderCartPage() {
    const cartItems = document.getElementById('cart-items');
    const cartSummaryEl = document.getElementById('cart-summary-details');
    if (!cartItems) return;

    // Fetch latest from server
    await Cart.syncFromServer();
    const cart = Cart.getCart();

    if (cart.length === 0) {
        cartItems.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🛒</div>
        <h3>Your cart is empty</h3>
        <p>Looks like you haven't added anything to your cart yet.</p>
        <a href="restaurants.html" class="btn btn-primary">Browse Restaurants</a>
      </div>`;
        if (cartSummaryEl) cartSummaryEl.parentElement.style.display = 'none';
        return;
    }

    cartItems.innerHTML = cart.map(item => `
    <div class="cart-item" data-id="${item.id}">
      <img src="${item.image}" alt="${item.name}">
      <div class="cart-item-info">
        <h4>${item.name}</h4>
        <p class="cart-item-desc">${item.restaurant || ''}</p>
        <p class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</p>
        <div class="quantity-control">
          <button onclick="changeQty('${item.id}', -1)">−</button>
          <span>${item.quantity}</span>
          <button onclick="changeQty('${item.id}', 1)">+</button>
        </div>
      </div>
      <button class="remove-btn" onclick="removeItem('${item.id}')">✕</button>
    </div>
  `).join('');

    updateSummary();
}

async function changeQty(id, delta) {
    const cart = Cart.getCart();
    const item = cart.find(i => i.id === id);
    if (item) {
        const newQty = item.quantity + delta;
        if (newQty <= 0) {
            await Cart.removeFromCart(id);
        } else {
            await Cart.updateQuantity(id, newQty);
        }
        renderCartPage();
    }
}

async function removeItem(id) {
    await Cart.removeFromCart(id);
    renderCartPage();
    showToast('Item removed from cart', 'info');
}

function updateSummary(discount = 0) {
    const el = document.getElementById('cart-summary-details');
    if (!el) return;
    const subtotal = Cart.getSubtotal();
    const delivery = Cart.getDeliveryFee();
    const tax = Cart.getTax();
    const total = Cart.getTotal(discount);

    el.innerHTML = `
    <div class="summary-row"><span>Subtotal</span><span>$${subtotal.toFixed(2)}</span></div>
    <div class="summary-row"><span>Delivery Fee</span><span>${delivery === 0 ? 'FREE' : '$' + delivery.toFixed(2)}</span></div>
    <div class="summary-row"><span>Tax</span><span>$${tax.toFixed(2)}</span></div>
    ${discount > 0 ? `<div class="summary-row" style="color:var(--secondary)"><span>Discount</span><span>-$${discount.toFixed(2)}</span></div>` : ''}
    <div class="summary-row total"><span>Total</span><span>$${total.toFixed(2)}</span></div>
  `;
}

async function applyPromoCode() {
    const input = document.getElementById('promo-code');
    if (!input) return;
    const result = await Cart.applyPromo(input.value);
    if (result) {
        showToast(`Promo applied: ${result.label}`, 'success');
        updateSummary(result.discountAmount);
    } else {
        showToast('Invalid promo code', 'error');
    }
}

// ─── Init ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await Cart.syncFromServer();
    renderCartPage();
});
