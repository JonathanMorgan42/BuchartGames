document.addEventListener('DOMContentLoaded', function() {
    console.log('Scores.js loaded');
    updatePointDistributionPreview();

    const startButton = document.getElementById('startStopwatch');
    if (startButton) {
        startButton.addEventListener('click', startStopwatch);
        document.getElementById('stopStopwatch').addEventListener('click', stopStopwatch);
        document.getElementById('resetStopwatch').addEventListener('click', resetStopwatch);
        document.getElementById('recordTime').addEventListener('click', recordCurrentTime);
    }

    const saveButton = document.getElementById('saveScoresBtn');
    if (saveButton) {
        document.getElementById('scoreForm')?.addEventListener('submit', function(e) {
            e.preventDefault();
            saveScores();
        });
    }

    // Calculate rankings and points on page load
    console.log('Calling updateRankingsAndPoints on load');
    updateRankingsAndPoints();
});

function updatePointDistributionPreview() {
    const container = document.getElementById('pointDistributionPreview');
    if (!container) return;

    const increment = parseInt(document.getElementById('pointIncrement')?.value) || 1;
    const teamCount = parseInt(document.getElementById('participatingTeamsCount')?.textContent) || 0;

    let html = '<div class="point-table">';
    html += '<div class="point-row header"><div class="point-cell">Place</div><div class="point-cell">Points</div></div>';

    for (let i = 0; i < teamCount; i++) {
        const place = i + 1;
        const points = (teamCount - i) * increment;
        html += `<div class="point-row ${place <= 3 ? 'highlight-' + place : ''}">`;
        html += `<div class="point-cell">${getOrdinalSuffix(place)}</div>`;
        html += `<div class="point-cell">${points}</div></div>`;
    }

    html += '</div>';
    container.innerHTML = html;
}

let stopwatchInterval, stopwatchTime = 0, stopwatchRunning = false;
const stopwatchDisplay = document.getElementById('stopwatchDisplay');

function startStopwatch() {
    if (stopwatchRunning) return;
    stopwatchRunning = true;
    clearInterval(stopwatchInterval);
    stopwatchInterval = setInterval(() => {
        stopwatchTime += 10;
        updateStopwatchDisplay();
    }, 10);
}

function stopStopwatch() {
    stopwatchRunning = false;
    clearInterval(stopwatchInterval);
}

function resetStopwatch() {
    stopwatchRunning = false;
    clearInterval(stopwatchInterval);
    stopwatchTime = 0;
    updateStopwatchDisplay();
}

function updateStopwatchDisplay() {
    if (!stopwatchDisplay) return;
    const minutes = Math.floor(stopwatchTime / 60000);
    const seconds = Math.floor((stopwatchTime % 60000) / 1000);
    const milliseconds = Math.floor(stopwatchTime % 1000);
    stopwatchDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(milliseconds).padStart(3, '0')}`;
}

function recordCurrentTime() {
    const teamSelect = document.getElementById('teamSelect');
    if (!teamSelect?.value) {
        alert('Please select a team');
        return;
    }
    const scoreInput = document.getElementById(`score-${teamSelect.value}`);
    if (scoreInput) {
        scoreInput.value = (stopwatchTime / 1000).toFixed(2);
        updateRankingsAndPoints();
    }
}

function incrementCounter(teamId) {
    const counter = document.getElementById(`counter-${teamId}`);
    const score = document.getElementById(`score-${teamId}`);
    if (counter && score) {
        const val = parseInt(counter.textContent) + 1;
        counter.textContent = val;
        score.value = val;
        updateRankingsAndPoints();
    }
}

function decrementCounter(teamId) {
    const counter = document.getElementById(`counter-${teamId}`);
    const score = document.getElementById(`score-${teamId}`);
    if (counter && score) {
        const val = Math.max(0, parseInt(counter.textContent) - 1);
        counter.textContent = val;
        score.value = val;
        updateRankingsAndPoints();
    }
}

function clearTeamScore(teamId) {
    const score = document.getElementById(`score-${teamId}`);
    const counter = document.getElementById(`counter-${teamId}`);
    if (score) score.value = '';
    if (counter) counter.textContent = '0';
    updateRankingsAndPoints();
}

function calculatePoints(rank, increment, totalTeams) {
    return Math.max((totalTeams - rank) * increment, 0);
}

function updateRankingsAndPoints() {
    console.log('updateRankingsAndPoints called');
    const pointIncrement = parseInt(document.getElementById('pointIncrement')?.value) || 1;
    const lowerIsBetter = document.getElementById('lowerIsBetter')?.value === 'true';
    console.log(`Point increment: ${pointIncrement}, Lower is better: ${lowerIsBetter}`);

    const teamScores = [];
    document.querySelectorAll('.team-score').forEach(el => {
        const value = parseFloat(el.value);
        if (!isNaN(value) && el.value !== '') {
            teamScores.push({ teamId: el.dataset.teamId, score: value });
            console.log(`Team ${el.dataset.teamId}: score = ${value}`);
        }
    });

    console.log(`Found ${teamScores.length} teams with scores`);
    teamScores.sort((a, b) => lowerIsBetter ? a.score - b.score : b.score - a.score);

    teamScores.forEach((team, index) => {
        const points = calculatePoints(index, pointIncrement, teamScores.length);
        const rank = index + 1;

        console.log(`Team ${team.teamId}: rank = ${rank}, points = ${points}`);
        document.getElementById(`rank-${team.teamId}`).textContent = rank;
        document.getElementById(`points-${team.teamId}`).textContent = points;
        document.getElementById(`points-input-${team.teamId}`).value = points;
    });

    document.querySelectorAll('.team-score').forEach(el => {
        if (!el.value || el.value === '') {
            const teamId = el.dataset.teamId;
            document.getElementById(`rank-${teamId}`).textContent = '-';
            document.getElementById(`points-${teamId}`).textContent = '0';
            document.getElementById(`points-input-${teamId}`).value = '0';
        }
    });
    console.log('updateRankingsAndPoints completed');
}

function saveScores() {
    const gameId = document.getElementById('game_id').value;
    const markCompleted = document.getElementById('markGameCompleted').checked;
    const notes = document.getElementById('game_notes')?.value;
    const csrf_token = document.querySelector('input[name="csrf_token"]').value;

    const scoresData = { scores: {}, isCompleted: markCompleted, notes: notes };

    document.querySelectorAll('.team-score').forEach(input => {
        const teamId = input.dataset.teamId;
        const score = input.value ? parseFloat(input.value) : null;
        const points = document.getElementById(`points-input-${teamId}`).value;
        const notes = document.getElementById(`notes-${teamId}`)?.value;

        if (score !== null) {
            scoresData.scores[teamId] = {
                score: score,
                points: parseInt(points),
                score_value: score,
                notes: notes
            };
        }
    });

    fetch(`/admin/scores/save/${gameId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify(scoresData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            sessionStorage.setItem('scoresSaved', 'true');
            window.location.href = '/games';
        } else {
            alert('Error saving scores: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error saving scores: ' + error.message);
    });
}

function getOrdinalSuffix(num) {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return num + "st";
    if (j === 2 && k !== 12) return num + "nd";
    if (j === 3 && k !== 13) return num + "rd";
    return num + "th";
}

function prepareFormSubmission() {
    console.log('prepareFormSubmission called - recalculating points before submit');
    // Recalculate all rankings and points before submitting
    updateRankingsAndPoints();

    // Log what we're about to submit
    console.log('Form data being submitted:');
    document.querySelectorAll('.team-score').forEach(el => {
        const teamId = el.dataset.teamId;
        const score = el.value;
        const points = document.getElementById(`points-input-${teamId}`).value;
        console.log(`Team ${teamId}: score=${score}, points=${points}`);
    });

    // Now submit the form manually
    console.log('Submitting form...');
    document.getElementById('liveScoreForm').submit();
}
