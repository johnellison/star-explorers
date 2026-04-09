"""Unit tests for game_engine.py"""

import pytest
import json
from datetime import datetime

# Import game engine components
from models import ChildProfile, TeamState, Question
from session import SessionState
from game_engine import GameEngine


@pytest.fixture
def sample_children():
    """Create sample children for testing."""
    return [
        ChildProfile(
            name="Reuben",
            age=7,
            title="Code Breaker",
            color="#FF69B4",
        ),
        ChildProfile(
            name="Jesse",
            age=4,
            title="Sound Seeker",
            color="#87CEEB",
        ),
    ]


@pytest.fixture
def sample_team():
    """Create sample team for testing."""
    return TeamState(
        team_name="Star Explorers",
        total_adventure_points=0,
        sessions_completed=0,
        current_arc=1,
        current_chapter=1,
        arc_name="The Enchanted Forest",
        characters_met=[],
        achievements=[],
        lightning_round_record=5,
    )


@pytest.fixture
def sample_session_state(sample_children, sample_team):
    """Create sample session state for testing."""
    return SessionState(
        session_number=1,
        children=sample_children,
        team=sample_team,
    )


def test_game_engine_initialization(sample_session_state):
    """Test GameEngine initializes with session state."""
    engine = GameEngine(sample_session_state)
    assert engine.state is not None
    assert engine.state == sample_session_state


def test_get_act(sample_session_state):
    """Test getting act information."""
    engine = GameEngine(sample_session_state)

    # Test act 1
    act = engine.get_act(1)
    assert act["act_num"] == 1
    assert act["act_name"] == "Opening Ritual"
    assert act["content_type"] == "intro"

    # Test act 3 (boss)
    act = engine.get_act(3)
    assert act["act_num"] == 3
    assert act["act_name"] == "Boss Challenge"
    assert act["content_type"] == "boss"


def test_get_progress_data(sample_session_state):
    """Test getting progress data."""
    engine = GameEngine(sample_session_state)
    progress = engine.get_progress_data()

    assert progress["team_score"] == 0
    assert progress["current_act"] == 1
    assert progress["elapsed_minutes"] >= 0
    assert "children" in progress
    assert "Reuben" in progress["children"]
    assert "Jesse" in progress["children"]


def test_submit_answer_correct(sample_session_state):
    """Test submitting a correct answer."""
    engine = GameEngine(sample_session_state)
    result = engine.submit_answer("Reuben", correct=True)

    assert result["success"] is True
    assert "result" in result
    assert result["result"]["correct"] is True
    assert result["result"]["points_earned"] in (3, 5)  # 5 if no hint, 3 if hint used


def test_submit_answer_wrong(sample_session_state):
    """Test submitting a wrong answer."""
    engine = GameEngine(sample_session_state)
    result = engine.submit_answer("Reuben", correct=False)

    assert result["success"] is True
    assert "result" in result
    assert result["result"]["correct"] is False
    assert result["result"]["points_earned"] == 0


def test_submit_answer_with_hint(sample_session_state):
    """Test submitting answer with hint used."""
    engine = GameEngine(sample_session_state)
    result = engine.submit_answer("Reuben", correct=True, hint_used=True)

    assert result["success"] is True
    assert result["result"]["points_earned"] == 3  # Fewer points with hint


def test_check_act_completion(sample_session_state):
    """Test checking act completion."""
    engine = GameEngine(sample_session_state)

    # Initially act 1 is not complete
    assert engine.check_act_completion(1) is False

    # Complete act 1
    engine.complete_act(1)

    # Now act 1 should be complete
    assert engine.check_act_completion(1) is True


def test_complete_act_advances_act(sample_session_state):
    """Test that completing act advances to next act."""
    engine = GameEngine(sample_session_state)

    assert engine.state.current_act == 1
    engine.complete_act(1)
    assert engine.state.current_act == 2


def test_check_session_completion(sample_session_state):
    """Test checking session completion."""
    engine = GameEngine(sample_session_state)

    # Initially not complete
    assert engine.check_session_completion() is False

    # Complete all acts
    for i in range(1, 6):
        engine.complete_act(i)

    # Now complete
    assert engine.check_session_completion() is True


def test_get_progress_data_includes_streak(sample_session_state):
    """Test that progress data includes streak information."""
    engine = GameEngine(sample_session_state)

    # Submit some correct answers to build streak
    engine.submit_answer("Reuben", correct=True)
    engine.submit_answer("Reuben", correct=True)
    engine.submit_answer("Reuben", correct=True)

    progress = engine.get_progress_data()
    assert progress["children"]["Reuben"]["streak"] == 3


def test_session_state_children_sorted(sample_session_state):
    """Test that SessionState sorts children by age."""
    # Jesse is younger (4) than Reuben (7)
    sorted_children = sample_session_state.sorted_children()
    assert len(sorted_children) == 2
    assert sorted_children[0].name == "Jesse"  # Youngest first
    assert sorted_children[1].name == "Reuben"


def test_session_state_elapsed_time(sample_session_state):
    """Test SessionState elapsed time calculation."""
    state = sample_session_state

    # Initially no start time
    assert state.elapsed_minutes == 0
    assert state.elapsed_str == "00:00"

    # Manually set start time
    import time

    state.start_time = time.time() - 180  # 3 minutes ago

    # Should show 3 minutes elapsed
    assert state.elapsed_minutes == 3
    assert state.elapsed_str == "03:00"
