"""Session engine - core game logic without UI concerns."""

import time
import random
from datetime import datetime

from models import ChildProfile, TeamState, SessionLog, Question, Callback
from spaced_rep import process_answer, build_session_queue, introduce_item
from questions import (
    load_question_bank,
    get_questions_for_child,
    get_boss_questions,
    get_lightning_round,
)
from story import (
    CAMPAIGN_WORLDS,
    build_story_flags,
    generate_recap,
    get_story_hook,
    get_cliffhanger,
    get_story_beat,
    get_boss_intro,
    get_character_status,
    get_movement_break,
    get_silly_break,
    get_secret_mission,
    generate_score_report,
    get_session_position,
    get_arc,
    get_level,
)


class SessionState:
    """Mutable state during a session."""

    def __init__(
        self, session_number: int, children: list[ChildProfile], team: TeamState
    ):
        self.session_number = session_number
        self.children = {c.name: c for c in children}
        self.team = team
        self.team_score = 0
        self.start_time = None
        self.current_act = 1
        self.current_child = None
        self.questions_asked = {c.name: 0 for c in children}
        self.questions_correct = {c.name: 0 for c in children}
        self.new_introduced = {c.name: 0 for c in children}
        self.items_mastered = {c.name: [] for c in children}
        self.streak = {c.name: 0 for c in children}
        self.consecutive_wrong = {c.name: 0 for c in children}
        self.achievements_earned = []
        self.callbacks_created = []
        self.question_bank = load_question_bank()
        self.session_queues = {}
        self.difficulty_override = {}  # child_name -> tier_delta
        self.paused = False
        self.notes = []

        # Build queues for each child
        for child in children:
            self.session_queues[child.name] = build_session_queue(
                child, session_number, self.question_bank
            )

    @property
    def elapsed_minutes(self) -> int:
        if not self.start_time:
            return 0
        return int((time.time() - self.start_time) / 60)

    @property
    def elapsed_str(self) -> str:
        mins = self.elapsed_minutes
        return f"{mins:02d}:00"

    def add_points(self, points: int, reason: str = ""):
        self.team_score += points
        self.team.total_adventure_points += points

    def sorted_children(self) -> list[ChildProfile]:
        """Return children sorted youngest first."""
        return sorted(self.children.values(), key=lambda c: c.age)


def start_session(children: list[ChildProfile], team: TeamState):
    """Initialize a session state for the web interface."""
    session_num = team.sessions_completed + 1
    state = SessionState(session_num, children, team)

    # Start session timer
    state.start_time = time.time()

    return state


def record_answer(
    state: SessionState,
    child_name: str,
    correct: bool,
    hint_used: bool = False,
    sr_item=None,
) -> dict:
    """Record an answer and return updated state data.

    Pure logic function - UI should handle all display.

    Returns dict with:
    - correct: bool - whether answer was correct
    - points_earned: int - points from this answer
    - streak_earned: str or None - achievement name if streak earned
    - should_increase_difficulty: bool - whether to bump difficulty
    - should_decrease_difficulty: bool - whether to lower difficulty
    - should_trigger_rescue: bool - whether rescue mode needed
    """
    child = state.children[child_name]

    if correct:
        state.questions_asked[child_name] += 1
        state.questions_correct[child_name] += 1
        state.streak[child_name] += 1
        state.consecutive_wrong[child_name] = 0
        child.total_correct += 1
        child.update_power_level()

        # Points
        points = 5 if not hint_used else 3
        state.add_points(points)

        # Update spaced rep
        if sr_item:
            process_answer(sr_item, True, hint_used, state.session_number)

        # Check for streak achievements
        streak_earned = _check_streak_achievement(state, child_name)

        # Auto-difficulty: 3 correct in a row -> bump up
        should_increase = (
            state.streak[child_name] >= 3 and state.streak[child_name] % 3 == 0
        )
        if should_increase:
            state.difficulty_override[child_name] = (
                state.difficulty_override.get(child_name, 0) + 1
            )

        return {
            "correct": True,
            "points_earned": points,
            "streak_earned": streak_earned,
            "should_increase_difficulty": should_increase,
            "should_decrease_difficulty": False,
            "should_trigger_rescue": False,
        }
    else:
        state.questions_asked[child_name] += 1
        state.streak[child_name] = 0
        state.consecutive_wrong[child_name] += 1
        state.add_points(0)

        # Update spaced rep
        if sr_item:
            process_answer(sr_item, False, False, state.session_number)

        # Auto-difficulty: 2 wrong in a row -> drop
        should_decrease = state.consecutive_wrong[child_name] >= 2
        if should_decrease:
            state.difficulty_override[child_name] = (
                state.difficulty_override.get(child_name, 0) - 1
            )

        # Trigger rescue mode after 3 wrong
        should_trigger_rescue = state.consecutive_wrong[child_name] >= 3

        return {
            "correct": False,
            "points_earned": 0,
            "streak_earned": None,
            "should_increase_difficulty": False,
            "should_decrease_difficulty": should_decrease,
            "should_trigger_rescue": should_trigger_rescue,
        }


def get_questions_for_round(
    state: SessionState, child_name: str, queue_key: str, count: int
) -> list:
    """Get questions for a round from the child's queue.

    Returns list of (question, sr_item) tuples.
    """
    queue = state.session_queues.get(child_name, {})
    items = queue.get(queue_key, [])

    result = []
    for q, sr_item in items[:count]:
        # If it's a new item, introduce it
        if sr_item is None:
            child = state.children[child_name]
            sr_item = introduce_item(child, q, state.session_number)
            state.new_introduced[child_name] += 1
        result.append((q, sr_item))

    return result


def get_boss_challenge(state: SessionState) -> dict:
    """Get boss challenge for current session.

    Returns dict with:
    - intro: str - boss introduction text
    - challenges: list - list of challenge parts, each with:
        - intro: str - part introduction
        - child: str - which child answers this part
        - question: Question - the question object
    - celebration: str - text for correct completion
    - failure_text: str - text for incorrect completion
    """
    boss_intro = get_boss_intro(state.session_number)
    child_ages = {c.name: c.age for c in state.sorted_children()}
    challenges = get_boss_questions(state.question_bank, child_ages)

    # Take up to 3 challenges
    challenge_parts = []
    for challenge in challenges[:3]:
        for part in challenge.get("parts", [])[:3]:
            challenge_parts.append(
                {
                    "intro": challenge.get("intro", ""),
                    "child": part.get("child"),
                    "question": part.get("question"),
                }
            )

    return {
        "intro": boss_intro,
        "challenges": challenge_parts,
        "celebration": "",
        "failure_text": (
            "So close! You almost had it! The Puzzle Goblin grins: "
            "'Not bad... not bad at all. Let's try to next one!'"
        ),
    }


def get_lightning_round_questions(state: SessionState) -> list:
    """Get lightning round questions.

    Returns list of (child_name, Question) tuples.
    """
    child_ages = {c.name: c.age for c in state.sorted_children()}
    return get_lightning_round(state.question_bank, child_ages, count=8)


def save_session(state: SessionState) -> None:
    """Save all session data.

    Pure data persistence function - UI handles all display.
    """
    # Update team state
    state.team.sessions_completed = state.session_number
    arc_num, _ = get_session_position(state.session_number)
    arc = get_arc(arc_num)
    level = get_level(state.session_number)
    state.team.current_arc = arc_num
    state.team.current_chapter = state.session_number
    state.team.arc_name = arc["name"]
    state.team.active_objective = level["objective"]

    # Add any new characters
    for char in arc.get("characters", []):
        if char not in state.team.characters_met:
            state.team.characters_met.append(char)

    completed_level_id = level["level_id"]
    if completed_level_id not in state.team.completed_levels:
        state.team.completed_levels.append(completed_level_id)

    reward_entry = {
        "world_number": level["world_number"],
        "world_name": level["world_name"],
        "level_number": level["level_number"],
        "level_name": level["level_name"],
        "name": level["reward"]["name"],
        "summary": level["reward"]["summary"],
        "icon": level["reward"]["icon"],
    }
    state.team.current_reward = reward_entry
    if reward_entry["name"] not in state.team.collected_relics:
        state.team.collected_relics.append(reward_entry["name"])
    state.team.items_collected = list(state.team.collected_relics)

    unlocked_world_count = min(((state.session_number - 1) // 5) + 2, len(CAMPAIGN_WORLDS))
    state.team.world_unlocks = [
        get_arc(world_number)["name"] for world_number in range(1, unlocked_world_count + 1)
    ]

    next_session = min(state.session_number + 1, 25)
    next_level = get_level(next_session)
    state.team.current_world = next_level["world_number"]
    state.team.current_level = next_level["level_number"]
    state.team.story_flags = build_story_flags(state.session_number)
    state.team.character_status = get_character_status(state.session_number)
    state.team.cliffhanger = get_cliffhanger(state.session_number)

    state.team.save()

    # Update and save children
    for child in state.children.values():
        child.sessions_completed = state.session_number
        child.save()

    # Save session log
    log = SessionLog(
        session_number=state.session_number,
        date=datetime.now().isoformat(),
        duration_minutes=state.elapsed_minutes,
        children={
            name: {
                "asked": state.questions_asked[name],
                "correct": state.questions_correct[name],
                "new": state.new_introduced[name],
            }
            for name in state.children
        },
        team_score=state.team_score,
        achievements_earned=state.achievements_earned,
        notes=state.notes,
    )
    log.save()


def _check_streak_achievement(state: SessionState, child_name: str) -> str or None:
    """Check and return streak-based achievement name if earned."""
    streak = state.streak[child_name]

    achievements = {
        3: ("Hat Trick", f"{child_name} got THREE in a row! That's a Hat Trick!"),
        5: ("On Fire", f"{child_name} is ON FIRE! Five correct in a row!"),
    }

    if streak in achievements:
        name, script = achievements[streak]
        full_name = f"{name} ({child_name})"
        if full_name not in state.team.achievements:
            state.team.achievements.append(full_name)
            state.achievements_earned.append(full_name)
            return name

    return None


def get_session_summary(state: SessionState) -> dict:
    """Generate session summary for display.

    Returns dict with:
    - session_stats: dict - statistics for report
    - report_text: str - formatted report from story module
    - cliffhanger: dict - current cliffhanger data
    - secret_mission: dict or None - secret mission if assigned
    """
    # Prepare session stats
    session_stats = {
        "team_score": state.team_score,
        "children": {},
    }
    for name in state.children:
        session_stats["children"][name] = {
            "correct": state.questions_correct[name],
            "asked": state.questions_asked[name],
            "new_learned": state.new_introduced[name],
            "mastered": state.items_mastered[name],
        }

    # Generate score report
    report = generate_score_report(
        state.team, list(state.children.values()), session_stats, state.session_number
    )

    # Get cliffhanger
    cliffhanger = get_cliffhanger(state.session_number)
    state.team.cliffhanger = cliffhanger

    # Get secret mission for next session
    secret_mission = None
    if state.session_number % 2 == 0:
        next_session = state.session_number + 1
        mission = get_secret_mission(next_session)
        secret_mission = {
            "description": mission,
            "assigned_session": next_session,
        }
        state.team.secret_mission = secret_mission

    return {
        "session_stats": session_stats,
        "report_text": report,
        "cliffhanger": cliffhanger,
        "secret_mission": secret_mission,
    }
