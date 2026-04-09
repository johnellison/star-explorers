# Star Explorers Improvements - Implementation Plan

## Task List

### PHASE 1: Cleanup & Foundation (Tasks 1-2)

- [x] **Task 1**: Remove CLI Components
  - Delete `main.py` and `display.py`
  - Refactor `session.py` to remove CLI display code, keep pure logic
  - Remove `rich` dependency from `requirements.txt`
  - Test: Flask app runs without CLI dependencies

- [x] **Task 2**: Extract Shared Logic (Simplified)
  - Create `game_engine.py` with pure game flow logic
  - Move game state management to `models.py` (GameState class)
  - Simplify `session.py` to story arcs & question filtering only
  - Refactor `app.py` to use GameState & GameEngine
  - Create `tests/test_game_engine.py` with unit tests

### PHASE 2: Core Interactivity (Tasks 3-4)

- [x] **Task 3**: Implement Tappable Multiple-Choice Answers
  - Backend: Add `/api/generate-choices` endpoint with distractor generation
  - Frontend: Add multiple-choice renderer with touch-optimized buttons
  - Frontend: Add CSS styles for `.choice-button` with animations
  - Add configuration toggle in `team.json` for multiple-choice mode
  - Test on iPad (touch) and desktop (keyboard fallback)

- [x] **Task 4**: Implement Text-to-Speech (TTS)
  - Frontend: Implement Web Speech API wrapper class
  - Auto-speak question when displayed
  - Add "Speak Again" button for replay
  - Add voice selection (child-friendly voices)
  - Add TTS toggle in `team.json`
  - Test on Safari (iPad) and Chrome

### PHASE 3: Content Expansion (Tasks 5-6)

- [x] **Task 5**: Expand Question Bank
  - Create `science_age4.json` (40 questions)
  - Create `science_age7.json` (50 questions)
  - Create `geography_age4.json` (40 questions)
  - Create `geography_age7.json` (50 questions)
  - Create `reading_age4.json` (40 questions)
  - Create `reading_age7.json` (50 questions)
  - Expand `math_age7.json` (+40 questions)
  - Expand `spelling_age4.json` (+10 questions)
  - Expand `spelling_age7.json` (+20 questions)
  - Test: All questions load without errors

### PHASE 4: Persistence & Progress (Tasks 7-8)

- [ ] **Task 7**: Implement Auto-Save and Fix Vercel Persistence
  - Add Vercel KV integration to `app.py`
  - Implement auto-save after every question to KV
  - Add session recovery on load (check KV for existing session)
  - Add conflict resolution (last-write-wins with timestamps)
  - Add "Game saved" indicator in frontend
  - Add "Recover session?" dialog
  - Backup to local file system for development
  - Add Vercel KV dependency to `requirements.txt`
  - Test: State persists across cold starts and browser refreshes

- [ ] **Task 8**: Implement Kid-Facing Progress Visualization
  - Define 10+ badge criteria in `app.py` (BADGES dict)
  - Track earned badges in ChildProfile
  - Add `/api/badges/{child_id}` endpoint
  - Frontend: Badge display modal with earned/locked states
  - Frontend: New badge popup with animation
  - Frontend: Progress bars per subject (math, spelling, science, etc.)
  - Create star map canvas (1 star = 1 session)
  - Animated star placement and constellation lines
  - Add "Progress" tab in main menu
  - Update `models.py` ChildProfile with progress stats
  - Test: Kids can navigate progress independently

### PHASE 5: Polish & Accessibility (Tasks 9-10)

- [ ] **Task 9**: Implement Calm Mode
  - Add `.calm-mode` class to CSS (disable animations, reduce speed)
  - Add calm mode toggle in frontend with localStorage persistence
  - Add calm mode indicator
  - Add calm mode setting to `team.json`
  - Test: Significantly reduces sensory overload

- [ ] **Task 10**: Testing & Documentation
  - Run unit tests (`pytest tests/`)
  - Integration tests: Full session flow with auto-save
  - Manual testing: Play full session on iPad (Safari)
  - Manual testing: Play full session on Chrome (desktop)
  - Test calm mode toggle
  - Test badge unlocks
  - Test star map navigation
  - Test session recovery after browser close
  - Update README.md with web-only architecture
  - Document new features (TTS, calm mode, progress)
  - Fix pre-existing LSP errors in codebase

### FINAL VERIFICATION

- [ ] **F1**: Code Review - All changes reviewed for quality, no stubs/TODOs
- [ ] **F2**: Functionality Test - Full session played end-to-end on iPad
- [ ] **F3**: Regression Test - Existing features work (spaced repetition, story arcs)
- [ ] **F4**: Deployment Test - Deploy to Vercel, test cold start persistence

---

## Summary

**Total Tasks**: 14 (10 implementation + 4 final verification)
**Estimated Effort**: ~35 hours over 2-3 weeks
**Key Milestones**:
- End of Phase 1: Codebase simplified, foundation solid
- End of Phase 2: Kids can interact independently
- End of Phase 3: 200+ new questions, 50 unique sessions
- End of Phase 4: Robust persistence, clear progress
- End of Phase 5: Polished, accessible, well-tested
