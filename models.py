"""Data models for Star Explorers."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json
import os
import shutil

_SOURCE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def _prepare_data_dir() -> str:
    """Resolve and initialize the writable data directory for the app."""
    configured_dir = os.environ.get("STAR_EXPLORERS_DATA_DIR")
    if configured_dir:
        data_dir = os.path.abspath(configured_dir)
    elif os.environ.get("VERCEL"):
        # Vercel functions have a read-only filesystem, so use scratch space.
        data_dir = "/tmp/star-explorers-data"
    else:
        data_dir = _SOURCE_DATA_DIR

    os.makedirs(data_dir, exist_ok=True)

    for subdir in ["children", "question_bank", "sessions"]:
        src = os.path.join(_SOURCE_DATA_DIR, subdir)
        dest = os.path.join(data_dir, subdir)
        if not os.path.exists(dest):
            shutil.copytree(src, dest)

    team_src = os.path.join(_SOURCE_DATA_DIR, "team.json")
    team_dest = os.path.join(data_dir, "team.json")
    if not os.path.exists(team_dest) and os.path.exists(team_src):
        shutil.copy2(team_src, team_dest)

    return data_dir


DATA_DIR = _prepare_data_dir()


@dataclass
class SpacedRepItem:
    """A single item tracked by the spaced repetition system."""
    item_id: str
    box: int = 1
    ease: float = 2.5
    interval_sessions: int = 1
    next_review_session: int = 1
    streak: int = 0
    times_seen: int = 0
    times_correct: int = 0
    last_result: str = ""
    introduced_session: int = 1
    mastered: bool = False

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class TopicProgress:
    """Progress within a single topic for a child."""
    topic_id: str
    subject: str
    difficulty_tier: int = 1
    items: dict = field(default_factory=dict)  # item_id -> SpacedRepItem

    @property
    def mastery_pct(self):
        if not self.items:
            return 0
        mastered = sum(1 for i in self.items.values() if i.mastered)
        return int((mastered / len(self.items)) * 100)

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            "subject": self.subject,
            "difficulty_tier": self.difficulty_tier,
            "items": {k: v.to_dict() for k, v in self.items.items()},
        }

    @classmethod
    def from_dict(cls, d):
        items = {}
        for k, v in d.get("items", {}).items():
            items[k] = SpacedRepItem.from_dict(v)
        return cls(
            topic_id=d["topic_id"],
            subject=d["subject"],
            difficulty_tier=d.get("difficulty_tier", 1),
            items=items,
        )


@dataclass
class ChildProfile:
    """Profile and progress for one child."""
    name: str
    age: int
    character_name: str
    character_title: str
    sessions_completed: int = 0
    total_correct: int = 0
    power_level: int = 1
    topics: dict = field(default_factory=dict)  # topic_id -> TopicProgress
    interests: list = field(default_factory=list)
    favourite_formats: list = field(default_factory=list)
    frustration_triggers: list = field(default_factory=list)

    @property
    def power_level_name(self):
        names = {
            1: "Apprentice Explorer",
            2: "Junior Explorer",
            3: "Explorer",
            4: "Senior Explorer",
            5: "Master Explorer",
            6: "Grand Explorer",
            7: "Legendary Explorer",
        }
        return names.get(self.power_level, "Legendary Explorer")

    def update_power_level(self):
        thresholds = [0, 51, 151, 301, 501, 801, 1201]
        for i, t in enumerate(thresholds):
            if self.total_correct >= t:
                self.power_level = i + 1

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "character_name": self.character_name,
            "character_title": self.character_title,
            "sessions_completed": self.sessions_completed,
            "total_correct": self.total_correct,
            "power_level": self.power_level,
            "topics": {k: v.to_dict() for k, v in self.topics.items()},
            "interests": self.interests,
            "favourite_formats": self.favourite_formats,
            "frustration_triggers": self.frustration_triggers,
        }

    @classmethod
    def from_dict(cls, d):
        topics = {}
        for k, v in d.get("topics", {}).items():
            topics[k] = TopicProgress.from_dict(v)
        c = cls(
            name=d["name"],
            age=d["age"],
            character_name=d["character_name"],
            character_title=d["character_title"],
            sessions_completed=d.get("sessions_completed", 0),
            total_correct=d.get("total_correct", 0),
            power_level=d.get("power_level", 1),
            topics=topics,
            interests=d.get("interests", []),
            favourite_formats=d.get("favourite_formats", []),
            frustration_triggers=d.get("frustration_triggers", []),
        )
        return c

    def save(self):
        path = os.path.join(DATA_DIR, "children", f"{self.name.lower()}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, name):
        path = os.path.join(DATA_DIR, "children", f"{name.lower()}.json")
        with open(path) as f:
            return cls.from_dict(json.load(f))


@dataclass
class Question:
    """A single question from the question bank."""
    id: str
    subject: str
    topic: str
    difficulty_tier: int
    age_range: list
    read_aloud: str
    correct_answers: list
    correct_response: str
    incorrect_response: str
    hint: str
    format: str = "open_ended"
    tags: list = field(default_factory=list)
    mnemonic: str = ""
    metacognitive_prompt: str = ""

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Callback:
    """A memorable moment to reference in future sessions."""
    session: int
    child: str
    event: str
    used: bool = False

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class TeamState:
    """Shared team state across all sessions."""
    team_name: str = "Star Explorers"
    total_adventure_points: int = 0
    sessions_completed: int = 0
    achievements: list = field(default_factory=list)
    current_arc: int = 1
    current_chapter: int = 1
    arc_name: str = "The Enchanted Forest"
    current_world: int = 1
    current_level: int = 1
    characters_met: list = field(default_factory=lambda: ["Captain Starlight"])
    items_collected: list = field(default_factory=list)
    completed_levels: list = field(default_factory=list)
    collected_relics: list = field(default_factory=list)
    story_flags: dict = field(default_factory=dict)
    active_objective: str = ""
    current_reward: dict = field(default_factory=dict)
    character_status: dict = field(default_factory=dict)
    world_unlocks: list = field(default_factory=lambda: ["The Enchanted Forest"])
    cliffhanger: str = ""
    callbacks: list = field(default_factory=list)
    secret_mission: dict = field(default_factory=dict)
    lightning_round_record: int = 0
    rhyme_chain_record: int = 0
    multiple_choice_mode: bool = False
    tts_enabled: bool = False

    def to_dict(self):
        d = self.__dict__.copy()
        d["callbacks"] = [c.to_dict() if isinstance(c, Callback) else c for c in self.callbacks]
        return d

    @classmethod
    def from_dict(cls, d):
        normalized = dict(d)
        if "collected_relics" not in normalized and normalized.get("items_collected"):
            normalized["collected_relics"] = list(normalized.get("items_collected", []))
        if "completed_levels" not in normalized and normalized.get("sessions_completed", 0):
            normalized["completed_levels"] = []
        if "world_unlocks" not in normalized:
            normalized["world_unlocks"] = [normalized.get("arc_name") or "The Enchanted Forest"]

        t = cls(**{k: v for k, v in normalized.items()
                   if k in cls.__dataclass_fields__ and k != "callbacks"})
        t.callbacks = [Callback.from_dict(c) if isinstance(c, dict) else c
                       for c in normalized.get("callbacks", [])]
        if not t.items_collected and t.collected_relics:
            t.items_collected = list(t.collected_relics)
        return t

    def save(self):
        path = os.path.join(DATA_DIR, "team.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls):
        path = os.path.join(DATA_DIR, "team.json")
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))


@dataclass
class SessionLog:
    """Log of a single session."""
    session_number: int
    date: str
    duration_minutes: int = 0
    children: dict = field(default_factory=dict)  # name -> {asked, correct, new, reviewed}
    team_score: int = 0
    achievements_earned: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    callbacks_created: list = field(default_factory=list)

    def to_dict(self):
        return self.__dict__.copy()

    def save(self):
        path = os.path.join(DATA_DIR, "sessions", f"session_{self.session_number:03d}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
