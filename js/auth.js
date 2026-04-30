// ============================================
// FLAVOUR FLEET — Supabase Auth Module
// ============================================

// Initialize Supabase client
const supabaseUrl = window.SUPABASE_URL || 'https://YOUR_PROJECT_ID.supabase.co';
const supabaseAnonKey = window.SUPABASE_ANON_KEY || 'YOUR_ANON_KEY';

// Check if Supabase is loaded
if (typeof supabase === 'undefined') {
    console.error('Supabase client not loaded. Add script tag before this script.');
}

const supabaseClient = supabase.createClient(supabaseUrl, supabaseAnonKey);

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

    // ── Register with Supabase ──
    async signup(name, email, password) {
        try {
            const { data, error } = await supabaseClient.auth.signUp({
                email: email,
                password: password,
                options: {
                    data: {
                        name: name
                    }
                }
            });

            if (error) {
                return {
                    success: false,
                    message: error.message || 'Registration failed'
                };
            }

            if (data.user) {
                // Create user profile in public.users table
                const { error: profileError } = await supabaseClient
                    .from('users')
                    .insert({
                        id: data.user.id,
                        email: email,
                        name: name,
                        role: 'user',
                        created_at: new Date().toISOString()
                    });

                if (profileError) {
                    console.warn('Profile creation failed:', profileError);
                }

                this._cacheSession({
                    id: data.user.id,
                    email: email,
                    name: name,
                    role: 'user'
                });

                return {
                    success: true,
                    message: 'Registration successful!',
                    user: {
                        id: data.user.id,
                        email: email,
                        name: name,
                        role: 'user'
                    }
                };
            }

            return {
                success: false,
                message: 'Registration failed'
            };
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Registration failed'
            };
        }
    },

    // ── Login with Supabase ──
    async login(email, password) {
        try {
            const { data, error } = await supabaseClient.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) {
                return {
                    success: false,
                    message: error.message || 'Login failed'
                };
            }

            if (data.user && data.session) {
                // Fetch user profile
                const { data: profile, error: profileError } = await supabaseClient
                    .from('users')
                    .select('*')
                    .eq('id', data.user.id)
                    .single();

                const user = profile || {
                    id: data.user.id,
                    email: email,
                    name: email.split('@')[0]
                };

                this._cacheSession(user);

                // Store token in sessionStorage for API calls
                sessionStorage.setItem('supabase_token', data.session.access_token);

                return {
                    success: true,
                    message: 'Login successful!',
                    user: user,
                    access_token: data.session.access_token
                };
            }

            return {
                success: false,
                message: 'Login failed'
            };
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Login failed'
            };
        }
    },

    // ── Logout ──
    async logout() {
        try {
            await supabaseClient.auth.signOut();
            localStorage.removeItem(this.SESSION_KEY);
            sessionStorage.removeItem('supabase_token');
            showToast('Logged out successfully', 'info');
            setTimeout(() => window.location.href = 'index.html', 500);
        } catch (error) {
            console.error('Logout error:', error);
            localStorage.removeItem(this.SESSION_KEY);
            sessionStorage.removeItem('supabase_token');
            showToast('Logged out', 'info');
            setTimeout(() => window.location.href = 'index.html', 500);
        }
    },

    // ── Get current user from backend ──
    async getCurrentUser() {
        try {
            const result = await API.get('/auth/profile');
            if (result.success && result.logged_in) {
                this._cacheSession(result.user);
                return result.user;
            }
        } catch (error) {
            console.error('Error fetching user profile:', error);
        }
        localStorage.removeItem(this.SESSION_KEY);
        return null;
    },

    // ── Update profile ──
    async updateProfile(data) {
        try {
            const result = await API.put('/auth/profile', data);
            if (result.success) {
                await this.getCurrentUser();
            }
            return result;
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Update failed'
            };
        }
    },

    // ── Password reset ──
    async requestPasswordReset(email) {
        try {
            const { error } = await supabaseClient.auth.resetPasswordForEmail(email);
            if (error) {
                return {
                    success: false,
                    message: error.message
                };
            }
            return {
                success: true,
                message: 'If email is registered, password reset link will be sent'
            };
        } catch (error) {
            return {
                success: false,
                message: error.message
            };
        }
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
    if (!loginForm || !signupForm) return;

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
    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage === 'login.html' && Auth.isLoggedIn()) {
        window.location.replace('profile.html');
        return;
    }
    initAuthPage();
    updateAuthUI();
});
