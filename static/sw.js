// Basic Service Worker to allow PWA installation
self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  // Pass-through fetch (no offline caching needed yet because the backend must be online for CV analysis)
  e.respondWith(fetch(e.request));
});
