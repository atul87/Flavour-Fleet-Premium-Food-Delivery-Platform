// ============================================
// FLAVOUR FLEET — API Client (js/api.js)
// ============================================

const API = {
    BASE: '/api',

    async request(method, endpoint, data = null) {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',   // send session cookie
        };
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        try {
            const res = await fetch(this.BASE + endpoint, options);
            const json = await res.json();
            return json;
        } catch (err) {
            console.error('API Error:', err);
            return { success: false, message: 'Network error. Please try again.' };
        }
    },

    get(endpoint) { return this.request('GET', endpoint); },
    post(endpoint, data) { return this.request('POST', endpoint, data); },
    put(endpoint, data) { return this.request('PUT', endpoint, data); },
    delete(endpoint) { return this.request('DELETE', endpoint); },
};
