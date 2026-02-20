// ============================================
// FLAVOUR FLEET — Admin Dashboard JS
// ============================================

const API = '';

// ── State ──────────────────────────────────
let state = {
    section: 'dashboard',
    adminUser: null,
    ordersPage: 1,
    ordersTotal: 0,
    menuPage: 1,
    usersPage: 1,
    editingId: null,
    charts: {},
};

// ── Boot ────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await checkAdminAuth();
    setupNav();
    setupSidebar();
    setupTopbarSearch();
    showSection('dashboard');
});

async function checkAdminAuth() {
    try {
        const res = await fetch('/api/auth/profile', { credentials: 'include' });
        const data = await res.json();
        if (!data.success || !data.logged_in || data.user.role !== 'admin') {
            window.location.href = '/login.html?redirect=admin';
            return;
        }
        state.adminUser = data.user;
        document.getElementById('admin-name').textContent = data.user.name;
        document.getElementById('admin-avatar-letter').textContent = data.user.name.charAt(0).toUpperCase();
        document.getElementById('topbar-avatar-letter').textContent = data.user.name.charAt(0).toUpperCase();
    } catch (e) {
        window.location.href = '/login.html?redirect=admin';
    }
}

// ── Navigation ──────────────────────────────
function setupNav() {
    document.querySelectorAll('.nav-item[data-section]').forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            showSection(section);
            // Close sidebar on mobile
            if (window.innerWidth <= 768) document.querySelector('.sidebar').classList.remove('open');
        });
    });
    document.getElementById('logout-btn').addEventListener('click', async () => {
        await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
        window.location.href = '/login.html';
    });
}

function setupSidebar() {
    const hamburger = document.getElementById('hamburger-btn');
    const sidebar = document.querySelector('.sidebar');
    if (hamburger) hamburger.addEventListener('click', () => sidebar.classList.toggle('open'));
}

function setupTopbarSearch() {
    const input = document.getElementById('topbar-search');
    if (input) {
        let t;
        input.addEventListener('input', () => {
            clearTimeout(t);
            t = setTimeout(() => {
                const val = input.value.trim();
                if (state.section === 'orders') loadOrders(1, document.getElementById('order-status-filter').value, val);
                if (state.section === 'menu') filterMenuTable(val);
                if (state.section === 'users') loadUsers(1, val);
            }, 300);
        });
    }
}

function showSection(name) {
    state.section = name;
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const sec = document.getElementById('section-' + name);
    if (sec) sec.classList.add('active');
    document.querySelector(`.nav-item[data-section="${name}"]`)?.classList.add('active');
    document.getElementById('topbar-title').textContent = sectionTitle(name);

    // Load section data
    const loaders = {
        dashboard: loadDashboard,
        orders: () => loadOrders(1),
        menu: loadMenu,
        restaurants: loadRestaurants,
        offers: loadOffers,
        users: loadUsers,
        analytics: loadAnalytics,
        settings: loadSettings,
    };
    if (loaders[name]) loaders[name]();
}

function sectionTitle(n) {
    return ({
        dashboard: '🏠 Dashboard', orders: '📦 Orders', menu: '🍔 Menu Items',
        restaurants: '🏪 Restaurants', offers: '🎟 Offers', users: '👥 Users',
        analytics: '📊 Analytics', settings: '⚙ Settings'
    })[n] || n;
}

// ── Dashboard ───────────────────────────────
async function loadDashboard() {
    try {
        const data = await apiFetch('/api/admin/stats');
        if (!data.success) return;
        const s = data.stats;
        setText('stat-orders', s.total_orders.toLocaleString());
        setText('stat-revenue', '$' + s.total_revenue.toFixed(2));
        setText('stat-users', s.total_users.toLocaleString());
        setText('stat-menu', s.total_menu_items.toLocaleString());
        setText('stat-restaurants', s.total_restaurants.toLocaleString());

        renderRecentOrders(data.recent_orders || []);
        await loadDashboardCharts();
    } catch (e) { console.error(e); }
}

function renderRecentOrders(orders) {
    const tbody = document.getElementById('recent-orders-body');
    if (!tbody) return;
    if (!orders.length) { tbody.innerHTML = '<tr><td colspan="5" class="empty-state"><p>No orders yet.</p></td></tr>'; return; }
    tbody.innerHTML = orders.map(o => `
    <tr>
      <td><strong>${o.order_id}</strong></td>
      <td>${o.name || 'Guest'}</td>
      <td>$${(o.total || 0).toFixed(2)}</td>
      <td>${statusBadge(o.status)}</td>
      <td>${formatDate(o.created_at)}</td>
    </tr>
  `).join('');
}

async function loadDashboardCharts() {
    try {
        const data = await apiFetch('/api/admin/analytics');
        if (!data.success) return;
        renderRevenueChart(data.daily_data);
        renderStatusChart(data.status_breakdown);
    } catch (e) { }
}

function renderRevenueChart(daily) {
    const ctx = document.getElementById('revenue-chart');
    if (!ctx) return;
    if (state.charts.revenue) state.charts.revenue.destroy();
    state.charts.revenue = new Chart(ctx, {
        type: 'line',
        data: {
            labels: daily.map(d => d.date),
            datasets: [{
                label: 'Revenue ($)',
                data: daily.map(d => d.revenue),
                borderColor: '#ff6b35',
                backgroundColor: 'rgba(255,107,53,.08)',
                tension: .4, fill: true,
                pointBackgroundColor: '#ff6b35',
                pointRadius: 4, pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { font: { size: 11 } } },
                y: { grid: { color: '#f3f4f6' }, ticks: { font: { size: 11 }, callback: v => '$' + v } }
            }
        }
    });
}

function renderStatusChart(breakdown) {
    const ctx = document.getElementById('status-chart');
    if (!ctx) return;
    if (state.charts.status) state.charts.status.destroy();
    const labels = Object.keys(breakdown).map(k => k.replace(/_/g, ' '));
    const values = Object.values(breakdown);
    const colors = ['#3b82f6', '#f59e0b', '#10b981', '#8b5cf6', '#ef4444'];
    state.charts.status = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data: values, backgroundColor: colors, borderWidth: 0, hoverOffset: 4 }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, boxWidth: 10 } } },
            cutout: '65%',
        }
    });
}

// ── Orders ──────────────────────────────────
async function loadOrders(page = 1, status = 'all', search = '') {
    state.ordersPage = page;
    const tbody = document.getElementById('orders-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;"><span class="spinner"></span></td></tr>';

    try {
        const params = new URLSearchParams({ page, per_page: 15, status, search });
        const data = await apiFetch('/api/admin/orders?' + params);
        state.ordersTotal = data.total;
        if (!data.orders.length) {
            tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="empty-icon">📦</div><h3>No orders found</h3></div></td></tr>';
            return;
        }
        tbody.innerHTML = data.orders.map(o => `
      <tr>
        <td><strong>${o.order_id}</strong></td>
        <td>${o.name || 'Guest'}</td>
        <td>${(o.items || []).length} items</td>
        <td><strong>$${(o.total || 0).toFixed(2)}</strong></td>
        <td>${o.payment_method || 'Card'}</td>
        <td>
          <select class="status-select ${o.status}" onchange="updateOrderStatus('${o.order_id}', this)">
            <option value="placed" ${o.status === 'placed' ? 'selected' : ''}>Placed</option>
            <option value="preparing" ${o.status === 'preparing' ? 'selected' : ''}>Preparing</option>
            <option value="out_for_delivery" ${o.status === 'out_for_delivery' ? 'selected' : ''}>Out for Delivery</option>
            <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
            <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
          </select>
        </td>
        <td>${formatDate(o.created_at)}</td>
        <td><button class="btn btn-sm btn-secondary" onclick="viewOrder(${JSON.stringify(o).replace(/"/g, '&quot;')})">View</button></td>
      </tr>
    `).join('');
        renderPagination('orders-pagination', page, Math.ceil(state.ordersTotal / 15), (p) => {
            loadOrders(p, document.getElementById('order-status-filter').value, document.getElementById('topbar-search')?.value || '');
        });
        setText('orders-count', `${state.ordersTotal} orders total`);
    } catch (e) { toast('Failed to load orders', 'error'); }
}

async function updateOrderStatus(orderId, select) {
    const status = select.value;
    select.className = 'status-select ' + status;
    try {
        const data = await apiFetch(`/api/admin/orders/${orderId}`, 'PUT', { status });
        if (data.success) toast('Order status updated ✓', 'success');
        else toast(data.message, 'error');
    } catch (e) { toast('Update failed', 'error'); }
}

function viewOrder(order) {
    const items = order.items || [];
    document.getElementById('view-order-content').innerHTML = `
    <div class="order-detail-grid">
      <div class="order-detail-item"><label>Order ID</label><span>${order.order_id}</span></div>
      <div class="order-detail-item"><label>Date</label><span>${formatDate(order.created_at)}</span></div>
      <div class="order-detail-item"><label>Customer</label><span>${order.name || 'Guest'}</span></div>
      <div class="order-detail-item"><label>Phone</label><span>${order.phone || '—'}</span></div>
      <div class="order-detail-item" style="grid-column:1/-1"><label>Address</label><span>${order.address || '—'}, ${order.city || ''} ${order.zip || ''}</span></div>
    </div>
    <h4 style="font-size:13px;font-weight:700;margin-bottom:8px;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.3px;">Items</h4>
    <div class="order-items-list">
      ${items.map(it => `<div class="order-item-row"><span class="order-item-name">${it.name}</span><span class="order-item-qty">×${it.quantity}</span><span>$${(it.price * it.quantity).toFixed(2)}</span></div>`).join('')}
    </div>
    <div class="order-price-row"><span>Subtotal</span><span>$${(order.subtotal || 0).toFixed(2)}</span></div>
    <div class="order-price-row"><span>Delivery</span><span>$${(order.delivery_fee || 0).toFixed(2)}</span></div>
    <div class="order-price-row"><span>Tax</span><span>$${(order.tax || 0).toFixed(2)}</span></div>
    ${order.discount ? `<div class="order-price-row"><span>Discount</span><span style="color:var(--success)">-$${(order.discount || 0).toFixed(2)}</span></div>` : ''}
    <div class="order-price-row total"><span>Total</span><span>$${(order.total || 0).toFixed(2)}</span></div>
    <div style="margin-top:14px">
      <label class="form-label">Update Status</label>
      <select class="form-control" id="view-order-status-select">
        ${['placed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'].map(s => `<option value="${s}" ${order.status === s ? 'selected' : ''}>${s.replace(/_/g, ' ')}</option>`).join('')}
      </select>
    </div>
  `;
    document.getElementById('view-order-save-btn').onclick = async () => {
        const ns = document.getElementById('view-order-status-select').value;
        const res = await apiFetch(`/api/admin/orders/${order.order_id}`, 'PUT', { status: ns });
        if (res.success) { toast('Status updated ✓', 'success'); closeModal('view-order-modal'); loadOrders(state.ordersPage); }
        else toast(res.message, 'error');
    };
    openModal('view-order-modal');
}

// Filter
document.addEventListener('DOMContentLoaded', () => {
    const sf = document.getElementById('order-status-filter');
    if (sf) sf.addEventListener('change', () => loadOrders(1, sf.value, document.getElementById('topbar-search')?.value || ''));

    // Export CSV
    const exportBtn = document.getElementById('export-orders-btn');
    if (exportBtn) exportBtn.addEventListener('click', exportOrdersCSV);
});

function exportOrdersCSV() {
    const rows = [['Order ID', 'Customer', 'Amount', 'Status', 'Date']];
    document.querySelectorAll('#orders-body tr').forEach(tr => {
        const cells = tr.querySelectorAll('td');
        if (cells.length > 1) {
            rows.push([cells[0].textContent.trim(), cells[1].textContent.trim(),
            cells[3].textContent.trim(), cells[5].querySelector('select')?.value || '', cells[6].textContent.trim()]);
        }
    });
    const csv = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n');
    downloadFile('orders.csv', 'text/csv', csv);
}

function downloadFile(name, type, content) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([content], { type }));
    a.download = name; a.click();
}

// ── Menu ────────────────────────────────────
let allMenuItems = [];
let menuCategoryFilter = 'all';

async function loadMenu() {
    const tbody = document.getElementById('menu-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;"><span class="spinner"></span></td></tr>';
    try {
        const data = await apiFetch('/api/admin/menu');
        allMenuItems = data.items || [];
        renderMenuTable(allMenuItems);
        setText('menu-count', `${allMenuItems.length} items`);
    } catch (e) { toast('Failed to load menu', 'error'); }
}

function filterMenuTable(search = '') {
    const q = search.toLowerCase();
    const cat = menuCategoryFilter;
    const filtered = allMenuItems.filter(it =>
        (cat === 'all' || it.category === cat) &&
        (!q || it.name.toLowerCase().includes(q) || it.restaurant?.toLowerCase().includes(q))
    );
    renderMenuTable(filtered);
}

function renderMenuTable(items) {
    const tbody = document.getElementById('menu-body');
    if (!tbody) return;
    if (!items.length) { tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">🍔</div><h3>No items found</h3></div></td></tr>'; return; }
    tbody.innerHTML = items.map(it => `
    <tr>
      <td><div class="td-img">
        <img src="${it.image || 'assets/images/default.png'}" alt="${it.name}" onerror="this.src='assets/images/default.png'">
        <div><div class="item-name">${it.name}</div><div class="item-sub">${it.restaurant || '—'}</div></div>
      </div></td>
      <td><span class="badge badge-gray">${it.category}</span></td>
      <td><strong>$${(it.price || 0).toFixed(2)}</strong></td>
      <td>⭐ ${it.rating || '—'}</td>
      <td>${it.badge ? `<span class="badge badge-orange">${it.badge}</span>` : '—'}</td>
      <td>${it.active !== false ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-gray">Inactive</span>'}</td>
      <td>
        <button class="btn btn-sm btn-secondary btn-icon" onclick='editMenuItem(${JSON.stringify(it).replace(/'/g, "&#39;")})'>✏️</button>
        <button class="btn btn-sm btn-danger btn-icon" onclick="deleteMenuItem('${it._id}','${it.name}')">🗑️</button>
      </td>
    </tr>
  `).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    const cf = document.getElementById('menu-category-filter');
    if (cf) cf.addEventListener('change', () => { menuCategoryFilter = cf.value; filterMenuTable(document.getElementById('topbar-search')?.value || ''); });
});

function openAddMenuItem() {
    state.editingId = null;
    document.getElementById('menu-modal-title').textContent = 'Add New Menu Item';
    document.getElementById('menu-form').reset();
    document.getElementById('menu-active-toggle').checked = true;
    openModal('menu-modal');
}

function editMenuItem(item) {
    state.editingId = item._id;
    document.getElementById('menu-modal-title').textContent = 'Edit Menu Item';
    document.getElementById('menu-item-name').value = item.name || '';
    document.getElementById('menu-item-price').value = item.price || '';
    document.getElementById('menu-item-category').value = item.category || '';
    document.getElementById('menu-item-restaurant').value = item.restaurant || '';
    document.getElementById('menu-item-description').value = item.description || '';
    document.getElementById('menu-item-badge').value = item.badge || '';
    document.getElementById('menu-item-rating').value = item.rating || 4.5;
    document.getElementById('menu-active-toggle').checked = item.active !== false;
    openModal('menu-modal');
}

async function saveMenuItem() {
    const body = {
        name: val('menu-item-name'),
        price: parseFloat(val('menu-item-price')),
        category: val('menu-item-category'),
        restaurant: val('menu-item-restaurant'),
        description: val('menu-item-description'),
        badge: val('menu-item-badge'),
        rating: parseFloat(val('menu-item-rating')) || 4.5,
        active: document.getElementById('menu-active-toggle').checked,
    };
    if (!body.name || !body.price || !body.category) { toast('Name, price, and category are required', 'warning'); return; }
    try {
        const url = state.editingId ? `/api/admin/menu/${state.editingId}` : '/api/admin/menu';
        const method = state.editingId ? 'PUT' : 'POST';
        const data = await apiFetch(url, method, body);
        if (data.success) {
            toast(state.editingId ? 'Item updated ✓' : 'Item added ✓', 'success');
            closeModal('menu-modal'); loadMenu();
        } else toast(data.message, 'error');
    } catch (e) { toast('Save failed', 'error'); }
}

function deleteMenuItem(id, name) {
    showConfirm(`Delete "${name}"?`, 'This item will be permanently removed from the menu.', async () => {
        const data = await apiFetch(`/api/admin/menu/${id}`, 'DELETE');
        if (data.success) { toast('Item deleted', 'success'); loadMenu(); }
        else toast(data.message, 'error');
    });
}

// ── Restaurants ─────────────────────────────
let allRestaurants = [];

async function loadRestaurants() {
    const tbody = document.getElementById('restaurants-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;"><span class="spinner"></span></td></tr>';
    try {
        const data = await apiFetch('/api/admin/restaurants');
        allRestaurants = data.restaurants || [];
        renderRestaurantsTable(allRestaurants);
        setText('restaurants-count', `${allRestaurants.length} restaurants`);
    } catch (e) { toast('Failed to load restaurants', 'error'); }
}

function renderRestaurantsTable(items) {
    const tbody = document.getElementById('restaurants-body');
    if (!tbody) return;
    if (!items.length) { tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">🏪</div><h3>No restaurants</h3></div></td></tr>'; return; }
    tbody.innerHTML = items.map(r => `
    <tr>
      <td><div class="td-img">
        <img src="${r.image || 'assets/images/default.png'}" alt="${r.name}" onerror="this.src='assets/images/default.png'">
        <div><div class="item-name">${r.name}</div><div class="item-sub">${r.address || '—'}</div></div>
      </div></td>
      <td><span class="badge badge-gray">${r.category || '—'}</span></td>
      <td>⭐ ${r.rating || '—'}</td>
      <td>🕒 ${r.delivery_time || '—'} min</td>
      <td>${r.price_range || '—'}</td>
      <td>${r.active !== false ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-gray">Inactive</span>'}</td>
      <td>
        <button class="btn btn-sm btn-secondary btn-icon" onclick='editRestaurant(${JSON.stringify(r).replace(/'/g, "&#39;")})'>✏️</button>
        <button class="btn btn-sm btn-danger btn-icon" onclick="deleteRestaurant('${r._id}','${r.name}')">🗑️</button>
      </td>
    </tr>
  `).join('');
}

function openAddRestaurant() {
    state.editingId = null;
    document.getElementById('restaurant-modal-title').textContent = 'Add Restaurant';
    document.getElementById('restaurant-form').reset();
    document.getElementById('restaurant-active-toggle').checked = true;
    openModal('restaurant-modal');
}

function editRestaurant(r) {
    state.editingId = r._id;
    document.getElementById('restaurant-modal-title').textContent = 'Edit Restaurant';
    document.getElementById('restaurant-name').value = r.name || '';
    document.getElementById('restaurant-category').value = r.category || '';
    document.getElementById('restaurant-description').value = r.description || '';
    document.getElementById('restaurant-rating').value = r.rating || 4.5;
    document.getElementById('restaurant-delivery-time').value = r.delivery_time || '';
    document.getElementById('restaurant-price-range').value = r.price_range || '$$';
    document.getElementById('restaurant-address').value = r.address || '';
    document.getElementById('restaurant-active-toggle').checked = r.active !== false;
    openModal('restaurant-modal');
}

async function saveRestaurant() {
    const body = {
        name: val('restaurant-name'),
        category: val('restaurant-category'),
        description: val('restaurant-description'),
        rating: parseFloat(val('restaurant-rating')) || 4.5,
        delivery_time: val('restaurant-delivery-time'),
        price_range: val('restaurant-price-range'),
        address: val('restaurant-address'),
        active: document.getElementById('restaurant-active-toggle').checked,
    };
    if (!body.name) { toast('Restaurant name is required', 'warning'); return; }
    try {
        const url = state.editingId ? `/api/admin/restaurants/${state.editingId}` : '/api/admin/restaurants';
        const method = state.editingId ? 'PUT' : 'POST';
        const data = await apiFetch(url, method, body);
        if (data.success) { toast(state.editingId ? 'Restaurant updated ✓' : 'Restaurant added ✓', 'success'); closeModal('restaurant-modal'); loadRestaurants(); }
        else toast(data.message, 'error');
    } catch (e) { toast('Save failed', 'error'); }
}

function deleteRestaurant(id, name) {
    showConfirm(`Delete "${name}"?`, 'This restaurant will be permanently removed.', async () => {
        const data = await apiFetch(`/api/admin/restaurants/${id}`, 'DELETE');
        if (data.success) { toast('Restaurant deleted', 'success'); loadRestaurants(); }
        else toast(data.message, 'error');
    });
}

// ── Offers ──────────────────────────────────
let allOffers = [];

async function loadOffers() {
    const tbody = document.getElementById('offers-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;"><span class="spinner"></span></td></tr>';
    try {
        const data = await apiFetch('/api/admin/offers');
        allOffers = data.offers || [];
        renderOffersTable(allOffers);
        setText('offers-count', `${allOffers.length} offers`);
    } catch (e) { toast('Failed to load offers', 'error'); }
}

function renderOffersTable(items) {
    const tbody = document.getElementById('offers-body');
    if (!tbody) return;
    if (!items.length) { tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">🎟</div><h3>No offers</h3></div></td></tr>'; return; }
    tbody.innerHTML = items.map(o => `
    <tr>
      <td><div class="td-img">
        <div class="offer-icon ${o.color || 'orange'}">${o.icon || '🎟'}</div>
        <div><div class="item-name">${o.code}</div><div class="item-sub">${o.title}</div></div>
      </div></td>
      <td>${o.discount_type === 'percent' ? o.discount_value + '%' : o.discount_type === 'flat' ? '$' + o.discount_value : 'Free Delivery'}</td>
      <td>${o.discount_type || 'percent'}</td>
      <td>$${o.min_order || 0}</td>
      <td>${o.valid_till || '—'}</td>
      <td>${o.active !== false ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-gray">Inactive</span>'}</td>
      <td>
        <button class="btn btn-sm btn-secondary btn-icon" onclick='editOffer(${JSON.stringify(o).replace(/'/g, "&#39;")})'>✏️</button>
        <button class="btn btn-sm btn-danger btn-icon" onclick="deleteOffer('${o._id}','${o.code}')">🗑️</button>
      </td>
    </tr>
  `).join('');
}

function openAddOffer() {
    state.editingId = null;
    document.getElementById('offer-modal-title').textContent = 'Add Promo Code';
    document.getElementById('offer-form').reset();
    document.getElementById('offer-active-toggle').checked = true;
    document.getElementById('offer-code-field').disabled = false;
    openModal('offer-modal');
}

function editOffer(o) {
    state.editingId = o._id;
    document.getElementById('offer-modal-title').textContent = 'Edit Offer';
    document.getElementById('offer-code').value = o.code || '';
    document.getElementById('offer-code-field').disabled = true;
    document.getElementById('offer-title').value = o.title || '';
    document.getElementById('offer-description').value = o.description || '';
    document.getElementById('offer-discount-type').value = o.discount_type || 'percent';
    document.getElementById('offer-discount-value').value = o.discount_value || '';
    document.getElementById('offer-min-order').value = o.min_order || 0;
    document.getElementById('offer-valid-till').value = o.valid_till || '';
    document.getElementById('offer-icon').value = o.icon || '🎟';
    document.getElementById('offer-active-toggle').checked = o.active !== false;
    openModal('offer-modal');
}

async function saveOffer() {
    const body = {
        code: val('offer-code').toUpperCase(),
        title: val('offer-title'),
        description: val('offer-description'),
        discount_type: val('offer-discount-type'),
        discount_value: parseFloat(val('offer-discount-value')) || 0,
        min_order: parseFloat(val('offer-min-order')) || 0,
        valid_till: val('offer-valid-till'),
        icon: val('offer-icon') || '🎟',
        active: document.getElementById('offer-active-toggle').checked,
    };
    if (!state.editingId && !body.code) { toast('Promo code is required', 'warning'); return; }
    if (!body.title) { toast('Title is required', 'warning'); return; }
    try {
        const url = state.editingId ? `/api/admin/offers/${state.editingId}` : '/api/admin/offers';
        const method = state.editingId ? 'PUT' : 'POST';
        const data = await apiFetch(url, method, body);
        if (data.success) { toast(state.editingId ? 'Offer updated ✓' : 'Offer created ✓', 'success'); closeModal('offer-modal'); loadOffers(); }
        else toast(data.message, 'error');
    } catch (e) { toast('Save failed', 'error'); }
}

function deleteOffer(id, code) {
    showConfirm(`Delete promo code "${code}"?`, 'This offer will be permanently removed.', async () => {
        const data = await apiFetch(`/api/admin/offers/${id}`, 'DELETE');
        if (data.success) { toast('Offer deleted', 'success'); loadOffers(); }
        else toast(data.message, 'error');
    });
}

// ── Users ───────────────────────────────────
async function loadUsers(page = 1, search = '') {
    const tbody = document.getElementById('users-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:24px;"><span class="spinner"></span></td></tr>';
    try {
        const params = new URLSearchParams({ page, per_page: 20, search });
        const data = await apiFetch('/api/admin/users?' + params);
        const users = data.users || [];
        if (!users.length) { tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">👥</div><h3>No users</h3></div></td></tr>'; return; }
        tbody.innerHTML = users.map(u => `
      <tr>
        <td><div class="td-img">
          <div class="admin-avatar-sm">${u.name?.charAt(0).toUpperCase() || '?'}</div>
          <div><div class="item-name">${u.name}</div><div class="item-sub">${u.email}</div></div>
        </div></td>
        <td>${u.phone || '—'}</td>
        <td>${u.order_count || 0} orders</td>
        <td>${formatDate(u.created_at)}</td>
        <td>
          <span class="badge ${u.role === 'admin' ? 'badge-orange' : 'badge-gray'}">${u.role || 'user'}</span>
          ${u._id !== state.adminUser?.id ? `
            <button class="btn btn-sm btn-secondary btn-icon" style="margin-left:4px"
              onclick="toggleUserRole('${u._id}','${u.role || 'user'}','${u.name}')">
              ${u.role === 'admin' ? '⬇ Demote' : '⬆ Promote'}
            </button>` : ''}
        </td>
      </tr>
    `).join('');
        setText('users-count', `${data.total} users total`);
        renderPagination('users-pagination', page, Math.ceil(data.total / 20), (p) => loadUsers(p, search));
    } catch (e) { toast('Failed to load users', 'error'); }
}

function toggleUserRole(id, currentRole, name) {
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    showConfirm(`${newRole === 'admin' ? 'Promote' : 'Demote'} "${name}"?`,
        `User will become an ${newRole}.`,
        async () => {
            const data = await apiFetch(`/api/admin/users/${id}/role`, 'PUT', { role: newRole });
            if (data.success) { toast('Role updated ✓', 'success'); loadUsers(); }
            else toast(data.message, 'error');
        });
}

// ── Analytics ───────────────────────────────
async function loadAnalytics() {
    try {
        const data = await apiFetch('/api/admin/analytics');
        if (!data.success) return;

        // Revenue trend
        const rCtx = document.getElementById('analytics-revenue-chart');
        if (rCtx) {
            if (state.charts.aRevenue) state.charts.aRevenue.destroy();
            state.charts.aRevenue = new Chart(rCtx, {
                type: 'bar',
                data: {
                    labels: data.daily_data.map(d => d.date),
                    datasets: [{
                        label: 'Revenue ($)',
                        data: data.daily_data.map(d => d.revenue),
                        backgroundColor: 'rgba(255,107,53,.7)',
                        borderRadius: 6, borderSkipped: false,
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { grid: { display: false } }, y: { ticks: { callback: v => '$' + v } } }
                }
            });
        }

        // Orders trend
        const oCtx = document.getElementById('analytics-orders-chart');
        if (oCtx) {
            if (state.charts.aOrders) state.charts.aOrders.destroy();
            state.charts.aOrders = new Chart(oCtx, {
                type: 'line',
                data: {
                    labels: data.daily_data.map(d => d.date),
                    datasets: [{
                        label: 'Orders',
                        data: data.daily_data.map(d => d.orders),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59,130,246,.08)',
                        tension: .4, fill: true,
                        pointBackgroundColor: '#3b82f6', pointRadius: 4,
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { grid: { display: false } }, y: { ticks: { stepSize: 1 } } }
                }
            });
        }

        // Top items
        const topEl = document.getElementById('top-items-list');
        if (topEl && data.top_items.length) {
            const max = data.top_items[0].count || 1;
            topEl.innerHTML = data.top_items.map((item, i) => `
        <div class="top-item-row">
          <div class="top-item-rank">${i + 1}</div>
          <div class="top-item-bar-wrap">
            <div class="top-item-name">${item.name}</div>
            <div class="top-item-bar"><div class="top-item-bar-fill" style="width:${(item.count / max * 100).toFixed(0)}%"></div></div>
          </div>
          <div class="top-item-count">${item.count}</div>
        </div>
      `).join('');
        } else if (topEl) topEl.innerHTML = '<p style="color:var(--text-muted);font-size:13px;text-align:center;padding:16px">No order data yet</p>';

    } catch (e) { console.error(e); }
}

// ── Settings ────────────────────────────────
async function loadSettings() {
    try {
        const data = await apiFetch('/api/admin/settings');
        if (!data.success) return;
        const s = data.settings;
        setValue('settings-platform-name', s.platform_name);
        setValue('settings-delivery-fee', s.delivery_fee);
        setValue('settings-free-threshold', s.free_delivery_threshold);
        setValue('settings-tax', s.tax_percent);
        setValue('settings-email', s.contact_email);
    } catch (e) { }
}

async function saveSettings() {
    const body = {
        platform_name: val('settings-platform-name'),
        delivery_fee: parseFloat(val('settings-delivery-fee')),
        free_delivery_threshold: parseFloat(val('settings-free-threshold')),
        tax_percent: parseFloat(val('settings-tax')),
        contact_email: val('settings-email'),
    };
    try {
        const data = await apiFetch('/api/admin/settings', 'PUT', body);
        if (data.success) toast('Settings saved ✓', 'success');
        else toast(data.message, 'error');
    } catch (e) { toast('Save failed', 'error'); }
}

// ── Modals ──────────────────────────────────
function openModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.add('open');
}

function closeModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove('open');
}

// Close on overlay click
document.addEventListener('click', e => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('open');
    }
});

// ── Confirm Dialog ──────────────────────────
function showConfirm(title, message, onConfirm) {
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;
    document.getElementById('confirm-yes-btn').onclick = () => {
        closeModal('confirm-modal');
        onConfirm();
    };
    openModal('confirm-modal');
}

// ── Toast ────────────────────────────────────
function toast(msg, type = 'info') {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ️'}</span><span class="toast-msg">${msg}</span>`;
    document.getElementById('toast-container').appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity .4s'; setTimeout(() => t.remove(), 400); }, 3000);
}

// ── Pagination ───────────────────────────────
function renderPagination(containerId, current, total, onPageClick) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const pages = [];
    for (let i = 1; i <= Math.min(total, 7); i++) pages.push(i);
    el.innerHTML = `
    <button class="page-btn" ${current <= 1 ? 'disabled' : ''} onclick="(${onPageClick.toString()})(${current - 1})">‹</button>
    ${pages.map(p => `<button class="page-btn ${p === current ? 'active' : ''}" onclick="(${onPageClick.toString()})(${p})">${p}</button>`).join('')}
    <button class="page-btn" ${current >= total ? 'disabled' : ''} onclick="(${onPageClick.toString()})(${current + 1})">›</button>
  `;
}

// ── Helpers ──────────────────────────────────
async function apiFetch(url, method = 'GET', body = null) {
    const opts = { method, credentials: 'include', headers: {} };
    if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
    const res = await fetch(url, opts);
    return await res.json();
}

function val(id) { return (document.getElementById(id)?.value || '').trim(); }
function setValue(id, val) { const el = document.getElementById(id); if (el) el.value = val; }
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }

function statusBadge(status) {
    const map = {
        placed: 'badge-info', preparing: 'badge-warning',
        out_for_delivery: 'badge-success', delivered: 'badge-success', cancelled: 'badge-danger'
    };
    return `<span class="badge ${map[status] || 'badge-gray'}">${(status || '').replace(/_/g, ' ')}</span>`;
}

function formatDate(iso) {
    if (!iso) return '—';
    try {
        return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return iso; }
}
