"""Session engine - orchestrates the Five-Act game session."""

import time
import random
from datetime import datetime

from models import ChildProfile, TeamState, SessionLog, Question, Callback
from spaced_rep import process_answer, build_session_queue, introduce_item
from questions import (load_question_bank, get_questions_for_child,
                       get_boss_questions, get_lightning_round)
from story import (generate_recap, get_story_hook, get_cliffhanger,
                   get_story_beat, get_boss_intro, get_movement_break,
                   get_silly_break, get_secret_mission, generate_score_report,
                   get_session_position)
import display


class SessionState:
    """Mutable state during a session."""

    def __init__(self, session_number: int, children: list[ChildProfile],
                 team: TeamState):
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


def run_session(children: list[ChildProfile], team: TeamState):
    """Run a complete game session."""
    session_num = team.sessions_completed + 1
    state = SessionState(session_num, children, team)

    # Pre-session setup
    arc_num, position = get_session_position(session_num)
    arc_name = team.arc_name if team.arc_name else "The Enchanted Forest"

    display.setup_screen(session_num, children, team, {
        "date": datetime.now().strftime("%A, %d %B %Y"),
        "arc_name": arc_name,
    })

    display.console.print(f"\n  [bold green][ENTER][/] Start session  "
                          f"[bold blue][p][/] Preview questions  "
                          f"[bold red][q][/] Cancel")

    key = display.get_key()
    if key == "q":
        return
    if key == "p":
        _preview_questions(state)
        display.prompt_continue("Press ENTER to start the session")

    # Start the session
    state.start_time = time.time()

    try:
        act1_opening(state)
        act2_first_quest(state)
        movement_break(state)
        act3_joint_challenge(state)
        silly_break(state)
        act4_second_quest(state)
        act5_closing(state)
    except KeyboardInterrupt:
        display.console.print("\n\n  [yellow]Session interrupted. Saving progress...[/]")
    except SessionEnd:
        display.console.print("\n  [yellow]Session ended early. Saving progress...[/]")

    # Save everything
    _save_session(state)
    display.console.print("\n  [green]Progress saved![/]")
    display.prompt_continue()


class SessionEnd(Exception):
    """Raised when the session is ended early."""
    pass


def _handle_key(state: SessionState, key: str) -> bool:
    """Handle global keypresses. Returns True if the key was consumed."""
    if key == "q":
        raise SessionEnd()
    if key == "b":
        _do_break(state)
        return True
    if key == "+":
        child = state.current_child
        if child:
            state.difficulty_override[child] = state.difficulty_override.get(child, 0) + 1
            display.info_message(f"Difficulty increased for next question")
        return True
    if key == "-":
        child = state.current_child
        if child:
            state.difficulty_override[child] = state.difficulty_override.get(child, 0) - 1
            display.info_message(f"Difficulty decreased for next question")
        return True
    if key == "*":
        display.console.print("  [yellow]Moment flagged as memorable![/]")
        return True
    if key == "t":
        display.console.print(f"  [dim]Elapsed: {state.elapsed_str} | "
                              f"Act {state.current_act} of 5 | "
                              f"Score: {state.team_score}[/]")
        return True
    return False


def _ask_question(state: SessionState, child_name: str, question: Question,
                  sr_item=None) -> bool:
    """Present a question and handle the response. Returns True if correct."""
    state.current_child = child_name
    child = state.children[child_name]

    display.clear()
    act_labels = {1: "Opening", 2: "First Quest", 3: "Joint Challenge",
                  4: "Second Quest", 5: "Closing"}
    display.header(
        state.session_number,
        f"Act {state.current_act}: {act_labels.get(state.current_act, '')}",
        f"{child_name}'s Turn",
        state.team_score,
        state.elapsed_str,
    )

    # Show the question
    display.question_display(
        read_aloud=question.read_aloud,
        answer=", ".join(question.correct_answers),
        correct_resp=question.correct_response,
        incorrect_resp=question.incorrect_response,
        hint=question.hint,
        metacognitive=question.metacognitive_prompt,
        mnemonic=question.mnemonic,
    )
    display.controls_bar()
    display.progress_bars({
        n: {"correct": state.questions_correct[n],
            "asked": state.questions_asked[n]}
        for n in state.children
    })

    # Get response
    used_hint = False
    while True:
        key = display.get_key()

        if _handle_key(state, key):
            continue

        if key in ("", "y"):  # ENTER or y = correct
            state.questions_asked[child_name] += 1
            state.questions_correct[child_name] += 1
            state.streak[child_name] += 1
            state.consecutive_wrong[child_name] = 0
            child.total_correct += 1
            child.update_power_level()

            # Points
            points = 5 if not used_hint else 3
            state.add_points(points)

            # Update spaced rep
            if sr_item:
                process_answer(sr_item, True, used_hint, state.session_number)

            # Check for streak achievements
            _check_streak_achievement(state, child_name)

            # Auto-difficulty: 3 correct in a row -> bump up
            if state.streak[child_name] >= 3 and state.streak[child_name] % 3 == 0:
                state.difficulty_override[child_name] = \
                    state.difficulty_override.get(child_name, 0) + 1
                display.info_message("AUTO: Difficulty increased!")

            return True

        elif key == "n":  # Wrong
            state.questions_asked[child_name] += 1
            state.streak[child_name] = 0
            state.consecutive_wrong[child_name] += 1
            state.add_points(0)

            # Update spaced rep
            if sr_item:
                process_answer(sr_item, False, False, state.session_number)

            # Auto-difficulty: 2 wrong in a row -> drop
            if state.consecutive_wrong[child_name] >= 2:
                state.difficulty_override[child_name] = \
                    state.difficulty_override.get(child_name, 0) - 1
                display.info_message("AUTO: Difficulty decreased")

                # Trigger rescue mode after 3 wrong
                if state.consecutive_wrong[child_name] >= 3:
                    _rescue_mode(state, child_name,
                                 question.topic if question else "this topic")

            return False

        elif key == "h":  # Hint
            used_hint = True
            display.console.print(f"\n  [yellow]HINT: {question.hint}[/]\n")

        elif key == "s":  # Skip
            state.consecutive_wrong[child_name] += 1
            if state.consecutive_wrong[child_name] >= 2:
                _rescue_mode(state, child_name,
                             question.topic if question else "this topic")
            return False


def _run_question_round(state: SessionState, child_name: str,
                        queue_key: str, count: int):
    """Run a round of questions for a child from their queue."""
    queue = state.session_queues.get(child_name, {})
    items = queue.get(queue_key, [])

    asked = 0
    for q, sr_item in items:
        if asked >= count:
            break

        # If it's a new item, introduce it
        if sr_item is None:
            child = state.children[child_name]
            sr_item = introduce_item(child, q, state.session_number)
            state.new_introduced[child_name] += 1

        _ask_question(state, child_name, q, sr_item)
        asked += 1


def act1_opening(state: SessionState):
    """Act 1: The Opening Ritual (0-8 minutes)."""
    state.current_act = 1
    display.clear()

    # Greeting chant
    display.header(state.session_number, "Act 1: Opening Ritual", "Everyone",
                   state.team_score, state.elapsed_str)

    if state.session_number == 1:
        # First session special intro
        names = " and ".join(c.name for c in state.sorted_children())
        display.read_aloud_block(
            f"Hey {names}! I have something REALLY special for today. "
            f"Are you ready? We're going to play a brand new game called "
            f"STAR EXPLORERS!\n\n"
            f"In this game, you are both explorers on an amazing adventure. "
            f"Our team is called... THE STAR EXPLORERS!\n\n"
            f"Let's practice our team chant:\n"
            f"I'll say: 'Adventurers, are you ready?'\n"
            f"And you both say: 'READY FOR ADVENTURE!'\n\n"
            f"Let's try it! Adventurers, are you ready?"
        )
    else:
        display.read_aloud_block(
            "Adventurers, are you ready?\n\n"
            "[Wait for: READY FOR ADVENTURE!]\n\n"
            "That's what I like to hear! Let's go!"
        )
    display.prompt_continue()

    # Recap
    if state.session_number > 1:
        display.clear()
        display.header(state.session_number, "Act 1: Opening Ritual", "Recap",
                       state.team_score, state.elapsed_str)
        recap = generate_recap(state.team, list(state.children.values()))
        if recap:
            display.read_aloud_block(recap, "PREVIOUSLY ON STAR EXPLORERS")
            display.prompt_continue()

        # Secret mission check
        if state.team.secret_mission:
            display.read_aloud_block(
                f"Before we start -- did you do your SECRET MISSION?\n\n"
                f"The mission was: {state.team.secret_mission.get('description', '')}\n\n"
                f"Tell me what you found!",
                "SECRET MISSION CHECK"
            )
            key = display.get_key("Did they complete it? [ENTER] Yes  [n] No: ")
            if key in ("", "y"):
                state.add_points(10, "Secret mission complete")
                display.console.print("  [green]+10 Adventure Points for the secret mission![/]")
            display.prompt_continue()

    # Warm-up round
    display.clear()
    display.header(state.session_number, "Act 1: Warm-Up", "Everyone",
                   state.team_score, state.elapsed_str)
    display.read_aloud_block(
        "Time for our warm-up! A few easy ones to get our brains going!",
        "WARM-UP ROUND"
    )
    display.prompt_continue()

    # 2 warm-up questions per child from mastered material
    for child in state.sorted_children():
        warmup = state.session_queues.get(child.name, {}).get("warmup", [])
        for q, sr in warmup[:2]:
            _ask_question(state, child.name, q, sr)

    # Story hook
    display.clear()
    display.header(state.session_number, "Act 1: Story Hook", "Everyone",
                   state.team_score, state.elapsed_str)
    hook = get_story_hook(state.session_number)
    display.read_aloud_block(hook, "THE ADVENTURE BEGINS")
    display.prompt_continue()


def act2_first_quest(state: SessionState):
    """Act 2: The First Quest (8-25 minutes)."""
    state.current_act = 2
    children = state.sorted_children()  # Youngest first

    for round_num in range(2):
        for child in children:
            # Determine which queue to use
            if round_num == 0:
                # Round 1: mandatory review
                queue_key = "mandatory"
            else:
                # Round 2: mix of new and scheduled
                queue_key = "new" if state.new_introduced[child.name] < 3 else "scheduled"

            _run_question_round(state, child.name, queue_key, count=3)

            # Story beat between turns
            beat = get_story_beat(state.session_number, round_num * 2 + children.index(child))
            display.clear()
            display.header(state.session_number, "Act 2: First Quest", "Story",
                           state.team_score, state.elapsed_str)
            display.story_text(beat)
            display.prompt_continue()


def movement_break(state: SessionState):
    """Movement break between Acts 2 and 3."""
    display.clear()
    display.header(state.session_number, "MOVEMENT BREAK", "Everyone",
                   state.team_score, state.elapsed_str)
    prompt = get_movement_break(state.session_number)
    display.read_aloud_block(prompt, "POWER-UP TIME!")
    display.prompt_continue("Press ENTER when they're done")


def act3_joint_challenge(state: SessionState):
    """Act 3: The Joint Challenge (28-40 minutes)."""
    state.current_act = 3
    display.clear()

    # Boss intro
    display.header(state.session_number, "Act 3: Boss Challenge", "TEAM",
                   state.team_score, state.elapsed_str)
    boss_intro = get_boss_intro(state.session_number)
    display.read_aloud_block(boss_intro, "BOSS CHALLENGE!")
    display.prompt_continue()

    # Boss questions
    child_ages = {c.name: c.age for c in state.sorted_children()}
    challenges = get_boss_questions(state.question_bank, child_ages)

    for i, challenge in enumerate(challenges[:3]):
        display.clear()
        display.header(state.session_number, f"Act 3: Boss Challenge {i+1}/3",
                       "TEAM", state.team_score, state.elapsed_str)
        display.read_aloud_block(challenge["intro"], f"CHALLENGE {i+1}")
        display.prompt_continue()

        all_correct = True
        for part in challenge["parts"]:
            correct = _ask_question(state, part["child"], part["question"])
            if correct:
                state.add_points(3)  # Extra boss points
            else:
                all_correct = False

        if all_correct:
            state.add_points(8, "Boss challenge bonus")
            display.clear()
            display.header(state.session_number, "Act 3: Boss Challenge",
                           "VICTORY!", state.team_score, state.elapsed_str)
            display.read_aloud_block(challenge["celebration"], "BOSS DEFEATED!")
        else:
            display.read_aloud_block(
                "So close! You almost had it! The Puzzle Goblin grins: "
                "'Not bad... not bad at all. Let's try the next one!'",
                "KEEP GOING!"
            )
        display.prompt_continue()

    # Story advancement
    beat = get_story_beat(state.session_number, 99)
    display.clear()
    display.header(state.session_number, "Act 3: Story", "Everyone",
                   state.team_score, state.elapsed_str)
    display.story_text(beat)
    display.prompt_continue()


def silly_break(state: SessionState):
    """Silly break between Acts 3 and 4."""
    display.clear()
    display.header(state.session_number, "SILLY BREAK", "Everyone",
                   state.team_score, state.elapsed_str)
    activity = get_silly_break(state.session_number)
    display.read_aloud_block(activity["read_aloud"], f"SILLY TIME: {activity['name']}")
    display.prompt_continue("Press ENTER when you're done being silly")


def act4_second_quest(state: SessionState):
    """Act 4: The Second Quest - Review and Treasure (43-53 minutes)."""
    state.current_act = 4

    # Mixed review round
    for child in state.sorted_children():
        queue = state.session_queues.get(child.name, {})
        # Use scheduled review items
        scheduled = queue.get("scheduled", [])
        for q, sr in scheduled[:3]:
            _ask_question(state, child.name, q, sr)

    # Treasure Chest
    display.clear()
    display.header(state.session_number, "Act 4: Treasure Chest", "BONUS",
                   state.team_score, state.elapsed_str)
    display.read_aloud_block(
        "You found a TREASURE CHEST! Inside is a BONUS question!\n\n"
        "If you get it right, you earn 10 EXTRA Adventure Points!\n"
        "If you don't, no worries -- the chest was just locked this time!",
        "TREASURE CHEST!"
    )
    display.prompt_continue()

    # Pick a slightly harder question for each child
    for child in state.sorted_children():
        qs = get_questions_for_child(state.question_bank, child.age)
        hard = [q for q in qs if q.difficulty_tier >= 3]
        if hard:
            q = random.choice(hard)
            correct = _ask_question(state, child.name, q)
            if correct:
                state.add_points(10, "Treasure chest bonus")
                display.console.print("  [bold yellow]+10 Treasure Chest Bonus![/]")
            else:
                display.console.print("  [dim]The chest was locked this time! "
                                      "We'll try again next time![/]")
            display.prompt_continue()

    # Lightning Round
    display.clear()
    display.header(state.session_number, "Act 4: Lightning Round", "SPEED!",
                   state.team_score, state.elapsed_str)
    display.read_aloud_block(
        "LIGHTNING ROUND! Quick-fire questions, alternating between you!\n"
        "True or false, yes or no -- as fast as you can!\n\n"
        f"Your record is {state.team.lightning_round_record} correct. "
        f"Can you beat it? Ready? GO!",
        "LIGHTNING ROUND!"
    )
    display.prompt_continue()

    child_ages = {c.name: c.age for c in state.sorted_children()}
    lightning = get_lightning_round(state.question_bank, child_ages, count=8)
    lightning_correct = 0

    for child_name, q in lightning:
        correct = _ask_question(state, child_name, q)
        if correct:
            lightning_correct += 1
            state.add_points(1, "Lightning round")

    if lightning_correct > state.team.lightning_round_record:
        state.team.lightning_round_record = lightning_correct
        display.console.print(
            f"\n  [bold yellow]NEW RECORD! {lightning_correct} correct![/]")
        state.add_points(15, "Beat lightning round record")
    else:
        display.console.print(
            f"\n  [dim]{lightning_correct} correct! "
            f"Record is {state.team.lightning_round_record}[/]")
    display.prompt_continue()


def act5_closing(state: SessionState):
    """Act 5: The Closing Ritual (53-60 minutes)."""
    state.current_act = 5
    display.clear()

    # Score report
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

    report = generate_score_report(state.team, list(state.children.values()),
                                   session_stats)
    display.header(state.session_number, "Act 5: Closing", "Everyone",
                   state.team_score, state.elapsed_str)
    display.score_report(report)
    display.prompt_continue()

    # Power level updates
    for child in state.sorted_children():
        display.console.print(
            f"  {child.name} is now a [bold]{child.power_level_name}[/] "
            f"({child.total_correct} total correct answers)")
    display.prompt_continue()

    # Cliffhanger
    display.clear()
    display.header(state.session_number, "Act 5: Cliffhanger", "Everyone",
                   state.team_score, state.elapsed_str)
    cliffhanger = get_cliffhanger(state.session_number)
    display.cliffhanger_display(cliffhanger)
    state.team.cliffhanger = cliffhanger
    display.prompt_continue()

    # "What do YOU think?"
    display.read_aloud_block(
        "What do YOU think is going to happen next?\n"
        "Think about it this week!",
        "WHAT DO YOU THINK?"
    )
    display.prompt_continue()

    # Secret mission (every other session)
    if state.session_number % 2 == 0:
        mission = get_secret_mission(state.session_number)
        display.read_aloud_block(
            f"Captain Starlight has a SECRET MISSION for you this week!\n\n"
            f"{mission}\n\n"
            f"Next time, you'll get BONUS POINTS for completing it!",
            "SECRET MISSION"
        )
        state.team.secret_mission = {
            "description": mission,
            "assigned_session": state.session_number,
        }
        display.prompt_continue()

    # Closing chant
    display.clear()
    names = " and ".join(c.name for c in state.sorted_children())
    display.read_aloud_block(
        f"Star Explorers, mission complete!\n\n"
        f"I love you {names}, and I'm so proud of you. "
        f"Talk to you next time!",
        "MISSION COMPLETE"
    )
    display.prompt_continue()


def _do_break(state: SessionState):
    """Insert an ad-hoc break."""
    display.clear()
    display.console.print("\n  [bold cyan]BREAK TIME![/]\n")
    display.console.print("  [1] Movement break")
    display.console.print("  [2] Silly break")
    display.console.print("  [3] Just pause for a moment")

    key = display.get_key("\n  Choice: ")
    if key == "1":
        prompt = get_movement_break(random.randint(0, 99))
        display.read_aloud_block(prompt, "POWER-UP!")
    elif key == "2":
        activity = get_silly_break(random.randint(0, 99))
        display.read_aloud_block(activity["read_aloud"], f"SILLY TIME: {activity['name']}")
    display.prompt_continue()


def _rescue_mode(state: SessionState, child_name: str, topic: str):
    """Activate rescue mode when a child is struggling."""
    display.rescue_mode(child_name, topic, [
        ("1", f"Switch to an easier topic"),
        ("2", "Simplify current topic"),
        ("3", "Take a fun break"),
        ("4", "Move to cooperative activity"),
    ])

    key = display.get_key("\n  Choice (or ENTER to continue): ")
    state.consecutive_wrong[child_name] = 0  # Reset

    if key == "1" or key == "3":
        _do_break(state)
    elif key == "4":
        # Skip ahead to joint activity
        pass


def _check_streak_achievement(state: SessionState, child_name: str):
    """Check and award streak-based achievements."""
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
            display.celebration(
                name, child_name, len(state.team.achievements),
                f"WAIT! Something special just happened!\n"
                f"{script}\n\n"
                f"The team now has {len(state.team.achievements)} badges total!\n"
                f"Can you both make a celebration sound? WOOHOO!"
            )
            display.prompt_continue()


def _preview_questions(state: SessionState):
    """Preview the question queue for the session."""
    display.clear()
    display.console.print("\n  [bold]Session Question Preview[/]\n")
    for child_name, queue in state.session_queues.items():
        display.console.print(f"  [cyan]{child_name}:[/]")
        for key in ["warmup", "mandatory", "scheduled", "new"]:
            items = queue.get(key, [])
            display.console.print(f"    {key}: {len(items)} questions")
            for q, sr in items[:3]:
                display.console.print(f"      - {q.read_aloud[:60]}...")
        display.console.print()


def _save_session(state: SessionState):
    """Save all session data."""
    # Update team state
    state.team.sessions_completed = state.session_number
    arc_num, _ = get_session_position(state.session_number)
    from story import get_arc
    arc = get_arc(arc_num)
    state.team.current_arc = arc_num
    state.team.current_chapter = state.session_number
    state.team.arc_name = arc["name"]

    # Add any new characters
    for char in arc.get("characters", []):
        if char not in state.team.characters_met:
            state.team.characters_met.append(char)

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
