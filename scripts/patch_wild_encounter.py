"""Patch engine.py with wild monster encounter system."""
import re

FILE = 'src/wordworld/core/engine.py'
with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# === Patch 1: Add WILD_COMBAT constants (after GAUGE_MAX) ===
old = "# ── 行动条（CTB） ───────────────────────────────────────────\nGAUGE_MAX = 1000  # 行动条满值，达到后可行动"
new = '''# ── 行动条（CTB） ───────────────────────────────────────────
GAUGE_MAX = 1000  # 行动条满值，达到后可行动

# ── 野外遇敌系统 ─────────────────────────────────────────
WILD_COMBAT_BASE_CHANCE = 0.35
WILD_COMBAT_HUNT_MULT = 2.0
WILD_COMBAT_SCOUT_MULT = 0.5
WILD_COMBAT_GATHER_MULT = 0.15
WILD_COMBAT_ROAM_MULT = 1.0
WILD_ELITE_WEIGHT = 0.15
WILD_MOB_WEIGHT = 0.85
RESPAWN_COOLDOWN_PERIODS = 3
BEAST_NAME_KEYWORDS = [
    "beast", "snake", "wolf", "tiger", "eagle", "spider", "scorpion", "insect",
    "dragon", "phoenix", "bear", "leopard", "fox", "lion", "elephant", "crocodile",
    "turtle", "frog", "monster", "serpent", "hawk", "hound", "ape",
]'''
content = content.replace(old, new)

# === Patch 2: Add defeated_enemies init ===
old = '        player.setdefault("equipped_storage_rings", [])'
new = '        player.setdefault("equipped_storage_rings", [])\n        player.setdefault("defeated_enemies", {})'
content = content.replace(old, new)

# === Patch 3: Add new methods before exploration_actions() ===
old = '    def exploration_actions(self) -> List[Dict[str, Any]]:'
new_methods = '''
    # ── 野外遇敌辅助方法 ─────────────────────────────────────

    def _current_period(self) -> int:
        """Current period index for cooldown tracking."""
        return int(self.player.get("day", 1)) * 4 + int(self.player.get("time_period", 0))

    def _is_story_enemy(self, enemy_id: str) -> bool:
        """Story enemies (boss/final_boss/rival/with win_next) never spawn in wild."""
        enemy = self.enemies.get(enemy_id, {})
        etype = enemy.get("type", "mob")
        if etype in ("boss", "final_boss", "rival"):
            return True
        if enemy.get("win_next") or enemy.get("lose_next"):
            return True
        if not enemy.get("can_kill", True):
            return True
        return False

    def _is_beast_enemy(self, enemy_id: str) -> bool:
        """Beast enemies drop materials only, no currency."""
        enemy = self.enemies.get(enemy_id, {})
        name = enemy.get("name", "")
        eid_lower = enemy_id.lower()
        return any(kw in name.lower() or kw in eid_lower for kw in BEAST_NAME_KEYWORDS)

    def _spawn_wild_enemy(self, map_level: int) -> Optional[Dict[str, Any]]:
        """Select a random wild enemy matching the map level."""
        current = self._current_period()
        candidates = []
        weights = []

        for eid, enemy in self.enemies.items():
            if self._is_story_enemy(eid):
                continue
            etype = enemy.get("type", "mob")
            if etype not in ("mob", "elite"):
                continue
            elv = int(enemy.get("level", 1))
            if abs(elv - map_level) > 5:
                continue
            last_defeat = self.player.get("defeated_enemies", {}).get(eid, -999)
            if current - last_defeat < RESPAWN_COOLDOWN_PERIODS:
                continue
            candidates.append(enemy)
            weights.append(WILD_ELITE_WEIGHT if etype == "elite" else WILD_MOB_WEIGHT)

        if not candidates:
            return None
        total_w = max(1, sum(weights))
        weights = [w / total_w for w in weights]
        return random.choices(candidates, weights=weights, k=1)[0]

    def _random_beast_loot(self, enemy_level: int, count: int = 1) -> List[str]:
        """Beast loot: materials only, no equipment/currency."""
        tier = self._tier_for_level(enemy_level)
        pool = LOOT_TABLE.get(tier, [])
        mat_ids = []
        mat_weights = []
        for pid, weight in pool:
            rule = self.item_rules.get(pid, {})
            itype = rule.get("type", "")
            if itype in ("material", "consumable") and not pid.startswith("eq_"):
                mat_ids.append(pid)
                mat_weights.append(weight)
        if not mat_ids:
            return []
        total_w = max(1, sum(mat_weights))
        results = []
        for _ in range(count):
            r = random.randint(1, total_w)
            cum = 0
            for i, w in enumerate(mat_weights):
                cum += w
                if r <= cum:
                    results.append(mat_ids[i])
                    break
        return results

    # ── 原有方法 ─────────────────────────────────────────────

    def exploration_actions(self) -> List[Dict[str, Any]]:'''
content = content.replace(old, new_methods)

# === Patch 4: Add wild combat branch in explore() ===
old = '''        # choose encounter
        chosen = random.choices(candidates, weights=weights, k=1)[0]
        self.active_encounter = chosen
        return chosen'''
if old not in content:
    # Try with comment variation
    old = '        chosen = random.choices(candidates, weights=weights, k=1)[0]\n        self.active_encounter = chosen\n        return chosen'

new = '''        # choose encounter
        chosen = random.choices(candidates, weights=weights, k=1)[0]
        self.active_encounter = chosen

        # wild encounter roll (independent of narrative encounters)
        if action_id in ("hunt", "roam", "scout"):
            mult_map = {
                "hunt": WILD_COMBAT_HUNT_MULT,
                "roam": WILD_COMBAT_ROAM_MULT,
                "scout": WILD_COMBAT_SCOUT_MULT,
            }
            wild_chance = WILD_COMBAT_BASE_CHANCE * mult_map.get(action_id, 1.0)
            if random.random() < wild_chance:
                map_rule = self.current_map()
                map_lv = int(map_rule.get("recommend_level", 1))
                wild_enemy = self._spawn_wild_enemy(map_lv)
                if wild_enemy:
                    self.begin_combat(wild_enemy["id"])
                    return {"id": "wild_combat",
                            "map_id": map_rule["id"],
                            "text": f"Encountered {wild_enemy['name']}!",
                            "options": [{"text": "Fight", "next": f"combat:{wild_enemy['id']}"}],
                            "weight": 100}

        return chosen'''
content = content.replace(old, new)

# === Patch 5: Modify _finish_combat_win ===
old = '''        # Level-matched loot (0-2 extra items)
        enemy_level = int(combat.get("level", 1))
        extra_drops = self._random_loot(enemy_level, count=random.randint(0, 2))'''
new = '''        # Record defeat for respawn tracking (wild enemies only)
        enemy_id = combat.get("enemy_id", "")
        if enemy_id and not self._is_story_enemy(enemy_id):
            self.player["defeated_enemies"][enemy_id] = self._current_period()

        # Level-matched loot (beast: material only; humanoid: normal)
        enemy_level = int(combat.get("level", 1))
        if self._is_beast_enemy(enemy_id):
            extra_drops = self._random_beast_loot(enemy_level, count=random.randint(1, 3))
        else:
            extra_drops = self._random_loot(enemy_level, count=random.randint(0, 2))'''
content = content.replace(old, new)

# === Patch 6: Skip stamina conditions ===
old = '    def _check_condition_token(self, token: str) -> bool:\n        m = self.COMPARISON_PATTERN.match(token)\n        if not m:\n            return False\n        key = m.group(1)\n        operator = m.group(2)\n        value = m.group(3)'
new = '    def _check_condition_token(self, token: str) -> bool:\n        m = self.COMPARISON_PATTERN.match(token)\n        if not m:\n            return False\n        key = m.group(1)\n        operator = m.group(2)\n        value = m.group(3)\n        # stamina removed, always pass\n        if key == "stamina":\n            return True'
content = content.replace(old, new)

# === Write ===
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print('engine.py patched with wild encounter system.')
