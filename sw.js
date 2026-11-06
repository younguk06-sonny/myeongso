// 명소찾기 서비스워커 — 앱 화면을 기기에 저장해 두어 빠르게 열리게 함
// 앱을 고친 뒤 GitHub에 다시 올릴 때는 아래 버전 숫자를 하나 올려 주세요 (v1 → v2)
const CACHE = 'myeongso-v2';
const FILES = [
  './', './index.html', './manifest.webmanifest',
  './icon-192.png', './icon-512.png', './icon-maskable-512.png',
  './apple-touch-icon.png', './favicon-32.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// 내 사이트 파일: 인터넷 먼저 → 실패하면 저장본 (항상 최신 화면 유지)
// 지도·검색 등 외부 요청은 건드리지 않음
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  e.respondWith(
    // 페이지 열기(navigate) 요청은 옵션을 붙이면 오류가 나서 주소로 새로 요청. 브라우저 임시 저장본 말고 서버에 최신인지 확인
    fetch(e.request.url, {cache: 'no-cache', credentials: 'same-origin'}).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return res;
    }).catch(() => caches.match(e.request).then(r => r || caches.match('./index.html')))
  );
});
