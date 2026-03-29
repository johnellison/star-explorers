"""Rich-based CLI display for Star Explorers."""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich import box

console = Console()

# Colour theme
GOLD = "yellow"
CYAN = "cyan"
GREEN = "green"
RED = "red"
MAGENTA = "magenta"
DIM = "dim"
BOLD = "bold"
BLUE = "blue"


def clear():
    """Clear the terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def header(session_num: int, act_label: str, child_turn: str,
           team_score: int, elapsed: str, total: str = "60:00"):
    """Render the top header bar."""
    title = Text()
    title.append("  STAR EXPLORERS", style=f"bold {GOLD}")
    title.append(f" - Session #{session_num}", style=GOLD)

    right = Text()
    right.append(f"Team Score: {team_score} pts", style=f"bold {GREEN}")

    console.print(Panel(
        Columns([title, Align(right, align="right")], expand=True),
        box=box.DOUBLE,
        style=CYAN,
    ))

    status = Text()
    status.append(f"  {act_label}", style=f"bold {MAGENTA}")
    status.append(f" | {child_turn}", style=BOLD)
    status.append(f"     Time: {elapsed} / {total}", style=DIM)
    console.print(status)
    console.print()


def story_text(text: str):
    """Display a story narrative segment."""
    console.print(Panel(
        Text(text, style="italic"),
        title="[bold magenta]STORY[/]",
        border_style="magenta",
        padding=(1, 2),
    ))
    console.print()


def question_display(read_aloud: str, answer: str, correct_resp: str,
                     incorrect_resp: str, hint: str,
                     metacognitive: str = "", mnemonic: str = ""):
    """Display a question with all response scripts."""
    # The main read-aloud block
    console.print(Panel(
        Text(read_aloud, style="bold white"),
        title="[bold yellow]READ ALOUD[/]",
        border_style="yellow",
        padding=(1, 2),
    ))

    # Answer line
    console.print(f"  [dim]ANSWER:[/] [bold]{answer}[/]")
    console.print()

    # Response scripts in a compact format
    console.print(f"  [green]IF CORRECT:[/] {correct_resp}")
    if metacognitive:
        console.print(f"             [cyan]{metacognitive}[/]")
    console.print(f"  [red]IF WRONG:[/]   {incorrect_resp}")
    if mnemonic:
        console.print(f"             [magenta]MNEMONIC: {mnemonic}[/]")
    console.print(f"  [yellow]IF STUCK:[/]   {hint}")
    console.print()


def controls_bar(extra: str = ""):
    """Display the controls bar at the bottom."""
    controls = Text()
    controls.append("  [ENTER]", style=f"bold {GREEN}")
    controls.append(" Correct  ", style=DIM)
    controls.append("[n]", style=f"bold {RED}")
    controls.append(" Wrong  ", style=DIM)
    controls.append("[h]", style=f"bold {GOLD}")
    controls.append(" Hint  ", style=DIM)
    controls.append("[s]", style=f"bold {BLUE}")
    controls.append(" Skip  ", style=DIM)
    controls.append("[b]", style=f"bold {MAGENTA}")
    controls.append(" Break", style=DIM)
    if extra:
        controls.append(f"  {extra}", style=DIM)
    console.print(Panel(controls, box=box.SIMPLE))


def progress_bars(children_stats: dict):
    """Display progress bars for each child."""
    parts = []
    for name, stats in children_stats.items():
        correct = stats.get("correct", 0)
        asked = stats.get("asked", 0)
        total = stats.get("total", asked if asked > 0 else 1)
        filled = int((correct / max(total, 1)) * 10)
        bar = "█" * filled + "░" * (10 - filled)
        parts.append(f"  {name}: {bar} {correct}/{asked} correct")
    console.print("\n".join(parts), style=DIM)


def celebration(badge_name: str, child_name: str, team_badges: int,
                read_aloud: str):
    """Display an achievement celebration."""
    console.print()
    console.print(Panel(
        Text(f"⭐ ACHIEVEMENT UNLOCKED ⭐\n\n{badge_name}", justify="center",
             style=f"bold {GOLD}"),
        border_style=GOLD,
        box=box.DOUBLE,
    ))
    console.print()
    console.print(Panel(
        Text(read_aloud, style="bold white"),
        title="[bold yellow]READ ALOUD[/]",
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print()
    console.print(f"  [dim]Press ENTER to continue[/]")


def rescue_mode(child_name: str, topic: str, options: list[tuple[str, str]]):
    """Display rescue mode when a child is struggling."""
    console.print()
    console.print(Panel(
        Text(f"RESCUE MODE - {child_name} seems stuck on {topic}",
             style=f"bold {RED}"),
        border_style=RED,
    ))
    for i, (key, desc) in enumerate(options, 1):
        console.print(f"  [{CYAN}][{i}][/{CYAN}] {desc}")
    console.print()

    # Encouragement script
    console.print(Panel(
        Text(
            f"That was a really tricky one. Even Captain Starlight "
            f"found that hard! Let's try something different...",
            style="italic",
        ),
        title="[bold yellow]ENCOURAGEMENT SCRIPT[/]",
        border_style="yellow",
        padding=(1, 2),
    ))


def setup_screen(session_num: int, children: list, team_state, story_info: dict):
    """Display the pre-session setup screen."""
    clear()
    console.print(Panel(
        Text("STAR EXPLORERS - Session Setup", justify="center",
             style=f"bold {GOLD}"),
        box=box.DOUBLE,
        border_style=CYAN,
    ))
    console.print()
    console.print(f"  Session #{session_num} | {story_info.get('date', 'Today')}")
    console.print()

    for child in children:
        console.print(f"  [bold]{child.name}[/] (age {child.age}) - {child.character_name}:")

        # Show topics with progress
        for topic_id, topic in child.topics.items():
            pct = topic.mastery_pct
            filled = int(pct / 10)
            bar = "█" * filled + "░" * (10 - filled)
            console.print(f"    {topic.subject}/{topic_id}: {bar} {pct}%")

        # Show review and new counts
        review_count = sum(
            1 for t in child.topics.values()
            for item in t.items.values()
            if not item.mastered and item.next_review_session <= session_num
        )
        console.print(f"    [dim]Items due for review: {review_count}[/]")
        console.print()

    # Story info
    console.print(f"  [magenta]Story:[/] {story_info.get('arc_name', 'The Enchanted Forest')}")
    if team_state.cliffhanger:
        console.print(f"  [dim]Previous cliffhanger: \"{team_state.cliffhanger[:80]}...\"[/]")
    console.print()
    console.print(f"  [dim]Total Adventure Points: {team_state.total_adventure_points}[/]")
    console.print(f"  [dim]Sessions completed: {team_state.sessions_completed}[/]")
    console.print()


def score_report(report_text: str):
    """Display the end-of-session score report."""
    console.print(Panel(
        Text(report_text, style=f"bold {GREEN}"),
        title=f"[bold {GOLD}]SESSION COMPLETE[/]",
        border_style=GOLD,
        box=box.DOUBLE,
        padding=(1, 2),
    ))


def cliffhanger_display(text: str):
    """Display the session cliffhanger."""
    console.print(Panel(
        Text(text, style="bold italic"),
        title=f"[bold {MAGENTA}]TO BE CONTINUED...[/]",
        border_style=MAGENTA,
        padding=(1, 2),
    ))


def read_aloud_block(text: str, title: str = "READ ALOUD"):
    """Generic read-aloud block."""
    console.print(Panel(
        Text(text, style="bold white"),
        title=f"[bold yellow]{title}[/]",
        border_style="yellow",
        padding=(1, 2),
    ))


def info_message(text: str):
    """Display an informational message."""
    console.print(f"  [cyan]{text}[/]")


def prompt_continue(message: str = "Press ENTER to continue"):
    """Prompt for ENTER to continue."""
    console.print(f"\n  [dim]{message}[/]")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass


def get_key(prompt: str = "") -> str:
    """Get a single keypress from the user."""
    if prompt:
        console.print(f"  [dim]{prompt}[/]", end="")
    try:
        val = input().strip().lower()
        return val
    except (EOFError, KeyboardInterrupt):
        return "q"


def print_separator():
    """Print a visual separator."""
    console.print("─" * 60, style=DIM)
