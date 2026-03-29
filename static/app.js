/* Star Explorers - Frontend Logic */

const $ = (sel) => document.querySelector(sel);
const content = () => $('#content');
const controlsBar = () => $('#controls-bar');

let state = null;
let pollTimer = null;

// --- Audio (Web Audio API synthesized sounds) ---

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playCorrectSound() {
    const now = audioCtx.currentTime;
    // Ascending C-E-G chime
    [261.63, 329.63, 392.00].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.15, now + i * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.12 + 0.4);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + i * 0.12);
        osc.stop(now + i * 0.12 + 0.4);
    });
}

function playWrongSound() {
    const now = audioCtx.currentTime;
    // Gentle descending two-note
    [300, 240].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.1, now + i * 0.15);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.15 + 0.3);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + i * 0.15);
        osc.stop(now + i * 0.15 + 0.3);
    });
}

function playLaunchSound() {
    const now = audioCtx.currentTime;
    // Rising sine sweep + noise whoosh
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(200, now);
    osc.frequency.exponentialRampToValueAtTime(800, now + 1.2);
    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 1.5);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 1.5);
}

function playBossIntroSound() {
    const now = audioCtx.currentTime;
    // Low rumble + dramatic hit
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.value = 60;
    gain.gain.setValueAtTime(0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.8);
    // Hit
    const hit = audioCtx.createOscillator();
    const hitGain = audioCtx.createGain();
    hit.type = 'sine';
    hit.frequency.value = 120;
    hitGain.gain.setValueAtTime(0.2, now + 0.6);
    hitGain.gain.exponentialRampToValueAtTime(0.001, now + 1.0);
    hit.connect(hitGain);
    hitGain.connect(audioCtx.destination);
    hit.start(now + 0.6);
    hit.stop(now + 1.0);
}

function playVictoryFanfare() {
    const now = audioCtx.currentTime;
    // Ascending C-E-G-C5 with triangle waves
    [261.63, 329.63, 392.00, 523.25].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.15, now + i * 0.2);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.2 + 0.5);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + i * 0.2);
        osc.stop(now + i * 0.2 + 0.5);
    });
}

function playStreakSound() {
    const now = audioCtx.currentTime;
    // Fast ascending arpeggio
    [261.63, 329.63, 392.00, 523.25, 659.25].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.12, now + i * 0.06);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.25);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + i * 0.06);
        osc.stop(now + i * 0.06 + 0.25);
    });
}

function playLightningSound() {
    const now = audioCtx.currentTime;
    // Sharp electrical zap
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(800, now);
    osc.frequency.exponentialRampToValueAtTime(200, now + 0.08);
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.12);
}

function playTransitionSound() {
    const now = audioCtx.currentTime;
    // Soft filtered whoosh
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(400, now);
    osc.frequency.exponentialRampToValueAtTime(600, now + 0.15);
    gain.gain.setValueAtTime(0.04, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.2);
}

function playCelebrationSound() {
    const now = audioCtx.currentTime;
    // Extended fanfare with vibrato sustain
    [261.63, 329.63, 392.00, 523.25].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.value = freq;
        const dur = i === 3 ? 1.2 : 0.3;
        gain.gain.setValueAtTime(0.15, now + i * 0.18);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.18 + dur);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + i * 0.18);
        osc.stop(now + i * 0.18 + dur);
    });
}

function playAchievementSound() {
    const now = audioCtx.currentTime;
    // Magical sustained chime with harmonic
    [523.25, 1046.50].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(i === 0 ? 0.12 : 0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 1.5);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 1.5);
    });
}

// --- Starfield ---

function createStarfield() {
    const sf = $('#starfield');
    sf.innerHTML = '';

    // Nebula patches — large blurred color blobs
    const nebulaColors = [
        'radial-gradient(circle, rgba(199,125,255,0.4), transparent 70%)',
        'radial-gradient(circle, rgba(123,47,247,0.3), transparent 70%)',
        'radial-gradient(circle, rgba(160,196,255,0.3), transparent 70%)',
    ];
    for (let i = 0; i < 3; i++) {
        const patch = document.createElement('div');
        patch.className = 'nebula-patch';
        const size = 300 + Math.random() * 400;
        patch.style.width = size + 'px';
        patch.style.height = size + 'px';
        patch.style.left = (10 + Math.random() * 80) + '%';
        patch.style.top = (10 + Math.random() * 80) + '%';
        patch.style.background = nebulaColors[i];
        sf.appendChild(patch);
    }

    // Stars — varied colors and sizes
    const starColors = [
        { color: '#ffffff', weight: 55 },
        { color: '#a0c4ff', weight: 18 },   // star-blue
        { color: '#c77dff', weight: 12 },   // nebula purple
        { color: '#fff5e0', weight: 8 },    // warm white
        { color: '#72efdd', weight: 7 },    // cosmic teal
    ];

    function pickStarColor() {
        const total = starColors.reduce((s, c) => s + c.weight, 0);
        let r = Math.random() * total;
        for (const sc of starColors) {
            r -= sc.weight;
            if (r <= 0) return sc.color;
        }
        return '#ffffff';
    }

    const count = 120;
    for (let i = 0; i < count; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        const size = Math.random() * 3.5 + 0.8;
        const color = pickStarColor();
        star.style.width = size + 'px';
        star.style.height = size + 'px';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.background = color;
        if (size > 2.5) {
            star.style.boxShadow = `0 0 ${size * 2}px ${color}`;
        }
        star.style.setProperty('--duration', (Math.random() * 3 + 2) + 's');
        star.style.setProperty('--max-opacity', Math.random() * 0.6 + 0.4);
        star.style.animationDelay = Math.random() * 5 + 's';
        sf.appendChild(star);
    }
}

// --- Shooting Stars ---

function spawnShootingStar() {
    const sf = $('#starfield');
    const star = document.createElement('div');
    star.className = 'shooting-star';
    star.style.left = Math.random() * 60 + '%';
    star.style.top = Math.random() * 50 + '%';

    const angle = 20 + Math.random() * 30;
    const distance = 250 + Math.random() * 200;
    const dx = Math.cos(angle * Math.PI / 180) * distance;
    const dy = Math.sin(angle * Math.PI / 180) * distance;
    const duration = 600 + Math.random() * 400;

    sf.appendChild(star);
    star.animate([
        { transform: 'translateX(0) translateY(0)', opacity: 1 },
        { transform: `translateX(${dx}px) translateY(${dy}px)`, opacity: 0 },
    ], { duration, easing: 'ease-out' });
    setTimeout(() => star.remove(), duration);
}

function startShootingStars() {
    function scheduleNext() {
        const delay = 12000 + Math.random() * 20000; // 12-32 seconds
        setTimeout(() => {
            spawnShootingStar();
            scheduleNext();
        }, delay);
    }
    scheduleNext();
}

// --- Particle Effects ---

function spawnStarBurst(x, y) {
    const container = $('#particles');
    const emojis = ['⭐', '✨', '🌟', '💫'];
    for (let i = 0; i < 12; i++) {
        const p = document.createElement('div');
        p.className = 'star-particle';
        p.textContent = emojis[i % emojis.length];
        const angle = (i / 12) * Math.PI * 2;
        const dist = 80 + Math.random() * 60;
        p.style.left = x + 'px';
        p.style.top = y + 'px';
        p.style.setProperty('--tx', Math.cos(angle) * dist + 'px');
        p.style.setProperty('--ty', Math.sin(angle) * dist + 'px');
        p.style.animation = 'none';
        p.style.fontSize = (18 + Math.random() * 16) + 'px';

        const keyframes = [
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            {
                transform: `translate(${Math.cos(angle) * dist}px, ${Math.sin(angle) * dist}px) scale(0.3)`,
                opacity: 0,
            },
        ];
        container.appendChild(p);
        p.animate(keyframes, { duration: 800 + Math.random() * 400, easing: 'ease-out' });
        setTimeout(() => p.remove(), 1200);
    }
}

function showPointsPopup(points) {
    const popup = document.createElement('div');
    popup.className = 'points-popup';
    popup.textContent = `+${points}`;
    popup.style.left = '50%';
    popup.style.top = '40%';
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 1300);
}

function showCascade() {
    const container = $('#particles');
    const emojis = ['⭐', '🌟', '✨', '🏆', '💫'];
    for (let i = 0; i < 20; i++) {
        setTimeout(() => {
            const p = document.createElement('div');
            p.className = 'star-particle';
            p.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            p.style.left = Math.random() * window.innerWidth + 'px';
            p.style.top = '-40px';
            p.style.fontSize = (20 + Math.random() * 20) + 'px';
            container.appendChild(p);
            setTimeout(() => p.remove(), 2200);
        }, i * 100);
    }
}

// --- Celebration Effects ---

function showScreenFlash(color) {
    const flash = document.createElement('div');
    flash.className = 'screen-flash';
    flash.style.background = color;
    document.body.appendChild(flash);
    flash.animate([
        { opacity: 0.3 },
        { opacity: 0 },
    ], { duration: 250, easing: 'ease-out' });
    setTimeout(() => flash.remove(), 250);
}

function showCometTrail() {
    const container = $('#particles');
    const comet = document.createElement('div');
    comet.className = 'comet-trail';
    comet.style.left = '-20px';
    comet.style.top = (10 + Math.random() * 40) + '%';
    container.appendChild(comet);

    comet.animate([
        { transform: 'translateX(0)', opacity: 1 },
        { transform: `translateX(${window.innerWidth + 100}px)`, opacity: 0 },
    ], { duration: 1200, easing: 'ease-in' });

    // Trail particles
    for (let i = 0; i < 6; i++) {
        setTimeout(() => {
            const trail = document.createElement('div');
            trail.className = 'comet-trail';
            trail.style.left = (i * 15) + '%';
            trail.style.top = comet.style.top;
            trail.style.width = '4px';
            trail.style.height = '4px';
            trail.style.opacity = '0.5';
            container.appendChild(trail);
            trail.animate([
                { opacity: 0.5, transform: 'scale(1)' },
                { opacity: 0, transform: 'scale(0.2)' },
            ], { duration: 400, easing: 'ease-out' });
            setTimeout(() => trail.remove(), 400);
        }, i * 100);
    }
    setTimeout(() => comet.remove(), 1300);
}

function showRocketLaunch() {
    const container = $('#particles');
    const rocket = document.createElement('div');
    rocket.className = 'star-particle';
    rocket.textContent = '🚀';
    rocket.style.left = '50%';
    rocket.style.top = '90%';
    rocket.style.fontSize = '48px';
    rocket.style.animation = 'none';
    container.appendChild(rocket);

    rocket.animate([
        { transform: 'translateY(0) scale(1) rotate(0deg)', opacity: 1 },
        { transform: 'translateY(-100vh) scale(0.3) rotate(-15deg)', opacity: 0 },
    ], { duration: 1500, easing: 'ease-in' });

    // Exhaust particles
    for (let i = 0; i < 15; i++) {
        setTimeout(() => {
            const exhaust = document.createElement('div');
            exhaust.className = 'star-particle';
            exhaust.textContent = ['🔥', '💨', '✨'][i % 3];
            exhaust.style.left = (48 + Math.random() * 4) + '%';
            exhaust.style.top = (85 - i * 4) + '%';
            exhaust.style.fontSize = '20px';
            exhaust.style.animation = 'none';
            container.appendChild(exhaust);
            exhaust.animate([
                { opacity: 1, transform: 'scale(1)' },
                { opacity: 0, transform: `scale(0.3) translateY(${50 + Math.random() * 50}px)` },
            ], { duration: 600, easing: 'ease-out' });
            setTimeout(() => exhaust.remove(), 600);
        }, i * 80);
    }
    setTimeout(() => rocket.remove(), 1500);
}

function showFireworks(count) {
    for (let i = 0; i < count; i++) {
        setTimeout(() => {
            const x = 100 + Math.random() * (window.innerWidth - 200);
            const y = 50 + Math.random() * (window.innerHeight * 0.5);
            spawnStarBurst(x, y);
        }, i * 350);
    }
}

function showScreenShake() {
    const main = $('main');
    main.classList.add('screen-shake');
    setTimeout(() => main.classList.remove('screen-shake'), 500);
}

function showExpandingRing() {
    const ring = document.createElement('div');
    ring.style.cssText = `
        position: fixed; top: 50%; left: 50%;
        width: 80px; height: 80px;
        border: 3px solid var(--gold);
        border-radius: 50%;
        pointer-events: none;
        z-index: 200;
        transform: translate(-50%, -50%) scale(0);
    `;
    document.body.appendChild(ring);
    ring.animate([
        { transform: 'translate(-50%, -50%) scale(0)', opacity: 0.8, borderWidth: '3px' },
        { transform: 'translate(-50%, -50%) scale(4)', opacity: 0, borderWidth: '1px' },
    ], { duration: 800, easing: 'ease-out' });
    setTimeout(() => ring.remove(), 800);
}

function animateScoreCounter(element, from, to, duration = 1500) {
    const start = performance.now();
    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        element.textContent = Math.round(from + (to - from) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// --- Screen Transitions ---

let lastScreen = null;

function transitionTo(renderFn, transitionClass = 'fade-in') {
    const main = content();
    main.style.animation = 'none';
    main.offsetHeight; // force reflow
    main.style.animation = `${transitionClass} 0.35s ease`;
    playTransitionSound();
    renderFn();
}

// --- Scene Image Helper ---

function imageHtml(src, alt) {
    if (!src) return '';
    return `<img src="${src}" alt="${alt || ''}" class="scene-image" onerror="this.style.display='none'" />`;
}

// --- API Calls ---

async function apiGet(url) {
    const res = await fetch(url);
    return res.json();
}

async function apiPost(url, body = {}) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return res.json();
}

async function fetchState() {
    state = await apiGet('/api/state');
    renderScreen();
}

async function doAction(action) {
    const result = await apiPost('/api/action', { action });

    if (result.correct === true) {
        playCorrectSound();
        showScreenFlash('rgba(74, 222, 128, 0.25)');
        spawnStarBurst(window.innerWidth / 2, window.innerHeight / 3);
        if (result.points) showPointsPopup(result.points);

        // Streak celebration
        if (result.streak >= 3) {
            setTimeout(() => {
                playStreakSound();
                showCometTrail();
            }, 300);
        }

        if (result.achievement) {
            playAchievementSound();
            showExpandingRing();
            showAchievement(result.achievement);
        }
    } else if (result.correct === false) {
        playWrongSound();
        showScreenFlash('rgba(248, 113, 113, 0.2)');
    }

    await fetchState();
}

async function startSession() {
    playLaunchSound();
    await apiPost('/api/session/start');
    await doAction('continue');
}

async function endSession() {
    const result = await apiPost('/api/session/end');
    state = { phase: 'no_session' };
    renderScreen();
}

// --- Achievement Overlay ---

function showAchievement(ach) {
    const overlay = $('#achievement-overlay');
    overlay.innerHTML = `
        <div class="achievement-content">
            <div class="achievement-star">⭐</div>
            <div class="achievement-name">${ach.name}</div>
            <div class="achievement-desc">${ach.description}</div>
        </div>
    `;
    overlay.classList.remove('hidden');
    showCascade();
    setTimeout(() => overlay.classList.add('hidden'), 3000);
}

// --- Status Bar ---

function updateStatusBar() {
    if (!state || state.phase === 'no_session') {
        $('#session-info').textContent = '';
        $('#score-display').textContent = '';
        $('#timer-display').textContent = '';
        return;
    }
    $('#session-info').textContent = `Session #${state.session_number} | ${state.arc_name || ''}`;
    $('#score-display').textContent = `${state.team_score} pts`;
    $('#timer-display').textContent = `${state.elapsed_minutes || 0} min`;
}

// --- Screen Renderers ---

function renderScreen() {
    updateStatusBar();

    if (!state || state.phase === 'no_session') {
        renderNoSession();
        return;
    }

    const screen = state.screen;
    const renderers = {
        'pre_session': renderPreSession,
        'question': renderQuestion,
        'story': renderStory,
        'break': renderBreak,
        'boss_intro': renderBossIntro,
        'boss_victory': renderBossVictory,
        'lightning_result': renderLightningResult,
        'score_report': renderScoreReport,
        'power_levels': renderPowerLevels,
        'cliffhanger': renderCliffhanger,
        'complete': renderComplete,
    };

    const renderer = renderers[screen];
    const transitionMap = {
        'story': 'slide-in-right',
        'boss_intro': 'zoom-in',
        'break': 'bounce-in',
    };
    const transition = transitionMap[screen] || 'fade-in';

    if (renderer) {
        if (screen !== lastScreen) {
            transitionTo(() => renderer(), transition);
        } else {
            renderer();
        }
    } else {
        transitionTo(() => renderStory(), 'slide-in-right');
    }
    lastScreen = screen;
}

function renderNoSession() {
    content().innerHTML = `
        <div class="no-session">
            ${imageHtml('/static/images/title_hero.png', 'Star Explorers')}
            <div class="title">STAR EXPLORERS</div>
            <div class="subtitle">Mission Control Ready</div>
        </div>
    `;
    controlsBar().innerHTML = `
        <button class="ctrl-btn launch" onclick="startSession()">
            🚀 Launch Mission
        </button>
    `;
}

function renderPreSession() {
    const children = state.children || {};
    const date = state.date || '';

    let childCards = '';
    for (const [name, c] of Object.entries(children)) {
        const cssClass = name.toLowerCase();
        const emoji = name === 'Jesse' ? '🔵' : '🩷';
        const topics = state.topics?.[name] || {};
        let topicBars = '';
        for (const [tid, t] of Object.entries(topics)) {
            topicBars += `
                <div class="progress-bar-container">
                    <div class="progress-bar">
                        <div class="progress-bar-fill ${cssClass === 'jesse' ? 'blue' : 'pink'}"
                             style="width: ${t.mastery_pct}%"></div>
                    </div>
                    <div class="progress-label">${t.subject}/${tid} - ${t.mastery_pct}% (${t.items_count} items)</div>
                </div>
            `;
        }
        childCards += `
            <div class="child-card ${cssClass}">
                <div class="child-avatar">${emoji}</div>
                <div class="child-info">
                    <h3>${c.character_name}</h3>
                    <div class="subtitle">Age ${c.age} | ${c.sessions_completed} sessions</div>
                    <div class="power">Level ${c.power_level}: ${c.power_level_name}</div>
                    ${topicBars}
                </div>
            </div>
        `;
    }

    const team = state.team || {};

    content().innerHTML = `
        <div class="dashboard-title">MISSION CONTROL</div>
        <div class="dashboard-subtitle">Session #${state.session_number} | ${date}</div>
        ${childCards}
        <div class="card" style="text-align: center;">
            ${imageHtml(state.image, state.arc_name)}
            <div style="color: var(--purple); font-size: 16px;">${state.arc_name}</div>
            <div style="color: var(--dim); font-size: 14px; margin-top: 4px;">
                Total Adventure Points: ${team.total_adventure_points || 0} |
                Achievements: ${(team.achievements || []).length}
            </div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn launch" onclick="doAction('continue')">
            🚀 Launch Mission
        </button>
    `;
}

function renderQuestion() {
    const q = state.question;
    const child = state.current_child;
    const cssClass = child?.toLowerCase() || '';
    const label = state.label || '';
    const isLightning = state.is_lightning;
    const isBoss = state.is_boss;
    const isTreasure = state.is_treasure;

    let borderClass = '';
    if (isBoss) borderClass = 'boss-border';
    else if (isTreasure) borderClass = 'gold-border';

    let headerExtra = '';
    if (isLightning) {
        headerExtra = `
            <div class="lightning-counter">${state.lightning_index}/${state.lightning_total}</div>
            <div class="lightning-label">${state.lightning_correct} correct so far</div>
        `;
    }
    if (state.remaining && !isLightning) {
        headerExtra += `<div style="text-align:center; color: var(--dim); font-size: 13px; margin-bottom: 8px;">${state.remaining} remaining</div>`;
    }

    content().innerHTML = `
        <div class="phase-label">${label}</div>
        ${headerExtra}
        <div class="child-turn ${cssClass}">${child}'s Turn</div>
        <div class="card ${borderClass}">
            <div class="read-aloud">${q.read_aloud}</div>
            <div class="answer-line">Answer: <strong>${q.correct_answers.join(' / ')}</strong></div>
            <div class="response-scripts">
                <div><span class="label if-correct">IF CORRECT:</span> ${q.correct_response}</div>
                ${q.metacognitive_prompt ? `<div style="color: var(--cyan); margin-left: 20px;">${q.metacognitive_prompt}</div>` : ''}
                <div><span class="label if-wrong">IF WRONG:</span> ${q.incorrect_response}</div>
                ${q.mnemonic ? `<div style="color: var(--purple); margin-left: 20px;">MNEMONIC: ${q.mnemonic}</div>` : ''}
                <div><span class="label if-stuck">IF STUCK:</span> ${q.hint}</div>
            </div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn correct" onclick="doAction('correct')">
            Correct <span class="ctrl-shortcut">Enter</span>
        </button>
        <button class="ctrl-btn wrong" onclick="doAction('wrong')">
            Wrong <span class="ctrl-shortcut">N</span>
        </button>
        <button class="ctrl-btn hint" onclick="doAction('hint')">
            Hint <span class="ctrl-shortcut">H</span>
        </button>
        <button class="ctrl-btn skip" onclick="doAction('skip')">
            Skip <span class="ctrl-shortcut">S</span>
        </button>
    `;
}

function renderStory() {
    const title = state.title || 'STORY';
    const text = state.text || '';
    const style = state.style === 'adventure' ? 'gold-border' : 'purple-border';

    content().innerHTML = `
        <div class="card ${style}">
            <div class="story-panel">
                ${imageHtml(state.image, title)}
                <div class="story-title">${title}</div>
                <div class="story-text">${text}</div>
            </div>
        </div>
    `;

    let btns = `<button class="ctrl-btn continue" onclick="doAction('continue')">Continue <span class="ctrl-shortcut">Enter</span></button>`;
    if (state.phase !== 'complete') {
        btns += `<button class="ctrl-btn end" onclick="endSession()">End Session</button>`;
    }
    controlsBar().innerHTML = btns;
}

function renderBreak() {
    const isMovement = state.break_type === 'movement';
    const emoji = isMovement ? '🏃' : '🤪';

    content().innerHTML = `
        <div class="card">
            <div class="break-emoji">${emoji}</div>
            <div class="break-title">${state.title}</div>
            <div class="break-text">${state.text}</div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('continue')">
            Done! Continue <span class="ctrl-shortcut">Enter</span>
        </button>
    `;
}

function renderBossIntro() {
    playBossIntroSound();
    content().innerHTML = `
        <div class="card boss-border">
            <div class="story-panel">
                ${imageHtml(state.image, 'Boss Challenge')}
                <div class="break-emoji">👹</div>
                <div class="story-title">${state.title}</div>
                <div class="story-text">${state.text}</div>
            </div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('continue')" style="border-color: var(--red); color: var(--red);">
            Face the Challenge! <span class="ctrl-shortcut">Enter</span>
        </button>
    `;
}

function renderBossVictory() {
    playVictoryFanfare();
    showScreenShake();
    showRocketLaunch();
    setTimeout(() => showCascade(), 500);
    content().innerHTML = `
        <div class="card green-border">
            <div class="story-panel">
                ${imageHtml(state.image, 'Victory')}
                <div class="break-emoji">🏆</div>
                <div class="story-title">${state.title}</div>
                <div class="story-text">${state.text}</div>
            </div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('boss_next')">
            Continue <span class="ctrl-shortcut">Enter</span>
        </button>
    `;
}

function renderLightningResult() {
    const record = state.new_record;
    if (record) {
        playLightningSound();
        showFireworks(5);
        showScreenFlash('rgba(255, 215, 0, 0.3)');
    }

    content().innerHTML = `
        <div class="card ${record ? 'gold-border' : ''}">
            <div class="lightning-counter">${state.lightning_correct}/${state.lightning_total}</div>
            <div style="text-align: center; font-size: 24px; margin-bottom: 12px;">
                ${record
                    ? `<span style="color: var(--gold);">NEW RECORD! 🏆</span>`
                    : `<span style="color: var(--dim);">Record: ${state.record}</span>`
                }
            </div>
            <div class="break-title">Lightning Round Complete!</div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('continue')">
            Continue <span class="ctrl-shortcut">Enter</span>
        </button>
    `;
}

function renderScoreReport() {
    const stats = state.stats || {};
    playCelebrationSound();
    showCascade();

    let childStats = '';
    for (const [name, s] of Object.entries(stats.children || {})) {
        const pct = s.asked > 0 ? Math.round((s.correct / s.asked) * 100) : 0;
        childStats += `
            <div style="margin: 12px 0;">
                <strong>${name}</strong>: ${s.correct}/${s.asked} correct (${pct}%)
                ${s.new_learned > 0 ? ` | ${s.new_learned} new learned` : ''}
            </div>
        `;
    }

    content().innerHTML = `
        <div class="card gold-border">
            <div class="phase-label">SESSION COMPLETE</div>
            <div class="score-number" id="score-counter">0</div>
            <div class="score-label">Adventure Points Earned</div>
            <div class="report-lines">${state.report}</div>
            <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1);">
                ${childStats}
            </div>
        </div>
    `;

    // Animate score counting up
    const scoreEl = document.getElementById('score-counter');
    if (scoreEl) animateScoreCounter(scoreEl, 0, state.team_score);

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('continue')">
            Continue <span class="ctrl-shortcut">Enter</span>
        </button>
    `;
}

function renderPowerLevels() {
    const levels = state.levels || {};
    let cards = '';
    for (const [name, l] of Object.entries(levels)) {
        const cssClass = name.toLowerCase();
        const color = cssClass === 'jesse' ? 'var(--jesse-color)' : 'var(--reuben-color)';
        cards += `
            <div class="card power-card">
                <div style="font-size: 28px; font-weight: 700; color: ${color};">${name}</div>
                <div class="power-level-number">${l.power_level}</div>
                <div class="power-level-name" style="color: ${color};">${l.power_level_name}</div>
                <div class="power-total">${l.total_correct} total correct answers</div>
            </div>
        `;
    }

    content().innerHTML = `
        <div class="phase-label">POWER LEVELS</div>
        ${cards}
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('continue')">
            Continue <span class="ctrl-shortcut">Enter</span>
        </button>
    `;
}

function renderCliffhanger() {
    content().innerHTML = `
        <div class="card purple-border">
            ${imageHtml(state.image, 'To be continued')}
            <div class="cliffhanger-text">${state.text}</div>
            <div class="cliffhanger-label">To be continued...</div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('continue')">
            Continue <span class="ctrl-shortcut">Enter</span>
        </button>
    `;
}

function renderComplete() {
    playCelebrationSound();
    showFireworks(8);
    showCascade();

    content().innerHTML = `
        <div class="card gold-border" style="text-align: center;">
            ${imageHtml(state.image, 'Mission Complete')}
            <div style="font-size: 72px; margin-bottom: 16px;">🚀</div>
            <div class="dashboard-title">${state.title}</div>
            <div class="story-text" style="margin-top: 16px;">${state.text}</div>
            <div class="score-number" style="margin-top: 20px;">${state.final_score}</div>
            <div class="score-label">Total Adventure Points This Session</div>
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn launch" onclick="endAndReturn()">
            🏠 Save & Return Home
        </button>
    `;
}

async function endAndReturn() {
    await endSession();
}

// --- Keyboard Shortcuts ---

document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    const key = e.key.toLowerCase();

    if (key === 'enter') {
        e.preventDefault();
        // Find the primary action button
        const correct = document.querySelector('.ctrl-btn.correct');
        const cont = document.querySelector('.ctrl-btn.continue');
        const launch = document.querySelector('.ctrl-btn.launch');
        if (correct) {
            doAction('correct');
        } else if (cont) {
            cont.click();
        } else if (launch) {
            launch.click();
        }
    } else if (key === 'n') {
        const btn = document.querySelector('.ctrl-btn.wrong');
        if (btn) doAction('wrong');
    } else if (key === 'h') {
        const btn = document.querySelector('.ctrl-btn.hint');
        if (btn) doAction('hint');
    } else if (key === 's') {
        const btn = document.querySelector('.ctrl-btn.skip');
        if (btn) doAction('skip');
    } else if (key === 'b') {
        // Break shortcut - trigger continue if on a break screen
    }
});

// --- Init ---

createStarfield();
startShootingStars();
fetchState();
