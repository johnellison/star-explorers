#!/usr/bin/env python3
"""Generate game art for Star Explorers using Google Imagen or Fal.ai Flux.

Usage:
    python generate_images.py              # Generate all missing images
    python generate_images.py --test       # Generate 5 arc scenes only (quick test)
    python generate_images.py --dry-run    # Show manifest without generating
    python generate_images.py --backend fal  # Force Fal.ai backend

Auto-detects backend: uses Google Imagen if GOOGLE_AI_STUDIO_KEY is set,
falls back to Fal.ai if FAL_KEY is set.
"""

import os
import sys
import time
import argparse
import base64

sys.path.insert(0, os.path.dirname(__file__))
from story import STORY_ARCS

# Load .env file if present
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "static", "images")

STYLE_PREFIX = (
    "Digital illustration in a children's adventure storybook style, "
    "vibrant jewel-tone colors, deep space celestial background with "
    "nebula purples and cosmic teals, warm inviting atmosphere, "
    "whimsical and magical, suitable for ages 4-7, painterly digital art "
    "with soft glowing highlights. "
)

SCENE_PREFIX = STYLE_PREFIX + "Wide landscape composition, sense of wonder and adventure. "
CHAR_PREFIX = STYLE_PREFIX + "Character portrait, centered composition, friendly expression, large expressive eyes. "
UI_PREFIX = STYLE_PREFIX + "Centered icon composition, bold and celebratory, glowing effects. "

# Character visual descriptions
CHARACTER_PROMPTS = {
    "captain_starlight": (
        "A wise and kind space captain with silver hair, a deep blue coat with "
        "glowing star emblem on the chest, warm smile, standing heroically against "
        "a starry sky backdrop. Human, approachable, fatherly figure."
    ),
    "wise_owl": (
        "A large, magical owl with iridescent purple and blue feathers, wearing "
        "tiny golden spectacles, perched on a glowing branch in an enchanted forest. "
        "Wise and gentle expression, surrounded by floating sparkles."
    ),
    "puzzle_goblin": (
        "A small mischievous goblin with bright green skin, pointy ears, wearing "
        "a patchwork vest covered in puzzle pieces. Playful grin, holding a glowing "
        "puzzle cube. Not scary, more silly and endearing."
    ),
    "crystal_dragon": (
        "A friendly young dragon made of translucent purple and blue crystals, "
        "glowing from within. Small and cute, with big sparkling eyes, tiny wings "
        "catching rainbow light. Sitting in a crystal cave."
    ),
    "echo_sprite": (
        "A tiny glowing sprite made of pure sound waves, translucent blue-white body, "
        "with musical notes floating around them. Joyful expression, bouncing through "
        "a crystal cave with echo ripples trailing behind."
    ),
    "island_guardian": (
        "A gentle giant made of living rock and tropical plants, with flowers "
        "growing from its shoulders and vines for hair. Kind mossy face with "
        "glowing amber eyes, standing on a golden beach at sunset."
    ),
    "professor_parrot": (
        "A colorful parrot wearing a tiny professor's mortarboard hat and monocle, "
        "with brilliant rainbow plumage. Standing on a stack of books on a tropical "
        "island, looking scholarly yet comical."
    ),
    "cloud_shepherd": (
        "A serene figure dressed in flowing white and silver robes, walking among "
        "fluffy cloud-sheep in a kingdom above the clouds. Gentle face, carrying "
        "a staff that trails stardust. Pastel sky colors."
    ),
    "word_weaver": (
        "An elegant figure sitting at a magical loom that weaves glowing letters "
        "and words into tapestries. Long flowing hair with words woven into it, "
        "surrounded by floating alphabet letters in golden light."
    ),
    "mirror_mage": (
        "A mysterious but friendly wizard made of reflective surfaces, wearing "
        "a robe that shows mirror reflections of other worlds. Holding a staff "
        "topped with a floating mirror. Surrounded by floating geometric shapes."
    ),
}


def arc_slug(arc_name):
    """Convert arc name to filename slug."""
    return arc_name.lower().replace("the ", "").replace(" ", "_")


def build_manifest():
    """Build the complete list of images to generate."""
    manifest = []

    # Title hero
    manifest.append({
        "path": "title_hero.png",
        "prompt": (
            SCENE_PREFIX
            + "Two small child explorers in space suits standing on a glowing asteroid, "
            "looking out at a vast colorful nebula filled with purple, teal, and gold. "
            "Magical, awe-inspiring, the beginning of an adventure."
        ),
        "category": "title",
    })

    # Arc scenes
    arc_descriptions = {
        "The Enchanted Forest": (
            "A magical enchanted forest at night under a starry sky, with bioluminescent "
            "trees glowing purple and blue, fireflies and sparkles floating everywhere, "
            "a winding path of golden light leading deeper into the forest. Mushrooms "
            "glow softly, and mystical creatures peek from behind trees."
        ),
        "The Crystal Caves": (
            "A vast underground crystal cave glowing with purple, blue, and teal crystals, "
            "reflecting light in rainbow patterns. Stalactites of pure crystal hang from "
            "the ceiling, a underground river flows with glowing water, and floating "
            "crystal orbs illuminate the cavern."
        ),
        "The Hidden Island": (
            "A mysterious tropical island seen from above, surrounded by turquoise water, "
            "with a dense jungle, golden sandy beaches, a volcano with a soft glow, "
            "and ancient ruins peeking through the trees. Birds and butterflies fly "
            "around. A telescope sits on the beach pointing to the sky."
        ),
        "The Sky Kingdom": (
            "A magnificent kingdom built on clouds high above the earth, with castles "
            "and towers made of solidified cloud and rainbow bridges connecting them. "
            "Cloud-sheep graze on cloud meadows, the sun sets in brilliant pink and gold, "
            "and words float in the air like golden butterflies."
        ),
        "The Puzzle Dimension": (
            "A surreal dimension where reality is broken — floating geometric shapes, "
            "Escher-like staircases going in impossible directions, numbers and letters "
            "floating in the air, portals showing different worlds, and a swirling "
            "vortex of purple and gold energy at the center. Trippy but friendly."
        ),
    }

    for story_arc in STORY_ARCS:
        slug = arc_slug(story_arc["name"])
        desc = arc_descriptions.get(story_arc["name"], story_arc["description"])
        manifest.append({
            "path": f"arcs/{slug}.png",
            "prompt": SCENE_PREFIX + desc,
            "category": "arc",
        })

    # Characters
    for char_slug, desc in CHARACTER_PROMPTS.items():
        manifest.append({
            "path": f"characters/{char_slug}.png",
            "prompt": CHAR_PREFIX + desc,
            "category": "character",
        })

    # Story hooks (5 arcs x 5 hooks = 25)
    for story_arc in STORY_ARCS:
        arc_num = story_arc["arc"]
        for i, hook in enumerate(story_arc["hooks"]):
            manifest.append({
                "path": f"hooks/arc{arc_num}_hook{i + 1}.png",
                "prompt": SCENE_PREFIX + hook,
                "category": "hook",
            })

    # Cliffhangers (5 arcs x 5 = 25)
    for story_arc in STORY_ARCS:
        arc_num = story_arc["arc"]
        for i, cliff in enumerate(story_arc["cliffhangers"]):
            manifest.append({
                "path": f"cliffhangers/arc{arc_num}_cliff{i + 1}.png",
                "prompt": SCENE_PREFIX + "Dramatic and mysterious scene. " + cliff,
                "category": "cliffhanger",
            })

    # Boss encounters
    manifest.append({
        "path": "boss/puzzle_goblin_challenge.png",
        "prompt": (
            SCENE_PREFIX
            + "A mischievous green goblin in a patchwork vest covered in puzzle pieces, "
            "cackling and holding up a glowing puzzle cube, standing in a dramatic pose "
            "on a rock. Dark dramatic lighting with red and purple glow. Boss battle "
            "energy, but still kid-friendly and not scary."
        ),
        "category": "boss",
    })
    manifest.append({
        "path": "boss/puzzle_goblin_defeated.png",
        "prompt": (
            SCENE_PREFIX
            + "A small green goblin sitting on the ground looking impressed and amazed, "
            "surrounded by solved puzzle pieces. Golden victory light streaming down, "
            "confetti and stars falling. The goblin is clapping. Celebratory, triumphant mood."
        ),
        "category": "boss",
    })

    # UI elements
    ui_images = {
        "achievement_unlocked.png": (
            "A glowing golden star trophy floating in space, surrounded by sparkles "
            "and confetti, with rays of golden light. Achievement unlocked celebration."
        ),
        "treasure_chest.png": (
            "A magical treasure chest opening with golden light pouring out, filled "
            "with glowing gems and stars, floating in space. The chest has celestial "
            "decorations and a star emblem on the lock."
        ),
        "lightning_round.png": (
            "A dramatic lightning bolt made of golden energy striking through a cosmic "
            "background, with speed lines and electrical sparkles. Fast, energetic, exciting."
        ),
        "mission_complete.png": (
            "Two child explorers in space suits raising their fists in triumph on top "
            "of a glowing planet, with fireworks and stars exploding in the sky. "
            "Celebratory, victorious, the end of a successful mission."
        ),
        "power_up.png": (
            "A glowing energy orb pulsing with rainbow cosmic energy, surrounded by "
            "swirling stardust and ascending light beams. Power level increasing, "
            "transformation energy."
        ),
    }
    for filename, desc in ui_images.items():
        manifest.append({
            "path": f"ui/{filename}",
            "prompt": UI_PREFIX + desc,
            "category": "ui",
        })

    return manifest


# --- Image Generation Backends ---

def generate_image_google(prompt):
    """Generate image using Google Imagen 3 via google-genai SDK."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GOOGLE_AI_STUDIO_KEY", "")
    if not api_key:
        raise ValueError("GOOGLE_AI_STUDIO_KEY not set")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            safety_filter_level="BLOCK_LOW_AND_ABOVE",
        ),
    )

    if not response.generated_images:
        raise RuntimeError("No images returned from Imagen API")

    return response.generated_images[0].image.image_bytes


def generate_image_fal(prompt):
    """Generate image using Fal.ai Flux Dev."""
    import requests

    api_key = os.environ.get("FAL_KEY", "")
    if not api_key:
        raise ValueError("FAL_KEY not set")

    response = requests.post(
        "https://fal.run/fal-ai/flux/dev",
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "prompt": prompt,
            "image_size": "landscape_16_9",
            "num_images": 1,
            "enable_safety_checker": True,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    image_url = data["images"][0]["url"]
    img_response = requests.get(image_url, timeout=60)
    img_response.raise_for_status()
    return img_response.content


def detect_backend():
    """Auto-detect which backend to use based on available keys."""
    if os.environ.get("GOOGLE_AI_STUDIO_KEY"):
        return "google"
    if os.environ.get("FAL_KEY"):
        return "fal"
    return None


def main():
    parser = argparse.ArgumentParser(description="Generate Star Explorers game art")
    parser.add_argument("--test", action="store_true", help="Generate only arc scenes (5 images)")
    parser.add_argument("--dry-run", action="store_true", help="Show manifest without generating")
    parser.add_argument("--category", type=str,
                        help="Only generate a specific category (title, arc, character, hook, cliffhanger, boss, ui)")
    parser.add_argument("--backend", type=str, choices=["google", "fal"],
                        help="Force a specific backend (default: auto-detect)")
    args = parser.parse_args()

    manifest = build_manifest()

    if args.test:
        manifest = [m for m in manifest if m["category"] == "arc"]
    elif args.category:
        manifest = [m for m in manifest if m["category"] == args.category]

    # Count what needs generating
    to_generate = []
    already_exist = 0
    for item in manifest:
        filepath = os.path.join(OUTPUT_DIR, item["path"])
        if os.path.exists(filepath):
            already_exist += 1
        else:
            to_generate.append(item)

    # Detect backend
    backend = args.backend or detect_backend()
    backend_label = {
        "google": "Google Imagen 3",
        "fal": "Fal.ai Flux Dev",
    }.get(backend, "none")

    print(f"\n{'=' * 60}")
    print(f"  STAR EXPLORERS - Image Generation")
    print(f"{'=' * 60}")
    print(f"  Backend:           {backend_label}")
    print(f"  Total in manifest: {len(manifest)}")
    print(f"  Already exist:     {already_exist}")
    print(f"  To generate:       {len(to_generate)}")
    print(f"{'=' * 60}\n")

    if args.dry_run:
        for item in manifest:
            filepath = os.path.join(OUTPUT_DIR, item["path"])
            exists = "EXISTS" if os.path.exists(filepath) else "MISSING"
            print(f"  [{exists}] {item['path']}")
            if not os.path.exists(filepath):
                print(f"           Prompt: {item['prompt'][:100]}...")
        return

    if not to_generate:
        print("  All images already exist! Nothing to generate.")
        return

    if not backend:
        print("  ERROR: No API key found.")
        print("  Set GOOGLE_AI_STUDIO_KEY or FAL_KEY in .env")
        sys.exit(1)

    generate_fn = generate_image_google if backend == "google" else generate_image_fal

    errors = []
    for i, item in enumerate(to_generate):
        filepath = os.path.join(OUTPUT_DIR, item["path"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        print(f"  [{i + 1}/{len(to_generate)}] Generating: {item['path']}...")

        try:
            img_bytes = generate_fn(item["prompt"])
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            size_kb = len(img_bytes) / 1024
            print(f"           Saved ({size_kb:.0f} KB)")
            # Rate limit between requests
            if i < len(to_generate) - 1:
                time.sleep(2)
        except Exception as e:
            print(f"           ERROR: {e}")
            errors.append((item["path"], str(e)))

    print(f"\n{'=' * 60}")
    print(f"  Generation complete!")
    print(f"  Successful: {len(to_generate) - len(errors)}")
    if errors:
        print(f"  Failed:     {len(errors)}")
        for path, err in errors:
            print(f"    - {path}: {err}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
