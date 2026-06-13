import sys
import unittest
from collections import deque
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wordworld.core.engine import GameEngine
from wordworld.ui.pygame_ui import (
    TILE_GARDEN,
    TILE_LANDMARK,
    TILE_WALL,
    TILE_WATER,
    _build_tile_map,
    _city_identity,
    _pick_template,
)


BLOCKED_TILES = {TILE_WALL, TILE_WATER, TILE_GARDEN, TILE_LANDMARK}


class CityArtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = GameEngine()
        self.engine.new_game("test")

    def test_major_cities_have_distinct_layouts_and_landmarks(self) -> None:
        city_ids = [
            "map_wutan",
            "map_mo_city",
            "map_salt_city",
            "map_jia_ma_capital",
            "map_canaan",
            "map_black_seal_city",
            "map_tianya_city",
            "map_sacred_dan_city",
        ]
        identities = [_city_identity(map_id) for map_id in city_ids]

        self.assertEqual(len(city_ids), len({identity["layout"] for identity in identities}))
        self.assertEqual(len(city_ids), len({identity["landmark"] for identity in identities}))

    def test_all_safe_map_interactions_are_reachable(self) -> None:
        failures = []
        for map_id, map_data in self.engine.maps.items():
            if not map_data.get("safe_zone", False):
                continue

            width, height, tile_defs, entity_defs = _pick_template(
                map_id, True, map_data.get("name", map_id)
            )
            grid, entities, _ = _build_tile_map(width, height, tile_defs, entity_defs)
            blocked_entities = [
                position
                for position in entities
                if grid[position[1]][position[0]] in BLOCKED_TILES
            ]
            if blocked_entities:
                failures.append((map_id, "blocked", blocked_entities))
                continue

            floors = [
                (x, y)
                for y in range(height)
                for x in range(width)
                if grid[y][x] not in BLOCKED_TILES and (x, y) not in entities
            ]
            self.assertTrue(floors, map_id)
            start = min(
                floors,
                key=lambda position: (
                    abs(position[0] - width // 2) + abs(position[1] - height // 2)
                ),
            )
            seen = {start}
            queue = deque([start])
            while queue:
                x, y = queue.popleft()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and grid[ny][nx] not in BLOCKED_TILES
                        and (nx, ny) not in seen
                    ):
                        seen.add((nx, ny))
                        queue.append((nx, ny))

            unreachable = [position for position in entities if position not in seen]
            if unreachable:
                failures.append((map_id, "unreachable", unreachable))

        self.assertEqual([], failures)

    def test_black_seal_city_never_uses_a_wilderness_template(self) -> None:
        map_data = self.engine.maps["map_black_seal_city"]
        width, height, _, entity_defs = _pick_template(
            "map_black_seal_city", True, map_data["name"]
        )

        self.assertEqual((20, 15), (width, height))
        self.assertTrue(any(entity[2] == 11 for entity in entity_defs))


if __name__ == "__main__":
    unittest.main()
