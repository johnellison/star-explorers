# Star Explorers

A colorful, space-themed educational game for kids (ages 4-7) played over video call. Dad operates the controls while the kids see big, animated visuals on a shared screen.

Features a Five-Act story structure with spaced repetition learning, boss challenges, lightning rounds, movement breaks, silly breaks, and an evolving narrative across 25 sessions.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/johnellison/star-explorers.git
cd star-explorers

# Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install flask

# First-time setup (creates child profiles and team data)
python app.py

# Launch web GUI
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## How It Works

### For Dad (the operator)

- **Keyboard shortcuts** while on a question screen:
  - `Enter` — Mark correct
  - `N` — Mark wrong
  - `H` — Show hint
  - `S` — Skip question
- **Continue** through story/break screens with `Enter`
- Share your browser tab over the video call so the kids see the big colorful visuals

### For the Kids

They see animated space-themed screens with:
- Big readable text (36-48px)
- Star-burst particle effects on correct answers
- Sound chimes for correct/wrong
- Story panels, boss challenges, movement breaks, and silly breaks
- Their own color-coded turn indicator (sky blue for Jesse, pink for Reuben)

## Game Structure (per session, ~60 minutes)

| Act | What happens |
|-----|-------------|
| 1. Opening | Team chant, recap, warm-up questions, story hook |
| 2. First Quest | Two rounds of questions with story beats |
| Break | Movement break (jumping, dancing, etc.) |
| 3. Boss Challenge | Cooperative boss fight — both kids answer together |
| Break | Silly break (tongue twisters, animal sounds, etc.) |
| 4. Second Quest | Review round, treasure chest bonus, lightning round |
| 5. Closing | Score report, power levels, cliffhanger, secret mission |

## Project Structure

```
star-explorers/
├── app.py              # Flask web server + state machine
├── models.py           # Data models (ChildProfile, TeamState, etc.)
├── session.py          # Core game logic (pure functions, no UI)
├── spaced_rep.py       # Spaced repetition engine (Modified Leitner + SM-2)
├── questions.py        # Question bank loader and filters
├── story.py            # Story arcs, breaks, cliffhangers
├── static/
│   ├── index.html      # Web GUI page shell
│   ├── style.css       # Space theme + CSS animations
│   └── app.js          # Frontend renderers + keyboard controls
└── data/
    ├── children/       # Child profile JSON files
    ├── question_bank/  # Question bank JSON files
    ├── sessions/       # Session log JSON files
└── team.json       # Team state
```

## Customization

### Adding Questions

Add JSON files to `data/question_bank/`. Each file is an array of question objects:

```json
[
  {
    "id": "unique_id",
    "subject": "Maths",
    "topic": "counting_1_5",
    "difficulty_tier": 1,
    "age_range": [3, 5],
    "read_aloud": "Can you count to 3?",
    "correct_answers": ["3", "1 2 3"],
    "correct_response": "Brilliant! You counted to 3!",
    "incorrect_response": "Let's try together: 1, 2, 3!",
    "hint": "Start with 1...",
    "format": "open_ended"
  }
]
```

### Child Profiles

Edit `data/children/jesse.json` or `data/children/reuben.json` to change names, ages, or character titles.
