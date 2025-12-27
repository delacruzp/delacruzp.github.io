const CACHE_NAME = 'recap-2025-v1';
const OFFLINE_URLS = [
  '/',
  '/index.html',
  '/best-of/2025-memories.html',
  '/manifest.json',
  '/img/icon-192.png',
  '/img/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(OFFLINE_URLS))
      .then(self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  // For navigation requests try network first, fall back to cache
  if (event.request.mode === 'navigate' || (event.request.method === 'GET' && event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html'))) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match('/best-of/2025-memories.html'))
    );
    return;
  }

  // For other assets, try cache first then network
  event.respondWith(
    caches.match(event.request).then(resp => resp || fetch(event.request).then(networkResp => {
      // populate cache for future
      return caches.open(CACHE_NAME).then(cache => {
        // don't cache opaque or cross-origin errors
        if (networkResp && networkResp.status === 200 && networkResp.type === 'basic') {
          cache.put(event.request, networkResp.clone());
        }
        return networkResp;
      });
    }).catch(() => {
      // fallback for images
      if (event.request.destination === 'image') {
        return caches.match('/img/icon-192.png');
      }
    }))
  );
});