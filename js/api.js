// ============================================
// FLAVOUR FLEET — API Client (js/api.js)
// ============================================

function resolveApiBase() {
    const explicitBase = (window.FLAVOUR_FLEET_API_BASE || '').trim();
    if (explicitBase) {
        return explicitBase.replace(/\/+$/, '') + '/api';
    }

    // GitHub Pages cannot serve backend routes, so use hosted API in production.
    if (window.location.hostname.includes('github.io')) {
        return 'https://flavour-fleet-api.onrender.com/api';
    }

    return '/api';
}

const API = {
    BASE: resolveApiBase(),

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
            const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
            const res = await fetch(this.BASE + normalizedEndpoint, options);
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
