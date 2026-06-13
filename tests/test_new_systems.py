"""综合测试：源火/功法/纳戒/拍卖行 新系统"""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from wordworld.core.engine import (
    GameEngine, FLAME_TIER_BONUS, FLAME_ALCHEMY_BONUS,
    HEAVENLY_FLAMES_FULL, TECHNIQUE_DATA,
    STORAGE_RINGS, MAX_STORAGE_OVERFLOW,
)


class TestFlameSystem(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_flame_tier_bonus_all_10(self):
        for tier in ["iron","refined","spirit","treasure","earth",
                     "heaven","mystic","saint","emperor","divine"]:
            self.assertIn(tier, FLAME_TIER_BONUS)
            self.assertIn(tier, FLAME_ALCHEMY_BONUS)

    def test_all_23_flames(self):
        self.assertEqual(len(HEAVENLY_FLAMES_FULL), 23)

    def test_equip_flame_needs_item(self):
        self.assertFalse(self.engine.equip_flame("item_flame_1"))

    def test_equip_flame_works(self):
        self.engine.player["items"] = ["item_flame_1"]
        self.assertTrue(self.engine.equip_flame("item_flame_1"))
        self.assertEqual(self.engine.player["equipped_flame"], "item_flame_1")

    def test_unequip_flame_returns(self):
        self.engine.player["items"] = ["item_flame_1"]
        self.engine.equip_flame("item_flame_1")
        self.assertTrue(self.engine.unequip_flame())
        self.assertIn("item_flame_1", self.engine.player["items"])

    def test_flame_collected_tracking(self):
        self.engine.player["items"] = ["item_flame_1"]
        self.engine.equip_flame("item_flame_1")
        self.assertIn("item_flame_1", self.engine.player["collected_flames"])

    def test_flame_atk_bonus(self):
        base = self.engine.player["atk"]
        self.engine.player["items"] = ["item_flame_1"]
        self.engine.equip_flame("item_flame_1")
        bonus = FLAME_TIER_BONUS["divine"]["atk"]
        self.assertEqual(self.engine.effective_atk(), base + bonus)

    def test_flame_alchemy_bonus(self):
        self.engine.player["items"] = ["item_flame_18"]
        self.engine.equip_flame("item_flame_18")
        self.assertEqual(
            self.engine._flame_alchemy_bonus("success"),
            FLAME_ALCHEMY_BONUS["refined"]["success"])


class TestTechniqueSystem(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_parse_effect_dsl(self):
        effects = self.engine._parse_technique_effect("atk:+8,fire_power:+15%")
        self.assertEqual(effects["atk"], (8, False))
        self.assertEqual(effects["fire_power"], (15, True))

    def test_parse_empty_effect(self):
        self.assertEqual(self.engine._parse_technique_effect(""), {})

    def test_no_technique_zero_bonus(self):
        self.assertEqual(self.engine._technique_stat_bonus("atk"), 0)

    def test_equip_technique_adds_known(self):
        tid = TECHNIQUE_DATA[0]["id"]
        self.engine.equip_technique(tid)
        self.assertIn(tid, self.engine.player["known_techniques"])

    def test_unequip_technique(self):
        # Find non-FenJue technique for second slot
        tid = None
        for t in TECHNIQUE_DATA:
            if t["id"] != self.engine.FEN_JUE_ID:
                tid = t["id"]
                break
        if tid is None:
            self.skipTest("No non-FenJue technique available")
        self.engine.equip_technique(tid)
        self.assertEqual(self.engine.player["second_technique"], tid)
        self.engine.unequip_technique()
        self.assertIsNone(self.engine.player["second_technique"])

    def test_effective_spd_exists(self):
        spd = self.engine.effective_spd()
        self.assertGreater(spd, 0)


class TestStorageRing(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_ring_no_item_fails(self):
        self.assertFalse(self.engine.equip_storage_ring("item_storage_ring_1"))

    def test_ring_increases_capacity(self):
        self.engine.player["items"] = ["item_storage_ring_1"]
        old = self.engine.inventory_capacity()
        self.engine.equip_storage_ring("item_storage_ring_1")
        self.assertGreater(self.engine.inventory_capacity(), old)

    def test_ring_removed_from_inv(self):
        self.engine.player["items"] = ["item_storage_ring_1"]
        self.engine.equip_storage_ring("item_storage_ring_1")
        self.assertNotIn("item_storage_ring_1", self.engine.player["items"])

    def test_multi_rings_stack(self):
        self.engine.player["items"] = ["item_storage_ring_1", "item_storage_ring_2"]
        self.engine.equip_storage_ring("item_storage_ring_1")
        self.engine.player["items"].append("item_storage_ring_2")
        self.engine.equip_storage_ring("item_storage_ring_2")
        self.assertEqual(len(self.engine.player.get("equipped_storage_rings", [])), 2)

    def test_overflow_capped(self):
        self.engine.player["storage_overflow"] = ["x"] * 300
        self.engine.player["items"] = ["item_storage_ring_1"]
        self.engine.equip_storage_ring("item_storage_ring_1")
        self.assertLessEqual(
            len(self.engine.player.get("storage_overflow", [])),
            MAX_STORAGE_OVERFLOW)


class TestAuctionSystem(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_refresh_creates_listings(self):
        self.assertIsInstance(self.engine.refresh_auction(), list)

    def test_buy_invalid_fails(self):
        self.assertFalse(self.engine.auction_buy(999))

    def test_sell_valid(self):
        self.engine.player["items"] = ["item_healing_powder"]
        self.assertTrue(self.engine.auction_sell(0, 100))

    def test_npc_cycle_no_crash(self):
        self.engine._npc_auction_cycle()
        self.assertTrue(True)


class TestDataIntegrity(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()

    def test_23_flames_in_items(self):
        for f in HEAVENLY_FLAMES_FULL:
            self.assertIn(f["id"], self.engine.item_rules)

    def test_42_element_pairs(self):
        from wordworld.data.elemental_rules import ELEMENTAL_RULES
        self.assertEqual(len(ELEMENTAL_RULES["cross_element_effects"]), 42)

    def test_technique_tiers_varied(self):
        tiers = {t["tier"] for t in TECHNIQUE_DATA}
        self.assertGreater(len(tiers), 1)

    def test_technique_prices_varied(self):
        prices = {t["price_buy"] for t in TECHNIQUE_DATA}
        self.assertGreater(len(prices), 1)

    def test_engine_methods_present(self):
        for m in ["equip_flame", "unequip_flame", "effective_spd",
                   "_npc_auction_cycle", "_flame_stat_bonus", "_flame_alchemy_bonus",
                   "_parse_technique_effect", "_technique_stat_bonus"]:
            self.assertTrue(hasattr(self.engine, m), f"Missing: {m}")


if __name__ == "__main__":
    unittest.main()
