"""Campaign narrative tests using the standard library test runner."""

import unittest

from models import TeamState
from story import build_campaign_snapshot, get_level, get_session_position


class StoryCampaignTests(unittest.TestCase):
    def test_session_position_maps_25_levels(self):
        self.assertEqual(get_session_position(1), (1, 1))
        self.assertEqual(get_session_position(5), (1, 5))
        self.assertEqual(get_session_position(6), (2, 1))
        self.assertEqual(get_session_position(25), (5, 5))

    def test_level_contains_campaign_fields(self):
        level = get_level(14)
        self.assertEqual(level["world_number"], 3)
        self.assertEqual(level["level_number"], 4)
        self.assertTrue(level["objective"])
        self.assertTrue(level["reward"]["name"])
        self.assertIn("characters_in_scene", level)
        self.assertEqual(level["movement_break"]["interaction"], "bridge_repair")

    def test_campaign_snapshot_marks_progress(self):
        team = TeamState(
            sessions_completed=3,
            completed_levels=["w1l1", "w1l2", "w1l3"],
            current_reward={"name": "Wishwood Cog"},
            collected_relics=["Forest Lantern Compass", "Whisper Leaf Map", "Wishwood Cog"],
        )
        snapshot = build_campaign_snapshot(team, 4)
        self.assertEqual(snapshot["world_number"], 1)
        self.assertEqual(snapshot["level_number"], 4)
        current_node = next(node for node in snapshot["map_nodes"] if node["current"])
        self.assertEqual(current_node["id"], "w1l4")
        completed = [node for node in snapshot["map_nodes"] if node["completed"]]
        self.assertEqual(len(completed), 3)


if __name__ == "__main__":
    unittest.main()
