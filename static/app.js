/* Star Explorers - Frontend Logic */

const $ = (sel) => document.querySelector(sel);
const content = () => $('#content');
const controlsBar = () => $('#controls-bar');

let state = null;
let pollTimer = null;
let demoMode = false;
let previewStep = -1;

const isStaticHost = window.location.hostname.endsWith('github.io') || window.location.protocol === 'file:';
const assetBase = isStaticHost ? '.' : '/static';

const PREVIEW_WORLD_NAMES = [
    'Enchanted Forest',
    'Crystal Caves',
    'Hidden Island',
    'Sky Kingdom',
    'Puzzle Dimension',
];

const PREVIEW_LEVEL_NAMES = [
    ['Whispering Grove', 'Lantern Run', 'Wishing Tree Workshop', 'Bridge of Echoes', 'Goblin Gate'],
    ['Glow Tunnel', 'Crystal Tracks', 'Shard Foundry', 'Echo Vault', 'Dragon Lift'],
    ['Driftwood Beach', 'Parrot Post', 'Shell Maze', 'Tide Workshop', 'Guardian Reef'],
    ['Cloud Steps', 'Windmill Row', 'Storm Station', 'Rainbow Span', 'Shepherd Peak'],
    ['Mirror Hall', 'Thread Gate', 'Puzzle Loom', 'Final Route', 'Star Forge'],
];

function assetPath(path) {
    if (!path) return '';
    if (path.startsWith('/static/')) {
        return `${assetBase}/${path.slice('/static/'.length)}`;
    }
    return path;
}

function previewCampaign() {
    const worldNumber = 1;
    const levelNumber = 3;
    const levelId = `w${worldNumber}l${levelNumber}`;
    const completed = new Set(['w1l1', 'w1l2']);
    const mapNodes = [];
    const worlds = PREVIEW_WORLD_NAMES.map((name, worldIndex) => {
        const worldNo = worldIndex + 1;
        PREVIEW_LEVEL_NAMES[worldIndex].forEach((levelName, levelIndex) => {
            const nodeId = `w${worldNo}l${levelIndex + 1}`;
            mapNodes.push({
                id: nodeId,
                world_number: worldNo,
                world_name: name,
                level_number: levelIndex + 1,
                level_name: levelName,
                completed: completed.has(nodeId),
                current: nodeId === levelId,
                unlocked: worldNo < worldNumber || nodeId === levelId || completed.has(nodeId),
            });
        });

        return {
            world_number: worldNo,
            name,
            theme: ['Forest repairs', 'Crystal routes', 'Island rescue', 'Sky bridges', 'Final weave'][worldIndex],
            unlocked: worldNo <= worldNumber,
            completed: worldNo < worldNumber,
            levels_completed: worldNo === 1 ? 2 : 0,
        };
    });

    return {
        world_number: worldNumber,
        world_name: PREVIEW_WORLD_NAMES[worldNumber - 1],
        level_number: levelNumber,
        level_name: 'Wishing Tree Workshop',
        level_id: levelId,
        objective: 'Repair the Wishing Tree before the forest loses its last safe shelter.',
        objective_label: `World ${worldNumber} · Level ${levelNumber}`,
        characters_in_scene: [
            { name: 'Captain Starlight', role: 'Mission guide' },
            { name: 'Wise Owl', role: 'Forest mentor' },
            { name: 'Puzzle Goblin', role: 'Troublemaker' },
        ],
        reward: {
            icon: '🌟',
            name: 'Lantern Seed',
            summary: 'A glowing seed that keeps safe paths lit through the forest.',
        },
        current_reward: {
            icon: '🪵',
            name: 'Bridge Nails',
            summary: 'Fresh repair tools for broken routes.',
        },
        reward_history: ['Whisper Leaves', 'Moon Lantern'],
        world_complete: false,
        next_level: {
            world_number: 1,
            world_name: 'Enchanted Forest',
            level_number: 4,
            level_name: 'Bridge of Echoes',
            objective: 'Cross the repaired bridge and follow the echo trail to the goblin gate.',
        },
        map_nodes: mapNodes,
        worlds,
        progress_copy: '2 of 25 levels cleared',
    };
}

function previewChildren() {
    return {
        Jesse: {
            age: 4,
            character_name: 'Jesse the Sound Seeker',
            sessions_completed: 2,
            power_level: 3,
            power_level_name: 'Spark Scout',
        },
        Reuben: {
            age: 7,
            character_name: 'Reuben the Code Breaker',
            sessions_completed: 2,
            power_level: 4,
            power_level_name: 'Route Builder',
        },
    };
}

function previewTopics() {
    return {
        Jesse: {
            sounds: { subject: 'Phonics', mastery_pct: 62, items_count: 12 },
        },
        Reuben: {
            reading: { subject: 'Reading', mastery_pct: 74, items_count: 18 },
            geography: { subject: 'Geography', mastery_pct: 48, items_count: 10 },
        },
    };
}

function previewTeam() {
    return {
        total_adventure_points: 64,
        achievements: ['First World Steps', 'Bridge Builder'],
        current_reward: {
            icon: '🪵',
            name: 'Bridge Nails',
            summary: 'Fresh repair tools for broken routes.',
        },
    };
}

function buildPreviewState() {
    if (previewStep < 0) {
        return { phase: 'no_session', screen: 'no_session', preview_mode: true };
    }

    const campaign = previewCampaign();
    const shared = {
        preview_mode: true,
        session_number: 3,
        phase: 'pre_session',
        screen: 'pre_session',
        title: 'Campaign Map',
        text: '',
        date: 'Static Preview',
        image: '/static/images/title_hero.png',
        arc_name: campaign.world_name,
        world_number: campaign.world_number,
        level_number: campaign.level_number,
        level_name: campaign.level_name,
        active_objective: campaign.objective,
        campaign,
        children: previewChildren(),
        topics: previewTopics(),
        team: previewTeam(),
        team_score: 18,
        elapsed_minutes: 4,
        multiple_choice_mode: false,
    };

    const screens = [
        {
            ...shared,
            phase: 'pre_session',
            screen: 'pre_session',
        },
        {
            ...shared,
            phase: 'act1_recap',
            screen: 'story',
            title: 'Campaign Recap',
            text: 'Previously on Star Explorers... you cleared Lantern Run, restored the moon lanterns, and tracked Puzzle Goblin to the Wishing Tree workshop.',
            style: 'story',
        },
        {
            ...shared,
            phase: 'act1_story_hook',
            screen: 'story',
            title: `Level ${campaign.level_number}: ${campaign.level_name}`,
            text: 'The Wishing Tree is cracking and the forest shelter is fading. Wise Owl points to missing repair parts while Puzzle Goblin slips into the branches above.',
            style: 'adventure',
        },
        {
            ...shared,
            phase: 'act2_round1',
            screen: 'question',
            label: 'OBJECTIVE PHASE 1',
            current_child: 'Reuben',
            remaining: 3,
            question: {
                id: 'preview_reading_1',
                read_aloud: 'What is another word for repair?',
                correct_answers: ['fix', 'mend', 'restore'],
                correct_response: 'Yes. Repair means to fix something that is broken.',
                incorrect_response: 'Not quite. Think about making a broken thing work again.',
                hint: 'You do this to a broken bridge or toy.',
            },
        },
        {
            ...shared,
            phase: 'movement_break',
            screen: 'break',
            break_type: 'movement',
            break_interaction: 'bridge_repair',
            title: 'POWER-UP TIME!',
            text: 'The workshop bridge snapped. Smash the repair nails into place so the team can reach the Wishing Tree roots.',
        },
        {
            ...shared,
            phase: 'act3_boss_intro',
            screen: 'boss_intro',
            title: `LEVEL BOSS · ${campaign.level_name}`,
            text: 'Puzzle Goblin blocks the final gear lock. Solve one last challenge to release the repair platform.',
            image: '/static/images/title_hero.png',
        },
        {
            ...shared,
            phase: 'act3_boss',
            screen: 'boss_victory',
            title: 'BOSS DEFEATED!',
            text: 'The repair platform snaps into place, the Wishing Tree glows again, and the forest shelter holds.',
            reward: campaign.reward,
            image: '/static/images/title_hero.png',
        },
        {
            ...shared,
            phase: 'act5_score',
            screen: 'score_report',
            report: 'LEVEL CLEAR: Wishing Tree Workshop\nObjective complete: Repair the Wishing Tree before the forest loses its last safe shelter.\nReward earned: Lantern Seed — A glowing seed that keeps safe paths lit through the forest.',
            reward: campaign.reward,
            next_level: campaign.next_level,
            world_complete: false,
            stats: {
                children: {
                    Jesse: { asked: 2, correct: 2, new_learned: 1 },
                    Reuben: { asked: 3, correct: 2, new_learned: 1 },
                },
            },
        },
        {
            ...shared,
            phase: 'act5_power_levels',
            screen: 'power_levels',
            reward: campaign.reward,
            next_level: campaign.next_level,
            world_complete: false,
            levels: {
                Jesse: { power_level: 3, power_level_name: 'Spark Scout', total_correct: 18 },
                Reuben: { power_level: 4, power_level_name: 'Route Builder', total_correct: 24 },
            },
        },
        {
            ...shared,
            phase: 'act5_cliffhanger',
            screen: 'cliffhanger',
            title: 'NEXT LEVEL UNLOCKED · Bridge of Echoes',
            text: 'The repaired roots uncover a hidden path. Beyond the bridge, Puzzle Goblin has left echo markers leading straight to the gate.',
            next_level: campaign.next_level,
            world_complete: false,
            image: '/static/images/title_hero.png',
        },
        {
            ...shared,
            phase: 'complete',
            screen: 'complete',
            title: 'LEVEL COMPLETE',
            text: 'This is the static GitHub Pages preview. The real game session flow runs against the Flask backend.',
            final_score: 18,
            image: '/static/images/title_hero.png',
        },
    ];

    return screens[Math.min(previewStep, screens.length - 1)];
}

function previewResult(action) {
    if (action === 'correct') {
        return { ok: true, correct: true, points: 5, streak: 3 };
    }
    if (action === 'wrong') {
        return { ok: true, correct: false, points: 0, streak: 0 };
    }
    return { ok: true };
}

async function previewApiGet(url) {
    if (url === '/api/state') {
        return buildPreviewState();
    }
    return {};
}

async function previewApiPost(url, body = {}) {
    if (url === '/api/session/start') {
        previewStep = 0;
        return { ok: true, session_number: 3 };
    }
    if (url === '/api/session/end') {
        previewStep = -1;
        return { ok: true, session_number: 3 };
    }
    if (url === '/api/action') {
        if (previewStep >= 0) {
            previewStep = Math.min(previewStep + 1, 10);
        }
        return previewResult(body.action);
    }
    if (url === '/api/generate-choices') {
        return {
            options: [
                { id: 'a', text: 'Fix' },
                { id: 'b', text: 'Hide' },
                { id: 'c', text: 'Scatter' },
                { id: 'd', text: 'Forget' },
            ],
        };
    }
    return {};
}

// --- Audio (Web Audio API synthesized sounds) ---

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playCorrectSound() {
    ensureAudioReady();
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

function ensureAudioReady() {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume().catch(() => {});
    }
}

function playWrongSound() {
    ensureAudioReady();
    const now = audioCtx.currentTime;
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
    ensureAudioReady();
    const now = audioCtx.currentTime;
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
    ensureAudioReady();
    const now = audioCtx.currentTime;
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
    ensureAudioReady();
    const now = audioCtx.currentTime;
    [261.63, 329.63, 392.0, 523.25].forEach((freq, i) => {
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
    ensureAudioReady();
    const now = audioCtx.currentTime;
    [261.63, 329.63, 392.0, 523.25, 659.25].forEach((freq, i) => {
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
    ensureAudioReady();
    const now = audioCtx.currentTime;
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
    ensureAudioReady();
    const now = audioCtx.currentTime;
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
    ensureAudioReady();
    const now = audioCtx.currentTime;
    [261.63, 329.63, 392.0, 523.25].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.value = freq;
        const duration = i === 3 ? 1.2 : 0.3;
        gain.gain.setValueAtTime(0.15, now + i * 0.18);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.18 + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + i * 0.18);
        osc.stop(now + i * 0.18 + duration);
    });
}

function playAchievementSound() {
    ensureAudioReady();
    const now = audioCtx.currentTime;
    [523.25, 1046.5].forEach((freq, i) => {
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

function playHammerHitSound(power = 1) {
    ensureAudioReady();
    const now = audioCtx.currentTime;

    const thud = audioCtx.createOscillator();
    const thudGain = audioCtx.createGain();
    thud.type = 'square';
    thud.frequency.setValueAtTime(180 + power * 30, now);
    thud.frequency.exponentialRampToValueAtTime(90, now + 0.14);
    thudGain.gain.setValueAtTime(0.12, now);
    thudGain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
    thud.connect(thudGain);
    thudGain.connect(audioCtx.destination);
    thud.start(now);
    thud.stop(now + 0.16);

    const ping = audioCtx.createOscillator();
    const pingGain = audioCtx.createGain();
    ping.type = 'triangle';
    ping.frequency.setValueAtTime(720, now + 0.02);
    ping.frequency.exponentialRampToValueAtTime(420, now + 0.12);
    pingGain.gain.setValueAtTime(0.08, now + 0.02);
    pingGain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
    ping.connect(pingGain);
    pingGain.connect(audioCtx.destination);
    ping.start(now + 0.02);
    ping.stop(now + 0.14);
}

function playBridgeFixedSound() {
    ensureAudioReady();
    const now = audioCtx.currentTime;
    [392.0, 523.25, 659.25, 784.0].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.14, now + i * 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.1 + 0.45);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now + i * 0.1);
        osc.stop(now + i * 0.1 + 0.45);
    });
}

// --- Starfield ---

function createStarfield() {
    const sf = $('#starfield');
    sf.innerHTML = '';

    const nebulaColors = [
        'radial-gradient(circle, rgba(199,125,255,0.4), transparent 70%)',
        'radial-gradient(circle, rgba(123,47,247,0.3), transparent 70%)',
        'radial-gradient(circle, rgba(160,196,255,0.3), transparent 70%)',
    ];

    for (let i = 0; i < 3; i += 1) {
        const patch = document.createElement('div');
        patch.className = 'nebula-patch';
        const size = 300 + Math.random() * 400;
        patch.style.width = `${size}px`;
        patch.style.height = `${size}px`;
        patch.style.left = `${10 + Math.random() * 80}%`;
        patch.style.top = `${10 + Math.random() * 80}%`;
        patch.style.background = nebulaColors[i];
        sf.appendChild(patch);
    }

    const starColors = [
        { color: '#ffffff', weight: 55 },
        { color: '#a0c4ff', weight: 18 },
        { color: '#c77dff', weight: 12 },
        { color: '#fff5e0', weight: 8 },
        { color: '#72efdd', weight: 7 },
    ];

    function pickStarColor() {
        const total = starColors.reduce((sum, item) => sum + item.weight, 0);
        let pick = Math.random() * total;
        for (const item of starColors) {
            pick -= item.weight;
            if (pick <= 0) return item.color;
        }
        return '#ffffff';
    }

    for (let i = 0; i < 120; i += 1) {
        const star = document.createElement('div');
        star.className = 'star';
        const size = Math.random() * 3.5 + 0.8;
        const color = pickStarColor();
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.background = color;
        if (size > 2.5) {
            star.style.boxShadow = `0 0 ${size * 2}px ${color}`;
        }
        star.style.setProperty('--duration', `${Math.random() * 3 + 2}s`);
        star.style.setProperty('--max-opacity', Math.random() * 0.6 + 0.4);
        star.style.animationDelay = `${Math.random() * 5}s`;
        sf.appendChild(star);
    }
}

function spawnShootingStar() {
    const sf = $('#starfield');
    const star = document.createElement('div');
    star.className = 'shooting-star';
    star.style.left = `${Math.random() * 60}%`;
    star.style.top = `${Math.random() * 50}%`;

    const angle = 20 + Math.random() * 30;
    const distance = 250 + Math.random() * 200;
    const dx = Math.cos((angle * Math.PI) / 180) * distance;
    const dy = Math.sin((angle * Math.PI) / 180) * distance;
    const duration = 600 + Math.random() * 400;

    sf.appendChild(star);
    star.animate(
        [
            { transform: 'translateX(0) translateY(0)', opacity: 1 },
            { transform: `translateX(${dx}px) translateY(${dy}px)`, opacity: 0 },
        ],
        { duration, easing: 'ease-out' }
    );
    setTimeout(() => star.remove(), duration);
}

function startShootingStars() {
    function scheduleNext() {
        const delay = 12000 + Math.random() * 20000;
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
    for (let i = 0; i < 12; i += 1) {
        const particle = document.createElement('div');
        particle.className = 'star-particle';
        particle.textContent = emojis[i % emojis.length];
        const angle = (i / 12) * Math.PI * 2;
        const distance = 80 + Math.random() * 60;
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;
        particle.style.animation = 'none';
        particle.style.fontSize = `${18 + Math.random() * 16}px`;
        container.appendChild(particle);
        particle.animate(
            [
                { transform: 'translate(0, 0) scale(1)', opacity: 1 },
                {
                    transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0.3)`,
                    opacity: 0,
                },
            ],
            { duration: 800 + Math.random() * 400, easing: 'ease-out' }
        );
        setTimeout(() => particle.remove(), 1200);
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
    for (let i = 0; i < 20; i += 1) {
        setTimeout(() => {
            const particle = document.createElement('div');
            particle.className = 'star-particle';
            particle.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            particle.style.left = `${Math.random() * window.innerWidth}px`;
            particle.style.top = '-40px';
            particle.style.fontSize = `${20 + Math.random() * 20}px`;
            container.appendChild(particle);
            setTimeout(() => particle.remove(), 2200);
        }, i * 100);
    }
}

function showScreenFlash(color) {
    const flash = document.createElement('div');
    flash.className = 'screen-flash';
    flash.style.background = color;
    document.body.appendChild(flash);
    flash.animate([{ opacity: 0.3 }, { opacity: 0 }], { duration: 250, easing: 'ease-out' });
    setTimeout(() => flash.remove(), 250);
}

function showCometTrail() {
    const container = $('#particles');
    const comet = document.createElement('div');
    comet.className = 'comet-trail';
    comet.style.left = '-20px';
    comet.style.top = `${10 + Math.random() * 40}%`;
    container.appendChild(comet);

    comet.animate(
        [
            { transform: 'translateX(0)', opacity: 1 },
            { transform: `translateX(${window.innerWidth + 100}px)`, opacity: 0 },
        ],
        { duration: 1200, easing: 'ease-in' }
    );

    for (let i = 0; i < 6; i += 1) {
        setTimeout(() => {
            const trail = document.createElement('div');
            trail.className = 'comet-trail';
            trail.style.left = `${i * 15}%`;
            trail.style.top = comet.style.top;
            trail.style.width = '4px';
            trail.style.height = '4px';
            trail.style.opacity = '0.5';
            container.appendChild(trail);
            trail.animate(
                [
                    { opacity: 0.5, transform: 'scale(1)' },
                    { opacity: 0, transform: 'scale(0.2)' },
                ],
                { duration: 400, easing: 'ease-out' }
            );
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

    rocket.animate(
        [
            { transform: 'translateY(0) scale(1) rotate(0deg)', opacity: 1 },
            { transform: 'translateY(-100vh) scale(0.3) rotate(-15deg)', opacity: 0 },
        ],
        { duration: 1500, easing: 'ease-in' }
    );

    for (let i = 0; i < 15; i += 1) {
        setTimeout(() => {
            const exhaust = document.createElement('div');
            exhaust.className = 'star-particle';
            exhaust.textContent = ['🔥', '💨', '✨'][i % 3];
            exhaust.style.left = `${48 + Math.random() * 4}%`;
            exhaust.style.top = `${85 - i * 4}%`;
            exhaust.style.fontSize = '20px';
            exhaust.style.animation = 'none';
            container.appendChild(exhaust);
            exhaust.animate(
                [
                    { opacity: 1, transform: 'scale(1)' },
                    { opacity: 0, transform: `scale(0.3) translateY(${50 + Math.random() * 50}px)` },
                ],
                { duration: 600, easing: 'ease-out' }
            );
            setTimeout(() => exhaust.remove(), 600);
        }, i * 80);
    }

    setTimeout(() => rocket.remove(), 1500);
}

function showFireworks(count) {
    for (let i = 0; i < count; i += 1) {
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
        position: fixed;
        top: 50%;
        left: 50%;
        width: 80px;
        height: 80px;
        border: 3px solid var(--gold);
        border-radius: 50%;
        pointer-events: none;
        z-index: 200;
        transform: translate(-50%, -50%) scale(0);
    `;
    document.body.appendChild(ring);
    ring.animate(
        [
            { transform: 'translate(-50%, -50%) scale(0)', opacity: 0.8, borderWidth: '3px' },
            { transform: 'translate(-50%, -50%) scale(4)', opacity: 0, borderWidth: '1px' },
        ],
        { duration: 800, easing: 'ease-out' }
    );
    setTimeout(() => ring.remove(), 800);
}

function animateScoreCounter(element, from, to, duration = 1500) {
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        element.textContent = Math.round(from + (to - from) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

let lastScreen = null;
let bridgeRepairState = { key: null, hits: 0, requiredHits: 6, complete: false };

function transitionTo(renderFn, transitionClass = 'fade-in') {
    const main = content();
    main.style.animation = 'none';
    main.offsetHeight;
    main.style.animation = `${transitionClass} 0.35s ease`;
    playTransitionSound();
    renderFn();
}

function imageHtml(src, alt) {
    if (!src) return '';
    return `<img src="${assetPath(src)}" alt="${alt || ''}" class="scene-image" onerror="this.style.display='none'" />`;
}

// --- Text-to-Speech (Web Speech API) ---

class TextToSpeech {
    constructor() {
        this.synth = window.speechSynthesis;
        this.enabled = true;
        this.voice = null;
        this.rate = 0.9;  // Slower for kids
        this.pitch = 1.1;  // Slightly higher for friendlier voice
        this.currentUtterance = null;
        
        // Initialize voices
        if (this.synth) {
            this.loadVoices();
        }
    }
    
    loadVoices() {
        // Wait for voices to load
        if (this.synth.getVoices().length > 0) {
            this.voices = this.synth.getVoices();
            this.selectChildFriendlyVoice();
        }
    }
    
    selectChildFriendlyVoice() {
        // Prefer child-friendly voices (higher pitch, slower)
        const preferred = this.voices.filter(v => 
            v.lang.startsWith('en') && 
            (v.name.includes('Google US') || 
             v.name.includes('Samantha') ||
             v.name.includes('Microsoft') ||
             v.name.includes('Daniel'))
        );
        
        if (preferred.length > 0) {
            this.voice = preferred[0];
        } else if (this.voices.length > 0) {
            this.voice = this.voices[0];
        }
    }
    
    speak(text, onEndCallback = null) {
        if (!this.enabled || !this.synth) {
            console.log('TTS not enabled or not supported');
            return;
        }
        
        // Cancel any ongoing speech
        if (this.currentUtterance) {
            this.synth.cancel();
        }
        
        const utterance = new SpeechSynthesisUtterance();
        utterance.text = text;
        utterance.voice = this.voice;
        utterance.rate = this.rate;
        utterance.pitch = this.pitch;
        
        if (onEndCallback) {
            utterance.onend = onEndCallback;
        }
        
        this.synth.speak(utterance);
        this.currentUtterance = utterance;
    }
    
    stop() {
        if (this.currentUtterance) {
            this.synth.cancel();
            this.currentUtterance = null;
        }
    }
    
    setEnabled(enabled) {
        this.enabled = enabled;
    }
    
    setVoice(voiceName) {
        this.voice = this.voices.find(v => v.name === voiceName) || this.voice;
    }
    
    speakQuestion(question) {
        if (!this.enabled || !question) return;
        
        // Speak the question text
        this.speak(question.read_aloud);
        
        // If there are multiple-choice options, speak them too
        if (question.correct_answers && question.correct_answers.length > 0) {
            const optionsText = question.correct_answers.slice(0, 3).join(', or ');
            setTimeout(() => {
                this.speak(`Options: ${optionsText}`);
            }, 500);
        }
    }
    
    speakCorrectResponse(question) {
        if (!this.enabled || !question) return;
        setTimeout(() => {
            this.speak(question.correct_response);
        }, 200);
    }
    
    speakWrongResponse(question) {
        if (!this.enabled || !question) return;
        setTimeout(() => {
            this.speak(question.incorrect_response);
        }, 200);
    }
}

// Global TTS instance
const tts = new TextToSpeech();

function toggleTTS() {
    tts.setEnabled(!tts.enabled);
    if (state?.screen === 'question') {
        renderScreen();
    }
}

function speakCurrentQuestion() {
    if (state && state.question) {
        tts.speakQuestion(state.question);
    }
}

// --- API Calls ---

async function apiGet(url) {
    if (demoMode) {
        return previewApiGet(url);
    }
    try {
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`GET ${url} failed with ${res.status}`);
        }
        return res.json();
    } catch (error) {
        if (isStaticHost) {
            demoMode = true;
            return previewApiGet(url);
        }
        throw error;
    }
}

async function apiPost(url, body = {}) {
    if (demoMode) {
        return previewApiPost(url, body);
    }
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            throw new Error(`POST ${url} failed with ${res.status}`);
        }
        return res.json();
    } catch (error) {
        if (isStaticHost) {
            demoMode = true;
            return previewApiPost(url, body);
        }
        throw error;
    }
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
    if (demoMode) {
        await fetchState();
        return;
    }
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
    const worldLevel = state.world_number && state.level_number
        ? `World ${state.world_number} · Level ${state.level_number}`
        : state.arc_name || '';
    $('#session-info').textContent = `Session #${state.session_number} | ${worldLevel}`;
    $('#score-display').textContent = `${state.team_score} pts`;
    $('#timer-display').textContent = `${state.elapsed_minutes || 0} min`;
}

// --- Screen Renderers ---

function renderScreen() {
    updateStatusBar();
    cleanupMultipleChoiceKeyboard();

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

function getCampaign() {
    return state?.campaign || {};
}

function renderCharacterChips(characters = []) {
    if (!characters.length) return '';
    const chips = characters.map((character) => `
        <div class="campaign-chip">
            <span class="campaign-chip-name">${character.name}</span>
            <span class="campaign-chip-role">${character.role || ''}</span>
        </div>
    `).join('');
    return `<div class="campaign-chip-row">${chips}</div>`;
}

function renderCampaignMap(campaign = getCampaign(), compact = false) {
    if (!campaign.worlds?.length || !campaign.map_nodes?.length) return '';

    const worldHtml = campaign.worlds.map((world) => {
        const nodes = campaign.map_nodes
            .filter((node) => node.world_number === world.world_number)
            .map((node) => `
                <div class="campaign-node ${node.completed ? 'completed' : ''} ${node.current ? 'current' : ''} ${node.unlocked ? 'unlocked' : 'locked'}">
                    <div class="campaign-node-badge">${node.level_number}</div>
                    <div class="campaign-node-name">${node.level_name}</div>
                </div>
            `)
            .join('');

        return `
            <div class="campaign-world ${world.completed ? 'completed' : ''} ${world.unlocked ? 'unlocked' : 'locked'}">
                <div class="campaign-world-header">
                    <div class="campaign-world-title">World ${world.world_number}: ${world.name}</div>
                    <div class="campaign-world-progress">${world.levels_completed}/5 cleared</div>
                </div>
                <div class="campaign-world-theme">${world.theme}</div>
                <div class="campaign-node-row">${nodes}</div>
            </div>
        `;
    }).join('');

    return `
        <div class="campaign-map ${compact ? 'compact' : ''}">
            <div class="campaign-map-header">
                <div class="campaign-map-title">Adventure Route</div>
                <div class="campaign-map-progress">${campaign.progress_copy || ''}</div>
            </div>
            ${worldHtml}
        </div>
    `;
}

function renderObjectiveBanner(compact = false) {
    const campaign = getCampaign();
    if (!campaign.level_name) return '';

    return `
        <div class="objective-banner ${compact ? 'compact' : ''}">
            <div class="objective-kicker">${campaign.objective_label || ''}</div>
            <div class="objective-title">${campaign.level_name}</div>
            <div class="objective-text">${state.active_objective || campaign.objective || ''}</div>
            ${renderCharacterChips(campaign.characters_in_scene || [])}
        </div>
    `;
}

function renderRewardCard(reward, title = 'Reward Earned') {
    if (!reward || !reward.name) return '';
    return `
        <div class="reward-card">
            <div class="reward-card-kicker">${title}</div>
            <div class="reward-card-main">
                <div class="reward-card-icon">${reward.icon || '⭐'}</div>
                <div>
                    <div class="reward-card-name">${reward.name}</div>
                    <div class="reward-card-summary">${reward.summary || ''}</div>
                </div>
            </div>
        </div>
    `;
}

function renderNextLevelCard(nextLevel, worldComplete = false) {
    if (!nextLevel) {
        return `
            <div class="next-level-card final">
                <div class="next-level-kicker">Campaign Finale</div>
                <div class="next-level-title">All 25 Levels Cleared</div>
                <div class="next-level-text">The Star Explorers restored every world and completed the full campaign.</div>
            </div>
        `;
    }

    return `
        <div class="next-level-card ${worldComplete ? 'world-complete' : ''}">
            <div class="next-level-kicker">${worldComplete ? 'World Clear' : 'Next Level Unlocked'}</div>
            <div class="next-level-title">World ${nextLevel.world_number} · Level ${nextLevel.level_number}: ${nextLevel.level_name}</div>
            <div class="next-level-text">${nextLevel.objective}</div>
        </div>
    `;
}

function renderNoSession() {
    content().innerHTML = `
        <div class="no-session">
            ${imageHtml('/static/images/title_hero.png', 'Star Explorers')}
            <div class="title">STAR EXPLORERS</div>
            <div class="subtitle">${demoMode ? 'Static Preview Mode' : 'Mission Control Ready'}</div>
            ${demoMode ? '<div class="story-text" style="max-width: 620px; margin: 18px auto 0;">GitHub Pages is running a frontend-only preview. Launch to view the campaign flow without the Flask backend.</div>' : ''}
        </div>
    `;
    controlsBar().innerHTML = `
        <button class="ctrl-btn launch" onclick="startSession()">
            ${demoMode ? '🎮 Open Preview' : '🚀 Launch Mission'}
        </button>
    `;
}

function renderPreSession() {
    const children = state.children || {};
    const date = state.date || '';
    const campaign = getCampaign();

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
        <div class="dashboard-title">CAMPAIGN MAP</div>
        <div class="dashboard-subtitle">Session #${state.session_number} | ${date}</div>
        <div class="card mission-brief-card">
            ${imageHtml(state.image, state.arc_name)}
            ${renderObjectiveBanner()}
            <div class="mission-brief-meta">
                Total Adventure Points: ${team.total_adventure_points || 0} |
                Achievements: ${(team.achievements || []).length}
            </div>
            ${renderRewardCard(team.current_reward, 'Latest Relic')}
            ${renderNextLevelCard(campaign.next_level, campaign.world_complete)}
        </div>
        <div class="card">${renderCampaignMap(campaign)}</div>
        <div class="team-card-grid">${childCards}</div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn launch" onclick="doAction('continue')">
            🚀 Start Level
        </button>
    `;
}

// Multiple-choice rendering
async function fetchMultipleChoiceOptions(questionId) {
    if (demoMode) {
        const data = await previewApiPost('/api/generate-choices', { question_id: questionId });
        return data.options || [];
    }
    try {
        const response = await fetch('/api/generate-choices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question_id: questionId }),
        });
        
        if (!response.ok) {
            console.error('Failed to fetch multiple-choice options:', response.status);
            return [];
        }
        
        const data = await response.json();
        return data.options || [];
    } catch (error) {
        console.error('Error fetching multiple-choice options:', error);
        return [];
    }
}

function renderMultipleChoice(options) {
    if (!options || options.length === 0) {
        return;
    }
    
    // Create button HTML for each option
    const buttonsHtml = options.map((opt, index) => `
        <button class="choice-button" data-option-id="${opt.id}" data-option-text="${opt.text}" onclick="handleChoiceSelect(event)">
            <span class="option-letter">${String.fromCharCode(65 + index)}</span>
            <span class="option-text">${opt.text}</span>
        </button>
    `).join('');
    
    return `
        <div class="multiple-choice-container">
            <div class="choice-label">Choose the right answer:</div>
            <div class="choice-buttons">${buttonsHtml}</div>
        </div>
    `;
}

function handleChoiceSelect(event) {
    const button = event.currentTarget;
    const optionText = button.dataset.optionText;
    const question = state.question;
    
    // Check if this is the correct answer
    const isCorrect = question && question.correct_answers && 
                      question.correct_answers.includes(optionText);
    
    // Visual feedback
    document.querySelectorAll('.choice-button').forEach(btn => {
        btn.disabled = true;  // Disable all buttons
    });
    
    if (isCorrect) {
        button.classList.add('correct');
        button.classList.remove('wrong');
        playCorrectSound();
        // Auto-continue after 2 seconds
        setTimeout(() => {
            doAction('correct');
        }, 2000);
    } else {
        button.classList.add('wrong');
        button.classList.remove('correct');
        playWrongSound();
        // Auto-continue after 2 seconds
        setTimeout(() => {
            doAction('wrong');
        }, 2000);
    }
}

function renderQuestion() {
    const q = state.question;
    const child = state.current_child;
    const cssClass = child?.toLowerCase() || '';
    const label = state.label || '';
    const isLightning = state.is_lightning;
    const isBoss = state.is_boss;
    const isTreasure = state.is_treasure;
    const useMultipleChoice = state.multiple_choice_mode === true;

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

    if (useMultipleChoice && q && q.id) {
        const questionId = q.id;
        fetchMultipleChoiceOptions(questionId).then(options => {
            if (!state || state.screen !== 'question' || state.question?.id !== questionId || state.multiple_choice_mode !== true) {
                return;
            }

            const multipleChoiceHtml = renderMultipleChoice(options);

            content().innerHTML = `
                ${renderObjectiveBanner(true)}
                <div class="phase-label">${label}</div>
                ${headerExtra}
                <div class="child-turn ${cssClass}">${child}'s Turn</div>
                <div class="card ${borderClass}">
                    <div class="read-aloud">${q.read_aloud}</div>
                    ${multipleChoiceHtml}
                </div>
            `;

            setupMultipleChoiceKeyboard(options);
            if (q && q.read_aloud) {
                tts.speakQuestion(q);
            }
        });

        controlsBar().innerHTML = `
            <button class="ctrl-btn toggle" onclick="toggleMultipleChoiceMode()">
                ${state.multiple_choice_mode ? '☐ Standard' : '☑ Multiple Choice'}
            </button>
            <button class="ctrl-btn tts" onclick="toggleTTS()">
                ${tts.enabled ? '🔊 Sound On' : '🔇 Sound Off'}
            </button>
            <button class="ctrl-btn speak-again" onclick="speakCurrentQuestion()">
                🔁 Speak Again
            </button>
            <button class="ctrl-btn skip" onclick="doAction('skip')">
                Skip <span class="ctrl-shortcut">S</span>
            </button>
        `;
    } else {
        content().innerHTML = `
            ${renderObjectiveBanner(true)}
            <div class="phase-label">${label}</div>
            ${headerExtra}
            <div class="child-turn ${cssClass}">${child}'s Turn</div>
            <div class="card ${borderClass}">
                <div class="read-aloud">${q.read_aloud}</div>
                <div class="answer-line">Answer: <strong>${q.correct_answers.join(' / ')}</strong></div>
                <div class="response-scripts">
                    <div><span class="label if-correct">IF CORRECT:</span> ${q.correct_response}</div>
                    <div><span class="label if-wrong">IF WRONG:</span> ${q.incorrect_response}</div>
                    ${q.metacognitive_prompt ? `<div style="color: var(--cyan); margin-left: 20px;">${q.metacognitive_prompt}</div>` : ''}
                    ${q.mnemonic ? `<div style="color: var(--purple); margin-left: 20px;">MNEMONIC: ${q.mnemonic}</div>` : ''}
                    <div><span class="label if-stuck">IF STUCK:</span> ${q.hint}</div>
                </div>
            </div>
        `;

        if (q && q.read_aloud) {
            tts.speakQuestion(q);
        }

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
            <button class="ctrl-btn toggle" onclick="toggleMultipleChoiceMode()">
                ${state.multiple_choice_mode ? '☐ Standard' : '☑ Multiple Choice'}
            </button>
            <button class="ctrl-btn tts" onclick="toggleTTS()">
                ${tts.enabled ? '🔊 Sound On' : '🔇 Sound Off'}
            </button>
            <button class="ctrl-btn speak-again" onclick="speakCurrentQuestion()">
                🔁 Speak Again
            </button>
            <button class="ctrl-btn skip" onclick="doAction('skip')">
                Skip <span class="ctrl-shortcut">S</span>
            </button>
        `;
    }
}

function setupMultipleChoiceKeyboard(options) {
    cleanupMultipleChoiceKeyboard();

    const handleKeyPress = (event) => {
        if (event.key >= '1' && event.key <= '4') {
            event.preventDefault();
            const optionIndex = parseInt(event.key) - 1;
            const buttons = document.querySelectorAll('.choice-button');
            if (buttons[optionIndex] && !buttons[optionIndex].disabled) {
                buttons[optionIndex].click();
            }
        }
    };

    document.addEventListener('keydown', handleKeyPress);
    window.multipleChoiceKeyboardHandler = handleKeyPress;
}

function cleanupMultipleChoiceKeyboard() {
    if (window.multipleChoiceKeyboardHandler) {
        document.removeEventListener('keydown', window.multipleChoiceKeyboardHandler);
        window.multipleChoiceKeyboardHandler = null;
    }
}

function toggleMultipleChoiceMode() {
    state.multiple_choice_mode = !state.multiple_choice_mode;
    renderScreen();
}

function renderStory() {
    const title = state.title || 'STORY';
    const text = state.text || '';
    const style = state.style === 'adventure' ? 'gold-border' : 'purple-border';

    content().innerHTML = `
        ${renderObjectiveBanner(true)}
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

function getBridgeRepairKey() {
    return `${state?.session_number || 0}:${state?.phase || ''}:${state?.text || ''}`;
}

function syncBridgeRepairState() {
    const key = getBridgeRepairKey();
    if (bridgeRepairState.key !== key) {
        bridgeRepairState = {
            key,
            hits: 0,
            requiredHits: 6,
            complete: false,
        };
    }
}

function getBridgeStatusText() {
    if (bridgeRepairState.complete) {
        return 'Bridge fixed. Charge across!';
    }
    const remaining = bridgeRepairState.requiredHits - bridgeRepairState.hits;
    return `${remaining} more smash${remaining === 1 ? '' : 'es'} to fix the bridge`;
}

function bridgeRescueHtml() {
    syncBridgeRepairState();

    const planks = Array.from({ length: bridgeRepairState.requiredHits }, (_, index) => `
        <div class="bridge-plank ${index < bridgeRepairState.hits ? 'repaired' : ''}"></div>
    `).join('');

    return `
        <div class="bridge-rescue-panel ${bridgeRepairState.complete ? 'complete' : ''}" id="bridge-rescue-panel">
            <div class="bridge-rescue-kicker">BROKEN BRIDGE RESCUE</div>
            <div class="bridge-rescue-status" id="bridge-status-text">${getBridgeStatusText()}</div>
            <div class="bridge-scene" id="bridge-scene">
                <div class="bridge-cliff left"></div>
                <div class="bridge-plank-row" id="bridge-plank-row">${planks}</div>
                <div class="bridge-cliff right"></div>
                <div class="bridge-gap-glow"></div>
                <div class="bridge-helper">🧒</div>
            </div>
            <div class="bridge-progress">
                <div class="bridge-progress-fill" id="bridge-progress-fill"></div>
            </div>
            <button class="bridge-hammer-btn ${bridgeRepairState.complete ? 'complete' : ''}" id="bridge-hammer-btn" onclick="hitBridgeNail()">
                <span class="hammer-icon">🔨</span>
                <span class="hammer-copy" id="bridge-hammer-copy">${bridgeRepairState.complete ? 'Bridge Fixed!' : 'Smash The Nail!'}</span>
                <span class="hammer-subcopy" id="bridge-hammer-subcopy">${bridgeRepairState.complete ? 'Tap again for sparkles' : 'Tap to hammer new planks into place'}</span>
            </button>
        </div>
    `;
}

function updateBridgeRepairUI(animate = false) {
    const panel = $('#bridge-rescue-panel');
    if (!panel) return;

    panel.classList.toggle('complete', bridgeRepairState.complete);

    const status = $('#bridge-status-text');
    const progressFill = $('#bridge-progress-fill');
    const hammerButton = $('#bridge-hammer-btn');
    const hammerCopy = $('#bridge-hammer-copy');
    const hammerSubcopy = $('#bridge-hammer-subcopy');
    const planks = document.querySelectorAll('.bridge-plank');
    const progressPercent = (bridgeRepairState.hits / bridgeRepairState.requiredHits) * 100;

    if (status) status.textContent = getBridgeStatusText();
    if (progressFill) progressFill.style.width = `${progressPercent}%`;
    if (hammerButton) hammerButton.classList.toggle('complete', bridgeRepairState.complete);
    if (hammerCopy) hammerCopy.textContent = bridgeRepairState.complete ? 'Bridge Fixed!' : 'Smash The Nail!';
    if (hammerSubcopy) {
        hammerSubcopy.textContent = bridgeRepairState.complete
            ? 'Tap again for sparkles'
            : 'Tap to hammer new planks into place';
    }

    planks.forEach((plank, index) => {
        plank.classList.toggle('repaired', index < bridgeRepairState.hits);
    });

    const continueButton = document.querySelector('.ctrl-btn.continue');
    if (continueButton) {
        continueButton.innerHTML = bridgeRepairState.complete
            ? 'Bridge Fixed! Continue <span class="ctrl-shortcut">Enter</span>'
            : 'Done! Continue <span class="ctrl-shortcut">Enter</span>';
    }

    if (animate) {
        panel.classList.remove('thump');
        hammerButton?.classList.remove('impact');
        void panel.offsetWidth;
        panel.classList.add('thump');
        hammerButton?.classList.add('impact');
        setTimeout(() => {
            panel.classList.remove('thump');
            hammerButton?.classList.remove('impact');
        }, 260);
    }
}

function showBridgeHitBurst(target, celebrate = false) {
    if (!target) return;

    const rect = target.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 3;
    const container = $('#particles');
    const tokens = celebrate ? ['✨', '🌟', '⭐', '🪵'] : ['✨', '💥', '🪵'];
    const count = celebrate ? 12 : 7;

    for (let i = 0; i < count; i += 1) {
        const particle = document.createElement('div');
        particle.className = 'star-particle';
        particle.textContent = tokens[i % tokens.length];
        particle.style.left = `${centerX}px`;
        particle.style.top = `${centerY}px`;
        particle.style.animation = 'none';
        particle.style.fontSize = `${16 + Math.random() * 14}px`;
        container.appendChild(particle);

        const angle = (i / count) * Math.PI * 2;
        const distance = 40 + Math.random() * 70;
        particle.animate(
            [
                { transform: 'translate(0, 0) scale(1)', opacity: 1 },
                {
                    transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0.3)`,
                    opacity: 0,
                },
            ],
            { duration: 450 + Math.random() * 250, easing: 'ease-out' }
        );
        setTimeout(() => particle.remove(), 800);
    }
}

function hitBridgeNail() {
    if (!state || state.screen !== 'break' || state.break_type !== 'movement' || state.break_interaction !== 'bridge_repair') return;

    syncBridgeRepairState();
    const hammerButton = $('#bridge-hammer-btn');

    if (bridgeRepairState.complete) {
        playHammerHitSound(0.7);
        showBridgeHitBurst(hammerButton, true);
        const scene = $('#bridge-scene');
        if (scene) {
            const rect = scene.getBoundingClientRect();
            spawnStarBurst(rect.left + rect.width / 2, rect.top + rect.height / 2);
        }
        return;
    }

    bridgeRepairState.hits = Math.min(bridgeRepairState.requiredHits, bridgeRepairState.hits + 1);
    playHammerHitSound(bridgeRepairState.hits / bridgeRepairState.requiredHits);
    showBridgeHitBurst(hammerButton);
    updateBridgeRepairUI(true);

    if (bridgeRepairState.hits >= bridgeRepairState.requiredHits) {
        bridgeRepairState.complete = true;
        playBridgeFixedSound();
        showScreenFlash('rgba(255, 215, 0, 0.16)');
        showCascade();
        const scene = $('#bridge-scene');
        if (scene) {
            const rect = scene.getBoundingClientRect();
            spawnStarBurst(rect.left + rect.width / 2, rect.top + rect.height / 2);
        }
        updateBridgeRepairUI(true);
    }
}

function renderBreak() {
    const isMovement = state.break_type === 'movement';
    const isBridgeRepair = isMovement && state.break_interaction === 'bridge_repair';
    const emoji = isBridgeRepair ? '🔨' : (isMovement ? '⚡' : '🎭');
    const rescueHtml = isBridgeRepair ? bridgeRescueHtml() : '';

    content().innerHTML = `
        ${renderObjectiveBanner(true)}
        <div class="card ${isBridgeRepair ? 'bridge-break-card' : ''}">
            <div class="break-emoji">${emoji}</div>
            <div class="break-title">${state.title}</div>
            <div class="break-text">${state.text}</div>
            ${rescueHtml}
        </div>
    `;

    controlsBar().innerHTML = `
        <button class="ctrl-btn continue" onclick="doAction('continue')">
            Back To The Mission <span class="ctrl-shortcut">Enter</span>
        </button>
    `;

    if (isBridgeRepair) {
        updateBridgeRepairUI();
    }
}

function renderBossIntro() {
    playBossIntroSound();
    content().innerHTML = `
        ${renderObjectiveBanner(true)}
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
        ${renderObjectiveBanner(true)}
        <div class="card green-border">
            <div class="story-panel">
                ${imageHtml(state.image, 'Victory')}
                <div class="break-emoji">🏆</div>
                <div class="story-title">${state.title}</div>
                <div class="story-text">${state.text}</div>
                ${renderRewardCard(state.reward, 'Level Reward')}
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
            <div class="phase-label">LEVEL CLEAR</div>
            <div class="story-title">${state.level_name || 'Mission Complete'}</div>
            <div class="score-number" id="score-counter">0</div>
            <div class="score-label">Adventure Points Earned</div>
            <div class="report-lines">${state.report}</div>
            ${renderRewardCard(state.reward, 'Relic Unlocked')}
            ${renderNextLevelCard(state.next_level, state.world_complete)}
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
        <div class="phase-label">TEAM RANKS</div>
        ${renderRewardCard(state.reward, 'Mission Reward')}
        ${cards}
        ${renderCampaignMap(getCampaign(), true)}
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
            <div class="phase-label">${state.world_complete ? 'WORLD COMPLETE' : 'NEXT ROUTE'}</div>
            <div class="story-title">${state.title || 'To Be Continued'}</div>
            <div class="cliffhanger-text">${state.text}</div>
            ${renderNextLevelCard(state.next_level, state.world_complete)}
            <div class="cliffhanger-label">${state.world_complete ? 'A new world opens...' : 'Continue the adventure...'}</div>
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
            ${renderCampaignMap(getCampaign(), true)}
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
    } else if (key === ' ' || key === 'b') {
        const hammer = document.getElementById('bridge-hammer-btn');
        if (hammer && state?.break_interaction === 'bridge_repair') {
            e.preventDefault();
            hitBridgeNail();
        }
    }
});

// --- Init ---

createStarfield();
startShootingStars();
fetchState();
