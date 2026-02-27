/* ====================================================
   FLAVOUR FLEET — Service Worker
   Cache-first for static assets, network-first for API.
   ==================================================== */

const CACHE_NAME = 'flavourfleet-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/menu.html',
    '/restaurants.html',
    '/offers.html',
    '/login.html',
    '/cart.html',
    '/tracking.html',
    '/css/style.css',
    '/css/animations.css',
    '/js/api.js',
    '/js/cart.js',
    '/js/auth.js',
    '/js/main.js',
    '/js/dynamic-render.js',
];

// Install — cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch — network-first for API, cache-first for static
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // API calls: network-first
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then((res) => res)
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Static assets: cache-first
    event.respondWith(
        caches.match(event.request).then((cached) => {
            return cached || fetch(event.request).then((res) => {
                // Cache new static assets
                if (res.status === 200) {
                    const clone = res.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return res;
            });
        })
    );
});
