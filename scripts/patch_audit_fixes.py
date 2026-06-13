"""Fix audit issues: remove stat clamp, redesign EXP, scale skills, fix typos."""

# === 1. Engine: Remove min() clamping from begin_combat ===
with open('src/wordworld/core/engine.py', 'r', encoding='utf-8') as f:
    eng = f.read()

old = '''        # 敌人属性钳制——保证各等级段 TTK 在 3-12 回合
        hp = max(30, min(enemy["hp"], 25 + enemy_level * 12))
        atk_c = max(4, min(enemy["atk"], 5 + enemy_level * 2))
        def_c = max(1, min(enemy["def"], 1 + enemy_level))
        spd_c = max(3, min(enemy["spd"], 4 + enemy_level))
        exp_c = max(8, min(enemy["exp_reward"], 10 + enemy_level * 5))'''

new = '''        # Use Excel raw values, only floor-guard against negatives
        hp = max(30, enemy.get("hp", 30))
        atk_c = max(4, enemy.get("atk", 4))
        def_c = max(1, enemy.get("def", 1))
        spd_c = max(3, enemy.get("spd", 3))
        exp_c = max(8, enemy.get("exp_reward", 8))'''
eng = eng.replace(old, new)

# === 2. Engine: Redesign EXP formula - progressive ===
old = '''    def _exp_for_progress(self, level: int) -> int:
        """按等级动态计算每 1% 修炼进度所需经验。

        优先使用配置表中的 Exp_Formula（如 level*25），
        否则回退到 Progress_Exp 固定值。
        """
        rule = self._progress_rule(level)
        if not rule:
            return 999999
        formula = rule.get("exp_formula", "")
        match = EXP_FORMULA_PATTERN.match(formula)
        if match:
            return level * int(match.group(1))
        return rule.get("progress_exp", 999999)'''

new = '''    def _exp_for_progress(self, level: int) -> int:
        """Progressive quadratic EXP: level * tier_multiplier.
        Scales smoothly from ~10 battles/level (low) to ~60 (high)."""
        if level <= 9:
            mult = 3
        elif level <= 19:
            mult = 7
        elif level <= 29:
            mult = 14
        elif level <= 39:
            mult = 24
        elif level <= 49:
            mult = 38
        elif level <= 59:
            mult = 55
        elif level <= 69:
            mult = 80
        elif level <= 79:
            mult = 110
        elif level <= 89:
            mult = 150
        else:
            mult = 200
        return level * mult'''
eng = eng.replace(old, new)

# === 3. Engine: Scale skill bonus with player ATK ===
old = '''                self.player["douqi"] -= cost
                bonus = self._skill_attack_bonus(skill["effect"])
                multiplier *= 1.25'''

new = '''                self.player["douqi"] -= cost
                bonus = self._skill_attack_bonus(skill["effect"])
                # Scale with player ATK to stay relevant at all levels
                bonus += int(self.effective_atk() * 0.5)
                multiplier *= 1.25'''
eng = eng.replace(old, new)

with open('src/wordworld/core/engine.py', 'w', encoding='utf-8') as f:
    f.write(eng)
print('Engine audit fixes applied.')

# === 4. Fix recipe typo ===
with open('src/wordworld/data/recipe_data.py', 'r', encoding='utf-8') as f:
    rec = f.read()

old_r = 'item_despiration_pill'
new_r = 'item_desperation_pill'
if old_r in rec:
    rec = rec.replace(old_r, new_r)
    with open('src/wordworld/data/recipe_data.py', 'w', encoding='utf-8') as f:
        f.write(rec)
    print(f'Fixed recipe typo: {old_r} -> {new_r}')
else:
    print('Recipe typo not found in file')

# === 5. Fix ITEM_PRICE_TABLE ===
with open('src/wordworld/core/engine.py', 'r', encoding='utf-8') as f:
    eng2 = f.read()
old_p = '"consumable": (10, 30),'
new_p = '"consumable": (10, 15),'
if old_p in eng2:
    eng2 = eng2.replace(old_p, new_p)
    with open('src/wordworld/core/engine.py', 'w', encoding='utf-8') as f:
        f.write(eng2)
    print('Fixed ITEM_PRICE_TABLE consumable ratio')

print('All audit fixes applied.')
