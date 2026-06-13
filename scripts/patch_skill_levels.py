"""Skill level system + dual technique slots + fixed FenJue."""
with open('src/wordworld/core/engine.py', 'r', encoding='utf-8') as f:
    eng = f.read()

# 1. Remove default skills — start with nothing
old = '        player.setdefault("known_skills", ["skill_bajibang", "skill_flame_mantra"])'
new = '        player.setdefault("known_skills", [])  # Learned through story'
eng = eng.replace(old, new)

# 2. Add skill_levels + second_technique + fixed_technique state
old = '        player.setdefault("equipped_storage_rings", [])\n        player.setdefault("defeated_enemies", {})'
new = '''        player.setdefault("equipped_storage_rings", [])
        player.setdefault("defeated_enemies", {})
        player.setdefault("skill_levels", {})
        player.setdefault("second_technique", None)
        player.setdefault("fixed_technique", None)  # FenJue
        player.setdefault("fen_jue_level", 0)'''
eng = eng.replace(old, new)

# 3. Add skill level system before _exp_for_progress
old = '    def _exp_for_progress(self, level: int) -> int:'
new_code = '''
    SKILL_LV_THRESHOLDS = {1: 0, 2: 10, 3: 30, 4: 60, 5: 100}
    SKILL_LV_MULT = {1: 1.0, 2: 1.12, 3: 1.30, 4: 1.50, 5: 1.75}
    SKILL_LV_CRIT = {1: 0, 2: 2, 3: 5, 4: 8, 5: 12}
    SKILL_LV_NAMES = {1: "Beginner", 2: "Skilled", 3: "Expert", 4: "Master", 5: "Grandmaster"}
    FEN_JUE_ID = "tech_火_焚天诀"

    def _record_skill_use(self, skill_id: str) -> None:
        if not skill_id:
            return
        sl = self.player.setdefault("skill_levels", {})
        entry = sl.setdefault(skill_id, {"level": 1, "uses": 0})
        entry["uses"] = entry.get("uses", 0) + 1
        new_lv = entry["level"]
        for lv in [2, 3, 4, 5]:
            if entry["uses"] >= self.SKILL_LV_THRESHOLDS[lv]:
                new_lv = lv
        if new_lv > entry["level"]:
            entry["level"] = new_lv
            skill = self.skills.get(skill_id, {})
            self.last_special = (
                f"Skill [{skill.get('name', skill_id)}] leveled up to "
                f"{self.SKILL_LV_NAMES[new_lv]} (Lv{new_lv})!"
            )

    def _skill_level_bonus(self, skill_id: str) -> tuple:
        if not skill_id:
            return (1.0, 0, 1)
        sl = self.player.get("skill_levels", {})
        entry = sl.get(skill_id, {"level": 1, "uses": 0})
        lv = entry.get("level", 1)
        return (self.SKILL_LV_MULT.get(lv, 1.0),
                self.SKILL_LV_CRIT.get(lv, 0), lv)

    # ── Dual Technique Slots ─────────────────────────────────

    def equip_technique(self, tech_id: str, slot: int = 0) -> bool:
        """slot 0=auto: FenJue→fixed, other→second. slot 1=fixed, 2=second."""
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tech_id), None)
        if tech is None:
            self.last_message = "Technique not found."
            return False
        if tech_id not in self.player.get("known_techniques", []):
            self.player.setdefault("known_techniques", []).append(tech_id)
        if tech_id == self.FEN_JUE_ID:
            self.player["fixed_technique"] = tech_id
            self.player["equipped_technique"] = tech_id
            self.last_message = f"Fixed technique: {tech['name']} ({tech['element']})"
            return True
        old = self.player.get("second_technique")
        self.player["second_technique"] = tech_id
        self.last_message = f"Equipped: {tech['name']} ({tech['element']})"
        if old:
            old_t = next((t for t in TECHNIQUE_DATA if t["id"] == old), {})
            self.last_message += f" (replaced {old_t.get('name', old)})"
        return True

    def unequip_technique(self) -> bool:
        tid = self.player.get("second_technique")
        if not tid:
            self.last_message = "No second technique equipped."
            return False
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), {})
        self.player["second_technique"] = None
        self.last_message = f"Unequipped: {tech.get('name', tid)}"
        return True

    def upgrade_fen_jue(self) -> bool:
        fid = self.player.get("equipped_flame")
        if not fid:
            self.last_message = "Need an equipped flame to upgrade FenJue."
            return False
        if self.player.get("fixed_technique") != self.FEN_JUE_ID:
            self.last_message = "Need FenJue equipped first."
            return False
        flame = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == fid), None)
        if not flame:
            return False
        self.player["equipped_flame"] = None
        fj = self.player.get("fen_jue_level", 0) + 1
        self.player["fen_jue_level"] = min(10, fj)
        self.last_message = (
            f"FenJue absorbed {flame['name']}! Now at layer {self.player['fen_jue_level']}."
        )
        return True

    def _exp_for_progress(self, level: int) -> int:'''
eng = eng.replace(old, new_code)

# 4. Remove old equip_technique/unequip_technique
old_eq = '''    def equip_technique(self, tech_id: str) -> bool:
        """装备功法（提供被动属性加成）。"""
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tech_id), None)
        if tech is None:
            self.last_message = "找不到该功法。"
            return False
        if tech_id not in self.player.get("known_techniques", []):
            self.player.setdefault("known_techniques", []).append(tech_id)
        self.player["equipped_technique"] = tech_id
        self.last_message = f"运起功法：{tech['name']}（{tech['element']}系）"
        return True

    def unequip_technique(self) -> bool:
        tid = self.player.get("equipped_technique")
        if not tid:
            self.last_message = "当前未装备功法。"
            return False
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), {})
        self.player["equipped_technique"] = None
        self.last_message = f"收功：{tech.get('name', tid)}"
        return True'''
if old_eq in eng:
    eng = eng.replace(old_eq, '\n    # Dual-slot equip/unequip defined above\n')
    print('Removed old single-slot methods')

# 5. Apply skill level bonus in combat
old = '''                self.player["douqi"] -= cost
                bonus = self._skill_attack_bonus(skill["effect"])
                # Scale with player ATK to stay relevant at all levels
                bonus += int(self.effective_atk() * 0.5)
                multiplier *= 1.25'''
new = '''                self.player["douqi"] -= cost
                bonus = self._skill_attack_bonus(skill["effect"])
                bonus += int(self.effective_atk() * 0.5)
                # Skill level bonus
                lv_mult, lv_crit, lv = self._skill_level_bonus(skill["id"])
                multiplier *= 1.25 * lv_mult
                crit_rate = int(self.player.get("crit_rate", 5))
                self.player["crit_rate"] = crit_rate + lv_crit
                self._record_skill_use(skill["id"])
                if lv >= 3:
                    logs.append(f"Lv{lv} skill! dmg x{lv_mult:.1f}")'''
eng = eng.replace(old, new)

# 6. Update _technique_stat_bonus for dual slots
old = '''    def _technique_stat_bonus(self, stat: str) -> int:
        """读取已装备功法的绝对值加成。"""
        tid = self.player.get("equipped_technique")
        if not tid:
            return 0
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
        if not tech:
            return 0
        effects = self._parse_technique_effect(tech.get("effect", ""))
        bonus, is_pct = effects.get(stat, (0, False))
        return bonus if not is_pct else 0'''
new = '''    def _technique_stat_bonus(self, stat: str) -> int:
        """Sum bonuses from fixed + second technique."""
        total = 0
        for tid in [self.player.get("fixed_technique"),
                     self.player.get("second_technique")]:
            if not tid:
                continue
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
            if not tech:
                continue
            effects = self._parse_technique_effect(tech.get("effect", ""))
            bonus, is_pct = effects.get(stat, (0, False))
            if not is_pct:
                total += bonus
        return total'''
eng = eng.replace(old, new)

# 7. Update _technique_stat_multiplier for dual slots
old = '''    def _technique_stat_multiplier(self, stat: str) -> float:
        """读取已装备功法的百分比乘数。"""
        tid = self.player.get("equipped_technique")
        if not tid:
            return 1.0
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
        if not tech:
            return 1.0
        effects = self._parse_technique_effect(tech.get("effect", ""))
        bonus, is_pct = effects.get(stat, (0, False))
        return 1.0 + bonus / 100.0 if is_pct else 1.0'''
new = '''    def _technique_stat_multiplier(self, stat: str) -> float:
        """Product of multipliers from both techniques."""
        total = 1.0
        for tid in [self.player.get("fixed_technique"),
                     self.player.get("second_technique")]:
            if not tid:
                continue
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
            if not tech:
                continue
            effects = self._parse_technique_effect(tech.get("effect", ""))
            bonus, is_pct = effects.get(stat, (0, False))
            if is_pct:
                total *= (1.0 + bonus / 100.0)
        return total'''
eng = eng.replace(old, new)

with open('src/wordworld/core/engine.py', 'w', encoding='utf-8') as f:
    f.write(eng)
print('Skill level + dual technique system complete.')
