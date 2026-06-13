"""Patch: gathering node pixel art + loot rarity system."""
import re

# === PART 1: Engine.py - Rarity System ===
with open('src/wordworld/core/engine.py', 'r', encoding='utf-8') as f:
    eng = f.read()

# Add rarity constants
old = '    ALL_TIERS = ["iron","refined","spirit","treasure","earth","heaven","mystic","saint","emperor","divine"]'
new = '''    ALL_TIERS = ["iron","refined","spirit","treasure","earth","heaven","mystic","saint","emperor","divine"]

    RARITY_MULTIPLIERS = {
        "common": 1.0, "uncommon": 1.2, "rare": 1.5,
        "epic": 1.8, "legendary": 2.2, "mythic": 3.0,
    }
    RARITY_BY_TYPE = {
        "final_boss": {"mythic": 10, "legendary": 25, "epic": 35, "rare": 20, "uncommon": 10},
        "boss":       {"legendary": 8, "epic": 22, "rare": 30, "uncommon": 30, "common": 10},
        "elite":      {"epic": 5, "rare": 15, "uncommon": 30, "common": 50},
        "mob":        {"rare": 5, "uncommon": 15, "common": 80},
    }

    @staticmethod
    def _roll_rarity(enemy_type: str) -> str:
        dist = GameEngine.RARITY_BY_TYPE.get(enemy_type, {"common": 100})
        r = random.randint(1, 100)
        cum = 0
        for rarity, chance in dist.items():
            cum += chance
            if r <= cum:
                return rarity
        return "common"

    @staticmethod
    def _rarity_stat_multiplier(rarity: str) -> float:
        return GameEngine.RARITY_MULTIPLIERS.get(rarity, 1.0)'''
eng = eng.replace(old, new)

# Add _equipped_rarity_multiplier and modify effective_atk/def/hp
old = '''    def effective_atk(self) -> int:
        base = int(self.player.get("atk", 0)) + self.get_equipped_bonus("atk")
        base += self._technique_stat_bonus("atk")
        base += self._flame_stat_bonus("atk")
        mult = self._technique_stat_multiplier("atk")
        return max(1, int(base * mult))'''
new = '''    def _equipped_rarity_multiplier(self) -> float:
        """Best rarity multiplier from equipped items."""
        best = 1.0
        for slot, item_id in self.player.get("equipped", {}).items():
            if item_id and item_id in EQUIPMENT_DATA:
                rarity = EQUIPMENT_DATA[item_id].get("rarity", "common")
                mult = self._rarity_stat_multiplier(rarity)
                if mult > best:
                    best = mult
        return best

    def effective_atk(self) -> int:
        base = int(self.player.get("atk", 0)) + self.get_equipped_bonus("atk")
        base += self._technique_stat_bonus("atk")
        base += self._flame_stat_bonus("atk")
        rarity_mult = self._equipped_rarity_multiplier()
        mult = self._technique_stat_multiplier("atk")
        return max(1, int(base * mult * rarity_mult))'''
eng = eng.replace(old, new)

old = '''    def effective_def(self) -> int:
        base = int(self.player.get("def", 0)) + self.get_equipped_bonus("def")
        base += self._technique_stat_bonus("def")
        base += self._flame_stat_bonus("def")
        mult = self._technique_stat_multiplier("def")
        return max(0, int(base * mult))'''
new = '''    def effective_def(self) -> int:
        base = int(self.player.get("def", 0)) + self.get_equipped_bonus("def")
        base += self._technique_stat_bonus("def")
        base += self._flame_stat_bonus("def")
        rarity_mult = self._equipped_rarity_multiplier()
        mult = self._technique_stat_multiplier("def")
        return max(0, int(base * mult * rarity_mult))'''
eng = eng.replace(old, new)

old = '''    def effective_max_hp(self) -> int:
        base = int(self.player.get("max_hp", 100))
        base += self.get_equipped_bonus("hp")
        base += self._technique_stat_bonus("hp")
        base += self._flame_stat_bonus("hp")
        mult = self._technique_stat_multiplier("hp")
        return max(1, int(base * mult))'''
new = '''    def effective_max_hp(self) -> int:
        base = int(self.player.get("max_hp", 100))
        base += self.get_equipped_bonus("hp")
        base += self._technique_stat_bonus("hp")
        base += self._flame_stat_bonus("hp")
        rarity_mult = self._equipped_rarity_multiplier()
        mult = self._technique_stat_multiplier("hp")
        return max(1, int(base * mult * rarity_mult))'''
eng = eng.replace(old, new)

# Modify _random_loot signature + add rarity filter
old = '''    def _random_loot(enemy_level: int, count: int = 1, tier_shift: int = 0) -> List[str]:'''
new = '''    def _random_loot(enemy_level: int, count: int = 1, tier_shift: int = 0,
                     enemy_type: str = "mob") -> List[str]:'''
eng = eng.replace(old, new)

old = '''    def _random_beast_loot(self, enemy_level: int, count: int = 1,
                            tier_shift: int = 0) -> List[str]:'''
new = '''    def _random_beast_loot(self, enemy_level: int, count: int = 1,
                            tier_shift: int = 0, enemy_type: str = "mob") -> List[str]:'''
eng = eng.replace(old, new)

# In _random_loot, after tier selection, add rarity filter
old = '''            pool = LOOT_TABLE.get(use_tier, LOOT_TABLE.get(tier, []))
            if not pool:
                continue
            ids = [p[0] for p in pool]'''
new = '''            pool = LOOT_TABLE.get(use_tier, LOOT_TABLE.get(tier, []))
            if not pool:
                continue
            # Rarity filter for equipment
            rolled_rarity = GameEngine._roll_rarity(enemy_type)
            rare_pool = [(pid, w) for pid, w in pool
                         if not pid.startswith("eq_") or
                         EQUIPMENT_DATA.get(pid, {}).get("rarity", "common") == rolled_rarity]
            if not rare_pool:
                rare_pool = pool
            ids = [p[0] for p in rare_pool]'''
eng = eng.replace(old, new)

# Fix _random_loot weight references
old = '''            weights = [p[1] for p in pool]
            total_w = sum(weights)'''
new = '''            weights = [p[1] for p in rare_pool]
            total_w = sum(weights)'''
eng = eng.replace(old, new)

# Pass enemy_type to loot functions
old = '''        if self._is_beast_enemy(enemy_id):
            extra_drops = self._random_beast_loot(enemy_level, count=random.randint(1, 3),
                                                   tier_shift=tier_shift)
        else:
            extra_drops = self._random_loot(enemy_level, count=random.randint(0, 2),
                                            tier_shift=tier_shift)'''
new = '''        if self._is_beast_enemy(enemy_id):
            extra_drops = self._random_beast_loot(enemy_level, count=random.randint(1, 3),
                                                   tier_shift=tier_shift,
                                                   enemy_type=enemy_type)
        else:
            extra_drops = self._random_loot(enemy_level, count=random.randint(0, 2),
                                            tier_shift=tier_shift,
                                            enemy_type=enemy_type)'''
eng = eng.replace(old, new)

with open('src/wordworld/core/engine.py', 'w', encoding='utf-8') as f:
    f.write(eng)
print('Engine rarity system patched.')

# === PART 2: pygame_ui.py - Gathering Art ===
with open('src/wordworld/ui/pygame_ui.py', 'r', encoding='utf-8') as f:
    ui = f.read()

# Add ENTITY_GATHER drawing branch
old = '''        elif etype == ENTITY_TREASURE:
            pygame.draw.rect(self.screen, (111, 58, 31), (sx + 6, sy + 15, 20, 13))
            pygame.draw.rect(self.screen, (178, 99, 41), (sx + 6, sy + 11, 20, 8))
            pygame.draw.rect(self.screen, (246, 191, 62), (cx - 2, sy + 17, 4, 7))
            pygame.draw.line(self.screen, (255, 222, 111), (sx + 8, sy + 12), (sx + 23, sy + 12), 2)'''
new = '''        elif etype == ENTITY_TREASURE:
            pygame.draw.rect(self.screen, (111, 58, 31), (sx + 6, sy + 15, 20, 13))
            pygame.draw.rect(self.screen, (178, 99, 41), (sx + 6, sy + 11, 20, 8))
            pygame.draw.rect(self.screen, (246, 191, 62), (cx - 2, sy + 17, 4, 7))
            pygame.draw.line(self.screen, (255, 222, 111), (sx + 8, sy + 12), (sx + 23, sy + 12), 2)
        elif etype == ENTITY_GATHER:
            self._draw_gather_icon(sx, sy, cx, cy, label)'''
ui = ui.replace(old, new)

# Add _draw_gather_icon before _draw_npc_icon
gather_art = '''
    def _draw_gather_icon(self, sx: int, sy: int, cx: int, cy: int, label: str) -> None:
        """Pixel art for gathering nodes: herb/ore/beast/spirit/core/crystal."""
        tick = pygame.time.get_ticks()
        glow = abs(int((tick / 400 % 2.0 - 1) * 60))
        if "\\u836f\\u6750" in label or "herb" in label.lower():
            pygame.draw.line(self.screen, (60, 160, 40), (cx, sy + 26), (cx, sy + 14), 3)
            pygame.draw.ellipse(self.screen, (40, 200, 50), (cx - 2, sy + 6, 10, 10))
            pygame.draw.ellipse(self.screen, (20, 180, 30), (cx - 10, sy + 12, 8, 6))
            pygame.draw.ellipse(self.screen, (100 + glow, 255, 100 + glow), (cx - 3, sy + 4, 4, 4))
            pygame.draw.circle(self.screen, (200, 255, 120, 180), (cx, sy + 8), 2, 1)
        elif "\\u77ff\\u77f3" in label or "ore" in label.lower():
            dark, mid = (80, 70, 60), (140, 120, 90)
            light = (200 + glow, 180 + glow, 140 + glow)
            pygame.draw.polygon(self.screen, dark, [(cx-6, sy+24), (cx+2, sy+26), (cx+4, sy+18), (cx-4, sy+12)])
            pygame.draw.polygon(self.screen, mid, [(cx-4, sy+12), (cx+4, sy+18), (cx+8, sy+8), (cx-2, sy+6)])
            pygame.draw.polygon(self.screen, light, [(cx-2, sy+6), (cx+8, sy+8), (cx+4, sy+2)])
            pygame.draw.circle(self.screen, (255, 240, 180, 150), (cx + 3, sy + 4), 2)
        elif "\\u517d\\u6750" in label or "beast" in label.lower():
            bone = (230, 220, 190)
            pygame.draw.line(self.screen, bone, (cx - 3, sy + 26), (cx + 4, sy + 10), 4)
            pygame.draw.circle(self.screen, (240, 235, 210), (cx - 4, sy + 24), 3, 2)
            pygame.draw.circle(self.screen, (240, 235, 210), (cx + 5, sy + 10), 3, 2)
            pygame.draw.line(self.screen, (200, 190, 160), (cx - 6, sy + 20), (cx - 2, sy + 26), 3)
        elif "\\u7075\\u8349" in label or "spirit" in label.lower():
            pygame.draw.rect(self.screen, (80, 40, 140), (cx - 1, sy + 12, 3, 14))
            for off in [(3, 4), (-8, 10), (5, 16)]:
                pulsing = (120 + glow, 80 + glow, 220 + glow)
                pygame.draw.ellipse(self.screen, pulsing, (cx + off[0] - 5, sy + off[1] - 4, 10, 8))
            pygame.draw.ellipse(self.screen, (200, 160, 255), (cx - 2, sy + 5, 6, 6))
        elif "\\u9b54\\u6838" in label or "core" in label.lower():
            pygame.draw.circle(self.screen, (60, 20, 80), (cx, sy + 15), 8)
            pygame.draw.circle(self.screen, (140 + glow, 40 + glow, 200 + glow), (cx, sy + 15), 5)
            pygame.draw.circle(self.screen, (220, 180, 255, 100), (cx - 1, sy + 13), 2)
            pygame.draw.circle(self.screen, (255, 255, 255, 80), (cx + 2, sy + 14), 1)
        elif "\\u6676\\u77f3" in label or "crystal" in label.lower():
            for i, (dx, dy, s) in enumerate([(-4, 22, 6), (3, 14, 5), (-2, 8, 4), (5, 20, 3)]):
                hue = (100 + i * 30, 200 + glow, 240 + i * 5)
                pygame.draw.polygon(self.screen, hue, [(cx+dx-s, sy+dy), (cx+dx+s, sy+dy), (cx+dx, sy+dy-s*2)])
            pygame.draw.circle(self.screen, (200, 255, 255, 150), (cx, sy + 12), 2)
        else:
            pygame.draw.rect(self.screen, (100, 160, 80), (sx + 8, sy + 14, 16, 12))
            pygame.draw.ellipse(self.screen, (140, 220, 100), (sx + 6, sy + 6, 20, 12))
            pygame.draw.circle(self.screen, (200, 255, 160, 120), (cx, sy + 10), 3, 1)
'''
ui = ui.replace(
    '    def _draw_npc_icon(self, sx: int, sy: int, npc_id: str) -> None:',
    gather_art + '\n    def _draw_npc_icon(self, sx: int, sy: int, npc_id: str) -> None:'
)

with open('src/wordworld/ui/pygame_ui.py', 'w', encoding='utf-8') as f:
    f.write(ui)
print('pygame_ui.py gathering art patched.')
