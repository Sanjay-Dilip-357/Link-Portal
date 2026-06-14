// static/js/app.js

// ===== CSRF Token Helper =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrfToken = getCookie('csrftoken');

// ===== Dark Mode =====
function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    const icon = document.getElementById('darkModeIcon');
    if (!toggle) return;

    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    updateDarkModeIcon(savedTheme, icon);

    toggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-bs-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        updateDarkModeIcon(next, icon);
    });
}

function updateDarkModeIcon(theme, icon) {
    if (!icon) return;
    if (theme === 'dark') {
        icon.className = 'bi bi-sun';
    } else {
        icon.className = 'bi bi-moon-stars';
    }
}

// ===== Auto Suggest =====
function initAutoSuggest() {
    const input = document.getElementById('searchInput');
    const dropdown = document.getElementById('suggestDropdown');
    if (!input || !dropdown) return;

    let debounceTimer;

    input.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const resp = await fetch(`/api/suggest/?q=${encodeURIComponent(query)}`);
                const data = await resp.json();

                if (data.results.length === 0) {
                    dropdown.style.display = 'none';
                    return;
                }

                dropdown.innerHTML = data.results.map(r => `
                    <div class="suggest-item" onclick="window.location.href='/go/${r.id}/'">
                        <img src="${r.favicon}" width="20" height="20" class="me-2 rounded" onerror="this.src='https://www.google.com/s2/favicons?domain=example.com&sz=64'">
                        <div class="flex-grow-1">
                            <div class="fw-medium small">${r.title}</div>
                            <div class="text-muted" style="font-size:0.75rem">${r.description}</div>
                        </div>
                        <div>
                            ${r.categories.map(c => `<span class="badge bg-primary-subtle text-primary" style="font-size:0.65rem">${c}</span>`).join(' ')}
                        </div>
                    </div>
                `).join('');

                dropdown.style.display = 'block';
            } catch (e) {
                console.error('Suggest error:', e);
            }
        }, 300);
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });

    // Close on Escape
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            dropdown.style.display = 'none';
        }
    });
}

// ===== Bookmarks =====
function initBookmarks() {
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        btn.addEventListener('click', async function (e) {
            e.preventDefault();
            const linkId = this.dataset.linkId;
            const icon = this.querySelector('i');

            try {
                const resp = await fetch(`/api/bookmark/${linkId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await resp.json();

                if (data.bookmarked) {
                    icon.className = 'bi bi-heart-fill text-danger';
                    showToast('Added to favorites!', 'success');
                } else {
                    icon.className = 'bi bi-heart';
                    showToast('Removed from favorites', 'info');
                }
            } catch (e) {
                console.error('Bookmark error:', e);
            }
        });
    });
}

function showBookmarks() {
    const modal = new bootstrap.Modal(document.getElementById('bookmarksModal'));
    const list = document.getElementById('bookmarksList');
    list.innerHTML = '<p class="text-center"><i class="bi bi-hourglass-split"></i> Loading...</p>';
    modal.show();

    // Find all bookmarked links on the page
    const bookmarkedCards = [];
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        const icon = btn.querySelector('i');
        if (icon && icon.classList.contains('bi-heart-fill')) {
            const card = btn.closest('.link-card') || btn.closest('.card');
            if (card) {
                const title = card.querySelector('.card-title')?.textContent || 'Unknown';
                const linkId = btn.dataset.linkId;
                bookmarkedCards.push({ title, linkId });
            }
        }
    });

    if (bookmarkedCards.length === 0) {
        list.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-heart display-4 text-muted"></i>
                <p class="text-muted mt-2">No favorites yet.<br>Click the heart icon on any link to save it.</p>
            </div>
        `;
    } else {
        list.innerHTML = bookmarkedCards.map(b => `
            <div class="d-flex align-items-center p-2 border-bottom">
                <div class="flex-grow-1">
                    <strong>${b.title}</strong>
                </div>
                <a href="/go/${b.linkId}/" target="_blank" class="btn btn-sm btn-primary rounded-pill">
                    <i class="bi bi-box-arrow-up-right"></i> Visit
                </a>
            </div>
        `).join('');
    }
}

// ===== Rating =====
function initRating() {
    document.querySelectorAll('.rate-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const linkId = this.dataset.linkId;
            document.getElementById('ratingLinkId').value = linkId;

            // Reset stars
            document.querySelectorAll('#starRating .star-btn').forEach(s => {
                s.className = 'bi bi-star star-btn';
            });

            new bootstrap.Modal(document.getElementById('ratingModal')).show();
        });
    });

    // Star hover and click
    document.querySelectorAll('#starRating .star-btn').forEach(star => {
        star.addEventListener('mouseenter', function () {
            const score = parseInt(this.dataset.score);
            document.querySelectorAll('#starRating .star-btn').forEach(s => {
                const sScore = parseInt(s.dataset.score);
                s.className = sScore <= score ? 'bi bi-star-fill star-btn active' : 'bi bi-star star-btn';
            });
        });

        star.addEventListener('click', async function () {
            const score = parseInt(this.dataset.score);
            const linkId = document.getElementById('ratingLinkId').value;

            try {
                const formData = new FormData();
                formData.append('score', score);

                const resp = await fetch(`/api/rate/${linkId}/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken },
                    body: formData
                });
                const data = await resp.json();

                bootstrap.Modal.getInstance(document.getElementById('ratingModal')).hide();
                showToast(`Rated ${score} stars! Average: ${data.avg_rating}`, 'success');

                // Refresh after small delay
                setTimeout(() => location.reload(), 1000);
            } catch (e) {
                console.error('Rating error:', e);
            }
        });
    });

    // Reset on mouse leave
    document.getElementById('starRating')?.addEventListener('mouseleave', function () {
        document.querySelectorAll('#starRating .star-btn').forEach(s => {
            if (!s.classList.contains('active')) {
                s.className = 'bi bi-star star-btn';
            }
        });
    });
}

// ===== Reports =====
function initReports() {
    document.querySelectorAll('.report-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const linkId = this.dataset.linkId;
            const linkTitle = this.dataset.linkTitle;
            document.getElementById('reportLinkId').value = linkId;
            document.getElementById('reportLinkTitle').textContent = linkTitle;
            new bootstrap.Modal(document.getElementById('reportModal')).show();
        });
    });

    document.getElementById('reportForm')?.addEventListener('submit', async function (e) {
        e.preventDefault();
        const linkId = document.getElementById('reportLinkId').value;
        const formData = new FormData();
        formData.append('report_type', document.getElementById('reportType').value);
        formData.append('message', document.getElementById('reportMessage').value);
        formData.append('email', document.getElementById('reportEmail').value);

        try {
            const resp = await fetch(`/api/report/${linkId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            });
            const data = await resp.json();

            if (data.success) {
                bootstrap.Modal.getInstance(document.getElementById('reportModal')).hide();
                showToast('Report submitted. Thank you!', 'success');
                this.reset();
            }
        } catch (e) {
            console.error('Report error:', e);
        }
    });
}

// ===== Feedback =====
function showFeedbackModal() {
    new bootstrap.Modal(document.getElementById('feedbackModal')).show();
}

function initFeedback() {
    document.getElementById('feedbackForm')?.addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData();
        formData.append('name', document.getElementById('fbName').value);
        formData.append('email', document.getElementById('fbEmail').value);
        formData.append('message', document.getElementById('fbMessage').value);

        try {
            const resp = await fetch('/api/feedback/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            });
            const data = await resp.json();

            if (data.success) {
                bootstrap.Modal.getInstance(document.getElementById('feedbackModal')).hide();
                showToast('Thank you for your feedback!', 'success');
                this.reset();
            }
        } catch (e) {
            console.error('Feedback error:', e);
        }
    });
}

// ===== Toast Notification =====
function showToast(message, type = 'info') {
    // Remove existing toasts
    document.querySelectorAll('.custom-toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `custom-toast alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} shadow-lg`;
    toast.style.cssText = 'position:fixed;top:20px;right:20px;z-index:99999;min-width:250px;animation:slideDown 0.3s ease;';
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : type === 'error' ? 'bi-exclamation-circle-fill' : 'bi-info-circle-fill'} me-2"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== PWA =====
function initPWA() {
    // Register Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => console.log('SW registered'))
            .catch(err => console.log('SW registration failed:', err));
    }

    // Install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;

        // Show install prompt after 30 seconds
        setTimeout(() => {
            const pwaEl = document.getElementById('pwaInstall');
            if (pwaEl) pwaEl.style.display = 'block';
        }, 30000);
    });

    document.getElementById('pwaInstallBtn')?.addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            deferredPrompt = null;
            document.getElementById('pwaInstall').style.display = 'none';
        }
    });

    document.getElementById('pwaCloseBtn')?.addEventListener('click', () => {
        document.getElementById('pwaInstall').style.display = 'none';
    });
}

// ===== Keyboard Shortcut =====
document.addEventListener('keydown', function (e) {
    // Press "/" to focus search
    if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        document.getElementById('searchInput')?.focus();
    }
});

// ===== Add animation CSS =====
const animStyle = document.createElement('style');
animStyle.textContent = `
    @keyframes slideDown { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
`;
document.head.appendChild(animStyle);

// ===== Initialize Everything =====
document.addEventListener('DOMContentLoaded', function () {
    initDarkMode();
    initAutoSuggest();
    initBookmarks();
    initRating();
    initReports();
    initFeedback();
    initPWA();
});