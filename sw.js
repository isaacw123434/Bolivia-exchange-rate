const CACHE_NAME = 'smart-pay-v5';
const ASSETS = [
  './',
  './index.html',
  './js/app.js',
  './static/output.css',
  'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap',
  'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  // Strategy for rates.json: Stale-While-Revalidate
  // Serve cached immediately, but update from network in background
  if (e.request.url.includes('rates.json')) {
    e.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cachedResponse = await cache.match(e.request);
        const fetchPromise = fetch(e.request).then((networkResponse) => {
          cache.put(e.request, networkResponse.clone());
          return networkResponse;
        });
        return cachedResponse || fetchPromise;
      })
    );
  } else {
    // Strategy for other assets: Cache First, fall back to network
    e.respondWith(
      caches.match(e.request).then((response) => {
        return response || fetch(e.request);
      })
    );
  }
});
