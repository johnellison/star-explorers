"""Game Engine - pure game flow logic without UI concerns."""

from models import ChildProfile, TeamState, Question
from session import (
    SessionState,
    start_session,
    record_answer,
    get_questions_for_round,
    get_boss_challenge,
    get_lightning_round_questions,
    save_session,
    get_session_summary,
)


class GameEngine:
    """Pure game flow orchestrator - no UI concerns."""

    def __init__(self, session_state: SessionState):
        self.state = session_state

    def initialize_session(self) -> None:
        """Initialize a new session. UI should display hook."""
        # Session already initialized with start time
        pass

    def get_act(self, act_num: int) -> dict:
        """Get act content for display.

        Returns dict with:
        - act_num: int - current act number
        - act_name: str - act label
        - content_type: str - type of content (question, story, break, etc.)
        - content: dict - act-specific data
        """
        act_labels = {
            1: {"name": "Opening Ritual", "type": "intro"},
            2: {"name": "First Quest", "type": "quest"},
            3: {"name": "Boss Challenge", "type": "boss"},
            4: {"name": "Second Quest", "type": "quest"},
            5: {"name": "Closing Ritual", "type": "closing"},
        }

        act_info = act_labels.get(act_num, {"name": "Unknown", "type": "intro"})

        return {
            "act_num": act_num,
            "act_name": act_info["name"],
            "content_type": act_info["type"],
        }

    def get_current_question_for_child(
        self, child_name: str, queue_key: str = "scheduled"
    ) -> tuple:
        """Get next question for a child from their queue.

        Returns (question, sr_item) or (None, None) if queue empty.
        """
        questions = get_questions_for_round(self.state, child_name, queue_key, count=1)

        if questions:
            return questions[0]  # Return first question with spaced rep item

        return (None, None)

    def submit_answer(
        self, child_name: str, correct: bool, hint_used: bool = False
    ) -> dict:
        """Submit an answer and return result.

        Returns dict with:
        - success: bool - whether answer was accepted
        - result: dict - from record_answer() function
        - new_difficulty_tier: int - adjusted difficulty tier for child
        """
        # Get current question's spaced rep item (if any)
        sr_item = None  # In a real implementation, track current question

        result = record_answer(self.state, child_name, correct, hint_used, sr_item)

        return {
            "success": True,
            "result": result,
            "new_difficulty_tier": self.state.difficulty_override.get(child_name, 0),
        }

    def check_act_completion(self, act_num: int) -> bool:
        """Check if current act is complete.

        For simple implementation, return True if current act matches act_num.
        Real implementation would track act-specific completion.
        """
        return self.state.current_act >= act_num

    def check_session_completion(self) -> bool:
        """Check if session is complete.

        Returns True if all acts completed.
        """
        return self.state.current_act >= 5

    def complete_act(self, act_num: int) -> None:
        """Mark act as complete and move to next."""
        self.state.current_act = act_num + 1

    def complete_session(self) -> dict:
        """Finalize session and generate summary.

        Returns session summary dict.
        """
        save_session(self.state)
        summary = get_session_summary(self.state)

        return summary

    def get_boss_data(self) -> dict:
        """Get boss challenge data for current session.

        Returns dict with boss intro and challenge parts.
        """
        return get_boss_challenge(self.state)

    def get_lightning_round_data(self) -> list:
        """Get lightning round questions.

        Returns list of (child_name, Question) tuples.
        """
        return get_lightning_round_questions(self.state)

    def get_progress_data(self) -> dict:
        """Get progress data for UI display.

        Returns dict with session stats and child progress.
        """
        return {
            "team_score": self.state.team_score,
            "current_act": self.state.current_act,
            "elapsed_minutes": self.state.elapsed_minutes,
            "elapsed_str": self.state.elapsed_str,
            "children": {
                name: {
                    "correct": self.state.questions_correct[name],
                    "asked": self.state.questions_asked[name],
                    "new_learned": self.state.new_introduced[name],
                    "mastered": self.state.items_mastered[name],
                    "streak": self.state.streak[name],
                }
                for name in self.state.children
            },
        }
