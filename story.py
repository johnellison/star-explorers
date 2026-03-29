"""Story engine for Star Explorers - narrative, recaps, cliffhangers."""

import random

# Story arc definitions
STORY_ARCS = [
    {
        "arc": 1,
        "name": "The Enchanted Forest",
        "sessions": 5,
        "theme": "Introduction and Discovery",
        "description": "The Star Explorers discover a magical forest where a mischievous Puzzle Goblin has scattered challenges.",
        "characters": ["Captain Starlight", "The Wise Owl", "The Puzzle Goblin"],
        "hooks": [
            "Captain Starlight has discovered a magical forest that needs your help!",
            "The Wise Owl guards the secrets of the forest, but first you must prove yourselves!",
            "The Puzzle Goblin has scrambled up the forest's magic! Only brave explorers can fix it!",
            "Deep in the forest, there's a tree that grants wishes -- but only to those who solve its riddles!",
            "The final challenge awaits! The Puzzle Goblin has one last trick up his sleeve...",
        ],
        "cliffhangers": [
            "As you walked through the forest, you heard a strange sound. Someone was SINGING! But who would be singing in the middle of a magical forest? And WHY?",
            "The Wise Owl whispered: 'There's a SECRET PATH that leads somewhere no explorer has ever been.' She looked around nervously. 'But we'll need to be brave to find it...'",
            "Just as you thought the forest was quiet, the ground started to SHAKE! The Puzzle Goblin appeared and said: 'You've done well... but my BIGGEST puzzle is still waiting!'",
            "Behind the oldest tree in the forest, you found a DOOR. A tiny, wooden door with strange symbols carved into it. What could be behind it?",
            "The Puzzle Goblin looked different this time. Instead of laughing, he looked... WORRIED. 'Something is happening in the Crystal Caves,' he whispered. 'I need your help.'",
        ],
    },
    {
        "arc": 2,
        "name": "The Crystal Caves",
        "sessions": 5,
        "theme": "Numbers and Patterns",
        "description": "Beneath the forest lies a network of crystal caves where numbers hold magical power.",
        "characters": ["The Crystal Dragon", "The Echo Sprite"],
        "hooks": [
            "The tiny door opens to reveal a staircase spiralling down into glowing crystal caves!",
            "The Crystal Dragon has lost her treasure -- crystals scattered throughout the caves, each one holding a number puzzle!",
            "Echo Sprite bounces your words around the caves! Can you use sounds and numbers to navigate?",
            "The deepest cave holds the Dragon's most precious crystal, but it's locked behind the hardest puzzle yet!",
            "The Crystal Dragon has a gift for you -- but first, one final challenge in the heart of the caves!",
        ],
        "cliffhangers": [
            "As you collected the last crystal, it started to GLOW. The Crystal Dragon looked surprised: 'That crystal... it's a MAP! And it shows... an ISLAND!'",
            "The Echo Sprite whispered something you could barely hear: 'The caves are connected to somewhere far away. Somewhere across the SEA.'",
            "You heard waves crashing! But you're underground! The Crystal Dragon smiled: 'There's a hidden river that flows all the way to the ocean...'",
            "A message appeared on the cave wall, glowing in crystal light: 'THE HIDDEN ISLAND AWAITS THOSE WHO ARE BRAVE ENOUGH TO FIND IT.'",
            "The Crystal Dragon spread her wings: 'I can fly you somewhere you've never been. Somewhere no explorer has visited for a hundred years. Are you brave enough?'",
        ],
    },
    {
        "arc": 3,
        "name": "The Hidden Island",
        "sessions": 5,
        "theme": "Nature and Discovery",
        "description": "A mysterious island where animals talk and nature holds the answers to puzzles.",
        "characters": ["The Island Guardian", "Professor Parrot"],
        "hooks": [
            "The Crystal Dragon lands on a beach of golden sand. Welcome to the Hidden Island!",
            "Professor Parrot knows EVERY word in the dictionary! But the Island Guardian has jumbled them all up!",
            "Strange footprints on the beach! What kind of creature made them? Time to investigate!",
            "The Island Guardian reveals the island's greatest secret: a treasure hidden at the very centre!",
            "The treasure is almost within reach! But the island has one final test for the Star Explorers...",
        ],
        "cliffhangers": [
            "ROAR! Something BIG is in the jungle! The Island Guardian's eyes went wide: 'I've never heard THAT sound before!'",
            "Professor Parrot found a bottle washed up on the shore. Inside was a letter that said: 'HELP! I'M TRAPPED IN THE SKY KINGDOM!'",
            "The island started to FLOAT! Just a little, like it was trying to lift off the water! 'It's waking up,' whispered the Island Guardian. 'The island... is ALIVE!'",
            "You found the treasure! But it wasn't gold or jewels. It was a TELESCOPE that could see all the way up to... a kingdom made entirely of CLOUDS!",
            "Through the telescope, you saw someone waving! Someone was trapped up there in the clouds! 'We need to find a way UP,' said Captain Starlight. But how do you get to a kingdom in the sky?",
        ],
    },
    {
        "arc": 4,
        "name": "The Sky Kingdom",
        "sessions": 5,
        "theme": "Words and Language",
        "description": "A kingdom above the clouds where words have magical power.",
        "characters": ["The Cloud Shepherd", "The Word Weaver"],
        "hooks": [
            "A rainbow bridge appears! It stretches all the way up to the clouds! Time to climb!",
            "The Cloud Shepherd tends his flock of cloud-sheep, but they only respond to special WORDS!",
            "The Word Weaver's loom is broken! Only by finding the right letters can you fix it!",
            "The sky is getting dark! The Word Weaver says only a powerful SPELL can bring back the sunshine!",
            "The person who was trapped has been freed! But they have an incredible story to tell...",
        ],
        "cliffhangers": [
            "The Cloud Shepherd showed you a cloud shaped like a DOOR. 'Beyond that door,' he said, 'is a place where nothing makes sense. A place of PUZZLES.'",
            "The Word Weaver finished her tapestry. It showed a picture of... YOU! Both of you! But in the picture, you were wearing CROWNS! What could it mean?",
            "A storm is coming! But this isn't a normal storm -- the rain is falling UPWARDS! 'The Puzzle Dimension is leaking through,' gasped Captain Starlight.",
            "The person you rescued had a message: 'The Puzzle Goblin isn't who you think he is. He's actually trying to PROTECT something.'",
            "The clouds parted and you saw it: a door made entirely of light, floating in mid-air. Beyond it, everything was backwards, upside down, and inside out. Welcome to... THE PUZZLE DIMENSION.",
        ],
    },
    {
        "arc": 5,
        "name": "The Puzzle Dimension",
        "sessions": 5,
        "theme": "Mixed Review and Challenge",
        "description": "A dimension where the rules of reality are different and every challenge combines all skills.",
        "characters": ["The Mirror Mage", "The Puzzle Goblin (now ally)"],
        "hooks": [
            "Everything here is topsy-turvy! Numbers float in the air and words rearrange themselves!",
            "The Mirror Mage shows you reflections of challenges you've faced before -- but now they're HARDER!",
            "The Puzzle Goblin is fighting alongside you now! 'I was trying to WARN you about this place!'",
            "At the centre of the Dimension is the source of all puzzles. If you can solve it, you'll become true Masters!",
            "The final challenge. Everything you've learned. Everything you've discovered. It all comes down to THIS.",
        ],
        "cliffhangers": [
            "The Mirror Mage smiled: 'You remind me of someone I knew long ago. Someone very brave. Someone called... Captain Starlight.' WHAT?!",
            "The Puzzle Goblin looked at you with tears in his eyes: 'I wasn't always a goblin, you know. Once, I was an explorer... just like you.'",
            "The walls of the Puzzle Dimension began to crack. Through the cracks, you could see... YOUR LIVING ROOM! The Puzzle Dimension is connected to the REAL WORLD!",
            "You solved the Master Puzzle! As you did, the entire Dimension started to change. It wasn't scary anymore. It was... BEAUTIFUL. And a new door appeared. A door home.",
            "Captain Starlight hugged you both. 'You've done it. You're no longer Apprentice Explorers. You're TRUE Star Explorers. And you know what? I think a new adventure is just beginning...'",
        ],
    },
]


def get_arc(arc_number: int) -> dict:
    """Get a story arc by number (1-indexed)."""
    idx = (arc_number - 1) % len(STORY_ARCS)
    return STORY_ARCS[idx]


def get_session_position(session_number: int) -> tuple[int, int]:
    """Get (arc_number, position_within_arc) for a session number.
    Returns 1-indexed values."""
    arc = ((session_number - 1) // 5) + 1
    position = ((session_number - 1) % 5) + 1
    return arc, position


def generate_recap(team_state, children) -> str:
    """Generate a 'Previously on...' recap."""
    if team_state.sessions_completed == 0:
        return ""

    arc = get_arc(team_state.current_arc)
    lines = [f"Previously on Star Explorers..."]

    # Reference the current arc
    lines.append(f"You were exploring {arc['name']}!")

    # Reference recent callbacks
    unused_callbacks = [c for c in team_state.callbacks if not c.used]
    for cb in unused_callbacks[-2:]:
        lines.append(f"{cb.child} {cb.event}!")
        cb.used = True

    # Add cliffhanger resolution tease
    if team_state.cliffhanger:
        lines.append(f"And remember... {team_state.cliffhanger}")
        lines.append("Let's find out what happens next!")

    return "\n".join(lines)


def get_story_hook(session_number: int) -> str:
    """Get the story hook for a session."""
    arc_num, position = get_session_position(session_number)
    arc = get_arc(arc_num)
    idx = min(position - 1, len(arc["hooks"]) - 1)
    return arc["hooks"][idx]


def get_cliffhanger(session_number: int) -> str:
    """Get the cliffhanger for the end of a session."""
    arc_num, position = get_session_position(session_number)
    arc = get_arc(arc_num)
    idx = min(position - 1, len(arc["cliffhangers"]) - 1)
    return arc["cliffhangers"][idx]


def get_story_beat(session_number: int, beat_number: int) -> str:
    """Get a mini story beat for between questions."""
    arc = get_arc(get_session_position(session_number)[0])
    characters = arc["characters"]

    beats = [
        f"Great work! {random.choice(characters)} nods approvingly. 'You're getting closer!'",
        "You found a piece of the puzzle! One step closer to solving the mystery!",
        f"'Impressive!' says {random.choice(characters)}. 'I didn't think anyone could do that!'",
        "A golden light flickers ahead. Something magical is happening!",
        "The path ahead is clearing. Your answers are making the magic stronger!",
        f"{random.choice(characters)} whispers: 'Keep going! You're almost there!'",
        "A treasure chest appears in the corner of your eye! But first, more challenges await...",
        "The ground beneath your feet glows with each correct answer!",
    ]
    return beats[beat_number % len(beats)]


def get_boss_intro(session_number: int) -> str:
    """Get the boss challenge introduction."""
    arc_num, position = get_session_position(session_number)

    if position <= 3:
        return (
            "The Puzzle Goblin jumps out from behind a rock! "
            "'Ha HA! You'll never solve MY puzzles!' he cackles. "
            "'I have THREE challenges, and you BOTH have to work together to solve them! "
            "If you get stuck, you can use one of your team's Hint Stars. Ready?'"
        )
    elif position == 4:
        return (
            "The ground shakes! This is the BIG boss challenge! "
            "The Puzzle Goblin looks more serious than usual. "
            "'This is my HARDEST puzzle yet,' he says. 'But I have a feeling "
            "you two might just be clever enough...' "
            "You need to work TOGETHER on this one. Ready?"
        )
    else:
        return (
            "For the final challenge of this adventure, something unexpected happens. "
            "The Puzzle Goblin walks up to you and says: 'I want to help you this time. "
            "Because what's ahead... even I find tricky.' "
            "Together, all of you face the ultimate challenge!"
        )


# Movement break prompts
MOVEMENT_BREAKS = [
    "POWER-UP TIME! Jump up and down 5 times and count each jump! Ready? Go!",
    "Time for a STRETCH! Can you touch your toes? Now reach for the sky! Now touch your toes again!",
    "ANIMAL CHALLENGE! Walk like a penguin to the other side of the room and back! Waddle waddle!",
    "Do your SILLIEST dance for 10 seconds! Ready? Go! Ten, nine, eight...",
    "FREEZE! Stand on one leg like a flamingo! How long can you hold it? Count to 10!",
    "SPIN CHALLENGE! Spin around 3 times! Are you dizzy? Tell me how dizzy from 1 to 10!",
    "JUMPING JACKS! Can you do 5 jumping jacks? Let me hear you count them!",
    "TIPPY TOES! Walk on your tippy toes to the door and back! As quietly as a mouse!",
    "STAR JUMPS! Do 3 star jumps and shout 'STAR EXPLORER' on each one!",
    "ROBOT WALK! Walk like a robot around the room! Beep boop beep!",
]

# Silly break activities
SILLY_BREAKS = [
    {
        "name": "Tongue Twister",
        "read_aloud": "Tongue twister time! Can you say this three times fast: 'She sells sea shells on the sea shore!' Ready? Go!",
    },
    {
        "name": "Silly Voices",
        "read_aloud": "SILLY VOICE CHALLENGE! Say 'The Star Explorers are the bravest team in the universe' in the silliest voice you can! Who can be silliest?",
    },
    {
        "name": "What Does It Say?",
        "read_aloud": "What sound does a TOASTER make? How about a WASHING MACHINE? What about a DOOR BELL? Make the sounds!",
    },
    {
        "name": "Opposite Day",
        "read_aloud": "It's OPPOSITE TIME! I'm going to say something, and you say the opposite! Ready? I say BIG, you say...",
    },
    {
        "name": "Tongue Twister 2",
        "read_aloud": "Try this one! 'Peter Piper picked a peck of pickled peppers!' Say it three times fast! Go!",
    },
    {
        "name": "Animal Sounds",
        "read_aloud": "Can you do your BEST elephant sound? Now a LION! Now a MONKEY! Now do ALL THREE at the same time!",
    },
    {
        "name": "Silly Song",
        "read_aloud": "Let's sing 'Twinkle Twinkle Little Star' but replace EVERY word with 'banana'! Ready? BANANA banana banana banana...",
    },
    {
        "name": "Whisper Shout",
        "read_aloud": "I'm going to say a word and you have to WHISPER it back. Ready? ELEPHANT! Now SHOUT it! ELEPHANT! Now whisper again!",
    },
]

# Secret mission templates
SECRET_MISSIONS = [
    "Before our next call, try to find THREE things in your house that are shaped like a {shape}. Remember them!",
    "This week, count how many steps it takes to walk from your bedroom to the kitchen! Remember the number!",
    "Can you find something in your house that starts with every letter in YOUR NAME? Try it this week!",
    "This week, notice what shapes you see when you're outside. Are there more circles or rectangles? Count them!",
    "Ask Mummy a maths question this week! Make up your own! Tell me what you asked next time!",
    "Find the BIGGEST number you can spot in your house this week. It might be on a clock, a book, or anywhere!",
    "This week, try to spot 5 words when you're out and about. On signs, shops, anything! Remember them!",
    "Can you teach someone at home one thing you learned in our game? Tell me who you taught next time!",
]


def get_movement_break(session_number: int) -> str:
    """Get a movement break prompt."""
    return MOVEMENT_BREAKS[session_number % len(MOVEMENT_BREAKS)]


def get_silly_break(session_number: int) -> dict:
    """Get a silly break activity."""
    return SILLY_BREAKS[session_number % len(SILLY_BREAKS)]


def get_secret_mission(session_number: int) -> str:
    """Get a secret mission for between sessions."""
    template = SECRET_MISSIONS[session_number % len(SECRET_MISSIONS)]
    shapes = ["circle", "triangle", "rectangle", "square"]
    return template.format(shape=shapes[session_number % len(shapes)])


def generate_score_report(team_state, children, session_stats) -> str:
    """Generate the session score report narrative."""
    lines = []
    total = session_stats.get("team_score", 0)
    lines.append(f"Today, the Star Explorers earned {total} Adventure Points!")

    total_all = team_state.total_adventure_points
    lines.append(f"That brings your all-time total to {total_all} points!")

    for child_name, stats in session_stats.get("children", {}).items():
        correct = stats.get("correct", 0)
        asked = stats.get("asked", 0)
        if asked > 0:
            lines.append(f"{child_name} answered {correct} out of {asked} questions!")
        if stats.get("mastered"):
            for topic in stats["mastered"]:
                lines.append(f"{child_name} MASTERED {topic}!")
        if stats.get("new_learned"):
            lines.append(f"{child_name} learned {stats['new_learned']} new things!")

    return "\n".join(lines)
