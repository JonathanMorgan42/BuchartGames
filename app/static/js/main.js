/**
 * Leaderboard View Toggle and Mobile Menu
 */

document.addEventListener('DOMContentLoaded', function() {
    // Leaderboard view toggle
    const tableViewBtn = document.getElementById('tableViewBtn');
    const cardViewBtn = document.getElementById('cardViewBtn');
    const tableView = document.getElementById('tableView');
    const cardView = document.getElementById('cardView');

    if (tableViewBtn && cardViewBtn && tableView && cardView) {
        const savedView = localStorage.getItem('leaderboardView') || 'table';
        switchView(savedView);

        tableViewBtn.addEventListener('click', () => switchView('table'));
        cardViewBtn.addEventListener('click', () => switchView('card'));

        function switchView(view) {
            if (view === 'card') {
                cardView.classList.remove('hidden');
                tableView.classList.add('hidden');
                cardViewBtn.classList.add('active');
                tableViewBtn.classList.remove('active');
                localStorage.setItem('leaderboardView', 'card');
            } else {
                tableView.classList.remove('hidden');
                cardView.classList.add('hidden');
                tableViewBtn.classList.add('active');
                cardViewBtn.classList.remove('active');
                localStorage.setItem('leaderboardView', 'table');
            }
        }
    }

    // Mobile menu toggle
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                navMenu.classList.remove('active');
            }
        });

        // Close menu when clicking a link
        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
            });
        });
    }
});

// Logout confirmation
const logoutLink = document.getElementById('logoutLink');
if (logoutLink) {
    logoutLink.addEventListener('click', function(e) {
        e.preventDefault();
        const confirmBar = document.getElementById('logoutConfirmBar');
        if (confirmBar) {
            confirmBar.style.display = 'block';
        }
    });
}

function closeLogoutConfirm() {
    const confirmBar = document.getElementById('logoutConfirmBar');
    if (confirmBar) {
        confirmBar.style.display = 'none';
    }
}
