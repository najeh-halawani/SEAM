/**
 * SEAM Theme Toggle — Light/Dark mode with localStorage persistence.
 * Loads BEFORE page renders to prevent flash of wrong theme.
 */
(function () {
    'use strict';

    const STORAGE_KEY = 'seam-theme';

    // Apply saved theme immediately (before DOM renders)
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }

    // Once DOM is ready, wire up the toggle button
    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('themeToggle');
        if (!btn) return;

        function updateIcon() {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            btn.textContent = isDark ? '☀️' : '🌙';
            btn.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
        }

        btn.addEventListener('click', () => {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (isDark) {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem(STORAGE_KEY, 'light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem(STORAGE_KEY, 'dark');
            }
            updateIcon();
        });

        updateIcon();
    });
})();
