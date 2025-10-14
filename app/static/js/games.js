/**
 * Games Page JavaScript
 * Handles game filtering and delete confirmation modal
 */

// Game search/filter functionality
function filterGames() {
    const input = document.getElementById('gameSearch');
    if (!input) return;

    const filter = input.value.toUpperCase();
    const table = document.getElementById('gamesTable');
    if (!table) return;

    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        const gameName = tr[i].getElementsByClassName('game-name')[0];
        if (gameName) {
            const textValue = gameName.textContent || gameName.innerText;
            if (textValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = '';
            } else {
                tr[i].style.display = 'none';
            }
        }
    }
}

// Initialize modal event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('deleteModal');
    if (!modal) return; // Only run if modal exists (admin users)

    // Close button (X)
    const closeBtn = modal.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal();
        });
    }

    // Close when clicking outside modal content
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    // ESC key to close modal
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });

    // Cancel button in modal
    const cancelBtn = modal.querySelector('.btn-secondary');
    if (cancelBtn && cancelBtn.getAttribute('onclick')) {
        // onclick attribute already handles this, but add event listener as backup
        cancelBtn.addEventListener('click', function(e) {
            if (e.target.tagName === 'BUTTON') {
                e.preventDefault();
                closeModal();
            }
        });
    }

    // Handle form submission
    const deleteForm = document.getElementById('deleteForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            // Let the form submit naturally
            console.log('Deleting game...');
        });
    }
});

// Delete confirmation modal
function confirmDelete(gameId, gameName) {
    const modal = document.getElementById('deleteModal');
    if (!modal) {
        console.error('Delete modal not found');
        return;
    }

    // Update modal content
    const gameToDeleteSpan = document.getElementById('gameToDelete');
    if (gameToDeleteSpan) {
        gameToDeleteSpan.textContent = gameName;
    }

    // Update form action with correct game ID
    const deleteForm = document.getElementById('deleteForm');
    if (deleteForm) {
        deleteForm.action = `/admin/games/delete/${gameId}`;
        console.log('Delete form action set to:', deleteForm.action);
    }

    // Show modal
    modal.style.display = 'block';

    // Prevent body scrolling when modal is open
    document.body.style.overflow = 'hidden';
}

// Close modal function
function closeModal() {
    const modal = document.getElementById('deleteModal');
    if (!modal) return;

    modal.style.display = 'none';

    // Re-enable body scrolling
    document.body.style.overflow = 'auto';
}

function updatePointDistributionPreview() {
    const container = document.getElementById('pointDistributionPreview');
    if (!container) return;

    const increment = parseInt(document.getElementById('point_scheme')?.value) || 1;
    const teamCount = 6;

    let html = '<div class="point-table">';
    html += '<div class="point-row header"><div class="point-cell">Place</div><div class="point-cell">Points</div></div>';

    for (let i = 0; i < teamCount; i++) {
        const place = i + 1;
        const points = (teamCount - i) * increment;
        html += `<div class="point-row ${place <= 3 ? 'highlight-' + place : ''}">`;
        html += `<div class="point-cell">${place}${getOrdinalSuffix(place)}</div>`;
        html += `<div class="point-cell">${points}</div>`;
        html += '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
}

function getOrdinalSuffix(num) {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return "st";
    if (j === 2 && k !== 12) return "nd";
    if (j === 3 && k !== 13) return "rd";
    return "th";
}

const pointSchemeElement = document.getElementById('point_scheme');
if (pointSchemeElement) {
    updatePointDistributionPreview();
    pointSchemeElement.addEventListener('change', updatePointDistributionPreview);
}
