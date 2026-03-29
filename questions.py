"""Question bank loader and manager."""

import json
import os
import random
from models import Question, DATA_DIR


def load_question_bank() -> list[Question]:
    """Load all questions from the question bank directory."""
    bank_dir = os.path.join(DATA_DIR, "question_bank")
    questions = []

    if not os.path.exists(bank_dir):
        return questions

    for filename in os.listdir(bank_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(bank_dir, filename)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        questions.append(Question.from_dict(item))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load {filename}: {e}")

    return questions


def get_questions_for_child(questions: list[Question], age: int,
                            subject: str = None,
                            topic: str = None,
                            difficulty_tier: int = None,
                            format_type: str = None) -> list[Question]:
    """Filter questions appropriate for a child."""
    filtered = []
    for q in questions:
        if age < q.age_range[0] or age > q.age_range[1]:
            continue
        if subject and q.subject != subject:
            continue
        if topic and q.topic != topic:
            continue
        if difficulty_tier is not None and q.difficulty_tier != difficulty_tier:
            continue
        if format_type and q.format != format_type:
            continue
        filtered.append(q)
    return filtered


def get_boss_questions(questions: list[Question],
                       child_ages: dict[str, int]) -> list[dict]:
    """Get questions for a cooperative boss challenge.

    Returns list of dicts with structure:
    {
        "intro": str,
        "parts": [
            {"child": name, "question": Question},
            {"child": name, "question": Question},
        ],
        "celebration": str,
    }
    """
    boss_questions = []

    # Get questions for each child
    for child_name, age in child_ages.items():
        child_qs = get_questions_for_child(questions, age)
        if child_qs:
            # Pick from reviewed/medium difficulty for boss challenges
            mid_tier = [q for q in child_qs if q.difficulty_tier <= 3]
            if mid_tier:
                boss_questions.append((child_name, random.choice(mid_tier)))

    # Build 3 boss challenges by pairing questions
    challenges = []
    sorted_names = sorted(child_ages.keys(), key=lambda n: child_ages[n])
    younger = sorted_names[0] if sorted_names else None
    older = sorted_names[-1] if len(sorted_names) > 1 else younger

    younger_qs = get_questions_for_child(questions, child_ages.get(younger, 4))
    older_qs = get_questions_for_child(questions, child_ages.get(older, 7))

    random.shuffle(younger_qs)
    random.shuffle(older_qs)

    intros = [
        "The Puzzle Goblin cackles: 'Try THIS one! You'll BOTH need to work together!'",
        "A mysterious door appears! To open it, BOTH explorers must answer!",
        "'One more!' shouts the Puzzle Goblin. 'And this one is my TRICKIEST yet!'",
    ]

    celebrations = [
        "AMAZING! You solved it together! The Puzzle Goblin stamps his foot: 'HOW?!'",
        "The door swings open! The light pours in! You did it as a TEAM!",
        "The Puzzle Goblin is speechless! Nobody has EVER solved all three! INCREDIBLE!",
    ]

    for i in range(min(3, len(younger_qs), len(older_qs))):
        challenges.append({
            "intro": intros[i % len(intros)],
            "parts": [
                {"child": younger, "question": younger_qs[i]},
                {"child": older, "question": older_qs[i]},
            ],
            "celebration": celebrations[i % len(celebrations)],
        })

    return challenges


def get_lightning_round(questions: list[Question],
                        child_ages: dict[str, int],
                        count: int = 10) -> list[tuple[str, Question]]:
    """Get rapid-fire questions alternating between children.

    Returns list of (child_name, Question) tuples.
    """
    result = []
    names = sorted(child_ages.keys(), key=lambda n: child_ages[n])

    for i in range(count):
        child = names[i % len(names)]
        age = child_ages[child]
        # Use easy/mastered-level questions for speed round
        qs = get_questions_for_child(questions, age)
        easy = [q for q in qs if q.difficulty_tier <= 2]
        if not easy:
            easy = qs
        if easy:
            q = random.choice(easy)
            result.append((child, q))

    return result
