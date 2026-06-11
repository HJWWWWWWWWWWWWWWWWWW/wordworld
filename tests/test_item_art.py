import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from wordworld.data.equipment_data import EQUIPMENT_DATA
from wordworld.data.item_data import ITEM_DATA
from wordworld.ui.item_art import visual_signature


class ItemArtTests(unittest.TestCase):
    def test_every_item_and_equipment_has_a_unique_visual_signature(self) -> None:
        item_ids = list(ITEM_DATA) + list(EQUIPMENT_DATA)
        signatures = [visual_signature(item_id) for item_id in item_ids]

        self.assertEqual(len(item_ids), 2538)
        self.assertEqual(len(signatures), len(set(signatures)))


if __name__ == "__main__":
    unittest.main()
