"""跨系统审计中发现的资源安全回归测试。"""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from wordworld.core.engine import (
    ALCHEMY_RECIPES,
    FURNACE_DATA,
    GameEngine,
    LOOT_TABLE,
    REMOVED_ITEM_IDS,
    TECHNIQUE_DATA,
)


class TestInventorySafety(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GameEngine()

    def test_use_furnace_equips_without_losing_it(self) -> None:
        furnace_id = FURNACE_DATA[0]["id"]
        self.game.player["items"] = [furnace_id]

        self.assertTrue(self.game.use_item(furnace_id))
        self.assertEqual(self.game.player["equipped_furnace"], furnace_id)

    def test_use_flame_equips_without_losing_it(self) -> None:
        flame_id = "item_flame_1"
        self.game.player["items"] = [flame_id]

        self.assertTrue(self.game.use_item(flame_id))
        self.assertEqual(self.game.player["equipped_flame"], flame_id)

    def test_use_storage_ring_routes_to_ring_system(self) -> None:
        ring_id = "item_storage_ring_1"
        self.game.player["items"] = [ring_id]
        old_capacity = self.game.inventory_capacity()

        self.assertTrue(self.game.use_item(ring_id))
        self.assertGreater(self.game.inventory_capacity(), old_capacity)

    def test_unsupported_item_is_not_consumed(self) -> None:
        item_id = "item_skill_reset_scroll"
        self.game.player["items"] = [item_id]

        self.assertFalse(self.game.use_item(item_id))
        self.assertIn(item_id, self.game.player["items"])

    def test_regen_item_creates_timed_status(self) -> None:
        item_id = "item_hp_regen_pill"
        self.game.player["items"] = [item_id]

        self.assertTrue(self.game.use_item(item_id))
        self.assertEqual(self.game.timed_status_value("hp_regen"), 20)
        self.assertNotIn(item_id, self.game.player["items"])

    def test_return_scroll_teleports_without_crashing(self) -> None:
        item_id = "item_return_scroll_1"
        self.game.player["items"] = [item_id]

        self.assertTrue(self.game.use_item(item_id))
        self.assertEqual(self.game.player["last_map"], "map_wutan")
        self.assertNotIn(item_id, self.game.player["items"])

    def test_legacy_inventory_counts_are_preserved(self) -> None:
        player = {"inventory": {"item_healing_powder": 3}}

        self.game._ensure_player_state(player)

        self.assertEqual(player["items"].count("item_healing_powder"), 3)


class TestAuctionSafety(unittest.TestCase):
    def test_full_inventory_does_not_charge_buyer(self) -> None:
        game = GameEngine()
        game.player["items"] = ["full"] * game.inventory_capacity()
        game.player["wallet"]["copper"] = 1000
        game.auction_listings = [{
            "id": "item_healing_powder",
            "name": "凝血散",
            "type": "consumable",
            "price": 100,
            "time_left": 10,
            "currency": "copper",
        }]
        game.auction_last_map = game.player["last_map"]
        game.auction_last_period = game.player["day"] * 4 + game.player["time_period"]

        self.assertFalse(game.auction_buy(0))
        self.assertEqual(game.player["wallet"]["copper"], 1000)

    def test_reading_auction_does_not_advance_countdown(self) -> None:
        game = GameEngine()
        game.auction_listings = [{
            "id": "item_healing_powder",
            "name": "凝血散",
            "type": "consumable",
            "price": 100,
            "time_left": 5,
            "currency": "copper",
        }]
        game.auction_last_map = game.player["last_map"]
        game.auction_last_period = game.player["day"] * 4 + game.player["time_period"]

        game.get_auction_listings()
        game.get_auction_listings()

        self.assertEqual(game.auction_listings[0]["time_left"], 5)

    def test_advancing_time_updates_auction_countdown(self) -> None:
        game = GameEngine()
        game.auction_listings = [{
            "id": "item_healing_powder",
            "name": "凝血散",
            "type": "consumable",
            "price": 100,
            "time_left": 5,
            "currency": "copper",
        }]

        game.advance_time(2)

        self.assertEqual(game.auction_listings[0]["time_left"], 3)


class TestTechniqueAudit(unittest.TestCase):
    def test_douqi_max_technique_changes_effective_cap(self) -> None:
        game = GameEngine()
        tech = next(t for t in TECHNIQUE_DATA if "douqi_max" in t["effect"])
        base = game.effective_max_douqi()

        game.equip_technique(tech["id"])

        self.assertGreater(game.effective_max_douqi(), base)

    def test_element_resistance_is_counted(self) -> None:
        game = GameEngine()
        tech = next(t for t in TECHNIQUE_DATA if "fire_resist" in t["effect"])

        game.equip_technique(tech["id"])

        self.assertGreater(game._technique_damage_resistance("火"), 0)


class TestDataReferenceAudit(unittest.TestCase):
    def test_all_enemy_skill_references_exist(self) -> None:
        game = GameEngine()
        missing = [
            (enemy_id, skill_id)
            for enemy_id, enemy in game.enemies.items()
            for skill_id in enemy.get("skills", [])
            if skill_id not in game.skills
        ]

        self.assertEqual(missing, [])

    def test_removed_special_items_are_absent_everywhere(self) -> None:
        game = GameEngine()
        self.assertTrue(REMOVED_ITEM_IDS.isdisjoint(game.item_rules))
        self.assertTrue(all(
            recipe["output"] not in REMOVED_ITEM_IDS for recipe in ALCHEMY_RECIPES
        ))
        self.assertTrue(all(
            item_id not in REMOVED_ITEM_IDS
            for entries in LOOT_TABLE.values()
            for item_id, _weight in entries
        ))


class TestTimedStatusAndCombatItems(unittest.TestCase):
    def test_regen_ticks_during_combat(self) -> None:
        game = GameEngine()
        game.player["items"] = ["item_hp_regen_pill"]
        game.use_item("item_hp_regen_pill")
        game.begin_training_combat()
        game.player["hp"] = 1

        game.combat_action("defend")

        self.assertGreater(game.player["hp"], 1)

    def test_poison_item_is_available_and_applies_poison(self) -> None:
        game = GameEngine()
        item_id = "item_poison_1"
        game.player["items"] = [item_id]
        game.begin_training_combat()

        self.assertIn(item_id, game.combat_usable_items())
        game.combat_action("item", item_id)

        self.assertGreater(game.combat.get("poison", 0), 0)
        self.assertNotIn(item_id, game.player["items"])


class TestGiftSelection(unittest.TestCase):
    def test_gift_requires_target_and_changes_relation(self) -> None:
        game = GameEngine()
        item_id = "item_gift_flower"
        game.player["items"] = [item_id]
        target = next(
            row["id"]
            for row in game.gift_targets()
            if game.relation_value(row["id"]) < 100
        )
        before = game.relation_value(target)

        self.assertFalse(game.use_item(item_id))
        self.assertIn(item_id, game.player["items"])
        self.assertTrue(game.use_item(item_id, target))
        self.assertGreater(game.relation_value(target), before)


if __name__ == "__main__":
    unittest.main()
