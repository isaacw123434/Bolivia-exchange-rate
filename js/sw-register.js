if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js', { scope: '/' })
            .then(reg => console.log('SW Registered!', reg.scope))
            .catch(err => console.log('SW Failed:', err));
    });
}
