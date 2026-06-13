"""Patch pygame_ui.py: fixed spawn points + gathering nodes + respawn system."""
import re

FILE = 'src/wordworld/ui/pygame_ui.py'
with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Patch 1: Add ENTITY_GATHER constant
content = content.replace(
    'ENTITY_ENCOUNTER = 18',
    'ENTITY_ENCOUNTER = 18\nENTITY_GATHER = 19'
)

# Patch 2: Add to colors/labels
content = content.replace(
    '    ENTITY_ENCOUNTER: (240, 140, 60),\n}',
    '    ENTITY_ENCOUNTER: (240, 140, 60),\n    ENTITY_GATHER: (100, 220, 100),\n}'
)
content = content.replace(
    '    ENTITY_ENCOUNTER: "!",\n}',
    '    ENTITY_ENCOUNTER: "!",\n    ENTITY_GATHER: "采",\n}'
)

# Patch 3: Add defeated_tiles to __init__
content = content.replace(
    '        self.flame_idx = 0',
    '        self.flame_idx = 0\n        self.defeated_tiles: dict = {}'
)

# Patch 4: Enhance _pick_template for auto-spawn
old_pick = '''    else:
        for keyword, tmpl in _MAP_TEMPLATES.items():
            if keyword in name_lower:
                return tmpl(map_id)
        return _wilderness_forest(map_id)'''
new_pick = '''    else:
        for keyword, tmpl in _MAP_TEMPLATES.items():
            if keyword in name_lower:
                w, h, tiles, entities = tmpl(map_id)
                return _auto_populate_wild(w, h, tiles, entities, name, map_id)
        w, h, tiles, entities = _wilderness_forest(map_id)
        return _auto_populate_wild(w, h, tiles, entities, name, map_id)'''
content = content.replace(old_pick, new_pick)

# Patch 4b: Add _auto_populate_wild function before _build_tile_map
auto_pop_func = '''def _auto_populate_wild(w, h, tiles, entities, name, map_id):
    """Auto-add enemies and gathering nodes to wilderness maps."""
    import random as _rnd
    level_hint = 5
    for kw, lv in [
        ("magic_mountains",5),("inner",15),("deep",25),("black_corner",22),
        ("canaan",20),("tager",30),("dan_region",35),("skyfire",40),
        ("beast_region",45),("dragon_island",55),("soul_mountains",60),
        ("ancient_ruins",65),("heaven_tomb",70),("yao_realm",75),
        ("bodhi_tree",65),("gu_clan",70),("demon_flame",80),
        ("emperor_cave",90),("wilderness",15),("desert",10),("cave",8),
        ("mountain",12),("valley",18),("peak",25),("abyss",35),
        ("tundra",28),("swamp",20),("volcano",30),("ruins",40),("tomb",50),
    ]:
        if kw in map_id.lower() or kw in name.lower():
            level_hint = lv
            break
    existing_enemies = sum(1 for e in entities if e[2] == ENTITY_ENEMY)
    existing_gather = sum(1 for e in entities if e[2] in (ENTITY_TREASURE, ENTITY_GATHER))
    target_enemies = max(3, min(8, level_hint // 8))
    enemies_added = 0
    for _ in range(target_enemies - existing_enemies):
        for __ in range(30):
            x, y = _rnd.randint(1, w-2), _rnd.randint(1, h-3)
            blocked = False
            for e in entities:
                if e[0] == x and e[1] == y:
                    blocked = True
                    break
            if blocked:
                continue
            for t in tiles:
                if t[0] == x and t[1] == y and t[2] in (TILE_WALL, TILE_WATER):
                    blocked = True
                    break
            if not blocked:
                enemy_label = _rnd.choice(["\\u9b54\\u517d","\\u86c7\\u4eba","\\u76d7\\u532a","\\u5996\\u517d","\\u4ea1\\u7075","\\u5b88\\u536b"])
                entities.append((x, y, ENTITY_ENEMY, enemy_label))
                enemies_added += 1
                break
    target_gather = max(2, min(6, level_hint // 12))
    gather_added = 0
    for _ in range(target_gather - existing_gather):
        for __ in range(30):
            x, y = _rnd.randint(1, w-2), _rnd.randint(1, h-3)
            blocked = False
            for e in entities:
                if e[0] == x and e[1] == y:
                    blocked = True
                    break
            if blocked:
                continue
            for t in tiles:
                if t[0] == x and t[1] == y and t[2] in (TILE_WALL, TILE_WATER):
                    blocked = True
                    break
            if not blocked:
                gather_label = _rnd.choice(["\\u836f\\u6750","\\u77ff\\u77f3","\\u517d\\u6750","\\u7075\\u8349","\\u9b54\\u6838","\\u6676\\u77f3"])
                entities.append((x, y, ENTITY_GATHER, gather_label))
                gather_added += 1
                break
    return w, h, tiles, entities

'''
content = content.replace(
    'def _build_tile_map(w, h, tile_defs, entity_defs):',
    auto_pop_func + 'def _build_tile_map(w, h, tile_defs, entity_defs):'
)

# Patch 5: Modify _start_combat_at for respawn
old_combat = '''                self._msg(f"与 {self.engine.combat['name']} 展开了战斗！")
                self.tile_entities.pop((x, y), None)
                self.entity_labels.pop((x, y), None)'''
new_combat = '''                self._msg(f"与 {self.engine.combat['name']} 展开了战斗！")
                # Mark for respawn instead of permanent removal
                self.defeated_tiles[(x, y)] = self.engine._current_period()'''
content = content.replace(old_combat, new_combat)

# Patch 6: Add _open_gather method before _open_treasure
gather_method = '''
    def _open_gather(self, x: int, y: int) -> None:
        """Collect materials from a gathering node."""
        import random as _rnd
        from wordworld.core.engine import GameEngine
        from wordworld.data.loot_table import LOOT_TABLE
        map_lv = self.engine.current_map().get("recommend_level", 1)
        tier = GameEngine._tier_for_level(map_lv)
        pool = LOOT_TABLE.get(tier, [])
        mat_ids, mat_weights = [], []
        for pid, weight in pool:
            rule = self.engine.item_rules.get(pid, {})
            itype = rule.get("type", "")
            if itype in ("material", "consumable") and not pid.startswith("eq_"):
                mat_ids.append(pid)
                mat_weights.append(weight)
        if not mat_ids:
            self._msg("Nothing here...")
            return
        count = _rnd.randint(1, 3)
        total_w = max(1, sum(mat_weights))
        found = []
        for _ in range(count):
            r = _rnd.randint(1, total_w)
            cum = 0
            for i, w in enumerate(mat_weights):
                cum += w
                if r <= cum:
                    lid = mat_ids[i]
                    if lid not in self.engine.player.get("items", []):
                        self.engine.player["items"].append(lid)
                    found.append(self.engine.item_name(lid))
                    break
        if found:
            self._msg("Gathered: " + ", ".join(found))
        self.engine.advance_time(1)
        self.defeated_tiles[(x, y)] = self.engine._current_period()

'''
content = content.replace(
    '    def _open_treasure(self, x: int, y: int) -> None:',
    gather_method + '    def _open_treasure(self, x: int, y: int) -> None:'
)

# Patch 7: Add ENTITY_GATHER trigger
old_trigger = '''    elif etype == ENTITY_ENCOUNTER:
        # not implemented yet
        pass'''
new_trigger = '''    elif etype == ENTITY_GATHER:
        self._open_gather(x, y)
    elif etype == ENTITY_ENCOUNTER:
        pass'''
content = content.replace(old_trigger, new_trigger)

# Patch 8: Skip defeated tiles in _key_explore
old_key = '''            ent = self._entity_at(nx, ny)
            if ent is not None:
                self._trigger_entity(nx, ny, ent)'''
new_key = '''            ent = self._entity_at(nx, ny)
            if ent is not None:
                dp = self.defeated_tiles.get((nx, ny), -999)
                cp = self.engine._current_period()
                if cp - dp >= 6:
                    self._trigger_entity(nx, ny, ent)
                elif ent != ENTITY_EXIT:
                    remaining = 6 - (cp - dp)
                    self._msg(f"This spot will refresh in {remaining} periods")'''
content = content.replace(old_key, new_key)

# Patch 9: Hide defeated tiles in render loop
old_render = '''        for (ex, ey), etype in list(self.tile_entities.items()):
            # Skip defeated tiles on cooldown
            defeat_p = self.defeated_tiles.get((ex, ey), -999)
            if self.engine._current_period() - defeat_p < 6:
                continue
            sx = (ex - cx) * TILE_SIZE + ox
            sy = (ey - cy) * TILE_SIZE + oy
            if 0 <= sx < screen_w - TILE_SIZE and 0 <= sy < screen_h - TILE_SIZE:
                self._draw_entity_icon(screen, sx, sy, etype,
                                       self.entity_labels.get((ex, ey), ""))'''
if old_render in content:
    # Already patched from before, search for original version
    pass

# Find original entity render loop
old_render2 = '''        for (ex, ey), etype in list(self.tile_entities.items()):
            sx = (ex - cx) * TILE_SIZE + ox
            sy = (ey - cy) * TILE_SIZE + oy
            if 0 <= sx < screen_w - TILE_SIZE and 0 <= sy < screen_h - TILE_SIZE:'''
new_render2 = '''        for (ex, ey), etype in list(self.tile_entities.items()):
            # Skip defeated tiles on cooldown
            dp = self.defeated_tiles.get((ex, ey), -999)
            if self.engine._current_period() - dp < 6:
                continue
            sx = (ex - cx) * TILE_SIZE + ox
            sy = (ey - cy) * TILE_SIZE + oy
            if 0 <= sx < screen_w - TILE_SIZE and 0 <= sy < screen_h - TILE_SIZE:'''
content = content.replace(old_render2, new_render2)

# Write
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print('pygame_ui.py patched with map spawn system.')
