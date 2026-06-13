"""Patch pygame_ui.py with new scenes: alchemy, auction, technique, flame,
ring/inventory enhancement, CTB gauge, menu integration."""
import re

FILE = 'src/wordworld/ui/pygame_ui.py'
with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# ── Patch 1: Scene constants ──
old = 'SCENE_ITEM_SELECT = "item_select"'
new = '''SCENE_ITEM_SELECT = "item_select"
SCENE_ALCHEMY = "alchemy"
SCENE_AUCTION = "auction"
SCENE_TECHNIQUE = "technique"
SCENE_FLAME = "flame"'''
content = content.replace(old, new)

# ── Patch 2: Init state variables ──
old = 'self.dialogue_idx = 0'
new = '''self.dialogue_idx = 0
        self.alchemy_idx = 0
        self.auction_idx = 0
        self.technique_idx = 0
        self.flame_idx = 0'''
content = content.replace(old, new)

# ── Patch 3: _on_key dispatch ──
old = '''    elif self.scene == SCENE_ITEM_SELECT and self.combat_ui:
        self.combat_ui.handle_key(e, self.engine)'''
new = '''    elif self.scene == SCENE_ITEM_SELECT and self.combat_ui:
        self.combat_ui.handle_key(e, self.engine)
    elif self.scene == SCENE_ALCHEMY:
        self._key_alchemy(e)
    elif self.scene == SCENE_AUCTION:
        self._key_auction(e)
    elif self.scene == SCENE_TECHNIQUE:
        self._key_technique(e)
    elif self.scene == SCENE_FLAME:
        self._key_flame(e)'''
content = content.replace(old, new)

# ── Patch 4: _render dispatch ──
old = '''    elif self.scene == SCENE_TRAVEL:
        self._render_travel()
    else:
        self._render_explore()'''
new = '''    elif self.scene == SCENE_TRAVEL:
        self._render_travel()
    elif self.scene == SCENE_ALCHEMY:
        self._render_alchemy()
    elif self.scene == SCENE_AUCTION:
        self._render_auction()
    elif self.scene == SCENE_TECHNIQUE:
        self._render_technique()
    elif self.scene == SCENE_FLAME:
        self._render_flame()
    else:
        self._render_explore()'''
content = content.replace(old, new)

# ── Patch 5: Menu items in _key_menu ──
old = '''items = ["返回游戏", "状态详情", "物品背包", "技能列表", "保存游戏", "读取存档", "退出游戏"]
        if e.key == pygame.K_ESCAPE or e.key == pygame.K_m:'''
new_items_key = '''items = ["返回游戏", "状态详情", "物品背包", "技能列表",
                  "炼药炼丹", "拍卖行", "功法切换", "异火大全",
                  "保存游戏", "读取存档", "退出游戏"]
        if e.key == pygame.K_ESCAPE or e.key == pygame.K_m:'''
content = content.replace(old, new_items_key)

# ── Patch 5b: Menu action dispatch in _key_menu ──
old = '''            if idx == 0:
                self.scene = SCENE_EXPLORE
                self._play_sound("cancel")
            elif idx == 1:
                self.menu_state = "status"'''
new = '''            if idx == 0:
                self.scene = SCENE_EXPLORE
                self._play_sound("cancel")
            elif idx == 1:
                self.menu_state = "status"
            elif idx == 4:
                self.scene = SCENE_ALCHEMY
                self._play_sound("confirm")
            elif idx == 5:
                self._update_auction_listings()
                self.scene = SCENE_AUCTION
                self._play_sound("confirm")
            elif idx == 6:
                self.scene = SCENE_TECHNIQUE
                self._play_sound("confirm")
            elif idx == 7:
                self.scene = SCENE_FLAME
                self._play_sound("confirm")'''
first_menu_dispatch = content.find(old)
if first_menu_dispatch != -1:
    content = content[:first_menu_dispatch] + new + content[first_menu_dispatch + len(old):]

# ── Patch 6: Menu items in _render_menu ──
old = '''items = ["返回游戏", "状态详情", "物品背包", "技能列表", "保存游戏", "读取存档", "退出游戏"]
        y = h // 2 - len(items) * 18'''
new_items_render = '''items = ["返回游戏", "状态详情", "物品背包", "技能列表",
                  "炼药炼丹", "拍卖行", "功法切换", "异火大全",
                  "保存游戏", "读取存档", "退出游戏"]
        y = h // 2 - len(items) * 18'''
content = content.replace(old, new_items_render)

# ── Patch 7: Add new scene methods (before _render_menu function) ──
new_scenes_code = '''
    # ── 炼药界面 ─────────────────────────────────────────────

    def _key_alchemy(self, e: pygame.event.Event) -> None:
        recipes = self.engine.available_recipes()
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.alchemy_idx = max(0, self.alchemy_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.alchemy_idx = min(max(0, len(recipes) - 1), self.alchemy_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if recipes and self.alchemy_idx < len(recipes):
                rid = recipes[self.alchemy_idx]["id"]
                self.engine.craft_pill(rid)
                self._play_sound("confirm")
        elif e.key == pygame.K_r:
            inv = self.engine.player.get("items", [])
            pills = [i for i in inv if self.engine.item_rules.get(i, {}).get("type") == "consumable"]
            if pills and self.select_idx < len(pills):
                self.engine.reverse_engineer(pills[self.select_idx])
                self._play_sound("confirm")
        elif e.key == pygame.K_d:
            self.engine.study_alchemy()
            self._play_sound("confirm")

    def _render_alchemy(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        fdata = self.engine._get_furnace_data()
        grade = self.engine.alchemy_grade_name()
        progress = self.engine.alchemy_progress_text()
        header = f"炼药术: {grade} [{progress}]  |  药鼎: {fdata.get('name', '无')} (加成+{fdata['bonus']}%)"
        t = self.font_small.render(header, True, (160, 160, 180))
        self.screen.blit(t, (20, 10))
        hint = self.font_small.render("[Up/Down]选择丹方 [Space]炼制 [R]逆向研究 [D]研读 [Esc]返回", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 180, 36))
        recipes = self.engine.available_recipes()
        y_pos = 70
        for i, r in enumerate(recipes):
            icon = "> " if i == self.alchemy_idx else "  "
            color = C_ACCENT if i == self.alchemy_idx else C_TEXT
            line = f"{icon}{r['name']} -> {r['output']} ({r['grade']}p, rate {r['rate']}%)"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 24
            if i == self.alchemy_idx and r.get("materials"):
                mats = ", ".join(r["materials"])
                mt = self.font_small.render(f"    Materials: {mats}", True, (140, 140, 160))
                self.screen.blit(mt, (20, y_pos))
                y_pos += 20
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))

    # ── 拍卖行界面 ───────────────────────────────────────────

    def _update_auction_listings(self) -> None:
        self.engine.get_auction_listings()
        self.auction_listings = self.engine.auction_listings
        self.auction_idx = 0

    def _key_auction(self, e: pygame.event.Event) -> None:
        listings = self.engine.auction_listings
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.auction_idx = max(0, self.auction_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.auction_idx = min(max(0, len(listings) - 1), self.auction_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if listings and self.auction_idx < len(listings):
                self.engine.auction_buy(self.auction_idx)
                self._play_sound("confirm")
                self._update_auction_listings()
        elif e.key == pygame.K_s:
            inv = self.engine.player.get("items", [])
            if inv and self.select_idx < len(inv):
                item_id = inv[self.select_idx]
                price = self.engine.item_rules.get(item_id, {}).get("price_sell", 100)
                self.engine.auction_sell(self.select_idx, max(1, price))
                self._play_sound("confirm")
                self._update_auction_listings()

    def _render_auction(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        wallet = self.engine.wallet_display(self.engine.player.get("wallet", {}))
        t = self.font_title.render(f"Auction  |  Funds: {wallet}", True, C_ACCENT)
        self.screen.blit(t, (20, 10))
        hint = self.font_small.render("[Up/Down]Select [Space]Buy [S]Sell selected [Esc]Back", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 170, 44))
        listings = self.engine.auction_listings
        y_pos = 70
        for i, item in enumerate(listings):
            icon = "> " if i == self.auction_idx else "  "
            color = C_ACCENT if i == self.auction_idx else C_TEXT
            cur = "Ancient" if item.get("currency") == "ancient" else "Copper"
            sold = " [Yours]" if item.get("player_sold") else ""
            left = item.get("time_left", 0)
            line = f"{icon}{item['name']} - {item['price']}{cur} ({left} periods left){sold}"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 26
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))

    # ── 功法界面 ─────────────────────────────────────────────

    def _key_technique(self, e: pygame.event.Event) -> None:
        known = self.engine.player.get("known_techniques", [])
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.technique_idx = max(0, self.technique_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.technique_idx = min(max(0, len(known) - 1), self.technique_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if known and self.technique_idx < len(known):
                tid = known[self.technique_idx]
                if self.engine.player.get("equipped_technique") == tid:
                    self.engine.unequip_technique()
                else:
                    self.engine.equip_technique(tid)
                self._play_sound("confirm")
        elif e.key == pygame.K_u:
            self.engine.unequip_technique()
            self._play_sound("confirm")

    def _render_technique(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        t = self.font_title.render("Techniques", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 10))
        current = self.engine.player.get("equipped_technique")
        cur_name = "None"
        if current:
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == current), None)
            cur_name = f"{tech['name']} ({tech['element']} tier:{tech['tier']})" if tech else current
        ct = self.font_small.render(f"Active: {cur_name}", True, (160, 200, 160))
        self.screen.blit(ct, (20, 36))
        hint = self.font_small.render("[Up/Down]Select [Space]Equip/Switch [U]Unequip [Esc]Back", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 160, 62))
        known = self.engine.player.get("known_techniques", [])
        y_pos = 90
        for i, tid in enumerate(known):
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
            if not tech:
                continue
            icon = "> " if i == self.technique_idx else "  "
            equipped = " [ACTIVE]" if tid == current else ""
            color = C_ACCENT if i == self.technique_idx else C_TEXT
            line = f"{icon}{tech['name']} ({tech['element']} {tech['tier']}){equipped}"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 22
            if i == self.technique_idx:
                eff = self.font_small.render(f"    Effect: {tech.get('effect', 'none')}  |  {tech.get('desc', '')}", True, (140, 140, 160))
                self.screen.blit(eff, (20, y_pos))
                y_pos += 20
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))

    # ── 异火界面 ─────────────────────────────────────────────

    def _key_flame(self, e: pygame.event.Event) -> None:
        collected = self.engine.player.get("collected_flames", [])
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.flame_idx = max(0, self.flame_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.flame_idx = min(len(HEAVENLY_FLAMES_FULL) - 1, self.flame_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.flame_idx < len(HEAVENLY_FLAMES_FULL):
                fid = HEAVENLY_FLAMES_FULL[self.flame_idx]["id"]
                if fid in self.engine.player.get("items", []):
                    self.engine.equip_flame(fid)
                elif self.engine.player.get("equipped_flame") == fid:
                    self.engine.unequip_flame()
                self._play_sound("confirm")
        elif e.key == pygame.K_u:
            self.engine.unequip_flame()
            self._play_sound("confirm")

    def _render_flame(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        collected = self.engine.player.get("collected_flames", [])
        current = self.engine.player.get("equipped_flame")
        t = self.font_title.render(f"Flames [{len(collected)}/23]", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 10))
        cur_name = "None"
        if current:
            f = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == current), None)
            cur_name = f"{f['name']} ({f['tier']})" if f else current
        ct = self.font_small.render(f"Active: {cur_name}", True, (160, 200, 160))
        self.screen.blit(ct, (20, 36))
        hint = self.font_small.render("[Up/Down]Select [Space]Equip/Store [U]Unequip [Esc]Back", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 160, 62))
        y_pos = 90
        for i, flame in enumerate(HEAVENLY_FLAMES_FULL):
            fid = flame["id"]
            owned = fid in collected or fid in self.engine.player.get("items", [])
            equipped = fid == current
            icon = "> " if i == self.flame_idx else "  "
            status = " [ACTIVE]" if equipped else (" [OWNED]" if owned else " [LOST]")
            color = C_ACCENT if i == self.flame_idx else (C_TEXT if owned else (100, 100, 110))
            line = f"{icon}#{flame['rank']} {flame['name']} ({flame['tier']}){status}"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 22
            if i == self.flame_idx:
                bonus = FLAME_TIER_BONUS.get(flame['tier'], {})
                abonus = FLAME_ALCHEMY_BONUS.get(flame['tier'], {})
                detail = f"    Combat: ATK+{bonus.get('atk',0)} SPD+{bonus.get('spd',0)} Fire+{bonus.get('fire_power',0)}  |  Alchemy: Success+{abonus.get('success',0)}% EXP+{abonus.get('exp',0)}"
                eff = self.font_small.render(detail, True, (140, 140, 160))
                self.screen.blit(eff, (20, y_pos))
                y_pos += 20
                desc = self.font_small.render(f"    {flame.get('desc', '')}", True, (120, 120, 140))
                self.screen.blit(desc, (20, y_pos))
                y_pos += 20
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))
'''

# Insert the new scene methods before the _render_menu function
old = '    def _render_menu(self) -> None:'
content = content.replace(old, new_scenes_code + '\n' + old)

# ── Patch 8: Enhance inventory for ring + skill_book ──
old = '''            else:
                rule = self.engine.item_rules.get(item_id, {})
                use_effect = rule.get("use_effect", "")
                if use_effect:
                    self.engine.use_item(item_id)
                    self._play_sound("confirm")'''
new = '''            else:
                rule = self.engine.item_rules.get(item_id, {})
                itype = rule.get("type", "")
                # storage ring
                if itype == "storage_ring":
                    self.engine.equip_storage_ring(item_id)
                    self._play_sound("confirm")
                # heavenly flame
                elif itype == "heavenly_flame":
                    self.engine.use_item(item_id)
                    self._play_sound("confirm")
                # furnace
                elif itype == "furnace":
                    self.engine.use_item(item_id)
                    self._play_sound("confirm")
                else:
                    use_effect = rule.get("use_effect", "")
                    if use_effect:
                        self.engine.use_item(item_id)
                        self._play_sound("confirm")'''
content = content.replace(old, new)

# ── Patch 9: Display inventory capacity in _render_inventory ──
old = '''        t = self.font_title.render("Inventory", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 10))
        # operation hint
        self.screen.blit(
            self.font_small.render("[Up/Down]Select [Space]Equip/Use [U]Unequip [I/Esc]Back", True, (120, 120, 130)),
            (w // 2 - 160, 44)
        )'''
new = '''        used = len(self.engine.player.get("items", []))
        cap = self.engine.inventory_capacity()
        overflow = len(self.engine.player.get("storage_overflow", []))
        cap_text = f"Inventory [{used}/{cap}]"
        if overflow:
            cap_text += f" Overflow +{overflow}"
        t = self.font_title.render(cap_text, True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 10))
        # operation hint
        self.screen.blit(
            self.font_small.render("[Up/Down]Select [Space]Equip/Use [U]Unequip [I/Esc]Back", True, (120, 120, 130)),
            (w // 2 - 160, 44)
        )'''
content = content.replace(old, new)

# ── Patch 10: Add CTB gauge in CombatView.render ──
old = '''        # menu
        if self.mode == MODE_SKILL_SELECT:'''
new = '''        # CTB action gauge
        c = engine.combat
        if c:
            p_gauge = c.get("player_gauge", 0)
            e_gauge = c.get("enemy_gauge", 0)
            p_pct = min(1.0, p_gauge / 1000.0)
            e_pct = min(1.0, e_gauge / 1000.0)
            # enemy gauge (above enemy HP bar)
            gx, gy, gw, gh = 10, 108, w - 20, 8
            pygame.draw.rect(screen, (30, 30, 40), (gx, gy, gw, gh), border_radius=2)
            pygame.draw.rect(screen, (220, 80, 80), (gx, gy, int(gw * e_pct), gh), border_radius=2)
            el = font_body.render(f"Gauge {e_gauge}/1000", True, (180, 180, 190))
            screen.blit(el, (gx + 4, gy - 2))
            # player gauge (bottom)
            py = h - 38
            pygame.draw.rect(screen, (30, 30, 40), (gx, py, gw, gh), border_radius=2)
            pygame.draw.rect(screen, (60, 200, 100), (gx, py, int(gw * p_pct), gh), border_radius=2)
            pl = font_body.render(f"Gauge {p_gauge}/1000", True, (180, 180, 190))
            screen.blit(pl, (gx + 4, py - 2))

        # menu
        if self.mode == MODE_SKILL_SELECT:'''
content = content.replace(old, new)

# ── Write back ──
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("pygame_ui.py patched successfully with 7 new scenes.")
