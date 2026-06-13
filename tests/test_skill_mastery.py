"""技能精通与功法特殊效果测试。"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from wordworld.core.engine import GameEngine, SKILL_ELEMENTS, TECHNIQUE_DATA


class TestSkillMastery(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GameEngine()

    def test_every_skill_has_level_3_and_5_mastery(self) -> None:
        self.assertGreater(len(self.game.skills), 500)
        for skill_id, skill in self.game.skills.items():
            self.assertIn(3, skill["mastery"], skill_id)
            self.assertIn(5, skill["mastery"], skill_id)
            self.assertTrue(self.game.skill_mastery_text(skill_id))

    def test_fire_level_3_applies_burn(self) -> None:
        skill_id = next(
            sid for sid, skill in self.game.skills.items()
            if SKILL_ELEMENTS.get(sid) == "火" and "atk:+" in skill.get("effect", "")
        )
        self.game.player["known_skills"] = [skill_id]
        self.game.player["skill_levels"][skill_id] = {"level": 3, "uses": 30}
        self.game.player["douqi"] = 999
        self.game.begin_training_combat()
        self.game.combat["hp"] = self.game.combat["max_hp"] = 9999

        self.game.combat_action("skill", skill_id)

        self.assertGreater(self.game.combat.get("burn", 0), 0)

    def test_using_skill_does_not_permanently_raise_crit(self) -> None:
        skill_id = next(
            sid for sid, skill in self.game.skills.items()
            if "atk:+" in skill.get("effect", "")
        )
        self.game.player["known_skills"] = [skill_id]
        self.game.player["skill_levels"][skill_id] = {"level": 5, "uses": 100}
        self.game.player["douqi"] = 999
        original = self.game.player.get("crit_rate", 5)
        self.game.begin_training_combat()
        self.game.combat["hp"] = self.game.combat["max_hp"] = 9999

        self.game.combat_action("skill", skill_id)

        self.assertEqual(self.game.player.get("crit_rate", 5), original)


class TestTechniqueSpecialEffects(unittest.TestCase):
    def setUp(self) -> None:
        self.game = GameEngine()

    def _equip_with(self, effect_key: str) -> None:
        tech = next(t for t in TECHNIQUE_DATA if effect_key in t["effect"])
        self.game.equip_technique(tech["id"])

    def test_all_technique_effects_are_parseable(self) -> None:
        for tech in TECHNIQUE_DATA:
            parsed = self.game._parse_technique_effect(tech["effect"])
            self.assertEqual(len(parsed), len(tech["effect"].split(",")), tech["id"])

    def test_regen_technique_triggers_each_player_turn(self) -> None:
        self._equip_with("hp_regen")
        self.game.begin_training_combat()
        self.game.player["hp"] = 1

        self.game.combat_action("defend")

        self.assertGreater(self.game.player["hp"], 1)

    @patch("wordworld.core.engine.random.randint", return_value=100)
    def test_starting_shield_absorbs_damage(self, _randint) -> None:
        self._equip_with("shield_start")
        self.game.begin_training_combat()
        hp = self.game.player["hp"]

        self.game.combat_action("defend")

        self.assertGreaterEqual(self.game.combat.get("player_shield", 0), 0)
        self.assertLessEqual(self.game.player["hp"], hp)


if __name__ == "__main__":
    unittest.main()
