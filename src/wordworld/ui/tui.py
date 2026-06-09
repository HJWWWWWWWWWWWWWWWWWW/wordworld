"""
WordWorld TUI — 终端图形界面。

方向键 + 回车控制。基于 Textual 框架。
运行：python -m wordworld.ui.tui
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Label, RichLog, Static

from wordworld.core.engine import GameEngine
from wordworld.config.paths import SAVE_PATH


# ═══════════════════════════════════════════════════════════════
# 常量和工具
# ═══════════════════════════════════════════════════════════════

SCREEN_MAP: dict[str, type["_SubScreen"]] = {}  # 注册到 _SubScreen.__init_subclass__


def _fmt(key: str, value: Any) -> str:
    return f"{key} {value}"


def _day_label(game: GameEngine) -> str:
    return "[夜]" if game.is_night() else "[昼]"


def _safe_label(game: GameEngine) -> str:
    return "[安]" if game.current_map()["safe_zone"] else ""


def _hp_bar(current: int, maximum: int, width: int = 12) -> str:
    filled = int(current / max(1, maximum) * width)
    return f"{'█' * filled}{'░' * (width - filled)} {current}/{maximum}"


# ═══════════════════════════════════════════════════════════════
# 子屏幕基类
# ═══════════════════════════════════════════════════════════════

class _SubScreen(Screen[None]):
    """所有子菜单和功能屏幕的基类。q/Esc 返回 Hub。"""

    BINDINGS = [
        Binding("escape,q", "dismiss", "返回"),
    ]

    def __init__(self, game: GameEngine) -> None:
        super().__init__()
        self.game = game

    def _after_action(self) -> None:
        """操作后：更新消息并返回 Hub。"""
        self.app.query_one("#hub-msg", Static).update(
            self.game.last_message or ""
        )
        self.dismiss()


# ═══════════════════════════════════════════════════════════════
# 子屏幕注册装饰器
# ═══════════════════════════════════════════════════════════════

def _register(key: str):
    def dec(cls):
        SCREEN_MAP[key] = cls
        return cls
    return dec


# ═══════════════════════════════════════════════════════════════
# 通用：纯文本信息屏（人物、斗技、故事等）
# ═══════════════════════════════════════════════════════════════

class InfoScreen(_SubScreen):
    """通用文本展示屏。设置 content_lines 即可。"""

    content_lines: list[str] = []

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("\n".join(self.content_lines), id="info-body")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#info-body").focus()


@_register("1")
class CharacterScreen(InfoScreen):
    def __init__(self, game: GameEngine) -> None:
        super().__init__(game)
        p = game.player
        lines = [
            f"[bold]{p['name']}[/]  {game.realm_name()}  Lv.{p['level']}",
            f"进度 {p['progress']:.1f}%  阅历 {p['adventure_points']}",
            "",
            f"生命 {p['hp']}/{p['max_hp']}  {_hp_bar(p['hp'], p['max_hp'])}",
            f"斗气 {p['douqi']}  体力 {p['stamina']}  银两 {p['silver']}",
            f"攻击 {p['atk']}  防御 {p['def']}  速度 {p['spd']}",
            f"暴击 {p.get('crit_rate',0)}%  命中 {p.get('hit_rate',0)}%",
            f"灵魂 {p['soul']}  炼药 {p['alchemy']}  声望 {p['reputation']}",
            f"经验 {p.get('exp',0)}  背包 {len(p.get('items',[]))}",
            "",
            "[bold]—— 人物关系 ——[/]",
        ]
        shown = 0
        for rule in game.relationship_rules.values():
            if not rule.get("visible", False):
                continue
            if rule.get("pre_condition") and not game.check_conditions(rule["pre_condition"]):
                continue
            target = rule["target"]
            name = game.npc_names.get(target, target)
            value = game.relation_value(target)
            stage = game.relation_stage(target)
            lines.append(f"  {name}（{rule.get('type','')}）：{value} [{stage}]")
            shown += 1
        if shown == 0:
            lines.append("  暂无已知关系。")
        self.content_lines = lines


@_register("3")
class SkillsScreen(InfoScreen):
    def __init__(self, game: GameEngine) -> None:
        super().__init__(game)
        skills = game.combat_skills()
        if not skills:
            self.content_lines = ["尚未掌握任何斗技。"]
            return
        lines = [f"[bold]—— 已学斗技（{len(skills)} 种）——[/]", ""]
        for skill in skills:
            lines.append(f"  {skill['name']}  [{skill.get('rank','')}]")
            lines.append(f"  类型：{skill.get('type','—')}  效果：{skill.get('effect','—')}")
            lines.append(f"  {skill.get('description','')}")
            lines.append("")
        self.content_lines = lines


# ═══════════════════════════════════════════════════════════════
# 物品
# ═══════════════════════════════════════════════════════════════

@_register("2")
class ItemsScreen(_SubScreen):
    def compose(self) -> ComposeResult:
        items = self.game.player.get("items", [])
        if not items:
            yield Static("行囊空空。")
            yield Footer()
            return

        lines = ["[bold]—— 行囊物品 ——[/]", ""]
        for index, item_id in enumerate(items, start=1):
            rule = self.game.item_rules.get(item_id, {})
            lines.append(
                f"  {index}. [bold]{self.game.item_name(item_id)}[/]"
                f"（{rule.get('type', '')}）"
            )
            lines.append(f"     {rule.get('description', '')}")

        with VerticalScroll():
            yield Static("\n".join(lines))
            yield Static("", id="sub-msg")
        with Horizontal():
            for index, item_id in enumerate(items[:9], start=1):
                yield Button(
                    str(index), id=f"use-{index}",
                    classes="item-btn",
                )
            yield Button("返回", id="btn-back")
        yield Footer()

    @on(Button.Pressed, ".item-btn")
    def _use_item(self, event: Button.Pressed) -> None:
        num = int(event.button.id.replace("use-", "")) if event.button.id else 0
        items = self.game.player.get("items", [])
        if 1 <= num <= len(items):
            self.game.use_item(items[num - 1])
            self.query_one("#sub-msg", Static).update(
                self.game.last_message or ""
            )
            self.refresh(recompose=True)

    @on(Button.Pressed, "#btn-back")
    def _back(self) -> None:
        self.dismiss()


# ═══════════════════════════════════════════════════════════════
# 修炼
# ═══════════════════════════════════════════════════════════════

@_register("4")
class CultivationScreen(_SubScreen):
    AUTO_FOCUS = "#cult-body"

    def compose(self) -> ComposeResult:
        pct = float(self.game.player.get("progress", 0))
        level = int(self.game.player["level"])
        bp = self.game._breakthrough_chance_bp(level)
        ct = f"{bp/100:.2f}%" if bp < 100 else f"{bp/100:.0f}%"

        lines = [
            f"[bold]修炼进度 {pct:.1f}%[/]  经验 {self.game.player.get('exp',0)}",
            f"斗气 {self.game.player['douqi']}  体力 {self.game.player['stamina']}",
            "",
        ]
        if pct >= 100.0 and level < 100:
            boundary = "[境界突破]" if self.game._is_realm_boundary(level) else "[段内突破]"
            lines.append(
                f"{boundary} 冲击 {self.game.realm_name()} Lv.{level+1}（成功率 {ct}）"
            )
        elif level >= 100:
            lines.append("斗帝之境，已臻化境。")
        else:
            lines.append("进度未满，还无法尝试突破。")

        with VerticalScroll(id="cult-body"):
            yield Static("\n".join(lines))
            yield Static("", id="sub-msg")

        with Horizontal():
            yield Button("修炼", id="btn-cultivate", variant="primary")
            if pct >= 100.0:
                yield Button("突破", id="btn-breakthrough", variant="warning")
            yield Button("切磋", id="btn-spar")
        yield Footer()

    @on(Button.Pressed, "#btn-cultivate")
    def _cultivate(self) -> None:
        self.game.cultivate()
        self._after_action()

    @on(Button.Pressed, "#btn-breakthrough")
    def _breakthrough(self) -> None:
        pct = float(self.game.player.get("progress", 0))
        if pct < 100.0:
            return
        self.game.breakthrough()
        self._after_action()

    @on(Button.Pressed, "#btn-spar")
    def _spar(self) -> None:
        self.game.begin_training_combat()
        if self.game.combat is not None:
            self.app.push_screen(CombatScreen(self.game))


# ═══════════════════════════════════════════════════════════════
# 探索
# ═══════════════════════════════════════════════════════════════

@_register("5")
class ExploreScreen(_SubScreen):
    def compose(self) -> ComposeResult:
        map_rule = self.game.current_map()
        cost = map_rule.get("stamina_cost", 5)
        night_cost = 2 if self.game.is_night() else 0
        total_cost = cost + night_cost

        night_text = f"（夜间 +{night_cost}）" if night_cost else ""
        yield Static(
            f"[bold]当前区域：{map_rule['name']}[/]\n"
            f"体力消耗：{total_cost} {night_text}\n"
            f"当前体力：{self.game.player['stamina']}"
        )
        with Horizontal():
            yield Button("开始探索", id="btn-explore", variant="primary")
            yield Button("返回", id="btn-back")
        yield Static("", id="sub-msg")
        yield Footer()

    @on(Button.Pressed, "#btn-explore")
    def _explore(self) -> None:
        encounter = self.game.explore()
        if encounter:
            self.app.push_screen(EncounterScreen(self.game))
        else:
            self._after_action()

    @on(Button.Pressed, "#btn-back")
    def _back(self) -> None:
        self.dismiss()


# ═══════════════════════════════════════════════════════════════
# 移动
# ═══════════════════════════════════════════════════════════════

@_register("6")
class TravelScreen(_SubScreen):
    def compose(self) -> ComposeResult:
        maps = self.game.available_maps()
        yield Static(
            f"[bold]—— 已解锁区域（{len(maps)} 处）——[/]", id="travel-title"
        )
        for index, m in enumerate(maps, start=1):
            cur = " [当前]" if m["id"] == self.game.current_map()["id"] else ""
            safe = "[安]" if m["safe_zone"] else ""
            yield Button(
                f"{index}. {safe} {m['name']}{cur}  Lv.{m['recommend_level']}",
                id=f"travel-{index}",
                variant="primary" if cur else "default",
            )
        yield Static("", id="sub-msg")
        yield Button("返回", id="btn-back")
        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def _back(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理旅行按钮。"""
        bid = event.button.id or ""
        if bid.startswith("travel-"):
            num = int(bid.replace("travel-", ""))
            maps = self.game.available_maps()
            if 1 <= num <= len(maps):
                self.game.travel(maps[num - 1]["id"])
                self.query_one("#sub-msg", Static).update(
                    self.game.last_message or ""
                )
                self.refresh(recompose=True)
        elif bid == "btn-back":
            self.dismiss()


# ═══════════════════════════════════════════════════════════════
# 主线
# ═══════════════════════════════════════════════════════════════

@_register("7")
class StoryScreen(_SubScreen):
    def compose(self) -> ComposeResult:
        phase = self.game.current_story_phase()
        if phase is None:
            yield Static("所有关键目标已完成。", id="story-body")
            yield Footer()
            return

        requirement = self.game.story_requirement()
        lines = [
            f"[bold][主线] {phase['title']}[/]",
            f"冒险阅历需求 {requirement} / 当前 {self.game.player['adventure_points']}",
            "",
            f"背景：{phase['background']}",
            f"目标：{phase['objective']}",
            f"风险：{phase['risk']}",
            "",
            "[bold]—— 子节点进度 ——[/]",
        ]
        current = self.game.current_story_subnode()
        for index, subnode in enumerate(phase["subnodes"], start=1):
            if index <= self.game.player["story_substage"]:
                m = "[✓]"
            elif subnode is current:
                m = "[▶]"
            else:
                m = "[ ]"
            lines.append(f"  {m} {subnode['title']}  ({subnode['condition']})")
            lines.append(f"     {subnode['objective']}")

        if current:
            lines.append(f"\n当前行动：{current['title']}")

        node = self.game.next_schedule_node()
        if node:
            parts = self.game.schedule_text(node).splitlines()
            lines.append(f"\n[日程] {parts[0]}｜{self.game.schedule_countdown_text(node)}")

        with VerticalScroll(id="story-body"):
            yield Static("\n".join(lines))
            yield Static("", id="sub-msg")
        with Horizontal():
            yield Button("尝试推进", id="btn-advance", variant="primary")
            yield Button("返回", id="btn-back")
        yield Footer()

    @on(Button.Pressed, "#btn-advance")
    def _advance(self) -> None:
        self.game.advance_story()
        self._after_action()

    @on(Button.Pressed, "#btn-back")
    def _back(self) -> None:
        self.dismiss()


# ═══════════════════════════════════════════════════════════════
# 系统
# ═══════════════════════════════════════════════════════════════

@_register("8")
class SystemScreen(_SubScreen):
    def compose(self) -> ComposeResult:
        map_rule = self.game.current_map()
        can_rest = map_rule["safe_zone"]
        rest_hint = "（安全区，可以休息）" if can_rest else "（非安全区，无法休息）"

        yield Static(
            f"当前 {self.game.time_text()}｜{map_rule['name']} {rest_hint}\n"
            f"生命 {self.game.player['hp']}/{self.game.player['max_hp']}"
            f"  体力 {self.game.player['stamina']}"
        )
        yield Static("", id="sub-msg")
        with Horizontal():
            if can_rest:
                yield Button("休息", id="btn-rest", variant="primary")
            yield Button("保存进度", id="btn-save", variant="success")
            yield Button("返回", id="btn-back")
            yield Button("退出游戏", id="btn-exit", variant="error")
        yield Footer()

    @on(Button.Pressed, "#btn-rest")
    def _rest(self) -> None:
        self.game.rest()
        self._after_action()

    @on(Button.Pressed, "#btn-save")
    def _save(self) -> None:
        self.game.save()
        self.game.last_message = "进度已保存。"
        self._after_action()

    @on(Button.Pressed, "#btn-back")
    def _back(self) -> None:
        self.dismiss()

    @on(Button.Pressed, "#btn-exit")
    def _exit(self) -> None:
        self.game.save()
        self.app.exit()


# ═══════════════════════════════════════════════════════════════
# 战斗
# ═══════════════════════════════════════════════════════════════

class CombatScreen(ModalScreen[None]):
    """回合战斗模态屏。"""

    BINDINGS = [
        Binding("1", "attack", "攻击"),
        Binding("2", "skill", "斗技"),
        Binding("3", "defend", "防御"),
        Binding("4", "item", "丹药"),
        Binding("5", "escape", "逃跑"),
        Binding("6", "auto", "自动战斗"),
    ]

    def __init__(self, game: GameEngine) -> None:
        super().__init__()
        self.game = game

    def compose(self) -> ComposeResult:
        with Container():
            yield RichLog(id="combat-log", highlight=True, markup=True)
            with Horizontal(id="combat-actions"):
                yield Button("1.攻击", id="btn-atk", variant="primary")
                yield Button("2.斗技", id="btn-skill")
                yield Button("3.防御", id="btn-def")
                yield Button("4.丹药", id="btn-item")
                yield Button("5.逃跑", id="btn-esc")
                yield Button("6.自动", id="btn-auto")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_combat()

    def _refresh_combat(self) -> None:
        log = self.query_one("#combat-log", RichLog)
        log.clear()
        log.write(self.game.combat_text())

    def _do_action(self, action: str, skill_id: Optional[str] = None) -> None:
        result = self.game.combat_action(action, skill_id)
        log = self.query_one("#combat-log", RichLog)
        log.write(f"\n{self.game.last_message}")

        if self.game.combat is None:
            # 战斗结束
            self._update_actions_enabled(False)
            self.set_timer(1.5, self.dismiss)
        else:
            self._refresh_combat()

    def _update_actions_enabled(self, enabled: bool) -> None:
        for bid in ("#btn-atk", "#btn-skill", "#btn-def", "#btn-item",
                     "#btn-esc", "#btn-auto"):
            try:
                self.query_one(bid, Button).disabled = not enabled
            except Exception:
                pass

    @on(Button.Pressed, "#btn-atk")
    def _atk(self) -> None: self._do_action("attack")

    @on(Button.Pressed, "#btn-skill")
    def _skill(self) -> None:
        skills = self.game.combat_skills()
        if not skills:
            self.game.last_message = "尚未掌握可用斗技。"
            self._refresh_combat()
            return
        if len(skills) == 1:
            self._do_action("skill", skills[0]["id"])
            return
        self.app.push_screen(SkillSelectScreen(self.game, skills, self._do_action))

    @on(Button.Pressed, "#btn-def")
    def _def(self) -> None: self._do_action("defend")

    @on(Button.Pressed, "#btn-item")
    def _item(self) -> None: self._do_action("item")

    @on(Button.Pressed, "#btn-esc")
    def _esc(self) -> None: self._do_action("escape")

    @on(Button.Pressed, "#btn-auto")
    def _auto(self) -> None:
        self.game.auto_battle()
        log = self.query_one("#combat-log", RichLog)
        log.write(f"\n{self.game.last_message}")
        self._update_actions_enabled(False)
        self.set_timer(2.0, self.dismiss)

    def action_attack(self) -> None: self._do_action("attack")
    def action_skill(self) -> None: self._skill()
    def action_defend(self) -> None: self._do_action("defend")
    def action_item(self) -> None: self._do_action("item")
    def action_escape(self) -> None: self._do_action("escape")
    def action_auto(self) -> None: self._auto()


class SkillSelectScreen(ModalScreen[None]):
    """战斗中选择斗技的弹出屏。"""

    def __init__(self, game: GameEngine, skills: list[dict], callback: Callable) -> None:
        super().__init__()
        self.game = game
        self.skills = skills
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Static("[bold]选择斗技[/]", id="skill-title")
        for i, skill in enumerate(self.skills[:9], start=1):
            yield Button(
                f"{i}. {skill['name']} [{skill.get('rank','')}]",
                id=f"sk-{i}",
            )
        yield Button("取消", id="sk-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "sk-cancel":
            self.dismiss()
            return
        num = btn_id.replace("sk-", "")
        if num.isdigit():
            idx = int(num) - 1
            if 0 <= idx < len(self.skills):
                self.callback("skill", self.skills[idx]["id"])
                self.dismiss()

    def on_mount(self) -> None:
        try:
            self.query_one("#sk-1").focus()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# 探索遭遇
# ═══════════════════════════════════════════════════════════════

class EncounterScreen(ModalScreen[None]):
    """探索遭遇模态屏。"""

    def __init__(self, game: GameEngine) -> None:
        super().__init__()
        self.game = game

    def compose(self) -> ComposeResult:
        encounter = self.game.active_encounter
        if encounter is None:
            self.dismiss()
            return

        yield Static(encounter["text"], id="enc-text")
        options = self.game.encounter_options()
        for index, option in options:
            yield Button(
                f"{index}. {option['text']}",
                id=f"enc-opt-{index}",
                variant="primary",
            )
        yield Button("离开", id="enc-leave")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "enc-leave":
            self.game.active_encounter = None
            self.game.last_message = "你谨慎地离开了现场。"
            self.dismiss()
            return
        num = btn_id.replace("enc-opt-", "")
        if num.isdigit():
            self.game.choose_encounter_option(int(num))
            self.dismiss()
            if self.game.combat is not None:
                self.app.push_screen(CombatScreen(self.game))


# ═══════════════════════════════════════════════════════════════
# 强制日程
# ═══════════════════════════════════════════════════════════════

class ScheduleScreen(ModalScreen[None]):
    """强制日程节点。"""

    def __init__(self, game: GameEngine) -> None:
        super().__init__()
        self.game = game

    def compose(self) -> ComposeResult:
        node = self.game.pending_schedule_node()
        if node is None:
            self.dismiss()
            return
        yield Static(self.game.schedule_text(node), id="sched-text")
        yield Static("时间已到，按回车参加并结算。", id="sched-hint")
        yield Button("确认参加", id="btn-sched", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#btn-sched")
    def _confirm(self) -> None:
        self.game.resolve_schedule_node()
        self.dismiss()


# ═══════════════════════════════════════════════════════════════
# Hub 主屏幕
# ═══════════════════════════════════════════════════════════════

class HubScreen(Screen[None]):
    """主 Hub 界面。定时刷新顶栏，通过按钮导航到子屏幕。"""

    BINDINGS = [
        Binding("1", "menu('1')", "人物", show=False),
        Binding("2", "menu('2')", "物品", show=False),
        Binding("3", "menu('3')", "斗技", show=False),
        Binding("4", "menu('4')", "修炼", show=False),
        Binding("5", "menu('5')", "探索", show=False),
        Binding("6", "menu('6')", "移动", show=False),
        Binding("7", "menu('7')", "主线", show=False),
        Binding("8", "menu('8')", "系统", show=False),
        Binding("q", "quit", "退出"),
    ]

    def __init__(self, game: GameEngine) -> None:
        super().__init__()
        self.game = game

    def compose(self) -> ComposeResult:
        # 顶栏
        with Container(id="top-bar"):
            with Horizontal():
                with Vertical(id="top-left"):
                    yield Label("", id="tl1")
                    yield Label("", id="tl2")
                    yield Label("", id="tl3")
                with Vertical(id="top-right"):
                    yield Label("", id="tr1")
                    yield Label("", id="tr2")
                    yield Label("", id="tr3")

        # 菜单按钮
        with Container(id="menu-grid"):
            with Horizontal(classes="menu-row"):
                yield Button("1.人物", id="hub-btn-1", variant="primary")
                yield Button("2.物品", id="hub-btn-2")
                yield Button("3.斗技", id="hub-btn-3")
                yield Button("4.修炼", id="hub-btn-4")
            with Horizontal(classes="menu-row"):
                yield Button("5.探索", id="hub-btn-5")
                yield Button("6.移动", id="hub-btn-6")
                yield Button("7.主线", id="hub-btn-7")
                yield Button("8.系统", id="hub-btn-8")

        # 消息区
        with Container(id="msg-area"):
            yield Static("欢迎来到斗气大陆。你的传奇，由此开始。", id="hub-msg")

        yield Footer()

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(1.0, self._check_schedule)
        self.set_interval(0.5, self._refresh)

    def _refresh(self) -> None:
        """刷新顶栏。"""
        game = self.game
        m = game.current_map()
        p = game.player
        phase = game.current_story_phase()
        prog = p["progress"]

        # 左列
        self.query_one("#tl1", Label).update(
            f"{_day_label(game)} {game.time_text()} {_safe_label(game)}"
        )
        self.query_one("#tl2", Label).update(m["name"])
        node = game.next_schedule_node()
        if node:
            parts = game.schedule_text(node).splitlines()
            self.query_one("#tl3", Label).update(
                f"[日程] {parts[0]}｜{game.schedule_countdown_text(node)}"
            )
        else:
            self.query_one("#tl3", Label).update("")

        # 右列
        if phase:
            subnode = game.current_story_subnode()
            task = phase["title"]
            if subnode:
                task += f" > {subnode['title']}"
            right_3 = f"[任务] {task}"
        else:
            right_3 = "所有目标已完成"

        self.query_one("#tr1", Label).update(
            f"{p['name']}｜{game.realm_name()} Lv.{p['level']}"
        )
        self.query_one("#tr2", Label).update(
            f"修炼 {prog:.1f}%｜"
            f"生命 {p['hp']}/{p['max_hp']}"
            f"  斗气 {p['douqi']}"
            f"  体力 {p['stamina']}"
            f"  阅历 {p['adventure_points']}"
        )
        self.query_one("#tr3", Label).update(right_3)

    def _check_schedule(self) -> None:
        if self.game.pending_schedule_node() is not None:
            self.app.push_screen(ScheduleScreen(self.game))

    # ── 菜单按钮事件 ──
    def _push(self, key: str) -> None:
        cls = SCREEN_MAP.get(key)
        if cls:
            self.app.push_screen(cls(self.game))

    @on(Button.Pressed, "#hub-btn-1")  # type: ignore[arg-type]
    def _m1(self) -> None: self._push("1")
    @on(Button.Pressed, "#hub-btn-2")  # type: ignore[arg-type]
    def _m2(self) -> None: self._push("2")
    @on(Button.Pressed, "#hub-btn-3")  # type: ignore[arg-type]
    def _m3(self) -> None: self._push("3")
    @on(Button.Pressed, "#hub-btn-4")  # type: ignore[arg-type]
    def _m4(self) -> None: self._push("4")
    @on(Button.Pressed, "#hub-btn-5")  # type: ignore[arg-type]
    def _m5(self) -> None: self._push("5")
    @on(Button.Pressed, "#hub-btn-6")  # type: ignore[arg-type]
    def _m6(self) -> None: self._push("6")
    @on(Button.Pressed, "#hub-btn-7")  # type: ignore[arg-type]
    def _m7(self) -> None: self._push("7")
    @on(Button.Pressed, "#hub-btn-8")  # type: ignore[arg-type]
    def _m8(self) -> None: self._push("8")

    def action_menu(self, key: str) -> None:
        self._push(key)

    def action_quit(self) -> None:
        self.app.exit()


# ═══════════════════════════════════════════════════════════════
# App
# ═══════════════════════════════════════════════════════════════

CSS = """
Screen {
    layout: vertical;
}

#top-bar {
    height: auto;
    padding: 0 1;
    border-bottom: heavy $primary;
    background: $panel;
}

#top-left {
    width: 30;
}

#top-right {
    width: 1fr;
    padding-left: 1;
}

#menu-grid {
    height: auto;
    padding: 1;
    border-bottom: solid $primary;
}

.menu-row {
    height: auto;
    align: center middle;
}

.menu-row Button {
    width: 18;
    margin: 0 1;
}

#msg-area {
    height: auto;
    min-height: 3;
    padding: 0 1 1 1;
    background: $surface;
}

#hub-msg {
    height: auto;
}

#combat-log {
    height: 12;
    border: solid $warning;
    background: $surface;
    padding: 0 1;
}

#combat-actions {
    height: auto;
    padding: 1;
    align: center middle;
}

#combat-actions Button {
    width: 14;
    margin: 0 1;
}

#sub-msg {
    height: auto;
    min-height: 1;
    color: $success;
}

#info-body {
    padding: 1 2;
}

Footer {
    background: $panel;
}
"""


class WordWorldApp(App[None]):
    """WordWorld 终端图形界面。"""

    CSS = CSS

    def __init__(self) -> None:
        super().__init__()
        self.game = GameEngine()

    def on_mount(self) -> None:
        if SAVE_PATH.exists():
            self.game.load()
        else:
            self.game.new_game()
        self.push_screen(HubScreen(self.game))


def main() -> None:
    """TUI 入口。"""
    app = WordWorldApp()
    app.run()


if __name__ == "__main__":
    main()
