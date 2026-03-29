#!/usr/bin/env python3
"""Star Explorers - An educational phone game CLI.

Usage:
    python main.py play          Start/continue a game session
    python main.py setup         First-time setup
    python main.py stats         View progress and statistics
    python main.py preview       Preview next session's questions
    python main.py reset         Reset all progress (with confirmation)
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from models import ChildProfile, TeamState, DATA_DIR
from session import run_session
from questions import load_question_bank
from spaced_rep import build_session_queue, get_difficulty_label
import display


def ensure_data_dirs():
    """Create data directories if they don't exist."""
    for subdir in ["children", "question_bank", "sessions", "scripts"]:
        os.makedirs(os.path.join(DATA_DIR, subdir), exist_ok=True)


def setup():
    """First-time setup - create child profiles."""
    ensure_data_dirs()
    display.clear()
    display.console.print("\n  [bold yellow]STAR EXPLORERS - First Time Setup[/]\n")

    # Check if profiles already exist
    reuben_path = os.path.join(DATA_DIR, "children", "reuben.json")
    jesse_path = os.path.join(DATA_DIR, "children", "jesse.json")

    if os.path.exists(reuben_path) and os.path.exists(jesse_path):
        display.console.print("  Profiles already exist!")
        display.console.print("  [dim]Use 'python main.py reset' to start over[/]")
        return load_children()

    # Create Reuben's profile
    reuben = ChildProfile(
        name="Reuben",
        age=7,
        character_name="Reuben the Code Breaker",
        character_title="Code Breaker",
    )
    reuben.save()
    display.console.print("  [green]Created profile for Reuben (age 7) - The Code Breaker[/]")

    # Create Jesse's profile
    jesse = ChildProfile(
        name="Jesse",
        age=4,
        character_name="Jesse the Sound Seeker",
        character_title="Sound Seeker",
    )
    jesse.save()
    display.console.print("  [green]Created profile for Jesse (age 4) - The Sound Seeker[/]")

    # Create team state
    team = TeamState()
    team.save()
    display.console.print("  [green]Created team: The Star Explorers[/]")

    # Verify question bank
    questions = load_question_bank()
    display.console.print(f"\n  [cyan]Question bank: {len(questions)} questions loaded[/]")

    if len(questions) == 0:
        display.console.print("  [yellow]Warning: No questions found in data/question_bank/[/]")
        display.console.print("  [dim]Add JSON question files to get started[/]")

    display.console.print("\n  [bold green]Setup complete! Run 'python main.py play' to start.[/]")
    return [reuben, jesse]


def load_children() -> list[ChildProfile]:
    """Load child profiles."""
    children = []
    children_dir = os.path.join(DATA_DIR, "children")
    if not os.path.exists(children_dir):
        return children

    for filename in sorted(os.listdir(children_dir)):
        if filename.endswith(".json"):
            name = filename.replace(".json", "").capitalize()
            try:
                children.append(ChildProfile.load(name.lower()))
            except Exception as e:
                display.console.print(f"  [red]Error loading {filename}: {e}[/]")

    return children


def play():
    """Start or continue a game session."""
    children = load_children()
    if not children:
        display.console.print("\n  [yellow]No profiles found. Running setup...[/]\n")
        children = setup()
        if not children:
            return

    team = TeamState.load()
    run_session(children, team)


def stats():
    """Display progress statistics."""
    children = load_children()
    team = TeamState.load()

    if not children:
        display.console.print("\n  [yellow]No profiles found. Run setup first.[/]")
        return

    display.clear()
    display.console.print("\n  [bold yellow]STAR EXPLORERS - Progress Dashboard[/]\n")

    # Team stats
    display.console.print(f"  [bold]Team: {team.team_name}[/]")
    display.console.print(f"  Sessions completed: {team.sessions_completed}")
    display.console.print(f"  Total Adventure Points: {team.total_adventure_points}")
    display.console.print(f"  Current Arc: {team.arc_name}")
    display.console.print(f"  Lightning Round Record: {team.lightning_round_record}")
    display.console.print(f"  Achievements: {len(team.achievements)}")
    for badge in team.achievements:
        display.console.print(f"    - {badge}")
    display.console.print()

    # Per-child stats
    for child in children:
        display.console.print(f"  [bold cyan]{child.name}[/] (age {child.age}) "
                              f"- {child.character_name}")
        display.console.print(f"  Power Level: {child.power_level} "
                              f"({child.power_level_name})")
        display.console.print(f"  Total Correct: {child.total_correct}")
        display.console.print(f"  Sessions: {child.sessions_completed}")
        display.console.print()

        if child.topics:
            display.console.print(f"  [dim]Topic Progress:[/]")
            for topic_id, topic in child.topics.items():
                pct = topic.mastery_pct
                filled = int(pct / 10)
                bar = "\u2588" * filled + "\u2591" * (10 - filled)
                total_items = len(topic.items)
                mastered_items = sum(1 for i in topic.items.values() if i.mastered)

                box_dist = {}
                for item in topic.items.values():
                    box_name = get_difficulty_label(item.box)
                    box_dist[box_name] = box_dist.get(box_name, 0) + 1

                display.console.print(
                    f"    {topic.subject}/{topic_id}: {bar} {pct}% "
                    f"({mastered_items}/{total_items} mastered)")
                for bname, bcount in box_dist.items():
                    display.console.print(f"      {bname}: {bcount}")
            display.console.print()

    # Next session preview
    next_session = team.sessions_completed + 1
    questions = load_question_bank()
    display.console.print(f"  [bold]Next Session: #{next_session}[/]")
    for child in children:
        queue = build_session_queue(child, next_session, questions)
        display.console.print(f"  {child.name}:")
        display.console.print(f"    Warmup: {len(queue['warmup'])} questions")
        display.console.print(f"    Review (mandatory): {len(queue['mandatory'])}")
        display.console.print(f"    Review (scheduled): {len(queue['scheduled'])}")
        display.console.print(f"    New material: {len(queue['new'])}")
    display.console.print()


def reset():
    """Reset all progress with confirmation."""
    display.console.print("\n  [bold red]WARNING: This will delete ALL progress![/]")
    display.console.print("  Type 'RESET' to confirm: ", end="")
    confirm = input().strip()
    if confirm == "RESET":
        import shutil
        for subdir in ["children", "sessions"]:
            path = os.path.join(DATA_DIR, subdir)
            if os.path.exists(path):
                shutil.rmtree(path)
                os.makedirs(path)
        team_path = os.path.join(DATA_DIR, "team.json")
        if os.path.exists(team_path):
            os.remove(team_path)
        display.console.print("  [green]Reset complete. Run 'python main.py setup'.[/]")
    else:
        display.console.print("  [dim]Reset cancelled.[/]")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    commands = {
        "play": play,
        "setup": setup,
        "stats": stats,
        "preview": lambda: stats(),  # Preview is part of stats
        "reset": reset,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
