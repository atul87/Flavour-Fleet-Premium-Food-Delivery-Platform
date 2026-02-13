// ============================================
// FLAVOUR FLEET — Auth Module (API-powered)
// ============================================

const Auth = {
    SESSION_KEY: 'flavourfleet_session',

    // ── Cache session locally for quick checks ──
    _cacheSession(user) {
        localStorage.setItem(this.SESSION_KEY, JSON.stringify(user));
    },

    getSession() {
        const data = localStorage.getItem(this.SESSION_KEY);
        return data ? JSON.parse(data) : null;
    },

    isLoggedIn() {
        return this.getSession() !== null;
    },

    // ── Register ──
    async signup(name, email, password) {
        const result = await API.post('/auth/register', { name, email, password });
        if (result.success && result.user) {
            this._cacheSession(result.user);
        }
        return result;
    },

    // ── Login ──
    async login(email, password) {
        const result = await API.post('/auth/login', { email, password });
        if (result.success && result.user) {
            this._cacheSession(result.user);
        }
        return result;
    },

    // ── Logout ──
    async logout() {
        await API.post('/auth/logout');
        localStorage.removeItem(this.SESSION_KEY);
        showToast('Logged out successfully', 'info');
        setTimeout(() => window.location.href = 'index.html', 500);
    },

    // ── Get current user profile from backend ──
    async getCurrentUser() {
        const result = await API.get('/auth/profile');
        if (result.success && result.logged_in) {
            this._cacheSession(result.user);
            return result.user;
        }
        // If server says not logged in, clear local cache
        localStorage.removeItem(this.SESSION_KEY);
        return null;
    },

    // ── Update profile ──
    async updateProfile(data) {
        const result = await API.put('/auth/profile', data);
        if (result.success) {
            // Refresh local cache
            await this.getCurrentUser();
        }
        return result;
    },

    // ── Validation helpers ──
    validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },
    validatePassword(password) {
        return password.length >= 6;
    }
};

// ─── Auth Page Logic ─────────────────────────────────
function initAuthPage() {
    const loginTab = document.getElementById('login-tab');
    const signupTab = document.getElementById('signup-tab');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (!loginTab) return;

    loginTab.addEventListener('click', () => {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
    });

    signupTab.addEventListener('click', () => {
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        signupForm.style.display = 'block';
        loginForm.style.display = 'none';
    });

    // Login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        if (!Auth.validateEmail(email)) {
            showToast('Please enter a valid email', 'error');
            return;
        }

        const result = await Auth.login(email, password);
        if (result.success) {
            showToast(result.message, 'success');
            // Sync cart badge after login
            if (typeof Cart !== 'undefined') Cart.syncFromServer();
            setTimeout(() => window.location.href = 'profile.html', 800);
        } else {
            showToast(result.message, 'error');
        }
    });

    // Signup
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;

        if (!name.trim()) {
            showToast('Please enter your name', 'error');
            return;
        }
        if (!Auth.validateEmail(email)) {
            showToast('Please enter a valid email', 'error');
            return;
        }
        if (!Auth.validatePassword(password)) {
            showToast('Password must be at least 6 characters', 'error');
            return;
        }

        const result = await Auth.signup(name, email, password);
        if (result.success) {
            showToast(result.message, 'success');
            setTimeout(() => window.location.href = 'profile.html', 800);
        } else {
            showToast(result.message, 'error');
        }
    });
}

function updateAuthUI() {
    const profileBtns = document.querySelectorAll('.nav-profile');
    const session = Auth.getSession();
    profileBtns.forEach(btn => {
        if (session) {
            btn.innerHTML = session.name.charAt(0).toUpperCase();
            btn.href = 'profile.html';
            btn.title = session.name;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initAuthPage();
    updateAuthUI();
});
