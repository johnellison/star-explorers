# Star Explorers - Web-First Improvement Plan

## Project Overview

Transform Star Explorers from a dual-interface (CLI + Web) educational game into a streamlined, web-first platform with enhanced features for two children (Reuben age 7, Jesse age 4).

**Current State:**
- Flask web app + CLI (main.py with rich)
- Two-player game: Reuben (Code Breaker), Jesse (Sound Seeker)
- 5-act story structure, 25 sessions total, 5 story arcs
- ~180 questions total (math + spelling only)
- Spaced repetition engine (Leitner + SM-2)
- AI-generated images for story art
- Deployed on Vercel with data persistence issues

## Goals

1. **Remove CLI entirely** - Simplify codebase, single interface (web)
2. **Enhance kid interactivity** - Tappable answers, text-to-speech
3. **Expand educational content** - More subjects, deeper question bank
4. **Improve persistence** - Fix Vercel data loss, add auto-save
5. **Add engagement features** - Calm mode, kid-facing progress, more story

## Non-Functional Requirements

- Maintain backward compatibility with existing data files
- Keep Flask + vanilla JS/HTML/CSS stack (no framework migration)
- Vercel deployment target
- Maintain game's core educational integrity (spaced repetition, 5-act structure)
- Support offline caching of critical resources

---

## REQUIREMENTS

### 1. Remove CLI Components

**Priority: HIGH**
**Effort: 2 hours**

Delete all CLI-specific code and make web the sole interface.

**Deliverables:**
- Delete `main.py` (CLI entry point)
- Delete `display.py` (Rich CLI display)
- Refactor `session.py`:
  - Remove CLI-specific display methods
  - Keep only game logic that web can call
  - Extract shared state management to models
- Update all documentation to reflect web-only architecture
- Remove `rich` dependency from requirements.txt
- Test: `python app.py` runs without CLI dependencies

**Files to Modify:**
- Delete: `main.py`, `display.py`
- Modify: `session.py` (remove CLI display, keep logic)
- Modify: `requirements.txt` (remove rich)

**Success Criteria:**
- No CLI import errors in `app.py`
- Web session flow unchanged
- Codebase reduced by ~1000 lines

---

### 2. Implement Tappable Multiple-Choice Answers

**Priority: HIGH**
**Effort: 4 hours**

Enable kids to tap answers on a tablet instead of relying entirely on dad's keyboard.

**Deliverables:**

**Backend (app.py):**
- Add endpoint `/api/generate-choices` that:
  - Takes current question and correct answer
  - Generates 3-4 distractor answers from same question bank
  - Returns shuffled options: [correct, distractor1, distractor2, distractor3]
- Store selected answer in session state
- Validate answer immediately on tap, show correct/incorrect feedback
- Update WebSessionState with multiple-choice mode

**Frontend (static/app.js):**
- Add multiple-choice renderer component:
  ```javascript
  function renderMultipleChoice(question, options) {
    // Display 4 clickable buttons
    // Highlight selected answer
    // Show green/red feedback after tap
    // Play sound (correct/wrong chime)
    // Auto-advance after 2s delay
  }
  ```
- Touch-optimized button sizing (minimum 48x48px for kids)
- Haptic feedback on tap (vibration API)
- Keyboard shortcut fallback (1, 2, 3, 4 keys)
- Animation: scale down slightly on press, pop on release

**Frontend (static/style.css):**
- Add `.choice-button` styles:
  - Large touch targets (60px height, 40% width on mobile)
  - Color-coded: default (gray), correct (green), wrong (red)
  - Transition animations for state changes
  - Dark mode compatible colors

**Configuration:**
- Add toggle in team.json: `"multiple_choice_mode": true`
- Per-child setting: can have one child use keyboard, one use taps

**Success Criteria:**
- Jesse can independently answer via taps on tablet
- Reuben can use keyboard shortcuts for speed
- Answer validation works correctly
- No lag between tap and feedback
- Backward compatible (keyboard still works)

---

### 3. Implement Text-to-Speech (TTS)

**Priority: HIGH**
**Effort: 3 hours**

Enable game to read questions aloud so Jesse (age 4) can play more independently.

**Deliverables:**

**Backend (app.py):**
- Add TTS text preparation:
  - Parse questions to extract spoken text
  - Include question + answer choices
  - Add encouraging voice lines ("Great job, Jesse!")
- API endpoint `/api/tts-config` returns text to speak

**Frontend (static/app.js):**
- Implement Web Speech API wrapper:
  ```javascript
  class TextToSpeech {
    constructor() {
      this.synth = window.speechSynthesis;
      this.enabled = true;
    }

    speak(text, voice = 'default') {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.voice = this.getVoice(voice); // Child-friendly voice
      this.synth.speak(utterance);
    }

    stop() {
      this.synth.cancel();
    }
  }
  ```
- Auto-speak question when displayed
- Speak correct answer after wrong attempt
- Add "Speak Again" button for replay
- Voice selection: prefer child-friendly voices (higher pitch, slower rate)

**Configuration:**
- Add to team.json: `"tts_enabled": true`
- Per-child voice setting: `"tts_voice": "child_us"` or `"tts_voice": "child_uk"`
- Speed adjustment: `"tts_rate": 0.9` (slower for kids)

**Fallback:**
- If browser doesn't support Web Speech API, show message: "TTS not available"
- Use server-side TTS (gTTS or similar) if needed in future

**Success Criteria:**
- Questions read aloud automatically
- Voice is clear and understandable for 4-year-old
- Can toggle on/off during game
- Works on iPad (Safari) and Chrome
- Doesn't overlap with sound effects

---

### 4. Expand Question Bank

**Priority: MEDIUM**
**Effort: 6 hours**

Add new subjects and more questions to sustain long-term learning.

**Deliverables:**

**New Question Categories:**

**Science (ages 4-7):**
- `science_age4.json`: 40 questions
  - Animals: habitats, sounds, babies, diet
  - Plants: parts (roots, leaves, flower), growth
  - Weather: sun, rain, wind, seasons
  - Space: sun, moon, stars, planets (basic)
  - Body: 5 senses, major organs (heart, brain), basic functions
- `science_age7.json`: 50 questions
  - States of matter: solid, liquid, gas
  - Forces: push, pull, friction, magnets
  - Life cycles: plants, butterflies, frogs
  - Solar system: planets order, Earth's features
  - Energy sources: sun, food, electricity basics

**Geography (ages 4-7):**
- `geography_age4.json`: 40 questions
  - Maps: what is a map, cardinal directions (N/S/E/W)
  - Continents: names, location (basic)
  - Landforms: mountain, valley, river, ocean, island
  - Climate: hot/cold places, seasons
  - Cultures: different foods, clothing, languages (basic)
- `geography_age7.json`: 50 questions
  - Countries: UK, USA, major countries, capitals
  - Oceans: names, locations
  - Map symbols: scale, legend, compass
  - Time zones: basic concept, day/night
  - Landmarks: famous mountains, buildings, rivers

**Reading Comprehension (ages 4-7):**
- `reading_age4.json`: 40 questions
  - Picture interpretation: What do you see? What happens next?
  - Simple stories: 3-sentence passages, main idea questions
  - Characters: feelings, actions, basic traits
  - Sequence: What happened first, next, last?
  - Vocabulary: simple synonyms, antonyms, context clues
- `reading_age7.json`: 50 questions
  - Short stories: 5-sentence passages, detailed questions
  - Inferences: Why did character do X?
  - Main idea vs details
  - Predictions: What will happen next?
  - Author's purpose: entertain, inform, persuade

**Expanded Math:**
- Add times tables 3, 4, 6, 7, 8, 9 to `math_age7.json` (+20 questions)
- Add fractions basics to `math_age7.json` (+10 questions)
- Add time concepts (clocks, hours, minutes) to `math_age7.json` (+10 questions)

**Expanded Spelling:**
- Add common word families (-at, -it, -op) to `spelling_age4.json` (+10 questions)
- Add more complex patterns to `spelling_age7.json` (+20 questions)

**Question Format:**
Each question follows existing JSON structure:
```json
{
  "question": "What do plants need to grow?",
  "answer": "Water, sun, soil, air",
  "category": "Science",
  "difficulty": 1,
  "age_group": "4-7",
  "hint": "Think about what you give a flower."
}
```

**Quality Standards:**
- Age-appropriate language
- Clear, unambiguous answers
- One correct answer per question
- Include hints for ~30% of questions
- Difficulty levels 1-5 mapped to spaced repetition boxes

**Success Criteria:**
- ~200 new questions added
- Question bank covers 5+ subjects (was 2)
- All questions load without errors
- Age-appropriate for both kids
- Balanced difficulty distribution

---

### 5. Implement Auto-Save and Fix Vercel Persistence

**Priority: HIGH**
**Effort: 4 hours**

Fix critical data loss issue and add robust auto-save.

**Problem Analysis:**
- Current implementation copies data to `/tmp` on Vercel
- `/tmp` is ephemeral - lost on cold starts
- Browser refresh loses in-memory session state
- No persistence during active session

**Solution:**

**Option 1: Vercel KV (Recommended)**
- Fast key-value storage, automatically persists
- Free tier: 256KB storage, sufficient for game state
- Simple API: `KV.get(key)`, `KV.put(key, value)`

**Option 2: External Database (Future)**
- Supabase, Firebase, or similar
- Overkill for current needs, but scalable

**Deliverables (Vercel KV):**

**Backend (app.py):**
- Add Vercel KV integration:
  ```python
  from vercel_kv import KV
  kv = KV()

  async def save_session(team_id: str, session_state: dict):
      await kv.put(f"session:{team_id}", json.dumps(session_state))

  async def load_session(team_id: str) -> dict:
      data = await kv.get(f"session:{team_id}")
      return json.loads(data) if data else None
  ```
- Implement auto-save after every question:
  - Save to KV immediately after answer validation
  - Save after act completion
  - Save on session end
- Add session recovery on load:
  - Check KV for existing session
  - Resume if found, create new if not
- Implement conflict resolution:
  - Last-write-wins (simple)
  - Timestamp in session state

**Frontend (static/app.js):**
- Add "Game saved" indicator after each question (subtle checkmark)
- Add "Recover session?" dialog if unsaved changes detected
- Add manual save button in settings

**Configuration:**
- Add Vercel KV environment variable: `KV_URL`
- Backup to local file system (development only):
  ```python
  if not os.getenv("VERCEL"):
      # Local file backup
      with open(f"data/sessions/backup_{team_id}.json", "w") as f:
          json.dump(session_state, f)
  ```

**Data Model Update:**
- Add `session_state.last_saved` timestamp
- Add `session_state.version` for conflict detection
- Keep local JSON files as cold storage (archive)

**Migration:**
- Script to migrate existing `data/team.json` and `data/children/*.json` to KV
- Keep JSON files as backup (don't delete)

**Success Criteria:**
- Game state persists across cold starts
- Auto-saves after every question
- Can resume interrupted sessions
- Local development still works with file fallback
- Vercel free tier limits not exceeded

---

### 6. Implement Calm Mode

**Priority: LOW**
**Effort: 3 hours**

Add toggle to reduce animations and sensory input for neurodivergent-friendly play.

**Deliverables:**

**Frontend (static/style.css):**
- Add `.calm-mode` class that:
  - Disables particle animations (`animation: none`)
  - Reduces starfield speed to 10% of normal
  - Removes transitions on state changes
  - Mutes background ambient sounds (if added later)
  - Reduces color saturation (less vibrant)
  - Disables flash effects

**Frontend (static/app.js):**
- Add calm mode toggle:
  ```javascript
  function toggleCalmMode() {
    document.body.classList.toggle('calm-mode');
    calmMode = !calmMode;
    localStorage.setItem('calmMode', calmMode);
    if (calmMode) {
      stopParticles(); // Freeze in place
    } else {
      startParticles(); // Resume
    }
  }
  ```
- Persist calm mode preference in localStorage
- Add calm mode button in settings (toggle icon)
- Show subtle indicator when calm mode is active

**Configuration:**
- Add to team.json: `"calm_mode": false`
- Per-child setting: each kid can have different preference
- Sync preference to server for multi-device consistency

**Visual Changes in Calm Mode:**
- Starfield: static stars, no movement
- Particles: removed entirely
- Buttons: no hover effects, simple border on focus
- Transitions: 0s (instant state changes)
- Colors: muted palette (dark blue background, white text)
- Feedback: simple color changes (green/red), no animations

**Success Criteria:**
- Calm mode can be toggled on/off instantly
- Preference persists across sessions
- Reduces sensory overload significantly
- Doesn't break game logic
- Kids can toggle independently

---

### 7. Implement Kid-Facing Progress Visualization

**Priority: MEDIUM**
**Effort: 5 hours**

Add visual rewards and progress tracking that kids can see and understand.

**Deliverables:**

**Badge System:**

**Backend (app.py):**
- Define badge criteria:
  ```python
  BADGES = {
    "first_correct": {"name": "First Star", "desc": "Answer your first question"},
    "streak_3": {"name": "Hot Streak", "desc": "3 correct in a row"},
    "streak_5": {"name": "On Fire", "desc": "5 correct in a row"},
    "streak_10": {"name": "Unstoppable", "desc": "10 correct in a row"},
    "act_complete": {"name": "Act Hero", "desc": "Complete an act"},
    "session_complete": {"name": "Session Master", "desc": "Complete a session"},
    "story_complete": {"name": "Story Champion", "desc": "Complete a story arc"},
    "all_correct": {"name": "Perfect Score", "desc": "100% in session"},
    "math_master": {"name": "Math Whiz", "desc": "50 math questions correct"},
    "spelling_master": {"name": "Spelling Bee", "desc": "50 spelling questions correct"},
  }
  ```
- Track earned badges in child profile
- API endpoint `/api/badges/{child_id}` returns earned badges
- Check for badge unlocks after every question

**Frontend (static/app.js):**
- Badge display modal:
  - Shows all badges with earned/locked state
  - New badges popup with animation when unlocked
  - Count: X / Y badges earned
  - Badge icons (emoji or simple SVG)
- Progress bar per badge category:
  - Math progress: 42/50 questions
  - Spelling progress: 38/50 questions
  - Overall progress: 80/100 sessions

**Star Map Visualization:**

**Frontend (static/app.js + style.css):**
- Create star map canvas:
  - Each session completed = new star on map
  - Stars form constellations (25 sessions = 1 constellation)
  - 5 constellations = 5 story arcs
  - Kids can tap completed stars to see what they learned
- Animated star placement:
  - New star appears with burst animation
  - Constellations connect with lines when complete
  - Show progress to next star
- Zoom/pan map for future (25+ sessions)
- Show current position (which session, which act)

**Frontend (static/style.css):**
- Star map styles:
  - Deep space background
  - Glowing stars (earned) vs. dim stars (future)
  - Constellation lines (subtle)
  - Child-friendly aesthetics

**Progress Dashboard:**

**Frontend (static/app.js):**
- Add "Progress" tab in main menu:
  - Shows badge collection
  - Shows star map
  - Shows streak stats (best streak, current streak)
  - Shows subject mastery (math, spelling, science, etc.)
  - Shows time played today/week
- Kids can access independently (no parent gate)

**Backend (models.py):**
- Add progress tracking to ChildProfile:
  ```python
  class ChildProfile:
      badges: List[str] = []
      total_questions_answered: int = 0
      correct_questions: int = 0
      best_streak: int = 0
      current_streak: int = 0
      subject_mastery: Dict[str, int] = {}  # subject -> correct count
  ```
- Update stats after every question

**Success Criteria:**
- Kids can see their badges and understand what they mean
- Star map shows clear progress through 125 sessions
- New badges pop up with excitement
- Progress persists across sessions
- Kids can navigate progress independently

---

### 8. Expand Story Content Beyond 25 Sessions

**Priority: MEDIUM**
**Effort: 4 hours**

Add new story arcs so game doesn't loop with modulo after 25 sessions.

**Current State:**
- 5 story arcs (Star Base, Nebula, Planet X, Black Hole, Homecoming)
- 5 sessions per arc = 25 total
- After 25, wraps back to start (same content)

**Deliverables:**

**New Story Arcs:**

**Arc 6: The Ancient Ruins**
- Sessions 26-30
- Theme: Discover alien artifacts on remote moon
- Learning objectives: history, archaeology basics
- Boss challenge: Decode alien message
- Lightning round: Rapid artifact identification

**Arc 7: The Crystal Cave**
- Sessions 31-35
- Theme: Explore bioluminescent underground world
- Learning objectives: light/refraction, cave ecosystems
- Boss challenge: Navigate crystal maze
- Lightning round: Match crystal colors to elements

**Arc 8: The Solar Storm**
- Sessions 36-40
- Theme: Survive massive space weather event
- Learning objectives: weather, energy, radiation
- Boss challenge: Shield calculations
- Lightning round: Quick math for survival

**Arc 9: The Friendly Aliens**
- Sessions 41-45
- Theme: First contact with peaceful species
- Learning objectives: communication, cultures, languages
- Boss challenge: Translate alien math
- Lightning round: Pattern matching alien language

**Arc 10: The Supernova**
- Sessions 46-50
- Theme: Observe dramatic stellar explosion
- Learning objectives: stars, explosions, gravity
- Boss challenge: Escape blast radius
- Lightning round: Speed calculations

**Breaks and Cliffhangers:**
- Add 2-3 new break activities per arc:
  - Space yoga (stretch prompts)
  - Zero-gravity dance (dance moves)
  - Alien greeting cards (draw)
- Add cliffhangers before each boss:
  - "A loud BOOM echoes through the ship!"
  - "The alien ship hails: 'WHO GOES THERE?'"
  - "The crystal cave begins to collapse!"

**Data Structure (story.py):**
```python
STORY_ARCS = {
    # ... existing arcs ...
    6: {
        "name": "The Ancient Ruins",
        "theme": "Archaeology & History",
        "sessions": 5,
        "boss": "Decode Alien Message",
        "lightning": "Artifact Identification",
        "cliffhanger": "A loud BOOM echoes!",
        "breaks": ["Space Yoga: Reach for the stars!", "Alien Freeze Dance"]
    },
    # ... arcs 7-10 ...
}
```

**AI Image Generation:**
- Generate 5 new boss images (one per new arc)
- Generate 5 new cliffhanger images
- Generate 10+ new break activity images
- Store in `static/images/` with consistent naming

**Backward Compatibility:**
- Existing sessions 1-25 unchanged
- New sessions append (no breaking changes)
- Old teams progress seamlessly into new content
- Add "Season 2" indicator after session 25

**Success Criteria:**
- 50 unique sessions total (was 25)
- 10 story arcs total
- Game doesn't repeat content for 50+ sessions
- New story quality matches existing arcs
- All AI-generated images created and loaded

---

### 9. Extract Shared Logic (Simplified Post-CLI Removal)

**Priority: MEDIUM**
**Effort: 3 hours**

After CLI removal, clean up duplicated/overlapping code and extract reusable components.

**Current State:**
- `app.py`: 829 lines - Flask routes + WebSessionState
- `session.py`: 723 lines - CLI game flow + logic
- After CLI removal, session.py will be much smaller (~400 lines of pure logic)

**Deliverables:**

**Extract to `models.py`:**
- Move game state management logic from WebSessionState to models:
  ```python
  class GameState:
      """Pure game logic, no UI concerns"""
      def __init__(self, team_state: TeamState):
          self.team = team_state
          self.current_session = None

      def start_session(self) -> SessionState:
          # Initialize new session
          pass

      def advance_act(self) -> None:
          # Move to next act
          pass

      def record_answer(self, child_id: str, correct: bool) -> None:
          # Update spaced repetition
          pass
  ```

**Extract to `game_engine.py` (new file):**
- Core game flow logic:
  ```python
  class GameEngine:
      """Orchestrates game flow without UI"""
      def __init__(self, game_state: GameState):
          self.state = game_state

      def run_session(self):
          """Generates next question, checks completion"""
          pass

      def check_act_completion(self):
          """Returns True if act complete"""
          pass

      def check_session_completion(self):
          """Returns True if session complete"""
          pass
  ```

**Refactor `session.py`:**
- Remove all CLI display code (already done in task 1)
- Remove game flow logic (moved to game_engine.py)
- Keep only:
  - Session initialization helpers
  - Story arc selection
  - Question filtering
  - ~~Remove or mark deprecated~~

**Refactor `app.py`:**
- Import GameState and GameEngine
- Simplify WebSessionState to be a thin wrapper:
  ```python
  WebSessionState:
      def __init__(self):
          self.game_state = GameState(team_state)
          self.engine = GameEngine(self.game_state)
      # Just adds Flask session management
  ```
- Remove duplicated logic (~200 lines)

**Add Tests (new file `tests/test_game_engine.py`):**
- Unit tests for GameState methods
- Unit tests for GameEngine flow
- Integration tests for full session simulation
- Mock spaced repetition engine

**File Structure After Refactor:**
```
.
├── models.py          # Data models (TeamState, ChildProfile, Question, GameState)
├── game_engine.py    # Pure game logic (no UI)
├── session.py         # Story arcs, question filtering (simplified)
├── app.py            # Flask routes (much simpler now)
├── spaced_rep.py      # Spaced repetition (unchanged)
├── questions.py       # Question loader (unchanged)
└── tests/
    └── test_game_engine.py  # New test file
```

**Success Criteria:**
- Code reduced by ~300 lines total
- Clear separation: data, logic, UI
- GameState has no Flask/CLI dependencies
- Tests pass for game engine
- Web functionality unchanged

---

## TESTING STRATEGY

### Unit Tests
- GameState and GameEngine methods (task 9)
- Badge calculation logic
- Spaced repetition edge cases

### Integration Tests
- Full session flow with auto-save
- Multiple-choice answer validation
- TTS audio generation

### Manual Testing
- Play full session on iPad (Safari)
- Play full session on Chrome (desktop)
- Test calm mode toggle
- Test badge unlocks
- Test star map navigation
- Test session recovery after browser close

### Regression Testing
- Existing question banks still load
- Spaced repetition still works correctly
- Story arc progression unchanged
- Image generation still works

---

## RISKS & MITIGATION

**Risk 1: Vercel KV limits exceeded**
- Mitigation: Compress state, archive old sessions, monitor usage

**Risk 2: TTS not supported on all browsers**
- Mitigation: Graceful degradation, visual-only mode fallback

**Risk 3: 50 sessions too many for attention span**
- Mitigation: Modular design, can stop at any arc, progress saved

**Risk 4: New question bank has quality issues**
- Mitigation: Peer review from other parents, A/B test with kids

**Risk 5: Refactoring breaks existing functionality**
- Mitigation: Comprehensive tests, gradual rollout, rollback plan

---

## DEPENDENCIES

**No new Python packages** (use existing stack)
- Flask 3.1.3
- Vercel SDK (for KV) - add to requirements.txt

**No new JavaScript libraries** (use vanilla JS)
- Web Speech API (built-in)
- Vibration API (built-in)
- localStorage (built-in)

---

## DELIVERABLES SUMMARY

1. Code cleanup: -1000 lines (CLI removed)
2. New features: Tappable answers, TTS, calm mode, badges, star map
3. Content expansion: ~200 new questions, 25 new sessions
4. Persistence: Vercel KV integration, auto-save
5. Architecture: Extracted GameState, GameEngine, simplified app.py
6. Tests: Game engine test coverage
7. Documentation: Updated README, web-only architecture

**Total Estimated Effort: ~35 hours**
**Suggested Timeline: 2-3 weeks (evenings/weekends)**
