"""
WordWorld GUI — tkinter 图形界面窗口。

方向键 + 回车控制，保持文字界面风格。
运行：python run_gui.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Optional

from wordworld.core.engine import GameEngine, wallet_display
from wordworld.config.paths import SAVE_PATH

# ═══════════════════════════════════════════════════════════════
# 配色和字体
# ═══════════════════════════════════════════════════════════════

FONT = ("Microsoft YaHei", 11)
FONT_BOLD = ("Microsoft YaHei", 11, "bold")
FONT_SMALL = ("Microsoft YaHei", 10)
FONT_TITLE = ("Microsoft YaHei", 14, "bold")

BG = "#1a1a2e"
BG_PANEL = "#16213e"
FG = "#e0e0e0"
FG_DIM = "#888888"
ACCENT = "#e94560"
ACCENT_GREEN = "#00cc66"
ACCENT_GOLD = "#ffaa00"
HIGHLIGHT = "#0f3460"
LISTBOX_BG = "#16213e"
LISTBOX_FG = "#e0e0e0"
LISTBOX_SELECT = "#e94560"


# ═══════════════════════════════════════════════════════════════
# 游戏窗口
# ═══════════════════════════════════════════════════════════════

class GameWindow(tk.Tk):
    """主游戏窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.title("斗破苍穹 · 文字回合制 RPG")
        self.geometry("900x650")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(800, 550)

        # ── 游戏引擎 ──
        self.game = GameEngine()

        # ── 界面状态 ──
        self._screen_stack: list[Callable[[], None]] = []
        self._screen_id = "hub"

        # ── 构建界面 ──
        self._build_top_bar()
        self._build_content()
        self._build_bottom_bar()

        # ── 全局快捷键 ──
        self.bind("<Escape>", lambda e: self._go_back())
        self.bind("<BackSpace>", lambda e: self._go_back())
        self.bind("q", lambda e: self._keyboard_back_or_quit())
        self.bind("<F5>", lambda e: self._save_game())

        # ── 启动游戏 ──
        self._start_game()
        self._show_hub()

    # ═══════════════════════════════════════════════════════════
    # 界面构建
    # ═══════════════════════════════════════════════════════════

    def _build_top_bar(self) -> None:
        """顶栏：时间/地点 + 角色状态。"""
        self.top_frame = tk.Frame(self, bg=BG_PANEL, height=104)
        self.top_frame.pack(fill="x", padx=0, pady=0)
        self.top_frame.pack_propagate(False)
        self.top_frame.grid_propagate(False)
        self.top_frame.grid_columnconfigure(0, weight=1, uniform="top_bar")
        self.top_frame.grid_columnconfigure(1, minsize=1)
        self.top_frame.grid_columnconfigure(2, weight=1, uniform="top_bar")
        self.top_frame.grid_rowconfigure(0, weight=1)

        # 左列
        left = tk.Frame(self.top_frame, bg=BG_PANEL)
        left.grid(row=0, column=0, sticky="nsew", padx=(15, 18), pady=10)
        self.lbl_time = tk.Label(left, text="", font=FONT_BOLD, fg=FG, bg=BG_PANEL, anchor="w")
        self.lbl_time.pack(fill="x")
        self.lbl_location = tk.Label(left, text="", font=FONT, fg=FG, bg=BG_PANEL, anchor="w")
        self.lbl_location.pack(fill="x")
        self.lbl_schedule = tk.Label(
            left, text="", font=FONT_SMALL, fg=ACCENT_GOLD, bg=BG_PANEL,
            anchor="nw", justify="left",
        )
        self.lbl_schedule.pack(fill="x")

        tk.Frame(self.top_frame, bg=HIGHLIGHT, width=1).grid(
            row=0, column=1, sticky="ns", pady=12,
        )

        # 右列
        right = tk.Frame(self.top_frame, bg=BG_PANEL)
        right.grid(row=0, column=2, sticky="nsew", padx=(18, 15), pady=10)
        self.lbl_char = tk.Label(right, text="", font=FONT_BOLD, fg=FG, bg=BG_PANEL, anchor="e")
        self.lbl_char.pack(fill="x")
        self.lbl_stats = tk.Label(right, text="", font=FONT_SMALL, fg=FG, bg=BG_PANEL, anchor="e")
        self.lbl_stats.pack(fill="x")
        self.lbl_quest = tk.Label(
            right, text="", font=FONT_SMALL, fg=ACCENT_GREEN, bg=BG_PANEL,
            anchor="ne", justify="right",
        )
        self.lbl_quest.pack(fill="x")
        self.top_frame.bind("<Configure>", self._resize_top_bar_text)

    def _resize_top_bar_text(self, event: tk.Event) -> None:
        """限制两侧长文本宽度，避免状态信息互相遮挡。"""
        wrap_length = max(260, event.width // 2 - 50)
        self.lbl_schedule.config(wraplength=wrap_length)
        self.lbl_quest.config(wraplength=wrap_length)

    def _build_content(self) -> None:
        """中间内容区：列表 + 详情。"""
        self.content_frame = tk.Frame(self, bg=BG)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 左侧菜单列表
        self.menu_list = tk.Listbox(
            self.content_frame,
            bg=LISTBOX_BG, fg=LISTBOX_FG,
            selectbackground=LISTBOX_SELECT, selectforeground="#ffffff",
            font=FONT, border=0, highlightthickness=0,
            width=22, height=20,
            activestyle="none",
        )
        self.menu_list.pack(side="left", fill="y", padx=(0, 10))
        self.menu_list.bind("<Double-Button-1>", lambda e: self._on_menu_select())
        self.menu_list.bind("<Return>", lambda e: self._on_menu_select())
        self.menu_list.bind("<space>", lambda e: self._on_menu_select())
        self.menu_list.bind("<Up>", lambda e: self._move_menu_focus(-1))
        self.menu_list.bind("<Left>", lambda e: self._move_menu_focus(-1))
        self.menu_list.bind("<Down>", lambda e: self._move_menu_focus(1))
        self.menu_list.bind("<Right>", lambda e: self._move_menu_focus(1))
        self.menu_list.bind("<Home>", lambda e: self._focus_menu_edge(False))
        self.menu_list.bind("<End>", lambda e: self._focus_menu_edge(True))

        # 右侧详情面板
        self.detail_frame = tk.Frame(self.content_frame, bg=BG_PANEL)
        self.detail_frame.pack(side="right", fill="both", expand=True)

        self.detail_text = tk.Text(
            self.detail_frame,
            bg=BG_PANEL, fg=FG,
            font=FONT, border=0,
            wrap="word", state="disabled",
            padx=15, pady=10,
        )
        self.detail_text.pack(fill="both", expand=True)
        # 配置文本标签
        self.detail_text.tag_configure("title", font=FONT_TITLE, foreground=ACCENT)
        self.detail_text.tag_configure("bold", font=FONT_BOLD, foreground=FG)
        self.detail_text.tag_configure("dim", foreground=FG_DIM)
        self.detail_text.tag_configure("gold", foreground=ACCENT_GOLD)
        self.detail_text.tag_configure("green", foreground=ACCENT_GREEN)
        self.detail_text.tag_configure("red", foreground=ACCENT)

    def _build_bottom_bar(self) -> None:
        """底栏：消息 + 操作提示。"""
        self.bottom_frame = tk.Frame(self, bg=BG_PANEL, height=60)
        self.bottom_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        self.bottom_frame.pack_propagate(False)

        self.lbl_message = tk.Label(
            self.bottom_frame, text="",
            font=FONT, fg=ACCENT_GREEN, bg=BG_PANEL,
            anchor="w", padx=15, pady=5,
        )
        self.lbl_message.pack(side="left", fill="x", expand=True)

        self.lbl_hint = tk.Label(
            self.bottom_frame,
            text="↑↓ 选择  ↵ 回车确认  Esc 返回",
            font=FONT_SMALL, fg=FG_DIM, bg=BG_PANEL,
            anchor="e", padx=15, pady=5,
        )
        self.lbl_hint.pack(side="right")

    # ═══════════════════════════════════════════════════════════
    # 刷新
    # ═══════════════════════════════════════════════════════════

    def _refresh_top_bar(self) -> None:
        """刷新顶栏。"""
        g = self.game
        m = g.current_map()
        p = g.player
        phase = g.current_story_phase()
        prog = p["progress"]

        self.lbl_time.config(
            text=f"{'[夜]' if g.is_night() else '[昼]'} {g.time_text()}  "
            f"{'[安]' if m['safe_zone'] else ''}"
        )
        self.lbl_location.config(text=m["name"])
        node = g.next_schedule_node()
        if node:
            parts = g.schedule_text(node).splitlines()
            self.lbl_schedule.config(text=f"📅 {parts[0]}｜{g.schedule_countdown_text(node)}")
        else:
            self.lbl_schedule.config(text="")

        self.lbl_char.config(text=f"{p['name']}｜{g.realm_name()} Lv.{p['level']}")
        self.lbl_stats.config(
            text=f"修炼 {prog:.1f}%｜生命 {p['hp']}/{p['max_hp']}"
            f"  斗气 {p['douqi']}  阅历 {p['adventure_points']}"
        )
        if phase:
            subnode = g.current_story_subnode()
            task = phase["title"]
            if subnode:
                task += f" > {subnode['title']}"
            self.lbl_quest.config(text=f"📋 {task}")
        else:
            self.lbl_quest.config(text="所有目标已完成")

    def _refresh(self) -> None:
        """完整刷新。"""
        self._refresh_top_bar()
        self.update_idletasks()

    def _show_message(self, text: str) -> None:
        self.lbl_message.config(text=text)

    # ═══════════════════════════════════════════════════════════
    # 菜单列表操作
    # ═══════════════════════════════════════════════════════════

    def _set_menu(self, items: list[str], callback: Optional[Callable] = None) -> None:
        """设置左侧菜单列表。"""
        self.menu_list.delete(0, "end")
        for item in items:
            self.menu_list.insert("end", item)
        if items:
            self.menu_list.select_set(0)
            self.menu_list.focus_set()
        self._menu_callback = callback

    def _on_menu_select(self) -> str:
        """菜单选择回调。"""
        sel = self.menu_list.curselection()
        if sel and hasattr(self, "_menu_callback") and self._menu_callback:
            self._menu_callback(sel[0])
        return "break"

    def _select_menu_index(self, index: int) -> None:
        self.menu_list.selection_clear(0, "end")
        self.menu_list.selection_set(index)
        self.menu_list.activate(index)
        self.menu_list.see(index)

    def _move_menu_focus(self, delta: int) -> str:
        """方向键循环移动焦点，并跳过空白分隔项。"""
        size = self.menu_list.size()
        if size == 0:
            return "break"
        selected = self.menu_list.curselection()
        index = selected[0] if selected else (0 if delta > 0 else size - 1)
        for _ in range(size):
            index = (index + delta) % size
            if str(self.menu_list.get(index)).strip():
                self._select_menu_index(index)
                break
        return "break"

    def _focus_menu_edge(self, from_end: bool) -> str:
        indexes = range(self.menu_list.size() - 1, -1, -1) if from_end else range(self.menu_list.size())
        for index in indexes:
            if str(self.menu_list.get(index)).strip():
                self._select_menu_index(index)
                break
        return "break"

    def _set_detail(self, *lines: str) -> None:
        """设置右侧详情区文本。"""
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        for line in lines:
            self.detail_text.insert("end", line + "\n")
        self.detail_text.config(state="disabled")

    def _set_detail_rich(self, parts: list[tuple[str, str]]) -> None:
        """设置带标签的详情文本。(text, tag) 列表。"""
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        for text, tag in parts:
            self.detail_text.insert("end", text, tag)
        self.detail_text.config(state="disabled")

    # ═══════════════════════════════════════════════════════════
    # 导航
    # ═══════════════════════════════════════════════════════════

    def _go_back(self) -> str:
        """返回上一屏。"""
        if self._screen_id == "encounter":
            self.game.leave_encounter()
            self._after_action()
        elif self._screen_id == "skill_select":
            self._show_combat()
        elif self._screen_id == "combat":
            self._do_combat_action("escape")
        else:
            self._show_hub()
        return "break"

    def _keyboard_back_or_quit(self) -> str:
        if self._screen_id == "hub":
            self._quit_game()
        else:
            self._go_back()
        return "break"

    def _push_screen(self, screen_func: Callable[[], None]) -> None:
        self._screen_stack.append(self._current_screen)
        self._current_screen = screen_func
        screen_func()

    def _after_action(self) -> None:
        """操作后刷新并返回 Hub。"""
        self._show_message(self.game.last_message or "")
        self._refresh_top_bar()
        if self._screen_stack:
            self._screen_stack.pop()()
        else:
            self._show_hub()

    # ═══════════════════════════════════════════════════════════
    # 游戏启动
    # ═══════════════════════════════════════════════════════════

    def _start_game(self) -> None:
        if SAVE_PATH.exists():
            self.game.load()
            self._show_message("存档已读取。")
        else:
            self.game.new_game()
            self._show_message("欢迎来到斗气大陆。你的传奇，由此开始。")

    def _save_game(self) -> None:
        self.game.save()
        self._show_message("进度已保存。")

    # ═══════════════════════════════════════════════════════════
    # Hub 主界面
    # ═══════════════════════════════════════════════════════════

    def _show_hub(self) -> None:
        """显示主 Hub。"""
        self._screen_stack.clear()
        self._current_screen = self._show_hub
        self._screen_id = "hub"
        self._refresh_top_bar()

        menu_items = [
            "1. 人物",
            "2. 物品",
            "3. 斗技",
            "4. 修炼",
            "5. 探索",
            "6. 移动",
            "7. 主线",
            "8. 系统",
            "",
            "q. 退出游戏",
        ]
        self._set_menu(menu_items, self._hub_select)
        self.lbl_hint.config(text="方向键选择  ↵/空格确认  数字键 1-8 快捷  Esc/退格返回")

        # 数字快捷键
        for i in range(1, 9):
            self.bind(str(i), lambda e, n=i: self._hub_action(n))

    def _hub_select(self, index: int) -> None:
        """Hub 菜单选择处理。"""
        if index == 9:  # 退出
            self._quit_game()
        elif index < 8:
            self._hub_action(index + 1)

    def _hub_action(self, num: int) -> None:
        """Hub 菜单动作（快捷键/回车）。"""
        actions: dict[int, Callable[[], None]] = {
            1: self._show_character,
            2: self._show_items,
            3: self._show_skills,
            4: self._show_cultivation,
            5: self._do_explore,
            6: self._show_travel,
            7: self._show_story,
            8: self._show_system,
        }
        action = actions.get(num)
        if action:
            self._screen_id = "submenu"
            action()

    def _quit_game(self) -> None:
        if messagebox.askyesno("退出", "确定退出游戏？（进度将自动保存）"):
            self.game.save()
            self.destroy()

    # ═══════════════════════════════════════════════════════════
    # 1. 人物
    # ═══════════════════════════════════════════════════════════

    def _show_character(self) -> None:
        p = self.game.player
        g = self.game

        parts: list[tuple[str, str]] = [
            (f"{p['name']}  {g.realm_name()}  Lv.{p['level']}\n", "title"),
            (f"修炼进度 {p['progress']:.1f}%  冒险阅历 {p['adventure_points']}\n\n", "dim"),
            (f"生命 {p['hp']}/{p['max_hp']}  斗气 {p['douqi']}  资金 {wallet_display(p.get('wallet', {}))}\n", ""),
            (f"攻击 {p['atk']}  防御 {p['def']}  速度 {p['spd']}", ""),
            (f"  暴击 {p.get('crit_rate',0)}%  命中 {p.get('hit_rate',0)}%\n", "dim"),
            (f"灵魂力量 {p['soul']}  炼药术 {p['alchemy']}  声望 {p['reputation']}\n", ""),
            (f"经验 {p.get('exp',0)}  背包 {len(p.get('items',[]))}/{p.get('inventory_slots',30)}\n\n", "dim"),
            ("—— 人物关系 ——\n", "gold"),
        ]
        shown = 0
        for rule in g.relationship_rules.values():
            if not rule.get("visible", False):
                continue
            if rule.get("pre_condition") and not g.check_conditions(rule["pre_condition"]):
                continue
            target = rule["target"]
            name = g.npc_names.get(target, target)
            value = g.relation_value(target)
            stage = g.relation_stage(target)
            parts.append((f"  {name}（{rule.get('type','')}）：{value} [{stage}]\n", "green"))
            shown += 1
        if shown == 0:
            parts.append(("  暂无已知关系。\n", "dim"))

        self._set_detail_rich(parts)
        self._set_menu(["返回"], lambda _: self._show_hub())

    # ═══════════════════════════════════════════════════════════
    # 2. 物品
    # ═══════════════════════════════════════════════════════════

    def _show_items(self) -> None:
        items = self.game.player.get("items", [])
        if not items:
            self._set_detail("行囊空空。")
            self._set_menu(["返回"], lambda _: self._show_hub())
            return

        lines = ["—— 行囊物品 ——", ""]
        for index, item_id in enumerate(items, start=1):
            rule = self.game.item_rules.get(item_id, {})
            lines.append(f"{index}. {self.game.item_name(item_id)}（{rule.get('type','')}）")
            lines.append(f"   {rule.get('description','')}")
        lines.append("")
        lines.append(f"共 {len(items)} 件")

        self._set_detail(*lines)

        menu = [f"使用 {self.game.item_name(iid)}" for iid in items] + ["返回"]
        self._set_menu(menu, lambda idx: self._use_item(idx, items))

    def _use_item(self, index: int, items: list[str]) -> None:
        if index < len(items):
            item_id = items[index]
            if self.game.item_rules.get(item_id, {}).get("use_effect") == "gift":
                self._show_gift_targets(item_id)
                return
            self.game.use_item(item_id)
            self._show_message(self.game.last_message or "")
        self._show_hub()

    def _show_gift_targets(self, item_id: str) -> None:
        targets = self.game.gift_targets()
        self._set_detail(
            f"选择「{self.game.item_name(item_id)}」的赠礼目标",
            *[f"{target['name']}（{target['stage']}）" for target in targets],
        )
        self._set_menu(
            [target["name"] for target in targets] + ["返回"],
            lambda idx: self._give_gift(idx, item_id, targets),
        )

    def _give_gift(self, index: int, item_id: str, targets: list[dict]) -> None:
        if index < len(targets):
            self.game.give_gift(item_id, targets[index]["id"])
            self._show_message(self.game.last_message or "")
        self._show_hub()

    # ═══════════════════════════════════════════════════════════
    # 3. 斗技
    # ═══════════════════════════════════════════════════════════

    def _show_skills(self) -> None:
        skills = self.game.combat_skills()
        if not skills:
            self._set_detail("尚未掌握任何斗技。")
            self._set_menu(["返回"], lambda _: self._show_hub())
            return

        lines = [f"—— 已学斗技（{len(skills)} 种）——", ""]
        for skill in skills:
            lines.append(f"  {skill['name']}  [{skill.get('rank','')}]")
            lines.append(f"  类型：{skill.get('type','—')}  效果：{skill.get('effect','—')}")
            lines.append(f"  {skill.get('description','')}")
            lines.append("")
        self._set_detail(*lines)
        self._set_menu(["返回"], lambda _: self._show_hub())

    # ═══════════════════════════════════════════════════════════
    # 4. 修炼
    # ═══════════════════════════════════════════════════════════

    def _show_cultivation(self) -> None:
        g = self.game
        pct = float(g.player.get("progress", 0))
        level = int(g.player["level"])

        lines = [
            f"修炼进度 {pct:.1f}%",
            f"经验 {g.player.get('exp',0)}  斗气 {g.player['douqi']}",
            "",
        ]
        menu = ["修炼", "返回"]

        if pct >= 100.0 and level < 100:
            bp = g._breakthrough_chance_bp(level)
            ct = f"{bp/100:.2f}%" if bp < 100 else f"{bp/100:.0f}%"
            boundary = "[境界突破]" if g._is_realm_boundary(level) else "[段内突破]"
            lines.append(f"{boundary} {g.realm_name()} Lv.{level} → Lv.{level+1}")
            lines.append(f"成功率：{ct}")
            menu = ["修炼", "突破", "切磋", "返回"]
        elif level >= 100:
            lines.append("斗帝之境，已臻化境。")
            menu = ["修炼", "切磋", "返回"]
        else:
            lines.append("进度未满，还无法尝试突破。")
            menu = ["修炼", "切磋", "返回"]

        self._set_detail(*lines)
        self._set_menu(menu, lambda idx: self._cult_action(idx, menu))

    def _cult_action(self, index: int, menu: list[str]) -> None:
        action = menu[index]
        if action == "修炼":
            self.game.cultivate()
        elif action == "突破":
            self.game.breakthrough()
        elif action == "切磋":
            self.game.begin_training_combat()
            if self.game.combat is not None:
                self._show_combat()
                return
        elif action == "返回":
            self._show_hub()
            return
        self._after_action()

    # ═══════════════════════════════════════════════════════════
    # 5. 探索
    # ═══════════════════════════════════════════════════════════

    def _do_explore(self) -> None:
        m = self.game.current_map()
        actions = self.game.exploration_actions()
        lines = [
            f"当前区域：{m['name']}",
            "",
            "选择探索取向：",
        ]
        for action in actions:
            lines.append(f"{action['name']}｜体力 -{action['cost']}")
            lines.append(f"  {action['description']}")
        self._set_detail(*lines)
        self._set_menu(
            [f"{action['name']}（体力 -{action['cost']}）" for action in actions] + ["返回"],
            lambda idx: self._explore_select(idx, actions),
        )

    def _explore_select(self, index: int, actions: list[dict]) -> None:
        if index < len(actions):
            encounter = self.game.explore(actions[index]["id"])
            if encounter:
                self._show_encounter()
            else:
                self._after_action()
        else:
            self._show_hub()

    # ═══════════════════════════════════════════════════════════
    # 6. 移动
    # ═══════════════════════════════════════════════════════════

    def _show_travel(self) -> None:
        maps = self.game.available_maps()
        lines = [f"—— 已解锁区域（{len(maps)} 处）——", ""]
        menu = []
        for m in maps:
            cur = " [当前]" if m["id"] == self.game.current_map()["id"] else ""
            safe = "[安]" if m["safe_zone"] else ""
            lines.append(f"{safe} {m['name']}{cur}  Lv.{m['recommend_level']}")
            lines.append(f"   {m['description']}")
            menu.append(f"{'📍' if cur else '  '} {m['name']}")
        menu.append("返回")
        self._set_detail(*lines)
        self._set_menu(menu, lambda idx: self._travel_to(idx, maps))

    def _travel_to(self, index: int, maps: list[dict]) -> None:
        if index < len(maps):
            self.game.travel(maps[index]["id"])
        self._after_action()

    # ═══════════════════════════════════════════════════════════
    # 7. 主线
    # ═══════════════════════════════════════════════════════════

    def _show_story(self) -> None:
        g = self.game
        phase = g.current_story_phase()
        if phase is None:
            self._set_detail("所有关键目标已完成。")
            self._set_menu(["返回"], lambda _: self._show_hub())
            return

        requirement = g.story_requirement()
        lines = [
            f"[主线] {phase['title']}",
            f"冒险阅历需求 {requirement} / 当前 {g.player['adventure_points']}",
            "",
            f"背景：{phase['background']}",
            f"目标：{phase['objective']}",
            f"风险：{phase['risk']}",
            "",
            "—— 子节点进度 ——",
        ]
        current = g.current_story_subnode()
        for index, subnode in enumerate(phase["subnodes"], start=1):
            if index <= g.player["story_substage"]:
                m = "[✓]"
            elif subnode is current:
                m = "[▶]"
            else:
                m = "[ ]"
            lines.append(f"  {m} {subnode['title']}  ({subnode['condition']})")
            lines.append(f"     {subnode['objective']}")
        if current:
            lines.append(f"\n当前行动：{current['title']}")

        self._set_detail(*lines)
        self._set_menu(["尝试推进", "返回"], self._story_select)

    def _story_select(self, index: int) -> None:
        if index == 0:
            self.game.advance_story()
        self._after_action()

    # ═══════════════════════════════════════════════════════════
    # 8. 系统
    # ═══════════════════════════════════════════════════════════

    def _show_system(self) -> None:
        m = self.game.current_map()
        can_rest = m["safe_zone"]
        rest_hint = "（安全区，可以休息）" if can_rest else "（非安全区，无法休息）"

        self._set_detail(
            f"当前 {self.game.time_text()}｜{m['name']} {rest_hint}",
            f"生命 {self.game.player['hp']}/{self.game.player['max_hp']}",
        )

        menu = []
        if can_rest:
            menu.append("休息")
        menu.extend(["保存进度", "返回主菜单", "退出游戏"])
        self._set_menu(menu, self._system_select)

    def _system_select(self, index: int) -> None:
        m = self.game.current_map()
        can_rest = m["safe_zone"]
        offset = 1 if can_rest else 0

        if can_rest and index == 0:
            self.game.rest()
            self._after_action()
        elif index == offset:
            self.game.save()
            self._show_message("进度已保存。")
            self._show_hub()
        elif index == offset + 1:
            self._show_hub()
        elif index == offset + 2:
            self._quit_game()

    # ═══════════════════════════════════════════════════════════
    # 战斗
    # ═══════════════════════════════════════════════════════════

    def _show_combat(self) -> None:
        """显示战斗界面。"""
        self._screen_id = "combat"
        self._refresh_combat_view()

        actions = ["普通攻击", "施展斗技", "防御", "使用丹药", "逃跑", "自动战斗"]
        self._set_menu(actions, self._combat_select)
        self.lbl_hint.config(text="↑↓ 选择  ↵ 确认  数字键 1-6 快捷")
        for i in range(1, 7):
            self.bind(str(i), lambda e, n=i: self._combat_action_by_num(n))

    def _refresh_combat_view(self) -> None:
        """刷新战斗信息。"""
        if self.game.combat is None:
            self._show_hub()
            return
        combat = self.game.combat
        p = self.game.player
        enemy_hp_bar = "█" * int(combat["hp"] / max(1, combat["max_hp"]) * 20)
        player_hp_bar = "█" * int(p["hp"] / max(1, p["max_hp"]) * 20)

        self.lbl_message.config(
            text=f"{combat['name']}  HP [{enemy_hp_bar}] {combat['hp']}/{combat['max_hp']}"
            f"  |  {p['name']}  HP [{player_hp_bar}] {p['hp']}/{p['max_hp']}"
        )

        self._set_detail(
            f"[bold]{combat['name']}[/bold]",
            f"HP: {combat['hp']}/{combat['max_hp']}",
            f"",
            f"你的 HP: {p['hp']}/{p['max_hp']}  斗气: {p['douqi']}",
        )

    def _combat_select(self, index: int) -> None:
        self._do_combat_action({
            0: "attack", 1: "skill", 2: "defend",
            3: "item", 4: "escape", 5: "auto",
        }.get(index, "attack"))

    def _combat_action_by_num(self, num: int) -> None:
        self._do_combat_action({
            1: "attack", 2: "skill", 3: "defend",
            4: "item", 5: "escape", 6: "auto",
        }.get(num, "attack"))

    def _do_combat_action(self, action: str) -> None:
        if action == "skill":
            skills = self.game.combat_skills()
            if not skills:
                self._show_message("尚未掌握可用斗技。")
                return
            self._show_skill_select(skills)
            return
        elif action == "item":
            items = self.game.combat_usable_items()
            if not items:
                self._show_message("没有可在战斗中使用的物品。")
                return
            self._set_detail("选择战斗物品：", *[
                f"  {self.game.item_name(item_id)}" for item_id in items
            ])
            self._set_menu(
                [self.game.item_name(item_id) for item_id in items] + ["取消"],
                lambda idx: self._combat_item_chosen(idx, items),
            )
            return
        elif action == "auto":
            self.game.auto_battle()
            self._show_message(self.game.last_message or "")
            if self.game.combat is None:
                self._after_action()
            else:
                self._refresh_combat_view()
            return

        result = self.game.combat_action(action)
        self._show_message(self.game.last_message or "")
        if self.game.combat is None:
            self._after_action()
        else:
            self._refresh_combat_view()

    def _show_skill_select(self, skills: list[dict]) -> None:
        """战斗中选斗技。"""
        self._screen_id = "skill_select"
        self._set_detail("选择斗技：", "")
        for skill in skills:
            self._set_detail(
                *self._get_detail_lines(),
                f"  {skill['name']} [{skill.get('rank','')}]",
            )
        menu = [f"{s['name']} [{s.get('rank','')}]" for s in skills] + ["取消"]
        self._set_menu(menu, lambda idx: self._skill_chosen(idx, skills))

    def _skill_chosen(self, index: int, skills: list[dict]) -> None:
        if index < len(skills):
            self.game.combat_action("skill", skills[index]["id"])
            self._show_message(self.game.last_message or "")
            if self.game.combat is None:
                self._after_action()
            else:
                self._refresh_combat_view()
        else:
            self._show_combat()

    def _combat_item_chosen(self, index: int, items: list[str]) -> None:
        if index < len(items):
            self.game.combat_action("item", items[index])
            self._show_message(self.game.last_message or "")
            if self.game.combat is None:
                self._after_action()
            else:
                self._refresh_combat_view()
        else:
            self._show_combat()

    def _get_detail_lines(self) -> list[str]:
        """获取当前 detail_text 内容。"""
        return self.detail_text.get("1.0", "end-1c").split("\n")

    # ═══════════════════════════════════════════════════════════
    # 探索遭遇
    # ═══════════════════════════════════════════════════════════

    def _show_encounter(self) -> None:
        self._screen_id = "encounter"
        enc = self.game.active_encounter
        if enc is None:
            self._after_action()
            return

        self._set_detail(enc["text"])
        options = self.game.encounter_options()
        menu = [opt["text"] for _, opt in options] + ["离开"]
        self._set_menu(menu, lambda idx: self._encounter_chosen(idx, options))

    def _encounter_chosen(self, index: int, options: list) -> None:
        if index < len(options):
            self.game.choose_encounter_option(options[index][0])
            self._show_message(self.game.last_message or "")
            if self.game.combat is not None:
                self._show_combat()
            else:
                self._after_action()
        else:
            self.game.leave_encounter()
            self._after_action()


# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    app = GameWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
