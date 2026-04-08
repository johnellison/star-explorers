#!/usr/bin/env python3
"""Star Explorers Web GUI - Flask server with state machine."""

import sys
import os
import time
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, send_from_directory

from models import ChildProfile, TeamState, SessionLog, DATA_DIR
from spaced_rep import process_answer, build_session_queue, introduce_item
from questions import (
    load_question_bank,
    get_questions_for_child,
    get_boss_questions,
    get_lightning_round,
)
from story import (
    CAMPAIGN_WORLDS,
    build_campaign_snapshot,
    build_story_flags,
    get_boss_victory,
    get_break_payload,
    generate_recap,
    get_arc,
    get_character_status,
    get_cliffhanger,
    generate_score_report,
    get_level,
    get_secret_mission,
    get_session_position,
    get_story_beat,
    get_story_hook,
    get_boss_intro,
)

app = Flask(__name__, static_folder="static")

# Single active session (only one dad at a time)
active_session = None


class WebSessionState:
    """Server-side state machine for a web session."""

    PHASES = [
        "pre_session",
        "act1_greeting",
        "act1_recap",
        "act1_warmup",
        "act1_story_hook",
        "act2_round1",
        "act2_story_beat1",
        "act2_round2",
        "act2_story_beat2",
        "movement_break",
        "act3_boss_intro",
        "act3_boss",
        "silly_break",
        "act4_review",
        "act4_treasure",
        "act4_lightning",
        "act5_score",
        "act5_power_levels",
        "act5_cliffhanger",
        "act5_mission",
        "complete",
    ]

    def __init__(self, children, team):
        self.session_number = team.sessions_completed + 1
        self.children = {c.name: c for c in children}
        self.team = team
        self.team_score = 0
        self.start_time = time.time()

        self.phase = "pre_session"
        self.phase_index = 0

        # Per-child tracking
        self.questions_asked = {c.name: 0 for c in children}
        self.questions_correct = {c.name: 0 for c in children}
        self.new_introduced = {c.name: 0 for c in children}
        self.items_mastered = {c.name: [] for c in children}
        self.streak = {c.name: 0 for c in children}
        self.consecutive_wrong = {c.name: 0 for c in children}
        self.achievements_earned = []

        # Question state
        self.question_bank = load_question_bank()
        self.session_queues = {}
        for child in children:
            self.session_queues[child.name] = build_session_queue(
                child, self.session_number, self.question_bank
            )

        # Current question being asked
        self.current_question = None
        self.current_child = None
        self.current_sr_item = None
        self.used_hint = False

        # Phase-specific state
        self.warmup_queue = []
        self.round_queue = []
        self.boss_challenges = []
        self.boss_index = 0
        self.boss_part_index = 0
        self.boss_all_correct = True
        self.lightning_queue = []
        self.lightning_index = 0
        self.lightning_correct = 0
        self.treasure_queue = []

        self._build_warmup_queue()
        self._build_round_queues()
        self._build_boss_challenges()
        self._build_lightning()
        self._build_treasure()

    def sorted_children(self):
        return sorted(self.children.values(), key=lambda c: c.age)

    @property
    def elapsed_minutes(self):
        return int((time.time() - self.start_time) / 60)

    def add_points(self, points):
        self.team_score += points
        self.team.total_adventure_points += points

    def _build_warmup_queue(self):
        queue = []
        for child in self.sorted_children():
            warmup = self.session_queues.get(child.name, {}).get("warmup", [])
            for q, sr in warmup[:2]:
                queue.append((child.name, q, sr))
        self.warmup_queue = queue

    def _build_round_queues(self):
        children = self.sorted_children()
        r1 = []
        r2 = []
        for child in children:
            sq = self.session_queues.get(child.name, {})
            mandatory = sq.get("mandatory", [])
            for q, sr in mandatory[:3]:
                r1.append((child.name, q, sr))
            new_items = sq.get("new", [])
            scheduled = sq.get("scheduled", [])
            source = (
                new_items if self.new_introduced.get(child.name, 0) < 3 else scheduled
            )
            for q, sr in source[:3]:
                r2.append((child.name, q, sr))
        self.round1_queue = r1
        self.round2_queue = r2

    def _build_boss_challenges(self):
        child_ages = {c.name: c.age for c in self.sorted_children()}
        self.boss_challenges = get_boss_questions(self.question_bank, child_ages)[:3]
        self.boss_index = 0
        self.boss_part_index = 0

    def _build_lightning(self):
        child_ages = {c.name: c.age for c in self.sorted_children()}
        self.lightning_queue = get_lightning_round(
            self.question_bank, child_ages, count=8
        )
        self.lightning_index = 0
        self.lightning_correct = 0

    def _build_treasure(self):
        queue = []
        for child in self.sorted_children():
            qs = get_questions_for_child(self.question_bank, child.age)
            hard = [q for q in qs if q.difficulty_tier >= 3]
            if hard:
                queue.append((child.name, random.choice(hard), None))
        self.treasure_queue = queue

    @staticmethod
    def _arc_slug(arc_name):
        return arc_name.lower().replace("the ", "").replace(" ", "_")

    def _all_interests(self):
        """Gather the union of all children's interests."""
        interests = []
        for c in self.children.values():
            interests.extend(getattr(c, "interests", []))
        return list(set(interests))

    def get_current_screen(self):
        """Return the current screen data for the frontend."""
        arc_num, position = get_session_position(self.session_number)
        arc = get_arc(arc_num)
        level = get_level(self.session_number)
        arc_slug = self._arc_slug(arc["name"])
        campaign = build_campaign_snapshot(self.team, self.session_number)

        base = {
            "phase": self.phase,
            "session_number": self.session_number,
            "team_score": self.team_score,
            "elapsed_minutes": self.elapsed_minutes,
            "arc_name": arc["name"],
            "world_number": level["world_number"],
            "level_number": level["level_number"],
            "level_name": level["level_name"],
            "active_objective": level["objective"],
            "campaign": campaign,
            "children": {
                name: {
                    "age": c.age,
                    "character_name": c.character_name,
                    "character_title": c.character_title,
                    "power_level": c.power_level,
                    "power_level_name": c.power_level_name,
                    "total_correct": c.total_correct,
                    "sessions_completed": c.sessions_completed,
                    "asked": self.questions_asked[name],
                    "correct": self.questions_correct[name],
                }
                for name, c in self.children.items()
            },
            "team": {
                "total_adventure_points": self.team.total_adventure_points,
                "sessions_completed": self.team.sessions_completed,
                "achievements": self.team.achievements,
                "lightning_round_record": self.team.lightning_round_record,
                "completed_levels": self.team.completed_levels,
                "collected_relics": self.team.collected_relics,
                "current_reward": self.team.current_reward,
                "world_unlocks": self.team.world_unlocks,
            },
        }

        if self.phase == "pre_session":
            base["screen"] = "pre_session"
            base["date"] = datetime.now().strftime("%A, %d %B %Y")
            base["image"] = f"/static/images/arcs/{arc_slug}.png"
            base["topics"] = {}
            for name, child in self.children.items():
                topics = {}
                for tid, t in child.topics.items():
                    topics[tid] = {
                        "subject": t.subject,
                        "mastery_pct": t.mastery_pct,
                        "items_count": len(t.items),
                    }
                base["topics"][name] = topics

        elif self.phase == "act1_greeting":
            base["screen"] = "story"
            if self.session_number == 1:
                names = " and ".join(c.name for c in self.sorted_children())
                base["title"] = "WELCOME, STAR EXPLORERS!"
                base["text"] = (
                    f"Hey {names}! I have something REALLY special for today. "
                    f"Are you ready? We're going to play a brand new game called "
                    f"STAR EXPLORERS!\n\n"
                    f"In this game, you are both explorers on an amazing adventure. "
                    f"Our team is called... THE STAR EXPLORERS!\n\n"
                    f"Let's practice our team chant:\n"
                    f"I'll say: 'Adventurers, are you ready?'\n"
                    f"And you both say: 'READY FOR ADVENTURE!'\n\n"
                    f"Today's first level is {level['level_name']}.\n"
                    f"Mission: {level['objective']}"
                )
            else:
                base["title"] = f"MISSION BRIEFING · LEVEL {position}"
                base["text"] = (
                    f"Adventurers, are you ready?\n\n"
                    f"[Wait for: READY FOR ADVENTURE!]\n\n"
                    f"Current level: {level['level_name']}\n"
                    f"Mission: {level['objective']}"
                )

        elif self.phase == "act1_recap":
            base["screen"] = "story"
            base["title"] = "CAMPAIGN RECAP"
            recap = generate_recap(self.team, list(self.children.values()))
            base["text"] = recap if recap else "This is our first adventure!"
            if self.team.secret_mission:
                base["secret_mission"] = self.team.secret_mission.get("description", "")

        elif self.phase == "act1_warmup":
            base = self._question_screen(base, self.warmup_queue, "LEVEL START")

        elif self.phase == "act1_story_hook":
            base["screen"] = "story"
            base["title"] = f"LEVEL {position}: {level['level_name']}"
            base["text"] = get_story_hook(self.session_number)
            base["style"] = "adventure"
            base["image"] = f"/static/images/hooks/arc{arc_num}_hook{position}.png"

        elif self.phase == "act2_round1":
            base = self._question_screen(base, self.round1_queue, "OBJECTIVE PHASE 1")

        elif self.phase in ("act2_story_beat1", "act2_story_beat2"):
            base["screen"] = "story"
            base["title"] = "LEVEL UPDATE"
            beat_num = 0 if self.phase == "act2_story_beat1" else 1
            base["text"] = get_story_beat(
                self.session_number, beat_num, self._all_interests()
            )
            base["style"] = "story"
            base["image"] = f"/static/images/arcs/{arc_slug}.png"

        elif self.phase == "act2_round2":
            base = self._question_screen(base, self.round2_queue, "OBJECTIVE PHASE 2")

        elif self.phase == "movement_break":
            movement_break = get_break_payload(self.session_number, "movement")
            base["screen"] = "break"
            base["break_type"] = "movement"
            base["title"] = movement_break["title"]
            base["text"] = movement_break["text"]
            base["break_interaction"] = movement_break.get("interaction")

        elif self.phase == "act3_boss_intro":
            base["screen"] = "boss_intro"
            base["title"] = f"LEVEL BOSS · {level['level_name']}"
            base["text"] = get_boss_intro(self.session_number)
            base["image"] = "/static/images/boss/puzzle_goblin_challenge.png"

        elif self.phase == "act3_boss":
            base = self._boss_screen(base)

        elif self.phase == "silly_break":
            silly_break = get_break_payload(self.session_number, "silly")
            base["screen"] = "break"
            base["break_type"] = "silly"
            base["title"] = silly_break["name"]
            base["text"] = silly_break["read_aloud"]

        elif self.phase == "act4_review":
            scheduled_queue = []
            for child in self.sorted_children():
                sq = self.session_queues.get(child.name, {})
                for q, sr in sq.get("scheduled", [])[:3]:
                    scheduled_queue.append((child.name, q, sr))
            base = self._question_screen(base, scheduled_queue, "FINAL STRETCH")

        elif self.phase == "act4_treasure":
            base = self._question_screen(base, self.treasure_queue, "BONUS ROUTE")
            base["is_treasure"] = True

        elif self.phase == "act4_lightning":
            base = self._lightning_screen(base)

        elif self.phase == "act5_score":
            base["screen"] = "score_report"
            session_stats = {
                "team_score": self.team_score,
                "children": {},
            }
            for name in self.children:
                session_stats["children"][name] = {
                    "correct": self.questions_correct[name],
                    "asked": self.questions_asked[name],
                    "new_learned": self.new_introduced[name],
                    "mastered": self.items_mastered[name],
                }
            base["report"] = generate_score_report(
                self.team, list(self.children.values()), session_stats, self.session_number
            )
            base["stats"] = session_stats
            base["reward"] = level["reward"]
            base["world_complete"] = level["world_complete"]
            base["next_level"] = level["next_level"]

        elif self.phase == "act5_power_levels":
            base["screen"] = "power_levels"
            base["levels"] = {
                c.name: {
                    "power_level": c.power_level,
                    "power_level_name": c.power_level_name,
                    "total_correct": c.total_correct,
                }
                for c in self.sorted_children()
            }
            base["reward"] = level["reward"]
            base["world_complete"] = level["world_complete"]
            base["next_level"] = level["next_level"]

        elif self.phase == "act5_cliffhanger":
            base["screen"] = "cliffhanger"
            base["title"] = (
                f"WORLD {level['world_number']} CLEAR"
                if level["world_complete"]
                else f"NEXT LEVEL UNLOCKED · {level['next_level']['level_name']}"
            )
            base["text"] = get_cliffhanger(self.session_number)
            base["image"] = (
                f"/static/images/cliffhangers/arc{arc_num}_cliff{position}.png"
            )
            base["world_complete"] = level["world_complete"]
            base["next_level"] = level["next_level"]

        elif self.phase == "act5_mission":
            base["screen"] = "story"
            if self.session_number % 2 == 0:
                mission = get_secret_mission(self.session_number, self._all_interests())
                base["title"] = "SIDE QUEST"
                base["text"] = (
                    f"Captain Starlight has a SIDE QUEST for you this week!\n\n"
                    f"{mission}\n\n"
                    f"Next time, you'll get BONUS POINTS for completing it!"
                )
            else:
                names = " and ".join(c.name for c in self.sorted_children())
                base["title"] = "RETURN TO THE MAP"
                base["text"] = (
                    f"Star Explorers, level clear!\n\n"
                    f"Captain Starlight marks the next route on the map for {names}. "
                    f"The adventure continues next session."
                )

        elif self.phase == "complete":
            base["screen"] = "complete"
            names = " and ".join(c.name for c in self.sorted_children())
            if self.session_number >= 25:
                base["title"] = "CAMPAIGN COMPLETE"
                base["text"] = (
                    f"Star Explorers, you restored every world.\n\n"
                    f"Captain Starlight crowns {names} as true Star Explorers. "
                    f"The map is bright again, and a new adventure can begin whenever you are ready."
                )
            else:
                base["title"] = "LEVEL COMPLETE"
                base["text"] = (
                    f"Star Explorers, level complete!\n\n"
                    f"Captain Starlight sends {names} back to mission control to rest before the next route unlocks."
                )
            base["final_score"] = self.team_score
            base["image"] = "/static/images/ui/mission_complete.png"

        return base

    def _question_screen(self, base, queue, label):
        if not queue:
            base["screen"] = "story"
            base["title"] = label
            base["text"] = "All done with this round! Great work!"
            base["auto_continue"] = True
            return base

        child_name, question, sr_item = queue[0]
        self.current_child = child_name
        self.current_question = question
        self.current_sr_item = sr_item
        self.used_hint = False

        base["screen"] = "question"
        base["label"] = label
        base["current_child"] = child_name
        base["multiple_choice_mode"] = self.team.multiple_choice_mode
        base["objective"] = get_level(self.session_number)["objective"]
        base["question"] = {
            "id": question.id,
            "read_aloud": question.read_aloud,
            "correct_answers": question.correct_answers,
            "correct_response": question.correct_response,
            "incorrect_response": question.incorrect_response,
            "hint": question.hint,
            "format": question.format,
            "metacognitive_prompt": question.metacognitive_prompt,
            "mnemonic": question.mnemonic,
        }
        base["remaining"] = len(queue)
        return base

    def _boss_screen(self, base):
        level = get_level(self.session_number)
        if self.boss_index >= len(self.boss_challenges):
            base["screen"] = "story"
            base["title"] = "BOSS DEFEATED!"
            base["text"] = get_boss_victory(self.session_number)
            return base

        challenge = self.boss_challenges[self.boss_index]

        if self.boss_part_index >= len(challenge["parts"]):
            # Show celebration/consolation
            if self.boss_all_correct:
                self.add_points(8)
                base["screen"] = "boss_victory"
                base["title"] = "BOSS DEFEATED!"
                base["text"] = challenge["celebration"] or get_boss_victory(self.session_number)
                base["image"] = "/static/images/boss/puzzle_goblin_defeated.png"
                base["reward"] = level["reward"]
            else:
                base["screen"] = "story"
                base["title"] = "KEEP GOING!"
                base["text"] = (
                    "So close! You almost had it! The Puzzle Goblin grins: "
                    "'Not bad... not bad at all. Let's try the next one!'"
                )
            return base

        part = challenge["parts"][self.boss_part_index]
        question = part["question"]
        child_name = part["child"]

        self.current_child = child_name
        self.current_question = question
        self.current_sr_item = None
        self.used_hint = False

        base["screen"] = "question"
        base["label"] = f"BOSS CHALLENGE {self.boss_index + 1}/3"
        base["is_boss"] = True
        base["current_child"] = child_name
        base["boss_intro_text"] = challenge["intro"]
        base["objective"] = level["objective"]
        base["multiple_choice_mode"] = self.team.multiple_choice_mode
        base["question"] = {
            "id": question.id,
            "read_aloud": question.read_aloud,
            "correct_answers": question.correct_answers,
            "correct_response": question.correct_response,
            "incorrect_response": question.incorrect_response,
            "hint": question.hint,
            "format": question.format,
            "metacognitive_prompt": question.metacognitive_prompt,
            "mnemonic": question.mnemonic,
        }
        return base

    def _lightning_screen(self, base):
        if self.lightning_index >= len(self.lightning_queue):
            # Lightning round complete
            base["screen"] = "lightning_result"
            base["lightning_correct"] = self.lightning_correct
            base["lightning_total"] = len(self.lightning_queue)
            base["record"] = self.team.lightning_round_record
            new_record = self.lightning_correct > self.team.lightning_round_record
            base["new_record"] = new_record
            if new_record:
                self.team.lightning_round_record = self.lightning_correct
                self.add_points(15)
            return base

        child_name, question = self.lightning_queue[self.lightning_index]
        self.current_child = child_name
        self.current_question = question
        self.current_sr_item = None
        self.used_hint = False

        base["screen"] = "question"
        base["label"] = "LIGHTNING ROUND!"
        base["is_lightning"] = True
        base["current_child"] = child_name
        base["lightning_index"] = self.lightning_index + 1
        base["lightning_total"] = len(self.lightning_queue)
        base["lightning_correct"] = self.lightning_correct
        base["objective"] = get_level(self.session_number)["objective"]
        base["multiple_choice_mode"] = self.team.multiple_choice_mode
        base["question"] = {
            "id": question.id,
            "read_aloud": question.read_aloud,
            "correct_answers": question.correct_answers,
            "correct_response": question.correct_response,
            "incorrect_response": question.incorrect_response,
            "hint": question.hint,
            "format": question.format,
            "metacognitive_prompt": question.metacognitive_prompt,
            "mnemonic": question.mnemonic,
        }
        return base

    def handle_action(self, action):
        """Handle a user action and advance the state machine.
        Returns dict with result info (for animations etc)."""
        result = {"action": action, "phase": self.phase}

        if action == "continue":
            self._advance_phase()
            result["new_phase"] = self.phase
            return result

        if action in ("correct", "wrong", "skip"):
            return self._handle_answer(action, result)

        if action == "hint":
            self.used_hint = True
            result["hint"] = self.current_question.hint if self.current_question else ""
            return result

        if action == "boss_next":
            self.boss_part_index = 0
            self.boss_index += 1
            self.boss_all_correct = True
            if self.boss_index >= len(self.boss_challenges):
                self._advance_phase()
            result["new_phase"] = self.phase
            return result

        return result

    def _handle_answer(self, action, result):
        child_name = self.current_child
        question = self.current_question
        sr_item = self.current_sr_item

        if action == "correct":
            correct = True
            self.questions_asked[child_name] += 1
            self.questions_correct[child_name] += 1
            self.streak[child_name] += 1
            self.consecutive_wrong[child_name] = 0

            child = self.children[child_name]
            child.total_correct += 1
            child.update_power_level()

            points = 5 if not self.used_hint else 3
            if self.phase == "act4_treasure":
                points = 10
            elif self.phase == "act4_lightning":
                points = 1
                self.lightning_correct += 1
            elif self.phase == "act3_boss":
                points = 3
            self.add_points(points)

            if sr_item:
                process_answer(sr_item, True, self.used_hint, self.session_number)

            result["correct"] = True
            result["points"] = points
            result["response"] = question.correct_response
            result["streak"] = self.streak[child_name]

            # Check streak achievements
            achievement = self._check_streak(child_name)
            if achievement:
                result["achievement"] = achievement

        elif action in ("wrong", "skip"):
            correct = False
            if action == "wrong":
                self.questions_asked[child_name] += 1
            self.streak[child_name] = 0
            self.consecutive_wrong[child_name] += 1

            if sr_item:
                process_answer(sr_item, False, False, self.session_number)

            result["correct"] = False
            result["response"] = question.incorrect_response
            result["consecutive_wrong"] = self.consecutive_wrong[child_name]

            if self.consecutive_wrong[child_name] >= 3:
                result["rescue"] = True
                self.consecutive_wrong[child_name] = 0

            if self.phase == "act3_boss":
                self.boss_all_correct = False

        # Advance to next question or next phase
        self._pop_current_question()
        result["new_phase"] = self.phase

        return result

    def _pop_current_question(self):
        """Remove current question from queue and advance if empty."""
        if self.phase == "act1_warmup":
            if self.warmup_queue:
                self.warmup_queue.pop(0)
            if not self.warmup_queue:
                self._advance_phase()

        elif self.phase == "act2_round1":
            if self.round1_queue:
                self.round1_queue.pop(0)
            if not self.round1_queue:
                self._advance_phase()

        elif self.phase == "act2_round2":
            if self.round2_queue:
                self.round2_queue.pop(0)
            if not self.round2_queue:
                self._advance_phase()

        elif self.phase == "act3_boss":
            self.boss_part_index += 1
            challenge = (
                self.boss_challenges[self.boss_index]
                if self.boss_index < len(self.boss_challenges)
                else None
            )
            if challenge and self.boss_part_index >= len(challenge["parts"]):
                pass  # Stay on boss phase to show victory/consolation

        elif self.phase == "act4_review":
            # Build temp scheduled queue
            scheduled_queue = []
            for child in self.sorted_children():
                sq = self.session_queues.get(child.name, {})
                for q, sr in sq.get("scheduled", [])[:3]:
                    scheduled_queue.append((child.name, q, sr))
            # Pop first scheduled item
            for child in self.sorted_children():
                sq = self.session_queues.get(child.name, {})
                scheduled = sq.get("scheduled", [])
                if scheduled:
                    scheduled.pop(0)
                    break
            # Check if all scheduled are done
            total_remaining = sum(
                len(self.session_queues.get(c.name, {}).get("scheduled", []))
                for c in self.sorted_children()
            )
            if total_remaining == 0:
                self._advance_phase()

        elif self.phase == "act4_treasure":
            if self.treasure_queue:
                self.treasure_queue.pop(0)
            if not self.treasure_queue:
                self._advance_phase()

        elif self.phase == "act4_lightning":
            self.lightning_index += 1
            if self.lightning_index >= len(self.lightning_queue):
                pass  # Stay to show results

    def _advance_phase(self):
        """Move to the next phase."""
        phase_order = [
            "pre_session",
            "act1_greeting",
            "act1_recap",
            "act1_warmup",
            "act1_story_hook",
            "act2_round1",
            "act2_story_beat1",
            "act2_round2",
            "act2_story_beat2",
            "movement_break",
            "act3_boss_intro",
            "act3_boss",
            "silly_break",
            "act4_review",
            "act4_treasure",
            "act4_lightning",
            "act5_score",
            "act5_power_levels",
            "act5_cliffhanger",
            "act5_mission",
            "complete",
        ]
        try:
            idx = phase_order.index(self.phase)
            if idx < len(phase_order) - 1:
                self.phase = phase_order[idx + 1]

                # Skip recap on first session
                if self.phase == "act1_recap" and self.session_number == 1:
                    self.phase = "act1_warmup"

                # Skip empty question phases
                if self.phase == "act1_warmup" and not self.warmup_queue:
                    self.phase = "act1_story_hook"
                if self.phase == "act2_round1" and not self.round1_queue:
                    self.phase = "act2_story_beat1"
                if self.phase == "act2_round2" and not self.round2_queue:
                    self.phase = "act2_story_beat2"

        except ValueError:
            self.phase = "complete"

    def _check_streak(self, child_name):
        streak = self.streak[child_name]
        achievements = {
            3: ("Hat Trick", f"{child_name} got THREE in a row!"),
            5: ("On Fire", f"{child_name} is ON FIRE! Five correct in a row!"),
        }
        if streak in achievements:
            name, desc = achievements[streak]
            full_name = f"{name} ({child_name})"
            if full_name not in self.team.achievements:
                self.team.achievements.append(full_name)
                self.achievements_earned.append(full_name)
                return {"name": name, "child": child_name, "description": desc}
        return None

    def save(self):
        """Save all session data."""
        self.team.sessions_completed = self.session_number
        arc_num, position = get_session_position(self.session_number)
        arc = get_arc(arc_num)
        level = get_level(self.session_number)
        self.team.current_arc = arc_num
        self.team.current_chapter = self.session_number
        self.team.arc_name = arc["name"]

        for char in arc.get("characters", []):
            if char not in self.team.characters_met:
                self.team.characters_met.append(char)

        completed_level_id = level["level_id"]
        if completed_level_id not in self.team.completed_levels:
            self.team.completed_levels.append(completed_level_id)

        reward_entry = {
            "world_number": level["world_number"],
            "world_name": level["world_name"],
            "level_number": level["level_number"],
            "level_name": level["level_name"],
            "name": level["reward"]["name"],
            "summary": level["reward"]["summary"],
            "icon": level["reward"]["icon"],
        }
        self.team.current_reward = reward_entry
        self.team.active_objective = level["objective"]
        if reward_entry["name"] not in self.team.collected_relics:
            self.team.collected_relics.append(reward_entry["name"])
        self.team.items_collected = list(self.team.collected_relics)

        unlocked_world_count = min(((self.session_number - 1) // 5) + 2, len(CAMPAIGN_WORLDS))
        self.team.world_unlocks = [
            get_arc(world_number)["name"] for world_number in range(1, unlocked_world_count + 1)
        ]

        next_session = min(self.session_number + 1, 25)
        next_level = get_level(next_session)
        self.team.current_world = next_level["world_number"]
        self.team.current_level = next_level["level_number"]
        self.team.story_flags = build_story_flags(self.session_number)
        self.team.character_status = get_character_status(self.session_number)

        self.team.cliffhanger = get_cliffhanger(self.session_number)

        if self.session_number % 2 == 0:
            mission = get_secret_mission(self.session_number)
            self.team.secret_mission = {
                "description": mission,
                "assigned_session": self.session_number,
            }

        self.team.save()

        for child in self.children.values():
            child.sessions_completed = self.session_number
            child.save()

        log = SessionLog(
            session_number=self.session_number,
            date=datetime.now().isoformat(),
            duration_minutes=self.elapsed_minutes,
            children={
                name: {
                    "asked": self.questions_asked[name],
                    "correct": self.questions_correct[name],
                    "new": self.new_introduced[name],
                }
                for name in self.children
            },
            team_score=self.team_score,
            achievements_earned=self.achievements_earned,
        )
        log.save()


def _load_children():
    children = []
    children_dir = os.path.join(DATA_DIR, "children")
    if not os.path.exists(children_dir):
        return children
    for filename in sorted(os.listdir(children_dir)):
        if filename.endswith(".json"):
            name = filename.replace(".json", "")
            try:
                children.append(ChildProfile.load(name))
            except Exception:
                pass
    return children


# --- Routes ---


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/session/start", methods=["POST"])
def start_session():
    global active_session
    children = _load_children()
    if not children:
        return jsonify({"error": "No child profiles found. Run setup first."}), 400
    team = TeamState.load()
    active_session = WebSessionState(children, team)
    return jsonify({"ok": True, "session_number": active_session.session_number})


@app.route("/api/state")
def get_state():
    if not active_session:
        return jsonify({"phase": "no_session"})
    return jsonify(active_session.get_current_screen())


@app.route("/api/action", methods=["POST"])
def do_action():
    if not active_session:
        return jsonify({"error": "No active session"}), 400
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action", "continue")
    result = active_session.handle_action(action)
    return jsonify(result)


@app.route("/api/session/end", methods=["POST"])
def end_session():
    global active_session
    if not active_session:
        return jsonify({"error": "No active session"}), 400
    active_session.save()
    summary = {
        "session_number": active_session.session_number,
        "team_score": active_session.team_score,
        "duration_minutes": active_session.elapsed_minutes,
        "children": {
            name: {
                "asked": active_session.questions_asked[name],
                "correct": active_session.questions_correct[name],
            }
            for name in active_session.children
        },
    }
    active_session = None
    return jsonify(summary)


@app.route("/api/stats")
def get_stats():
    children = _load_children()
    team = TeamState.load()
    return jsonify(
        {
            "team": team.to_dict(),
            "children": [c.to_dict() for c in children],
        }
    )


@app.route("/api/generate-choices", methods=["POST"])
def generate_choices():
    """Generate multiple-choice options for a question.

    Request body: {"question_id": str}
    Response: {"options": [{"id": str, "text": str}]} - shuffled, correct first
    """
    global active_session
    if not active_session:
        return jsonify({"error": "No active session"}), 400

    data = request.get_json(force=True, silent=True) or {}
    question_id = data.get("question_id")

    if not question_id:
        return jsonify({"error": "question_id required"}), 400

    # Find the question in the current question bank
    question = None
    for child_name, queue in active_session.session_queues.items():
        for q, sr in queue.get("scheduled", []):
            if q and q.id == question_id:
                question = q
                break
        if question:
            break

    if not question:
        return jsonify({"error": "Question not found"}), 404

    # Generate distractors from same age group and subject
    distractors = []

    # Get age-appropriate questions from bank
    age = None
    for child in active_session.children.values():
        if question.id in active_session.session_queues.get(child.name, {}).get(
            "new", []
        ):
            age = child.age
            break

    if age:
        # Get questions from same age group
        from questions import get_questions_for_child

        all_questions = get_questions_for_child(active_session.question_bank, age)

        # Filter for same subject/topic if available
        same_subject = []
        for q in all_questions:
            if q.id != question_id:
                # Same format (e.g., both open-ended or both multiple choice)
                if hasattr(q, "format") and hasattr(question, "format"):
                    if q.format == question.format:
                        same_subject.append(q)
                else:
                    # Simple: same subject
                    if hasattr(q, "subject") and hasattr(question, "subject"):
                        if q.subject == question.subject:
                            same_subject.append(q)

        # Pick 3 random distractors
        random.shuffle(same_subject)
        distractors = same_subject[:3]

    # Combine correct answer with distractors, shuffle
    all_options = question.correct_answers + distractors
    random.shuffle(all_options)

    # Ensure correct answer is first in options list (for frontend)
    # Move correct answer to position 0
    if question.correct_answers and question.correct_answers[0] in all_options:
        correct_answer = question.correct_answers[0]
        all_options.remove(correct_answer)
        all_options.insert(0, correct_answer)

    # Create option objects with IDs
    options = [
        {"id": f"opt_{i}", "text": opt}
        for i, opt in enumerate(all_options[:4])  # Max 4 options
    ]

    return jsonify({"options": options})


if __name__ == "__main__":
    # Ensure data dirs exist
    for subdir in ["children", "question_bank", "sessions"]:
        os.makedirs(os.path.join(DATA_DIR, subdir), exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
