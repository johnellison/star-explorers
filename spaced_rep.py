"""Spaced repetition engine using Modified Leitner System with SM-2 ease scaling."""

from models import SpacedRepItem, ChildProfile, TopicProgress, Question
import random

# Box configurations: (base_interval_sessions, description)
BOX_CONFIG = {
    1: (1, "New & Struggling"),
    2: (1, "Learning"),
    3: (2, "Practised"),
    4: (4, "Strong"),
    5: (8, "Mastered"),
}


def process_answer(item: SpacedRepItem, correct: bool, used_hint: bool,
                   current_session: int) -> SpacedRepItem:
    """Update a spaced repetition item after an answer."""
    item.times_seen += 1

    if correct:
        item.times_correct += 1
        item.last_result = "correct_with_hint" if used_hint else "correct"

        # Ease factor adjustment
        item.ease = min(3.5, item.ease + 0.1)

        # For boxes 3-5, hint-assisted correct doesn't count for streak
        if used_hint and item.box >= 3:
            pass  # Don't increment streak
        else:
            item.streak += 1

        # Check for box advancement (need 2 consecutive correct)
        if item.streak >= 2 and item.box < 5:
            item.box += 1
            item.streak = 0

        # Check for mastery
        if (item.box == 5 and item.streak >= 4
                and item.times_correct >= 10 and item.ease > 2.3):
            item.mastered = True

    else:
        item.last_result = "wrong"
        item.streak = 0
        item.ease = max(1.3, item.ease - 0.2)

        # Demotion rules (gentler for higher boxes)
        if item.box == 1:
            pass  # Stay in box 1
        elif item.box == 2:
            item.box = 1
        elif item.box == 3:
            item.box = 2
        elif item.box == 4:
            item.box = 2
        elif item.box == 5:
            item.box = 3
            item.mastered = False

    # Calculate next review interval
    base_interval = BOX_CONFIG[item.box][0]
    item.interval_sessions = max(1, round(base_interval * (item.ease / 2.5)))
    item.next_review_session = current_session + item.interval_sessions

    return item


def build_session_queue(child: ChildProfile, current_session: int,
                        question_bank: list[Question]) -> dict:
    """Build the question queue for a child's session.

    Returns dict with keys: warmup, mandatory, scheduled, new
    Each value is a list of (Question, SpacedRepItem) tuples.
    """
    warmup = []
    mandatory = []
    scheduled = []
    new_items = []

    # Build lookup of questions by ID
    q_by_id = {q.id: q for q in question_bank}

    # Collect all items across topics
    all_items = []
    for topic in child.topics.values():
        for item_id, sr_item in topic.items.items():
            if item_id in q_by_id:
                all_items.append((q_by_id[item_id], sr_item, topic))

    # 1. WARMUP: mastered items for confidence building (3-4)
    mastered = [(q, sr) for q, sr, _ in all_items if sr.mastered]
    random.shuffle(mastered)
    warmup = mastered[:4]

    # 2. MANDATORY: Box 1 + Box 2 items due for review
    for q, sr, _ in all_items:
        if sr.mastered:
            continue
        if sr.box == 1:
            mandatory.append((q, sr))
        elif sr.box == 2 and sr.next_review_session <= current_session:
            mandatory.append((q, sr))

    random.shuffle(mandatory)

    # 3. SCHEDULED: Box 3/4/5 items due for review
    for q, sr, _ in all_items:
        if sr.mastered:
            continue
        if sr.box >= 3 and sr.next_review_session <= current_session:
            scheduled.append((q, sr))

    # Sort by staleness (most overdue first)
    scheduled.sort(key=lambda x: x[1].next_review_session)
    scheduled = scheduled[:6]  # Cap at 6

    # 4. NEW MATERIAL: Only if mandatory queue is manageable
    if len(mandatory) < 8:
        # Find questions not yet introduced to this child
        introduced_ids = set()
        for topic in child.topics.values():
            introduced_ids.update(topic.items.keys())

        # Filter by age range
        available = [q for q in question_bank
                     if q.id not in introduced_ids
                     and child.age >= q.age_range[0]
                     and child.age <= q.age_range[1]]

        # Sort by difficulty tier for progressive introduction
        available.sort(key=lambda q: q.difficulty_tier)
        new_items = [(q, None) for q in available[:3]]

    return {
        "warmup": warmup,
        "mandatory": mandatory,
        "scheduled": scheduled,
        "new": new_items,
    }


def introduce_item(child: ChildProfile, question: Question,
                   current_session: int) -> SpacedRepItem:
    """Introduce a new question to a child's tracking."""
    sr = SpacedRepItem(
        item_id=question.id,
        box=1,
        ease=2.5,
        interval_sessions=1,
        next_review_session=current_session + 1,
        introduced_session=current_session,
    )

    # Ensure topic exists
    if question.topic not in child.topics:
        child.topics[question.topic] = TopicProgress(
            topic_id=question.topic,
            subject=question.subject,
        )

    child.topics[question.topic].items[question.id] = sr
    return sr


def get_difficulty_label(box: int) -> str:
    """Human-readable label for a box number."""
    return BOX_CONFIG.get(box, (0, "Unknown"))[1]
