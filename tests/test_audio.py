import sys
import re
import unittest
from pathlib import Path
from types import SimpleNamespace


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wordworld.ui.pygame_ui import (
    PROGRAMMATIC_AMBIENT_PROFILES,
    PROGRAMMATIC_SOUND_RECIPES,
    PygameGame,
)


class ProgrammaticAudioTests(unittest.TestCase):
    def test_all_gameplay_sound_categories_have_valid_recipes(self) -> None:
        expected = {
            "step", "bump", "select", "confirm", "cancel", "alert", "travel",
            "treasure", "buy", "sell", "rest", "cultivate", "story", "hit",
            "critical", "skill", "defend", "charge", "item", "victory",
            "defeat", "escape", "save", "load", "equip",
        }

        self.assertTrue(expected.issubset(PROGRAMMATIC_SOUND_RECIPES))
        for name, recipe in PROGRAMMATIC_SOUND_RECIPES.items():
            self.assertTrue(recipe, name)
            for frequency, duration, wave_type, volume in recipe:
                self.assertGreater(frequency, 0, name)
                self.assertGreater(duration, 0, name)
                self.assertIn(wave_type, {"square", "sine", "noise"}, name)
                self.assertGreater(volume, 0, name)

    def test_all_required_ambient_profiles_exist(self) -> None:
        self.assertEqual(
            {"city", "wild", "danger", "battle"},
            set(PROGRAMMATIC_AMBIENT_PROFILES),
        )

    def test_every_literal_sound_trigger_has_a_recipe(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "wordworld"
            / "ui"
            / "pygame_ui.py"
        ).read_text(encoding="utf-8")
        triggered = set(re.findall(r'_play_sound\("([a-z_]+)"\)', source))

        self.assertTrue(triggered.issubset(PROGRAMMATIC_SOUND_RECIPES))

    def test_combat_results_route_to_distinct_sounds(self) -> None:
        game = object.__new__(PygameGame)
        game.engine = SimpleNamespace(last_message="")
        played = []
        game._play_sound = played.append

        game._play_combat_result("won", "attack")
        game._play_combat_result("lost", "attack")
        game._play_combat_result("continue", "skill")
        game._play_combat_result("continue", "item")
        game.engine.last_message = "触发暴击"
        game._play_combat_result("continue", "attack")

        self.assertEqual(
            ["victory", "defeat", "skill", "item", "critical"],
            played,
        )


if __name__ == "__main__":
    unittest.main()
