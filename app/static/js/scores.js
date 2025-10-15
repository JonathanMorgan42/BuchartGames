/**
 * Live Scoring JavaScript
 * Mobile-optimized single-team scoring with penalties
 */

// Global state
let currentTeamId = null;
let globalTimer = null;
let globalStartTime = 0;
let globalElapsed = 0;
let teamScores = {};
let teamPenalties = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeScores();
    updateRankingsOverview();
    attachEventListeners();
});

// Attach event listeners using data attributes
function attachEventListeners() {
    // Team selector
    const teamSelector = document.querySelector('[data-action="switch-team"]');
    if (teamSelector) {
        teamSelector.addEventListener('change', switchTeam);
    }

    // Score input
    const scoreInput = document.querySelector('[data-action="score-change"]');
    if (scoreInput) {
        scoreInput.addEventListener('input', onScoreChange);
    }

    // Score increment/decrement buttons
    const incrementBtn = document.querySelector('[data-action="increment-score"]');
    if (incrementBtn) {
        incrementBtn.addEventListener('click', incrementScore);
    }

    const decrementBtn = document.querySelector('[data-action="decrement-score"]');
    if (decrementBtn) {
        decrementBtn.addEventListener('click', decrementScore);
    }

    // Stopwatch buttons
    const startBtn = document.querySelector('[data-action="start-stopwatch"]');
    if (startBtn) {
        startBtn.addEventListener('click', startStopwatch);
    }

    const stopBtn = document.querySelector('[data-action="stop-stopwatch"]');
    if (stopBtn) {
        stopBtn.addEventListener('click', stopStopwatch);
    }

    const resetBtn = document.querySelector('[data-action="reset-stopwatch"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetStopwatch);
    }

    // Penalty increment/decrement buttons (stackable)
    document.querySelectorAll('[data-action="increment-penalty"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const penaltyId = this.getAttribute('data-penalty-id');
            const penaltyValue = parseFloat(this.getAttribute('data-penalty-value'));
            const penaltyUnit = this.getAttribute('data-penalty-unit');
            incrementPenalty(penaltyId, penaltyValue, penaltyUnit);
        });
    });

    document.querySelectorAll('[data-action="decrement-penalty"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const penaltyId = this.getAttribute('data-penalty-id');
            decrementPenalty(penaltyId);
        });
    });

    // Penalty tags (one-time)
    document.querySelectorAll('[data-action="toggle-penalty-tag"]').forEach(tag => {
        tag.addEventListener('click', function() {
            const penaltyId = this.getAttribute('data-penalty-id');
            const penaltyValue = parseFloat(this.getAttribute('data-penalty-value'));
            const penaltyUnit = this.getAttribute('data-penalty-unit');
            togglePenaltyTag(penaltyId, penaltyValue, penaltyUnit);
        });
    });

    // Clear team button
    const clearBtn = document.querySelector('[data-action="clear-team"]');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearCurrentTeam);
    }
}

// Initialize scores from existing data
function initializeScores() {
    if (typeof window.existingScores !== 'undefined') {
        Object.keys(window.existingScores).forEach(teamId => {
            const score = window.existingScores[teamId];
            teamScores[teamId] = {
                baseScore: parseFloat(score.score_value) || 0,
                penaltyTotal: 0,
                finalScore: parseFloat(score.score_value) || 0,
                rank: 0,
                points: parseInt(score.points) || 0
            };
        });
    }

    // Initialize all teams
    if (typeof window.teamsData !== 'undefined') {
        window.teamsData.forEach(team => {
            if (!teamScores[team.id]) {
                teamScores[team.id] = {
                    baseScore: 0,
                    penaltyTotal: 0,
                    finalScore: 0,
                    rank: 0,
                    points: 0
                };
            }
            teamPenalties[team.id] = {};
        });
    }
}

// Switch to selected team
function switchTeam() {
    const selector = document.getElementById('team-selector');
    const teamId = selector.value;
    const scoringCard = document.getElementById('team-scoring-card');

    if (!teamId) {
        scoringCard.classList.add('display-none');
        currentTeamId = null;
        return;
    }

    currentTeamId = teamId;
    const team = window.teamsData.find(t => t.id == teamId);

    // Show scoring card
    scoringCard.classList.remove('display-none');

    // Update team header
    document.getElementById('selected-team-name').textContent = team.name;
    document.getElementById('team-color').style.backgroundColor = team.color;

    // Load team's current score
    const teamScore = teamScores[teamId];
    document.getElementById('score-input').value = teamScore.baseScore || '';

    // Reset timer when changing teams
    resetStopwatch();

    // Update rank and points display
    updateCurrentTeamDisplay();

    // Load penalties for this team
    loadTeamPenalties(teamId);

    // Scroll to scoring card
    document.getElementById('team-scoring-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Update current team's rank and points display
function updateCurrentTeamDisplay() {
    if (!currentTeamId) return;

    const teamScore = teamScores[currentTeamId];
    const rankBadge = document.getElementById('rank-badge');
    const rankDisplay = document.getElementById('rank-display');
    const pointsDisplay = document.getElementById('points-display');

    // Update rank with medal styling
    rankDisplay.textContent = teamScore.rank > 0 ? getOrdinalSuffix(teamScore.rank) : '-';

    // Add medal class
    rankBadge.className = 'rank-badge';
    if (teamScore.rank === 1) rankBadge.classList.add('rank-1');
    else if (teamScore.rank === 2) rankBadge.classList.add('rank-2');
    else if (teamScore.rank === 3) rankBadge.classList.add('rank-3');

    // Update points
    pointsDisplay.textContent = teamScore.points;
}

// Load penalties for current team
function loadTeamPenalties(teamId) {
    if (!teamPenalties[teamId]) teamPenalties[teamId] = {};

    const penalties = teamPenalties[teamId];

    // Reset all penalty displays
    if (window.penaltiesData) {
        window.penaltiesData.forEach(penalty => {
            const count = penalties[penalty.id] || 0;

            if (penalty.stackable) {
                // Update counter
                const counterElement = document.getElementById(`penalty-count-${penalty.id}`);
                if (counterElement) {
                    counterElement.textContent = count;
                }
            } else {
                // Update tag selection
                const tagElement = document.getElementById(`penalty-tag-${penalty.id}`);
                if (tagElement) {
                    if (count > 0) {
                        tagElement.classList.add('selected');
                        tagElement.querySelector('.penalty-tag-icon').textContent = '🔵';
                    } else {
                        tagElement.classList.remove('selected');
                        tagElement.querySelector('.penalty-tag-icon').textContent = '⚪';
                    }
                }
            }
        });
    }

    updatePenaltyTotals();
}

// Unified score input handlers
function incrementScore() {
    if (!currentTeamId) return;

    const input = document.getElementById('score-input');
    const currentValue = parseFloat(input.value) || 0;
    input.value = (currentValue + 1).toFixed(2);
    onScoreChange();
}

function decrementScore() {
    if (!currentTeamId) return;

    const input = document.getElementById('score-input');
    const currentValue = parseFloat(input.value) || 0;
    if (currentValue > 0) {
        input.value = (currentValue - 1).toFixed(2);
        onScoreChange();
    }
}

function onScoreChange() {
    if (!currentTeamId) return;

    const baseScore = parseFloat(document.getElementById('score-input').value) || 0;
    teamScores[currentTeamId].baseScore = baseScore;

    updatePenaltyTotals();
    calculateRankingsAndPoints();
    updateCurrentTeamDisplay();
    updateRankingsOverview();
    saveToHiddenInputs();
}

// Penalty handlers - Stackable
function incrementPenalty(penaltyId, value, unit) {
    if (!currentTeamId) return;

    if (!teamPenalties[currentTeamId][penaltyId]) {
        teamPenalties[currentTeamId][penaltyId] = 0;
    }

    teamPenalties[currentTeamId][penaltyId]++;

    const counterElement = document.getElementById(`penalty-count-${penaltyId}`);
    if (counterElement) {
        counterElement.textContent = teamPenalties[currentTeamId][penaltyId];
    }

    updatePenaltyTotals();
    calculateRankingsAndPoints();
    updateCurrentTeamDisplay();
    updateRankingsOverview();
    saveToHiddenInputs();
}

function decrementPenalty(penaltyId) {
    if (!currentTeamId) return;

    if (!teamPenalties[currentTeamId][penaltyId] || teamPenalties[currentTeamId][penaltyId] === 0) {
        return;
    }

    teamPenalties[currentTeamId][penaltyId]--;

    const counterElement = document.getElementById(`penalty-count-${penaltyId}`);
    if (counterElement) {
        counterElement.textContent = teamPenalties[currentTeamId][penaltyId];
    }

    updatePenaltyTotals();
    calculateRankingsAndPoints();
    updateCurrentTeamDisplay();
    updateRankingsOverview();
    saveToHiddenInputs();
}

// Penalty handlers - One-time (toggle)
function togglePenaltyTag(penaltyId, value, unit) {
    if (!currentTeamId) return;

    const tagElement = document.getElementById(`penalty-tag-${penaltyId}`);

    if (!teamPenalties[currentTeamId][penaltyId]) {
        teamPenalties[currentTeamId][penaltyId] = 0;
    }

    // Toggle
    if (teamPenalties[currentTeamId][penaltyId] === 0) {
        teamPenalties[currentTeamId][penaltyId] = 1;
        tagElement.classList.add('selected');
        tagElement.querySelector('.penalty-tag-icon').textContent = '🔵';
    } else {
        teamPenalties[currentTeamId][penaltyId] = 0;
        tagElement.classList.remove('selected');
        tagElement.querySelector('.penalty-tag-icon').textContent = '⚪';
    }

    updatePenaltyTotals();
    calculateRankingsAndPoints();
    updateCurrentTeamDisplay();
    updateRankingsOverview();
    saveToHiddenInputs();
}

// Update penalty totals display
function updatePenaltyTotals() {
    if (!currentTeamId) return;

    const baseScore = teamScores[currentTeamId].baseScore || 0;
    let penaltyTotal = 0;

    // Calculate total penalties
    if (window.penaltiesData && teamPenalties[currentTeamId]) {
        window.penaltiesData.forEach(penalty => {
            const count = teamPenalties[currentTeamId][penalty.id] || 0;
            penaltyTotal += count * penalty.value;
        });
    }

    const finalScore = baseScore + penaltyTotal;

    // Update displays (only if elements exist - they won't exist when there are no penalties)
    const baseScoreDisplay = document.getElementById('base-score-display');
    const penaltyTotalDisplay = document.getElementById('penalty-total-display');
    const finalScoreDisplay = document.getElementById('final-score-display');

    if (baseScoreDisplay) baseScoreDisplay.textContent = baseScore.toFixed(2);
    if (penaltyTotalDisplay) penaltyTotalDisplay.textContent = penaltyTotal.toFixed(2);
    if (finalScoreDisplay) finalScoreDisplay.textContent = finalScore.toFixed(2);

    // Update team score (CRITICAL: Always update this regardless of whether penalty elements exist)
    teamScores[currentTeamId].penaltyTotal = penaltyTotal;
    teamScores[currentTeamId].finalScore = finalScore;
}

// Calculate rankings and points for all teams
function calculateRankingsAndPoints() {
    const teamsWithScores = [];

    Object.keys(teamScores).forEach(teamId => {
        if (teamScores[teamId].finalScore > 0 || teamScores[teamId].baseScore > 0) {
            teamsWithScores.push({
                id: teamId,
                score: teamScores[teamId].finalScore
            });
        }
    });

    // Sort teams by score
    const scoringDirection = window.gameData.scoringDirection;
    if (scoringDirection === 'lower_better') {
        teamsWithScores.sort((a, b) => a.score - b.score);
    } else {
        teamsWithScores.sort((a, b) => b.score - a.score);
    }

    // Assign ranks and calculate points
    const pointScheme = window.gameData.pointScheme;
    const totalTeams = window.gameData.teamsCount;

    teamsWithScores.forEach((team, index) => {
        const rank = index + 1;
        const points = (totalTeams - rank + 1) * pointScheme;

        teamScores[team.id].rank = rank;
        teamScores[team.id].points = points;
    });

    // Reset ranks for teams without scores
    Object.keys(teamScores).forEach(teamId => {
        const hasScore = teamsWithScores.some(t => t.id == teamId);
        if (!hasScore) {
            teamScores[teamId].rank = 0;
            teamScores[teamId].points = 0;
        }
    });
}

// Update rankings overview display
function updateRankingsOverview() {
    const rankingsList = document.getElementById('rankings-list');
    if (!rankingsList) return;

    // Get teams with scores
    const teamsWithScores = [];

    Object.keys(teamScores).forEach(teamId => {
        const team = window.teamsData.find(t => t.id == teamId);
        if (team && teamScores[teamId].rank > 0) {
            teamsWithScores.push({
                id: teamId,
                name: team.name,
                color: team.color,
                rank: teamScores[teamId].rank,
                score: teamScores[teamId].finalScore,
                points: teamScores[teamId].points
            });
        }
    });

    // Sort by rank
    teamsWithScores.sort((a, b) => a.rank - b.rank);

    // Build HTML
    let html = '';
    if (teamsWithScores.length === 0) {
        html = '<p class="no-scores">No scores entered yet</p>';
    } else {
        teamsWithScores.forEach(team => {
            const medalClass = team.rank <= 3 ? `rank-${team.rank}` : '';
            html += `
                <div class="ranking-item ${medalClass}">
                    <div class="ranking-position">
                        <span class="ranking-number">${team.rank}</span>
                        ${team.rank === 1 ? '<span class="medal">🥇</span>' : ''}
                        ${team.rank === 2 ? '<span class="medal">🥈</span>' : ''}
                        ${team.rank === 3 ? '<span class="medal">🥉</span>' : ''}
                    </div>
                    <div class="ranking-team">
                        <div class="ranking-color" style="background-color: ${team.color}"></div>
                        <span class="ranking-name">${team.name}</span>
                    </div>
                    <div class="ranking-stats">
                        <span class="ranking-score">${team.score.toFixed(2)}</span>
                        <span class="ranking-points">${team.points} pts</span>
                    </div>
                </div>
            `;
        });
    }

    rankingsList.innerHTML = html;
}

// Save to hidden inputs for form submission
function saveToHiddenInputs() {
    Object.keys(teamScores).forEach(teamId => {
        const scoreInput = document.getElementById(`score-${teamId}`);
        const pointsInput = document.getElementById(`points-input-${teamId}`);
        const penaltiesInput = document.getElementById(`penalties-${teamId}`);

        if (scoreInput) {
            scoreInput.value = teamScores[teamId].finalScore || '';
        }

        if (pointsInput) {
            pointsInput.value = teamScores[teamId].points || 0;
        }

        if (penaltiesInput && teamPenalties[teamId]) {
            penaltiesInput.value = JSON.stringify(teamPenalties[teamId]);
        }
    });
}

// Clear current team
function clearCurrentTeam() {
    if (!currentTeamId) return;

    if (!confirm('Are you sure you want to clear this team\'s score and penalties?')) {
        return;
    }

    // Reset score
    document.getElementById('score-input').value = '';
    teamScores[currentTeamId].baseScore = 0;
    teamScores[currentTeamId].penaltyTotal = 0;
    teamScores[currentTeamId].finalScore = 0;

    // Reset penalties
    teamPenalties[currentTeamId] = {};

    // Reload display
    loadTeamPenalties(currentTeamId);
    updatePenaltyTotals();
    calculateRankingsAndPoints();
    updateCurrentTeamDisplay();
    updateRankingsOverview();
    saveToHiddenInputs();
}

// Stopwatch functions (for time-based games)
function startStopwatch() {
    if (!currentTeamId) {
        alert('Please select a team first');
        return;
    }

    globalStartTime = Date.now() - globalElapsed;

    if (globalTimer) {
        clearInterval(globalTimer);
    }

    globalTimer = setInterval(() => {
        globalElapsed = Date.now() - globalStartTime;
        document.getElementById('timer-display').textContent = formatTimeWithMillis(globalElapsed);
    }, 10); // Update every 10ms for smooth milliseconds
}

function stopStopwatch() {
    if (globalTimer) {
        clearInterval(globalTimer);
        globalTimer = null;

        if (currentTeamId) {
            const seconds = (globalElapsed / 1000).toFixed(3);
            document.getElementById('score-input').value = seconds;
            onScoreChange(); // This auto-saves the score to the hidden inputs

            // Show a brief success message
            const timerDisplay = document.getElementById('timer-display');
            const originalColor = timerDisplay.style.color;
            timerDisplay.style.color = '#22c55e'; // Green color
            setTimeout(() => {
                timerDisplay.style.color = originalColor;
            }, 1000);
        }
    }
}

function resetStopwatch() {
    if (globalTimer) {
        clearInterval(globalTimer);
        globalTimer = null;
    }
    globalElapsed = 0;
    const timerDisplay = document.getElementById('timer-display');
    if (timerDisplay) {
        timerDisplay.textContent = '00:00.000';
    }
}

function formatTime(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function formatTimeWithMillis(milliseconds) {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    const millis = Math.floor((milliseconds % 1000));

    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${String(millis).padStart(3, '0')}`;
}

// Helper function for ordinal suffixes
function getOrdinalSuffix(num) {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return num + "st";
    if (j === 2 && k !== 12) return num + "nd";
    if (j === 3 && k !== 13) return num + "rd";
    return num + "th";
}
