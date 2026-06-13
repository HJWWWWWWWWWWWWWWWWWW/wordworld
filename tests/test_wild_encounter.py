"""Wild encounter system tests."""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from wordworld.core.engine import (
    GameEngine, WILD_COMBAT_BASE_CHANCE, RESPAWN_COOLDOWN_PERIODS,
)


class TestWildEncounter(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_constants_defined(self):
        self.assertGreater(WILD_COMBAT_BASE_CHANCE, 0)

    def test_current_period(self):
        self.assertIsInstance(self.engine._current_period(), int)

    def test_story_enemy_detection(self):
        self.assertTrue(self.engine._is_story_enemy("boss_hun_tiandi"))
        self.assertTrue(self.engine._is_story_enemy("enemy_nalan"))
        self.assertFalse(self.engine._is_story_enemy("mob_alley_thief"))

    def test_beast_enemy_detection(self):
        self.assertTrue(self.engine._is_beast_enemy("mob_ancient_beast_skeleton"))
        self.assertFalse(self.engine._is_beast_enemy("mob_alley_thief"))

    def test_spawn_wild_enemy_level_match(self):
        enemy = self.engine._spawn_wild_enemy(5)
        if enemy:
            elv = int(enemy.get("level", 1))
            self.assertTrue(abs(elv - 5) <= 5)
            self.assertIn(enemy.get("type"), ("mob", "elite"))

    def test_spawn_respects_cooldown(self):
        enemy = self.engine._spawn_wild_enemy(5)
        if enemy:
            self.engine.player["defeated_enemies"][enemy["id"]] = self.engine._current_period()
            enemy2 = self.engine._spawn_wild_enemy(5)
            if enemy2:
                self.assertNotEqual(enemy2["id"], enemy["id"])

    def test_spawn_excludes_story_bosses(self):
        for _ in range(20):
            enemy = self.engine._spawn_wild_enemy(50)
            if enemy:
                self.assertNotIn(enemy.get("type"), ("boss", "final_boss", "rival"))

    def test_random_beast_loot_no_currency(self):
        loot = self.engine._random_beast_loot(10, count=5)
        for lid in loot:
            rule = self.engine.item_rules.get(lid, {})
            self.assertIn(rule.get("type", ""), ("material", "consumable"))

    def test_stamina_condition_bypass(self):
        self.assertTrue(self.engine.check_conditions("stamina>=10"))

    def test_defeated_enemies_initialized(self):
        self.assertIsInstance(self.engine.player.get("defeated_enemies"), dict)

    def test_new_methods_exist(self):
        for m in ["_is_story_enemy", "_is_beast_enemy", "_current_period",
                   "_spawn_wild_enemy", "_random_beast_loot"]:
            self.assertTrue(hasattr(self.engine, m), f"Missing: {m}")


class TestExploreIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_explore_no_crash(self):
        self.engine.player["last_map"] = "map_magic_mountains"
        self.engine.player["adventure_points"] = 100
        result = self.engine.explore("hunt")
        self.assertTrue(result is None or isinstance(result, dict))

    def test_explore_wutan_safezone(self):
        self.engine.player["last_map"] = "map_wutan"
        result = self.engine.explore("roam")
        self.assertTrue(result is None or isinstance(result, dict))


if __name__ == "__main__":
    unittest.main()
