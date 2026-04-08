"""Story engine for Star Explorers - continuous campaign narrative."""

import random


def _level(
    number,
    name,
    objective,
    intro,
    beat_1,
    beat_2,
    movement_title,
    movement_text,
    silly_name,
    silly_text,
    boss_intro,
    reward_name,
    reward_summary,
    reward_icon,
    next_hook,
    characters,
    boss_victory,
    break_interaction=None,
):
    return {
        "level_number": number,
        "level_name": name,
        "objective": objective,
        "intro": intro,
        "progress_beats": [beat_1, beat_2],
        "movement_break": {
            "title": movement_title,
            "text": movement_text,
            "interaction": break_interaction,
        },
        "silly_break": {
            "name": silly_name,
            "read_aloud": silly_text,
        },
        "boss_intro": boss_intro,
        "boss_victory": boss_victory,
        "reward": {
            "name": reward_name,
            "summary": reward_summary,
            "icon": reward_icon,
        },
        "next_hook": next_hook,
        "characters_in_scene": characters,
    }


def _world(number, name, theme, description, characters, world_reward, levels):
    hooks = [level["intro"] for level in levels]
    cliffhangers = [level["next_hook"] for level in levels]
    return {
        "arc": number,
        "world_number": number,
        "name": name,
        "theme": theme,
        "description": description,
        "characters": characters,
        "world_reward": world_reward,
        "sessions": len(levels),
        "levels": levels,
        "hooks": hooks,
        "cliffhangers": cliffhangers,
    }


CHARACTER_GUIDE = {
    "Captain Starlight": {
        "role": "Mission guide and steady team leader.",
        "summary": "Captain Starlight keeps the team moving, explains the stakes, and celebrates every unlocked path.",
    },
    "Wise Owl": {
        "role": "Forest mentor.",
        "summary": "The Wise Owl teaches the Star Explorers how each solved challenge repairs the world around them.",
    },
    "Puzzle Goblin": {
        "role": "Rival who slowly becomes an ally.",
        "summary": "The Puzzle Goblin causes trouble early on, then reveals he has been trying to hold the Puzzle Dimension back.",
    },
    "The Crystal Dragon": {
        "role": "Guardian transport and relic keeper.",
        "summary": "The Crystal Dragon protects the caves, rewards brave progress, and carries the team between worlds.",
    },
    "Echo Sprite": {
        "role": "Scout and clue repeater.",
        "summary": "Echo Sprite bounces clues around the caves and turns hidden routes into playable goals.",
    },
    "The Island Guardian": {
        "role": "Protector of living places.",
        "summary": "The Island Guardian watches over the Hidden Island and raises the stakes whenever the island reacts to danger.",
    },
    "Professor Parrot": {
        "role": "Word expert and comic support.",
        "summary": "Professor Parrot keeps language puzzles lively while delivering the clue that pushes the campaign upward to the clouds.",
    },
    "The Cloud Shepherd": {
        "role": "Path builder.",
        "summary": "The Cloud Shepherd opens safe routes through the sky and turns spoken commands into traversal mechanics.",
    },
    "The Word Weaver": {
        "role": "World repair specialist.",
        "summary": "The Word Weaver makes the campaign feel cumulative by turning solved challenges into repaired cloth, sunshine, and opened doors.",
    },
    "The Mirror Mage": {
        "role": "Final world truth revealer.",
        "summary": "The Mirror Mage forces the team to revisit what they learned and frames the final world as the source of every earlier problem.",
    },
}


CAMPAIGN_WORLDS = [
    _world(
        1,
        "The Enchanted Forest",
        "Discovery and Repair",
        "The team learns that each solved challenge restores a forest that has been scrambled by puzzle magic.",
        ["Captain Starlight", "Wise Owl", "Puzzle Goblin"],
        {"name": "Forest Lantern Compass", "icon": "🧭"},
        [
            _level(
                1,
                "Lantern Trail",
                "Relight the fallen star lanterns and open the forest gate.",
                "Captain Starlight lands beside a dark forest gate. The star lanterns that once lit the path are out, and the Wise Owl says the only way forward is to relight them one by one.",
                "A row of lanterns flickers back to life. The Wise Owl points deeper into the trees: the forest is starting to remember the way.",
                "More lanterns glow and a trail of gold sparks climbs toward the gate lock. Somewhere ahead, the Puzzle Goblin laughs and runs.",
                "Charge The Lanterns",
                "Do 5 big star jumps to send fresh starlight into the lantern trail. Count every jump out loud.",
                "Owl Echo Check",
                "The Wise Owl gives a secret forest call. Copy it back in your silliest owl voice so she knows the team is ready.",
                "The Puzzle Goblin tangles the gate in glowing roots and shouts, 'If you want in, you have to untwist my gate puzzle first!'",
                "Forest Lantern Compass",
                "A bright compass that points toward places your teamwork can repair next.",
                "🧭",
                "The gate opens, and the Wise Owl whispers that the next path can only be seen by those who listen carefully to the trees.",
                ["Captain Starlight", "Wise Owl", "Puzzle Goblin"],
                "The roots fall away and the lantern gate bursts open. Captain Starlight lifts the Forest Lantern Compass and says, 'Level clear. The forest trusts you now.'",
            ),
            _level(
                2,
                "Whispering Grove",
                "Collect whisper leaves and reveal the hidden route through the grove.",
                "Inside the forest, every path curls back on itself. The Wise Owl explains that only whisper leaves can reveal the true route, but the Puzzle Goblin keeps blowing them away before anyone can read them.",
                "The first whisper leaves glow with silver writing. Captain Starlight reads the clues aloud, and a safe trail appears between the trees.",
                "The hidden route widens into a clear lane of moonlight. At the far end stands the oldest tree in the forest, humming with locked-up magic.",
                "Sneak Past The Brambles",
                "Tiptoe like quiet explorers past the scratchy brambles. Reach one arm high, then crouch low, then tiptoe back again.",
                "Leaf Decoder",
                "Professor Owl says each whisper leaf sounds funny when read backwards. Say one silly made-up leaf word in your best secret-agent voice.",
                "A swirl of flying leaves becomes a spinning puzzle wall. The Puzzle Goblin cackles, 'Catch the clues if you can! The grove won't tell you anything for free!'",
                "Whisper Leaf Map",
                "A map of hidden routes etched onto enchanted leaves.",
                "🍃",
                "The moonlit lane ends at the oldest tree in the forest. Beneath its roots, a tiny door begins to glow.",
                ["Captain Starlight", "Wise Owl", "Puzzle Goblin"],
                "The spinning leaves settle into a readable map. Captain Starlight smiles: 'Now we know where the secret door is hiding.'",
            ),
            _level(
                3,
                "Wishing Tree Workshop",
                "Repair the Wishing Tree before the forest loses its last safe shelter.",
                "The oldest tree opens into a workshop filled with snapped gears, carved stars, and half-finished wishes. The Wise Owl explains that the Puzzle Goblin stole the tree's best parts because he thought someone else would steal them first.",
                "One by one, the workshop lights switch back on. The Wishing Tree starts carving glowing symbols into the bark.",
                "The tree's branches stretch wide and reveal a root-shaped keyhole under the floorboards. The Puzzle Goblin is still nearby, but now he sounds more worried than proud.",
                "Workshop Stretch",
                "Pretend to lift heavy wooden beams into place. Reach up high, bend down low, then hammer the last beam with 3 big air taps.",
                "Wish Test",
                "The Wishing Tree wants to know if the team is kind and clever. Whisper one brave wish and one silly wish into your hands, then blow them toward the tree.",
                "The Puzzle Goblin builds a rattling workshop machine around the tree and yells, 'If the tree gets repaired, the caves will wake up! You don't understand yet!'",
                "Wishwood Cog",
                "A carved wooden cog that can unlock root-powered machines.",
                "⚙️",
                "When the Wishing Tree steadies, its roots pull back and uncover a tiny door with a star-shaped slot.",
                ["Captain Starlight", "Wise Owl", "Puzzle Goblin"],
                "The workshop machine clatters apart, and the Wishing Tree drops a glowing cog into Captain Starlight's hands.",
            ),
            _level(
                4,
                "Root Door Riddles",
                "Unlock the tiny root door beneath the oldest tree.",
                "Captain Starlight fits the Wishwood Cog into the root door, but five carved runes still block the way. The Wise Owl says the door was built to protect something important below the forest.",
                "The top runes spin into place and the root door creaks open just enough to leak blue crystal light.",
                "The last rune clicks, and cold cave air rushes upward. The Puzzle Goblin stops laughing altogether and stares at the stairway in silence.",
                "Rune Reach",
                "Stretch up to tap the top rune, crouch to tap the bottom rune, then spin once like the rune wheel turning into place.",
                "Door Password Practice",
                "The root door loves silly passwords. Make up a tiny magic word and say it in a whisper, then in a giant booming voice.",
                "The locked door sprouts twisting wooden faces that ask the team for one final riddle. The Puzzle Goblin mutters, 'Maybe if the door stayed shut, we'd all be safer.'",
                "Rootwork Key",
                "A key that opens old locks built by the forest itself.",
                "🗝️",
                "The stairway below glows with crystal light, and a distant underground river begins to roar.",
                ["Captain Starlight", "Wise Owl", "Puzzle Goblin"],
                "The tiny door swings wide and reveals a spiralling staircase into the Crystal Caves.",
            ),
            _level(
                5,
                "Goblin's Warning",
                "Stabilize the cave mouth before the forest magic spills underground.",
                "At the bottom of the stairway, the cave mouth is cracking. The Puzzle Goblin finally admits he has been moving pieces around because something deeper below is pushing puzzle magic upward into every world.",
                "The Wise Owl helps seal the first crack, and the cave walls stop shaking long enough for the team to move forward.",
                "A crystal breeze clears the dust. The Puzzle Goblin leaves behind a map shard and disappears into the glow, shouting, 'Catch up if you want answers!'",
                "Cave Brace Drill",
                "Plant your feet wide like a cave brace, push your hands forward, then hold strong while you count to 5.",
                "Emergency Owl Signal",
                "Send the Wise Owl's warning call down the tunnel: one quiet 'hoo', one loud 'HOO', and one super-silly echo.",
                "The cracked cave mouth turns into a final forest boss gate. Captain Starlight shouts over the rumble: 'Seal it now, or the whole forest goes dark again!'",
                "Cave Map Shard",
                "A shard of glowing crystal map that points toward the lower tunnels.",
                "🧩",
                "The forest is safe, but the map shard reveals a route into the Crystal Caves. The Puzzle Goblin's warning was real.",
                ["Captain Starlight", "Wise Owl", "Puzzle Goblin"],
                "As the cave mouth steadies, Captain Starlight lifts the map shard and says, 'World 1 complete. Now we follow the trouble underground.'",
            ),
        ],
    ),
    _world(
        2,
        "The Crystal Caves",
        "Patterns and Echoes",
        "The team chases the source of the strange puzzle magic into the caves and begins collecting the tools needed to cross into new worlds.",
        ["Captain Starlight", "The Crystal Dragon", "Echo Sprite", "Puzzle Goblin"],
        {"name": "Ocean Prism Route", "icon": "💎"},
        [
            _level(
                1,
                "Prism Descent",
                "Restore the crystal lift and descend safely into the lower caves.",
                "The root stairway ends beside a shattered crystal lift. Echo Sprite zips between the broken rails while the Crystal Dragon watches from the shadows, waiting to see whether the Star Explorers can rebuild the path down.",
                "The lift hums back to life and the lowest crystals pulse with number-light.",
                "The platform reaches the lower cavern, where crystal doors reflect the team in a hundred shimmering copies.",
                "Crystal Charge",
                "Jump, clap, and freeze three times to charge the lift crystals. Make each clap as sharp as crystal light.",
                "Echo Check",
                "Echo Sprite speaks in bouncy sounds. Repeat a silly echo phrase and make it get quieter each time.",
                "A crystal guardian seal locks the lift in place. The Crystal Dragon lowers her head and says, 'Show me you can finish what you start.'",
                "Prism Lantern",
                "A lantern that shines through hidden crystal seams.",
                "💎",
                "The restored lift sinks deeper into the caves, where the echoes are spelling directions on the walls.",
                ["Captain Starlight", "The Crystal Dragon", "Echo Sprite"],
                "The lift settles at the lower cavern and the Crystal Dragon steps aside. 'You may continue,' she says.",
            ),
            _level(
                2,
                "Echo Tunnel Relay",
                "Follow Echo Sprite's clues and collect the three number crystals.",
                "The lower tunnels split in every direction. Echo Sprite promises to guide the team, but only if they can follow the order of the bouncing clues before the sound fades away.",
                "The first two number crystals ring together, forming a safe path over the glowing cave floor.",
                "The third crystal unlocks a circular chamber covered in treasure marks. The Crystal Dragon smiles for the first time.",
                "Tunnel Dash",
                "Run on the spot for 10 beats, then freeze and point left, right, and straight ahead like you are following Echo Sprite through the tunnels.",
                "Echo Orchestra",
                "Make one tiny echo sound, one medium echo sound, and one giant cave echo sound. Echo Sprite says the last one should shake the walls.",
                "The final tunnel seals itself with an echo lock. The Crystal Dragon warns, 'Only the team that can follow the true pattern will hear the door open.'",
                "Resonance Bell",
                "A bell that rings whenever the right pattern is found.",
                "🔔",
                "The echo lock opens onto the Crystal Dragon's treasure halls, but several treasure beams are broken and flickering.",
                ["Captain Starlight", "The Crystal Dragon", "Echo Sprite"],
                "The tunnel answers with a bright chime, and Echo Sprite loops happily around the team's heads.",
            ),
            _level(
                3,
                "Dragon's Hoard Recovery",
                "Return the scattered treasure crystals to the Crystal Dragon.",
                "Broken treasure beams zigzag across the cavern floor. The Crystal Dragon explains that the Puzzle Goblin moved some treasure to keep it from being stolen by the deeper magic spreading through the caves.",
                "One treasure beam reconnects, lighting the first shelf of the Dragon's hoard.",
                "The hoard chamber opens fully, revealing a river chart hidden behind the treasure vault.",
                "Treasure Haul",
                "Pretend to carry heavy crystals from one side of the room to the other. Big careful steps. No dropping the treasure.",
                "Dragon Voice Test",
                "The Crystal Dragon wants to hear a tiny dragon voice and a gigantic dragon voice. Try both, then roar your best victory roar.",
                "A glittering crystal vault rises up and blocks the final hoard shelf. The Crystal Dragon says, 'Return the last piece, and I will trust you with a route nobody else can see.'",
                "Scale Seal",
                "A dragon-mark seal that opens guarded vaults and protected routes.",
                "🐉",
                "Behind the restored hoard, a chart of water currents reveals a hidden underground river flowing toward the sea.",
                ["Captain Starlight", "The Crystal Dragon", "Puzzle Goblin"],
                "The last treasure crystal slots into place, and the Dragon's vault opens with a beam of blue-gold light.",
            ),
            _level(
                4,
                "River Of Reflections",
                "Cross the underground river by activating the pattern beacons.",
                "The river under the caves reflects upside-down stars. Captain Starlight can see an exit toward the sea, but only the right sequence of pattern beacons will keep the stepping stones above water.",
                "The first beacon rises, turning the river into a glowing dotted path.",
                "Three beacons shine together and form a bridge of mirrored crystal. Beyond it, sea-wind pours through the cave mouth.",
                "Beacon Hops",
                "Hop from one imaginary stepping stone to the next. Count each safe hop so Captain Starlight knows the bridge is holding.",
                "River Reporter",
                "Describe the river in one brave voice and one very silly voice. Echo Sprite wants both versions for the cave records.",
                "A mirror current swirls into a final beacon lock. Captain Starlight points ahead: 'Cross this, and we reach the coast route.'",
                "Tide Compass",
                "A compass that points toward safe water routes.",
                "🌊",
                "The sea can be heard clearly now. The Crystal Dragon says the team is almost ready for the heart of the caves.",
                ["Captain Starlight", "The Crystal Dragon", "Echo Sprite"],
                "The beacons connect into a shining path across the river, and the sea breeze rushes in.",
            ),
            _level(
                5,
                "Heart Of The Caves",
                "Unlock the Dragon Heart Crystal and reveal the route to the Hidden Island.",
                "At the deepest chamber sits the Dragon Heart Crystal, dark and still. The Crystal Dragon explains that it will only awaken for a team that can solve the final cave sequence together.",
                "Cracks of light spread through the Dragon Heart Crystal. The chamber walls fill with the shape of waves and distant islands.",
                "The crystal brightens into a full ocean map, and a river tunnel opens all the way to the surface.",
                "Heartbeat Charge",
                "Tap your chest, clap twice, then stomp once. The Dragon Heart Crystal is matching the team's rhythm.",
                "Crystal Countdown",
                "Count down from 5 like the whole cave is about to launch you toward the sea.",
                "The Dragon Heart Crystal floats into the air and projects a giant final cave puzzle. The Crystal Dragon says, 'Solve this, and the coast path is yours.'",
                "Ocean Map Prism",
                "A prism that projects the ocean route to the Hidden Island.",
                "🗺️",
                "The Dragon Heart Crystal reveals a bright route out to sea, where a hidden island waits beyond the mist.",
                ["Captain Starlight", "The Crystal Dragon", "Echo Sprite", "Puzzle Goblin"],
                "The Dragon Heart Crystal blazes awake and projects the route to the Hidden Island across the cavern ceiling.",
            ),
        ],
    ),
    _world(
        3,
        "The Hidden Island",
        "Investigation and Discovery",
        "The team reaches a living island that reacts to their progress and hides the route to the sky.",
        ["Captain Starlight", "The Island Guardian", "Professor Parrot", "Puzzle Goblin"],
        {"name": "Tide Telescope", "icon": "🔭"},
        [
            _level(
                1,
                "Beachhead Beacon",
                "Light the beach beacons so the Island Guardian can find you.",
                "The Crystal Dragon lands the team on a silent beach. The Island Guardian cannot approach until the three beach beacons are lit, because the whole island has gone dim.",
                "The first beacon lights and the tide pulls back to reveal stone arrows in the sand.",
                "All three beacons blaze together, and the Island Guardian steps out of the mist to welcome the team properly.",
                "Beacon Sprint",
                "Run to the first beacon, reach high to light it, then sprint to the second and third. Count every light-up step.",
                "Seagull Code",
                "Professor Parrot teaches the team a beach signal. Say it once like a polite explorer and once like a very bossy seagull.",
                "A ring of dark shells spins into a beacon lock. The Island Guardian calls, 'Light this last beacon and the island will let you pass.'",
                "Shell Beacon",
                "A shell lantern that calls island allies when lit.",
                "🐚",
                "The beach path opens into the jungle, where giant footprints cross the sand toward the trees.",
                ["Captain Starlight", "The Island Guardian", "Professor Parrot"],
                "The final beach beacon flares to life and the Island Guardian bows in thanks.",
            ),
            _level(
                2,
                "Jungle Footprint Trail",
                "Track the giant footprints to the talking jungle.",
                "The jungle floor is covered in giant footprints and broken branches. Professor Parrot insists they belong to something important, while the Island Guardian says the island itself is trying to guide the team.",
                "The footprints line up with glowing plants that mark the safe route.",
                "The trail leads to a vine gate that opens only when the team follows the island's pattern correctly.",
                "Jungle Stomp",
                "Stomp like a giant island beast, then freeze and listen for the next footprint clue.",
                "Parrot Narrator",
                "Professor Parrot wants a jungle report. Describe the biggest footprint in a serious explorer voice and then in your silliest parrot voice.",
                "A vine gate slams down over the final clearing. The Island Guardian says, 'The island is testing whether you truly followed its trail.'",
                "Footprint Journal",
                "A journal that records clues left by living places.",
                "📘",
                "The jungle trail opens to a rocky overlook where Professor Parrot's broken signal tower leans over the sea.",
                ["Captain Starlight", "The Island Guardian", "Professor Parrot"],
                "The vine gate opens, and the island's glowing footprints fade into a neat trail behind the team.",
            ),
            _level(
                3,
                "Parrot Signal Tower",
                "Help Professor Parrot rebuild the signal tower.",
                "Professor Parrot's old signal tower once called friendly ships and explorers to the island. Now it leans sideways, and the only thing still working is the emergency telescope mount at the top.",
                "The tower frame straightens, and the top platform points toward the clouds.",
                "The rebuilt tower catches a flashing signal from far above. Someone is trapped in the Sky Kingdom and needs help.",
                "Tower Builder",
                "Pretend to carry three tower pieces into place. Lift, balance, and lock them with a stomp.",
                "Parrot Broadcast",
                "Send a rescue message through the tower. Say 'Star Explorers reporting in!' once clearly and once like a squawking radio signal.",
                "The final tower brace locks behind a gusty puzzle wall. Professor Parrot squawks, 'Fix this, and we can send the message sky-high!'",
                "Sky Telescope Lens",
                "A powerful lens that can spot routes far above the clouds.",
                "🔭",
                "Through the repaired tower lens, the team sees broken ruins across a deep ravine and a clue about a bridge to the starwatch ruins.",
                ["Captain Starlight", "Professor Parrot", "The Island Guardian"],
                "The signal tower stands tall again, and the emergency lens flashes with a message from the sky.",
            ),
            _level(
                4,
                "Bridge To Starwatch Ruins",
                "Repair the broken bridge and reach the starwatch ruins.",
                "To reach the island's starwatch ruins, the team must cross a broken plank bridge hanging over a roaring gorge. The Island Guardian says the ruins contain the mechanism that points the telescope upward for good.",
                "Fresh planks stretch halfway across the ravine. Professor Parrot starts shouting directions from the near side.",
                "The repaired bridge reaches the far ledge, and the starwatch ruins crackle with stored starlight.",
                "Bridge Repair",
                "The bridge needs power and brave hammering. Tap the planks into place and keep the crossing steady.",
                "Builder Cheer",
                "Shout one big builder cheer for every new plank. The louder the cheer, the steadier the bridge.",
                "The broken bridge twists into a final repair puzzle. Captain Starlight braces the ropes and shouts, 'One more push and the route is ours!'",
                "Starwatch Gear",
                "A brass gear that turns observatories and old sky machines.",
                "🪵",
                "The starwatch ruins awaken and point a beam toward the glowing heart of the island.",
                ["Captain Starlight", "Professor Parrot", "The Island Guardian"],
                "The last plank slams into place, and the whole bridge glows long enough for the team to race across.",
                break_interaction="bridge_repair",
            ),
            _level(
                5,
                "Living Island Heart",
                "Reach the island heart chamber and claim the Tide Telescope.",
                "The beam from the ruins leads to the centre of the island, where giant roots circle a hidden chamber. The Island Guardian admits the island is alive and has been waiting for explorers brave enough to wake its heart safely.",
                "The chamber walls bloom with maps of wind, tide, and starlight routes.",
                "At the centre pedestal, the Tide Telescope rises from the island heart and points toward a kingdom above the clouds.",
                "Island Heartbeat",
                "Put one hand on your heart and stomp softly with the island's pulse: tap, tap, stomp. Keep the rhythm together.",
                "Treasure Reveal",
                "Before the island shows its treasure, make your biggest excited gasp and your tiniest surprised squeak.",
                "The island heart projects a final living puzzle. The Island Guardian says, 'Solve this, and the island will trust you with its greatest treasure.'",
                "Tide Telescope",
                "A telescope that can see routes hidden between the sea and the sky.",
                "🔭",
                "Through the Tide Telescope, the team sees a trapped messenger in the Sky Kingdom and a cloud path waiting to be restored.",
                ["Captain Starlight", "The Island Guardian", "Professor Parrot", "Puzzle Goblin"],
                "The island heart lifts the Tide Telescope into Captain Starlight's hands, and the clouds above part to reveal the next world.",
            ),
        ],
    ),
    _world(
        4,
        "The Sky Kingdom",
        "Language, Routes, and Rescue",
        "The team climbs into the clouds, repairs the sky's broken machinery, and learns that the Puzzle Goblin has been trying to hold the final world back.",
        ["Captain Starlight", "The Cloud Shepherd", "The Word Weaver", "Puzzle Goblin"],
        {"name": "Door Of Light Sigil", "icon": "☁️"},
        [
            _level(
                1,
                "Rainbow Bridge Ascent",
                "Secure the rainbow bridge and open a safe cloud path.",
                "The Tide Telescope projects a rainbow bridge into the clouds, but only half of it holds. The Cloud Shepherd says the Star Explorers must stabilize the climb before the route dissolves.",
                "The rainbow bridge stops flickering and the lowest cloud platforms lock into place.",
                "The team reaches the first cloud gate, where the Shepherd's flock scatters in all directions.",
                "Cloud Climb",
                "Reach high like you are climbing the rainbow bridge, then march in place to keep the cloud path steady.",
                "Bridge Count",
                "Count each glowing step as if you are calling the whole team up the bridge one by one.",
                "A storm knot tangles the bridge's final span. The Cloud Shepherd says, 'Untie this, and the Sky Kingdom will let you in.'",
                "Cloudstep Badge",
                "A badge that keeps safe cloud paths solid beneath your feet.",
                "☁️",
                "The first cloud gate opens, and the Shepherd begs for help gathering his scattered cloud-sheep.",
                ["Captain Starlight", "The Cloud Shepherd"],
                "The storm knot bursts and the rainbow bridge settles into a steady path through the clouds.",
            ),
            _level(
                2,
                "Shepherd's Lost Flock",
                "Round up the cloud-sheep using special command words.",
                "Cloud-sheep drift across the kingdom, carrying pieces of the route markers with them. The Cloud Shepherd says only the right words spoken in the right order will bring them home.",
                "The first flock drifts back to the pen and drops a missing route marker.",
                "The whole flock returns, leaving a clear path to the Word Weaver's broken loom hall.",
                "Cloud Herding",
                "Sweep your arms gently like you are guiding cloud-sheep back into a pen. Big sweep, little sweep, clap to close the gate.",
                "Command Voice",
                "Try one calm shepherd voice and one extra-bossy shepherd voice. The cloud-sheep only listen when you sound confident.",
                "A cloud gate forms a final word-lock around the flock pen. The Shepherd calls, 'Say the right commands and bring them home!'",
                "Shepherd's Whistle",
                "A whistle that turns helpful words into moving paths.",
                "🐑",
                "With the flock safe, the Shepherd leads the team to the Word Weaver, whose loom is tearing apart in the wind.",
                ["Captain Starlight", "The Cloud Shepherd", "The Word Weaver"],
                "The cloud-sheep settle in place, and the route markers point straight toward the loom hall.",
            ),
            _level(
                3,
                "Weaver's Loom Repair",
                "Repair the Word Weaver's loom before the storm tears the sky apart.",
                "The Word Weaver's loom is snapping glowing threads as fast as she can mend them. She explains that the sky is losing words, which means bridges, doors, and sunshine spells are all starting to fail.",
                "New threads stretch across the loom, weaving a path of letters through the hall.",
                "The repaired loom forms a half-finished spell cloth showing the team opening a door made of light.",
                "Thread Pull",
                "Pretend to pull shining threads from one side to the other. Long pull, twist, and lock them into place.",
                "Spell Sound Check",
                "The Word Weaver wants to hear what a strong spell sounds like. Say one glowing magic word and then one ridiculous nonsense spell word.",
                "A knot of storm-words locks the loom in place. The Word Weaver says, 'Untangle this, and the sky can start healing.'",
                "Sun-Thread Spool",
                "A spool of enchanted thread strong enough to mend sky-routes and spells.",
                "🧵",
                "The repaired loom reveals that an upside-down storm is opening a door toward the Puzzle Dimension.",
                ["Captain Starlight", "The Word Weaver", "The Cloud Shepherd"],
                "The final storm knot comes loose and the loom throws a ribbon of golden thread high across the hall.",
            ),
            _level(
                4,
                "Upward Storm",
                "Cast the sunshine spell and stop the upside-down rain.",
                "The sky above the kingdom is raining upward. The Word Weaver says the storm is being pulled toward the Puzzle Dimension, and only a full sunshine spell can seal the leak long enough to rescue the trapped messenger.",
                "The first lines of the sunshine spell rise into the clouds and push the upside-down rain back.",
                "The storm opens just enough to reveal a floating door of light and a trapped messenger calling for help beyond it.",
                "Storm Brace",
                "Plant your feet, push the storm back with both hands, then punch one fist into the air like the sunshine spell is landing.",
                "Weather Report",
                "Describe the upside-down storm like a brave weather reporter and then like the silliest cloud in the whole kingdom.",
                "The storm condenses into a final spell knot. Captain Starlight says, 'Break this, and we reach the messenger.'",
                "Stormglass Charm",
                "A charm that steadies magic whenever worlds start to leak into each other.",
                "⛈️",
                "With the storm pushed aside, the floating door of light swings within reach.",
                ["Captain Starlight", "The Word Weaver", "Puzzle Goblin"],
                "The sunshine spell catches, the rain falls the right way again, and the floating door gleams clear and steady.",
            ),
            _level(
                5,
                "Door Of Light",
                "Rescue the trapped messenger and open the route to the Puzzle Dimension.",
                "Beyond the floating door, the trapped messenger reveals the truth: the Puzzle Goblin has not been trying to stop the team. He has been trying to slow the spread of the Puzzle Dimension before it spills into every world at once.",
                "The messenger escapes, and the door of light begins forming a stable frame around the team.",
                "The opened door reveals a backwards world of floating symbols. The Puzzle Goblin finally asks the team to trust him for the next stage.",
                "Rescue Reach",
                "Reach one hand up like you are helping the messenger climb through the door, then pull back with a giant heroic step.",
                "Truth Test",
                "Say one sentence like you believe the Puzzle Goblin and one sentence like you still are not sure. Captain Starlight says both feelings are allowed.",
                "The floating door locks in place with a final rescue puzzle. The messenger points through the light and says, 'Solve this, and you can still stop the Dimension from breaking everything.'",
                "Door Of Light Sigil",
                "A sigil that keeps a door between worlds safely open.",
                "🚪",
                "The route to the Puzzle Dimension stabilizes, and the team enters with the Puzzle Goblin at their side.",
                ["Captain Starlight", "The Cloud Shepherd", "The Word Weaver", "Puzzle Goblin"],
                "The door frame solidifies into a portal, and the rescued messenger bows before the Star Explorers.",
            ),
        ],
    ),
    _world(
        5,
        "The Puzzle Dimension",
        "Mastery and Resolution",
        "The Star Explorers revisit everything they learned, combine every relic, and repair the source of the world's puzzle magic.",
        ["Captain Starlight", "The Mirror Mage", "Puzzle Goblin"],
        {"name": "Twin Star Crowns", "icon": "👑"},
        [
            _level(
                1,
                "Mirror Maze",
                "Navigate the reflected maze and learn the Puzzle Dimension's rules.",
                "Inside the Puzzle Dimension, every path reflects another path and every answer seems to echo twice. The Mirror Mage appears and says the team must learn the rules of the place before they can hope to change it.",
                "One set of mirrors clears, revealing a direct line through the maze.",
                "The team reaches a chamber where older challenges float in the air like glowing memories.",
                "Mirror March",
                "Step left, step right, then copy the same steps backwards like you are escaping a mirror maze.",
                "Reflection Voice",
                "Say one phrase normally and then say it again like your mirror reflection is trying to copy you badly.",
                "The Mirror Mage seals the maze with a final reflection gate. 'If you understand the rules,' she says, 'show me now.'",
                "Mirror Token",
                "A token that reveals the true path when the world tries to trick you.",
                "🪞",
                "Past the maze waits a hall of fractured memories, including one Captain Starlight has not seen in years.",
                ["Captain Starlight", "The Mirror Mage", "Puzzle Goblin"],
                "The mirror gate slides aside, and the Dimension's reflections stop shifting for the first time.",
            ),
            _level(
                2,
                "Fractured Memories",
                "Recover Captain Starlight's lost map memories.",
                "The Mirror Mage reveals that the Puzzle Dimension stole part of Captain Starlight's old map, which is why no one understood the full route until now. The team must rebuild the memory path before the final doors appear.",
                "A missing map line returns, showing how all four earlier worlds connect to the same broken engine.",
                "Captain Starlight remembers the final route to the Puzzle Core and hands the team the missing last marker.",
                "Memory Steps",
                "Take one big step for the forest, one for the caves, one for the island, and one for the sky so the whole adventure lines up again.",
                "Memory Replay",
                "Say your favourite world so far in a proud voice, then say what made it fun in one quick excited sentence.",
                "A shattered map memory rises into a final lock. Captain Starlight steadies herself and says, 'Let's finish restoring this together.'",
                "Memory Shard",
                "A shard that reconnects routes when old clues have been lost.",
                "🧠",
                "The rebuilt map points straight toward the Puzzle Goblin's hidden destination: the cracking Puzzle Core.",
                ["Captain Starlight", "The Mirror Mage", "Puzzle Goblin"],
                "Captain Starlight's missing route flares back into view, and the final path to the core becomes clear.",
            ),
            _level(
                3,
                "Goblin Truth Run",
                "Fight beside the Puzzle Goblin and seal the first reality crack.",
                "The Puzzle Goblin finally tells the whole truth: he used tricks, stolen pieces, and scrambled puzzles because he never had enough power to seal the cracks on his own. Now he asks the team to run beside him instead of after him.",
                "The first reality crack seals, and the worlds stop flickering for a moment.",
                "A second, much larger crack opens at the centre of the Puzzle Core chamber. Every relic the team collected starts glowing at once.",
                "Seal The Crack",
                "Sprint on the spot, stomp once, and throw both hands forward like you are sealing a crack in the air.",
                "Goblin Pep Talk",
                "Give the Puzzle Goblin one brave sentence so he knows the team is with him now.",
                "The reality crack grows into a final run gate. The Puzzle Goblin shouts, 'One last push and we reach the core!'",
                "Goblin Star Key",
                "A key that locks unstable puzzle magic back into its proper place.",
                "⭐",
                "With the first crack sealed, the Puzzle Core wakes and demands a final master solution.",
                ["Captain Starlight", "Puzzle Goblin", "The Mirror Mage"],
                "The crack snaps shut around the Star Key, and the Puzzle Goblin laughs with relief instead of mischief.",
            ),
            _level(
                4,
                "Master Puzzle Engine",
                "Reach the core and solve the engine that twists every world.",
                "At the heart of the Dimension floats the Master Puzzle Engine, built from broken routes, lost words, and stolen map pieces. The Mirror Mage says it can be reset only by a team that understands every world it damaged.",
                "One section of the engine untwists, and the relics begin orbiting in the right order.",
                "The engine's crown socket opens, waiting for one final combined solution from the whole team.",
                "Core Power",
                "Pretend to lift each relic into the air one by one, then lock them together with one giant superhero pose.",
                "Engine Countdown",
                "Count down the final engine reset like a launch sequence. Make 'one' as dramatic as possible.",
                "The Master Puzzle Engine forms the biggest puzzle gate yet. Captain Starlight says, 'Everything you learned leads here.'",
                "Crown Frame",
                "The frame that every earlier relic locks into for the final repair.",
                "👑",
                "The engine opens at the centre and reveals space for the final twin crowns.",
                ["Captain Starlight", "The Mirror Mage", "Puzzle Goblin"],
                "The Master Puzzle Engine slows, and every relic snaps into the waiting Crown Frame.",
            ),
            _level(
                5,
                "Star Explorer Coronation",
                "Use every relic to restore the worlds and earn the Twin Star Crowns.",
                "Forest light, crystal routes, island tides, sky threads, and puzzle keys all gather around the Crown Frame. Captain Starlight says the final repair can only be done by true Star Explorers working together.",
                "The first crown lights up and a wave of repaired magic rushes back through every world.",
                "The second crown shines, and every earlier world appears safe, bright, and connected once more.",
                "Crown Charge",
                "Raise both hands high like you are lifting the final crowns into the sky. Hold them up while you count to 5 together.",
                "Victory Voice",
                "Say 'We are the Star Explorers!' once like a champion and once like the whole universe is cheering back.",
                "The final crown lock appears above the repaired engine. Captain Starlight smiles and says, 'This is the last level. Let's finish the whole adventure.'",
                "Twin Star Crowns",
                "The crowns that mark Jesse and Reuben as true Star Explorers.",
                "👑",
                "The worlds are restored. Captain Starlight promises that a new adventure can begin whenever the team is ready.",
                ["Captain Starlight", "Puzzle Goblin", "The Mirror Mage"],
                "The Twin Star Crowns blaze to life, and every world appears repaired across the night sky.",
            ),
        ],
    ),
]

STORY_ARCS = CAMPAIGN_WORLDS
TOTAL_LEVELS = sum(len(world["levels"]) for world in CAMPAIGN_WORLDS)

THEMED_BEATS = {
    "dinosaurs": [
        "A cosmic dinosaur stomps along the path beside you. Even it can tell the level is almost clear.",
        "Tiny dino footprints appear next to the route markers, like the adventure itself is cheering you on.",
    ],
    "karate": [
        "That progress beat lands like a perfect karate move. Fast, sharp, and right on target.",
        "Captain Starlight grins. 'That was a black-belt answer if I ever saw one.'",
    ],
    "violin": [
        "A bright violin note rings through the scene as the level objective clicks one step closer to complete.",
        "The route ahead hums like a perfectly tuned string section.",
    ],
    "woodworking": [
        "Piece by piece, you're building the level back into shape like expert makers.",
        "Every solved challenge feels like another strong plank locked into place.",
    ],
    "science": [
        "Captain Starlight says this is real explorer science: observe, test, solve, repeat.",
        "The clues start lining up like a brilliant experiment that finally worked.",
    ],
    "space": [
        "The stars above the level flash like checkpoint lights turning green.",
        "Even in the strangest world, the space routes seem to be cheering for your progress.",
    ],
    "parkrun": [
        "This level is turning into a strong finishing run. One steady step at a time.",
        "Captain Starlight calls out, 'Keep your pace. The finish is getting closer.'",
    ],
}

SECRET_MISSIONS = [
    "Side Quest: find three things at home that match today's world and tell Captain Starlight next time.",
    "Side Quest: teach someone one clue or fact you learned on this level.",
    "Side Quest: spot a shape, number, or word in the real world and bring the discovery back to mission control.",
]

THEMED_SECRET_MISSIONS = {
    "woodworking": [
        "Side Quest: build a tiny bridge, tower, or machine from blocks, cardboard, or wood and report back.",
    ],
    "dinosaurs": [
        "Side Quest: invent a space dinosaur and decide which world it would protect.",
    ],
    "violin": [
        "Side Quest: listen for one heroic tune that sounds like a level clear theme.",
    ],
    "karate": [
        "Side Quest: create a three-move explorer kata for the next mission briefing.",
    ],
    "science": [
        "Side Quest: test one small science question at home and tell the team what happened.",
    ],
    "space": [
        "Side Quest: find one space fact that sounds like it belongs in the next world.",
    ],
    "parkrun": [
        "Side Quest: count your fastest ten running or marching steps and compare them next session.",
    ],
}


def get_session_position(session_number: int) -> tuple[int, int]:
    """Get (world_number, level_number) for a session number. Returns 1-indexed values."""
    safe_session = min(max(session_number, 1), TOTAL_LEVELS)
    world = ((safe_session - 1) // 5) + 1
    level = ((safe_session - 1) % 5) + 1
    return world, level


def get_arc(arc_number: int) -> dict:
    """Get a campaign world by number (1-indexed)."""
    idx = (arc_number - 1) % len(CAMPAIGN_WORLDS)
    return CAMPAIGN_WORLDS[idx]


def get_level(session_number: int) -> dict:
    """Get the specific level payload for a session number."""
    world_number, level_number = get_session_position(session_number)
    world = get_arc(world_number)
    level = world["levels"][level_number - 1].copy()
    level["world_number"] = world_number
    level["world_name"] = world["name"]
    level["theme"] = world["theme"]
    level["world_description"] = world["description"]
    level["level_id"] = f"w{world_number}l{level_number}"
    level["world_complete"] = level_number == len(world["levels"])
    if session_number < TOTAL_LEVELS:
        next_world_number, next_level_number = get_session_position(session_number + 1)
        next_world = get_arc(next_world_number)
        next_level = next_world["levels"][next_level_number - 1]
        level["next_level"] = {
            "world_number": next_world_number,
            "world_name": next_world["name"],
            "level_number": next_level_number,
            "level_name": next_level["level_name"],
            "objective": next_level["objective"],
        }
    else:
        level["next_level"] = None
    return level


def _completed_level_ids(team_state) -> set[str]:
    completed = set(team_state.completed_levels or [])
    if not completed and getattr(team_state, "sessions_completed", 0):
        for session in range(1, team_state.sessions_completed + 1):
            world_number, level_number = get_session_position(session)
            completed.add(f"w{world_number}l{level_number}")
    return completed


def get_character_status(session_number: int) -> dict:
    """Return lightweight status summaries for the active cast."""
    statuses = {
        "Captain Starlight": "Guiding the team toward the next repair mission.",
        "Puzzle Goblin": "Causing trouble and hiding the real danger." if session_number < 5 else
        "Watching the team nervously and warning them when the deeper danger gets close." if session_number < 15 else
        "Fighting beside the Star Explorers to seal the Puzzle Dimension.",
    }
    if session_number >= 1:
        statuses["Wise Owl"] = "Teaching the team how repaired magic changes the world." if session_number <= 5 else "Waiting in the forest, proud of the team's first world clear."
    if session_number >= 6:
        statuses["The Crystal Dragon"] = "Guarding the route below and rewarding real progress." if session_number <= 10 else "Ready to carry the team between worlds when needed."
        statuses["Echo Sprite"] = "Turning clues into safe cave routes." if session_number <= 10 else "Still echoing useful clues from the caves."
    if session_number >= 11:
        statuses["The Island Guardian"] = "Protecting the living island and testing brave choices."
        statuses["Professor Parrot"] = "Keeping signals, clues, and jokes flying at the same speed."
    if session_number >= 16:
        statuses["The Cloud Shepherd"] = "Opening cloud paths and keeping the sky safe to cross."
        statuses["The Word Weaver"] = "Repairing broken sky magic one strong thread at a time."
    if session_number >= 21:
        statuses["The Mirror Mage"] = "Revealing the truth behind every earlier world and every broken route."
    return statuses


def build_story_flags(session_number: int) -> dict:
    """Return coarse campaign flags for UI and narrative summaries."""
    return {
        "forest_cleared": session_number > 5,
        "caves_cleared": session_number > 10,
        "island_cleared": session_number > 15,
        "sky_cleared": session_number > 20,
        "puzzle_goblin_warning_known": session_number >= 5,
        "puzzle_goblin_allied": session_number >= 20,
        "finale_unlocked": session_number >= 21,
    }


def build_campaign_snapshot(team_state, session_number: int) -> dict:
    """Return campaign map and current-level metadata for the frontend."""
    level = get_level(session_number)
    completed = _completed_level_ids(team_state)

    world_summaries = []
    for world in CAMPAIGN_WORLDS:
        world_level_ids = {f"w{world['world_number']}l{i}" for i in range(1, 6)}
        unlocked = world["world_number"] <= level["world_number"]
        world_summaries.append(
            {
                "world_number": world["world_number"],
                "name": world["name"],
                "theme": world["theme"],
                "description": world["description"],
                "unlocked": unlocked,
                "completed": world_level_ids.issubset(completed),
                "levels_completed": len(world_level_ids.intersection(completed)),
            }
        )

    map_nodes = []
    for world in CAMPAIGN_WORLDS:
        for node in world["levels"]:
            node_id = f"w{world['world_number']}l{node['level_number']}"
            map_nodes.append(
                {
                    "id": node_id,
                    "world_number": world["world_number"],
                    "world_name": world["name"],
                    "level_number": node["level_number"],
                    "level_name": node["level_name"],
                    "completed": node_id in completed,
                    "current": node_id == level["level_id"],
                    "unlocked": world["world_number"] < level["world_number"]
                    or node_id == level["level_id"]
                    or node_id in completed,
                }
            )

    current_reward = getattr(team_state, "current_reward", {}) or {}
    collected_relics = getattr(team_state, "collected_relics", []) or []

    return {
        "world_number": level["world_number"],
        "world_name": level["world_name"],
        "level_number": level["level_number"],
        "level_name": level["level_name"],
        "level_id": level["level_id"],
        "objective": level["objective"],
        "objective_label": f"World {level['world_number']} · Level {level['level_number']}",
        "characters_in_scene": [
            {
                "name": name,
                "role": CHARACTER_GUIDE.get(name, {}).get("role", ""),
            }
            for name in level["characters_in_scene"]
        ],
        "reward": level["reward"],
        "reward_history": collected_relics,
        "current_reward": current_reward,
        "world_complete": level["world_complete"],
        "next_level": level["next_level"],
        "map_nodes": map_nodes,
        "worlds": world_summaries,
        "story_flags": build_story_flags(session_number),
        "character_status": get_character_status(session_number),
        "progress_copy": (
            f"{len(completed)} of {TOTAL_LEVELS} levels cleared"
            if completed
            else "Your campaign begins with Level 1"
        ),
    }


def generate_recap(team_state, children) -> str:
    """Generate a proper continuous-campaign recap."""
    if team_state.sessions_completed == 0:
        return ""

    last_level = get_level(team_state.sessions_completed)
    lines = [
        "Previously on Star Explorers...",
        f"You cleared Level {last_level['level_number']}: {last_level['level_name']} in {last_level['world_name']}.",
        f"Mission complete: {last_level['objective']}",
    ]

    current_reward = getattr(team_state, "current_reward", {}) or {}
    if current_reward.get("name"):
        lines.append(f"You earned the {current_reward['name']}: {current_reward.get('summary', '')}")
    elif last_level["reward"]["name"]:
        lines.append(f"You earned the {last_level['reward']['name']}.")

    unused_callbacks = [c for c in team_state.callbacks if not c.used]
    for callback in unused_callbacks[-2:]:
        lines.append(f"{callback.child} {callback.event}!")
        callback.used = True

    if team_state.cliffhanger:
        lines.append(team_state.cliffhanger)

    next_session = min(team_state.sessions_completed + 1, TOTAL_LEVELS)
    next_level = get_level(next_session)
    if next_session <= TOTAL_LEVELS and next_session != team_state.sessions_completed:
        lines.append(f"Next mission: {next_level['level_name']} in {next_level['world_name']}.")

    return "\n".join(lines)


def get_story_hook(session_number: int) -> str:
    """Get the main level intro copy for a session."""
    level = get_level(session_number)
    return f"{level['intro']}\n\nOBJECTIVE: {level['objective']}"


def get_cliffhanger(session_number: int) -> str:
    """Get the next-level/world unlock hook for the end of a session."""
    level = get_level(session_number)
    return level["next_hook"]


def get_story_beat(session_number: int, beat_number: int, interests: list = None) -> str:
    """Get a deterministic in-level progress beat."""
    level = get_level(session_number)
    beat = level["progress_beats"][beat_number % len(level["progress_beats"])]

    if interests:
        themed_pool = []
        for interest in interests:
            themed_pool.extend(THEMED_BEATS.get(interest, []))
        if themed_pool:
            extra = themed_pool[(session_number + beat_number) % len(themed_pool)]
            return f"{beat}\n\n{extra}"

    return beat


def get_boss_intro(session_number: int) -> str:
    """Get the level boss introduction."""
    return get_level(session_number)["boss_intro"]


def get_boss_victory(session_number: int) -> str:
    """Get the level boss victory copy."""
    return get_level(session_number)["boss_victory"]


def get_break_payload(session_number: int, break_type: str) -> dict:
    """Return the structured break payload for the current level."""
    level = get_level(session_number)
    if break_type == "movement":
        return level["movement_break"]
    return level["silly_break"]


def get_movement_break(session_number: int, interests: list = None) -> str:
    """Get the in-world movement break text for the level."""
    return get_break_payload(session_number, "movement")["text"]


def get_silly_break(session_number: int, interests: list = None) -> dict:
    """Get the in-world silly break payload for the level."""
    return get_break_payload(session_number, "silly")


def get_secret_mission(session_number: int, interests: list = None) -> str:
    """Get a side quest for between sessions."""
    pool = list(SECRET_MISSIONS)
    if interests:
        for interest in interests:
            pool.extend(THEMED_SECRET_MISSIONS.get(interest, []))
    return pool[(session_number - 1) % len(pool)]


def generate_score_report(team_state, children, session_stats, session_number=None) -> str:
    """Generate a level-complete report instead of a detached score summary."""
    active_session = session_number or max(team_state.sessions_completed + 1, 1)
    level = get_level(active_session)
    lines = [
        f"LEVEL CLEAR: {level['level_name']}",
        f"Objective complete: {level['objective']}",
        f"Reward earned: {level['reward']['name']} — {level['reward']['summary']}",
        f"The team earned {session_stats.get('team_score', 0)} Adventure Points on this level.",
    ]

    total_all = team_state.total_adventure_points
    if total_all:
        lines.append(f"Campaign total: {total_all} Adventure Points.")

    for child_name, stats in session_stats.get("children", {}).items():
        correct = stats.get("correct", 0)
        asked = stats.get("asked", 0)
        if asked > 0:
            lines.append(f"{child_name}: {correct}/{asked} correct on this mission.")
        if stats.get("mastered"):
            for topic in stats["mastered"]:
                lines.append(f"{child_name} mastered {topic}.")
        if stats.get("new_learned"):
            lines.append(f"{child_name} unlocked {stats['new_learned']} new learning steps.")

    if level["next_level"]:
        lines.append(
            f"Next level unlocked: {level['next_level']['level_name']} in {level['next_level']['world_name']}."
        )
    else:
        lines.append("Final campaign level cleared. The worlds are restored.")

    return "\n".join(lines)
