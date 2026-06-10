import re
import unicodedata
from typing import Optional

from wordworld.core.engine import GameEngine
from wordworld.config.paths import SAVE_PATH


_CHINESE_NUMBER_MAP = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2,
    "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}

_MAIN_COMMAND_ALIASES = {
    "人物": "1", "状态": "1", "属性": "1",
    "物品": "2", "行囊": "2", "背包": "2", "道具": "2",
    "斗技": "3", "技能": "3", "功法": "3",
    "修炼": "4",
    "探索": "5", "探索区域": "5",
    "移动": "6", "移动区域": "6", "区域移动": "6",
    "主线": "7", "推进": "7", "推进主线": "7", "剧情": "7",
    "系统": "8", "菜单": "8",
    "休息": "rest", "保存": "save", "存档": "save",
    "突破": "breakthrough", "切磋": "spar",
    "退出": "q", "离开": "q",
}

W = 72  # 界面宽度


def normalize_input(raw: str) -> str:
    return unicodedata.normalize("NFKC", raw).strip().lower()


def parse_menu_number(raw: str) -> Optional[int]:
    text = normalize_input(raw)
    if not text:
        return -1
    if text in {"q", "b"}:
        return None
    if text in _CHINESE_NUMBER_MAP:
        return _CHINESE_NUMBER_MAP[text]
    match = re.match(r"^(\d+)", text)
    if match:
        return int(match.group(1))
    return -1


def parse_main_command(raw: str) -> str:
    text = normalize_input(raw)
    if text in {"q", "b"}:
        return "q"
    number = parse_menu_number(text)
    if number is None:
        return "q"
    if number != -1:
        return str(number)
    compact_text = re.sub(r"[\s.。:：、-]+", "", text)
    return _MAIN_COMMAND_ALIASES.get(compact_text, text)


def bar(char: str = "=") -> None:
    print(char * W)


def thin() -> None:
    print("-" * W)


def ask_number(prompt: str = "> ") -> Optional[int]:
    number = parse_menu_number(input(prompt))
    if number == -1:
        print("请输入有效数字，或输入 b 返回。")
    return number


def show_result(game: GameEngine) -> None:
    if game.last_message:
        msg(game.last_message)


def press_enter() -> None:
    input("  按回车继续…")


# ═══════════════════════════════════════════════════════════════
# 战斗 & 探索
# ═══════════════════════════════════════════════════════════════

def combat_loop(game: GameEngine) -> None:
    while game.combat is not None:
        bar()
        print(game.combat_text())
        thin()
        print("  1.普通攻击  2.施展斗技  3.防御  4.使用丹药  5.逃跑  6.自动战斗")
        choice = ask_number()
        if choice is None:
            choice = 5
        if choice == 1:
            game.combat_action("attack")
        elif choice == 2:
            skills = game.combat_skills()
            if not skills:
                game.last_message = "尚未掌握可用斗技。"
                show_result(game)
                continue
            thin()
            print("  选择斗技：")
            for index, skill in enumerate(skills, start=1):
                print(f"  {index}. {skill['name']} [{skill.get('rank','')}]  "
                      f"{skill.get('description','')}")
            skill_choice = ask_number()
            if skill_choice is None or not 1 <= skill_choice <= len(skills):
                continue
            game.combat_action("skill", skills[skill_choice - 1]["id"])
        elif choice == 3:
            game.combat_action("defend")
        elif choice == 4:
            game.combat_action("item")
        elif choice == 5:
            game.combat_action("escape")
        elif choice == 6:
            game.auto_battle()
        else:
            game.last_message = "没有这个战斗行动。"
        show_result(game)


def encounter_loop(game: GameEngine) -> None:
    encounter = game.active_encounter
    if encounter is None:
        show_result(game)
        return
    bar()
    print(encounter["text"])
    options = game.encounter_options()
    print()
    for index, option in options:
        print(f"  {index}. {option['text']}")
    thin()
    choice = ask_number()
    if choice is None:
        game.leave_encounter()
        show_result(game)
        return
    game.choose_encounter_option(choice)
    show_result(game)
    if game.combat is not None:
        combat_loop(game)


def exploration_menu(game: GameEngine) -> None:
    bar()
    print(f"  当前区域：{game.current_map()['name']}  当前体力：{game.player['stamina']}")
    thin()
    actions = game.exploration_actions()
    for index, action in enumerate(actions, start=1):
        print(f"  {index}.{action['name']}（体力 -{action['cost']}）")
        print(f"    {action['description']}")
    print("  b.返回")
    choice = ask_number()
    if choice is None or not 1 <= choice <= len(actions):
        return
    game.explore(actions[choice - 1]["id"])
    encounter_loop(game)
    press_enter()


def resolve_required_schedule(game: GameEngine) -> None:
    node = game.pending_schedule_node()
    if node is None:
        return
    bar()
    print(game.schedule_text(node))
    print()
    input("  时间已到，按回车参加并结算。")
    game.resolve_schedule_node()
    show_result(game)


# ═══════════════════════════════════════════════════════════════
# 底部消息框
# ═══════════════════════════════════════════════════════════════

_msg_lines: list[str] = []


def msg(*lines: str) -> None:
    """写入消息框。"""
    _msg_lines.clear()
    _msg_lines.extend(lines)


def msg_clear() -> None:
    _msg_lines.clear()


def msg_box() -> None:
    """渲染底部消息框。"""
    thin()
    if _msg_lines:
        for line in _msg_lines:
            print(f"  {line}")
    else:
        print("  暂无消息。")


# ═══════════════════════════════════════════════════════════════
# 主界面渲染
# ═══════════════════════════════════════════════════════════════

def _fmt_left(text: str, width: int = 28) -> str:
    """中英文混排左列补齐/截断（中文占 2 宽度）。"""
    w = sum(2 if ord(c) > 127 else 1 for c in text)
    if w <= width:
        return text + ' ' * (width - w)
    result, cur = '', 0
    for c in text:
        cw = 2 if ord(c) > 127 else 1
        if cur + cw > width - 1:
            result += '…'
            break
        result += c
        cur += cw
    return result


def render_hub(game: GameEngine) -> None:
    """渲染主界面——顶层信息 + 菜单 + 消息框。"""
    map_rule = game.current_map()
    phase = game.current_story_phase()

    bar()
    # ── 顶层：左 3 行 / 右 3 行对齐 ──
    day_phase = "[夜]" if game.is_night() else "[昼]"
    safe_tag = "[安]" if map_rule["safe_zone"] else ""
    prog = game.player['progress']

    # 左列
    left_1 = f"{day_phase} {game.time_text()} {safe_tag}"
    left_2 = f"{map_rule['name']}"
    node = game.next_schedule_node()
    if node:
        parts = game.schedule_text(node).splitlines()
        left_3 = f"[日程] {parts[0]}｜{game.schedule_countdown_text(node)}"
    else:
        left_3 = ""

    # 右列
    right_1 = f"{game.player['name']}｜{game.realm_name()} Lv.{game.player['level']}"
    right_2 = (f"修炼 {prog:.1f}%｜"
               f"生命 {game.player['hp']}/{game.player['max_hp']}"
               f"  斗气 {game.player['douqi']}"
               f"  体力 {game.player['stamina']}"
               f"  阅历 {game.player['adventure_points']}")
    if phase:
        subnode = game.current_story_subnode()
        task = f"{phase['title']}"
        if subnode:
            task += f" > {subnode['title']}"
        right_3 = f"[任务] {task}"
    else:
        right_3 = "所有目标已完成"

    print(f"  {_fmt_left(left_1)}  {right_1}")
    print(f"  {_fmt_left(left_2)}  {right_2}")
    print(f"  {_fmt_left(left_3)}  {right_3}")

    # ── 中层：菜单 ──
    thin()
    print("  1.人物        2.物品        3.斗技        4.修炼")
    print("  5.探索        6.移动        7.主线        8.系统")
    print("  q.退出")

    # ── 底层：消息框 ──
    msg_box()


# ═══════════════════════════════════════════════════════════════
# 二级菜单（信息输出到消息框）
# ═══════════════════════════════════════════════════════════════

def menu_character(game: GameEngine) -> None:
    """人物详情 -> 消息框"""
    p = game.player
    lines = [
        f"[{p['name']}]  {game.realm_name()}  Lv.{p['level']}  "
        f"修炼进度 {p['progress']:.1f}%  冒险阅历 {p['adventure_points']}",
        "",
        f"生命 {p['hp']}/{p['max_hp']}  斗气 {p['douqi']}/{game.attribute_rules['douqi']['max']}"
        f"  体力 {p['stamina']}  银两 {p['silver']}",
        f"攻击 {p['atk']}  防御 {p['def']}  速度 {p['spd']}"
        f"  暴击 {p.get('crit_rate',0)}%  命中 {p.get('hit_rate',0)}%",
        f"灵魂力量 {p['soul']}  炼药术 {p['alchemy']}  声望 {p['reputation']}",
        f"经验 {p.get('exp',0)}  毒抗 {p.get('poison_resist',0)}"
        f"  背包 {len(p.get('items',[]))}/{p.get('inventory_slots',30)}",
        "",
        "—— 人物关系 ——",
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
    lines.append("")
    lines.append("按回车返回…")
    msg(*lines)
    render_hub(game)
    press_enter()


def menu_items(game: GameEngine) -> None:
    """物品 -> 消息框展示 + 使用"""
    while True:
        items = game.player.get("items", [])
        if not items:
            msg("行囊空空。", "", "按回车返回…")
            break

        lines = ["—— 行囊物品 ——", ""]
        for index, item_id in enumerate(items, start=1):
            rule = game.item_rules.get(item_id, {})
            lines.append(f"  {index}. {game.item_name(item_id)}"
                         f"（{rule.get('type', '')}）")
            lines.append(f"     {rule.get('description', '')}")
        lines.append("")
        lines.append(f"共 {len(items)} 件｜输入编号使用，b 返回")
        msg(*lines)
        render_hub(game)

        choice = ask_number()
        if choice is None:
            return
        if 1 <= choice <= len(items):
            game.use_item(items[choice - 1])
            show_result(game)
            press_enter()


def menu_skills(game: GameEngine) -> None:
    """斗技 -> 消息框"""
    skills = game.combat_skills()
    if not skills:
        msg("尚未掌握任何斗技。", "", "按回车返回…")
        render_hub(game)
        press_enter()
        return

    lines = [f"—— 已学斗技（{len(skills)} 种）——", ""]
    for skill in skills:
        lines.append(f"  {skill['name']}  [{skill.get('rank','')}]")
        lines.append(f"  类型：{skill.get('type','—')}  效果：{skill.get('effect','—')}")
        lines.append(f"  {skill.get('description','')}")
        lines.append("")
    lines.append("按回车返回…")
    msg(*lines)
    render_hub(game)
    press_enter()


def menu_cultivation(game: GameEngine) -> None:
    """修炼子菜单"""
    while True:
        pct = float(game.player.get("progress", 0))
        level = int(game.player["level"])

        lines = [
            f"修炼进度 {pct:.1f}%  "
            f"经验 {game.player.get('exp', 0)}  "
            f"斗气 {game.player['douqi']}/{game.attribute_rules['douqi']['max']}"
            f"  体力 {game.player['stamina']}",
            "",
            "  1. 修炼 —— 消耗体力，运转斗气获得经验",
        ]

        if pct >= 100.0 and level < 100:
            bp = game._breakthrough_chance_bp(level)
            ct = f"{bp/100:.2f}%" if bp < 100 else f"{bp/100:.0f}%"
            boundary = "[境界突破]" if game._is_realm_boundary(level) else "[段内突破]"
            lines.append(f"  2. {boundary} 突破 —— 冲击 {game.realm_name()} Lv.{level+1}"
                         f"（成功率 {ct}）")
        elif level >= 100:
            lines.append("  2. 突破 —— 斗帝之境，已臻化境")
        else:
            lines.append("  2. 突破 —— 进度未满，暂不可用")

        lines.append("  3. 切磋 —— 与陪练弟子对战")
        lines.append("")
        lines.append("输入编号操作，b 返回")
        msg(*lines)
        render_hub(game)

        choice = normalize_input(input("> "))
        if choice in {"b", "q"}:
            return
        if choice == "1":
            game.cultivate()
            show_result(game)
            press_enter()
        elif choice == "2":
            if pct >= 100.0 and level < 100:
                bp = game._breakthrough_chance_bp(level)
                ct = f"{bp/100:.2f}%" if bp < 100 else f"{bp/100:.0f}%"
                boundary = "[境界突破]" if game._is_realm_boundary(level) else "[段内突破]"
                msg(
                    f"{boundary} {game.realm_name()} Lv.{level} -> Lv.{level+1}",
                    f"成功率：{ct}",
                    "",
                    "1. 尝试突破  2. 暂不突破",
                )
                render_hub(game)
                sub = ask_number()
                if sub == 1:
                    game.breakthrough()
                    show_result(game)
                    press_enter()
            elif level >= 100:
                game.last_message = "你已是斗帝之境，无需突破。"
                show_result(game)
                press_enter()
            else:
                game.last_message = "修炼进度未满，还无法尝试突破。"
                show_result(game)
                press_enter()
        elif choice == "3":
            game.begin_training_combat()
            combat_loop(game)
            render_hub(game)


def menu_story(game: GameEngine) -> None:
    """主线 -> 消息框"""
    while True:
        phase = game.current_story_phase()
        if phase is None:
            msg("所有关键目标已完成。", "", "按回车返回…")
            break

        requirement = game.story_requirement()
        lines = [
            f"[主线] {phase['title']}",
            f"冒险阅历需求 {requirement} / 当前 {game.player['adventure_points']}",
            "",
            f"背景：{phase['background']}",
            f"目标：{phase['objective']}",
            f"风险：{phase['risk']}",
            "",
            "—— 子节点进度 ——",
        ]
        current = game.current_story_subnode()
        for index, subnode in enumerate(phase["subnodes"], start=1):
            if index <= game.player["story_substage"]:
                m = "[v]"
            elif subnode is current:
                m = "[>]"
            else:
                m = "[ ]"
            lines.append(f"  {m} {subnode['title']}  ({subnode['condition']})")
            lines.append(f"     {subnode['objective']}")

        if current:
            lines.append(f"\n当前行动：{current['title']}")
        else:
            lines.append(f"\n阶段结算条件：{phase['condition']}")

        node = game.next_schedule_node()
        if node:
            parts = game.schedule_text(node).splitlines()
            lines.append(f"\n[日程] {parts[0]}｜{game.schedule_countdown_text(node)}")

        lines.append("")
        lines.append("1. 尝试推进  2. 返回")
        msg(*lines)
        render_hub(game)

        choice = ask_number()
        if choice != 1:
            return
        game.advance_story()
        show_result(game)
        press_enter()


def _travel_menu(game: GameEngine) -> None:
    """移动 -> 消息框 + 选择"""
    while True:
        maps = game.available_maps()
        lines = [f"—— 已解锁区域（{len(maps)} 处）——", ""]
        for index, map_rule in enumerate(maps, start=1):
            cur = " [当前]" if map_rule["id"] == game.current_map()["id"] else ""
            safe = "[安]" if map_rule["safe_zone"] else ""
            lines.append(f"  {index}. {safe} {map_rule['name']}{cur}"
                         f"  Lv.{map_rule['recommend_level']}")
            lines.append(f"     {map_rule['description']}")
        lines.append("")
        lines.append("输入编号移动，b 返回")
        msg(*lines)
        render_hub(game)

        choice = ask_number()
        if choice is None:
            return
        if 1 <= choice <= len(maps):
            game.travel(maps[choice - 1]["id"])
            show_result(game)
            press_enter()


def menu_system(game: GameEngine) -> None:
    """系统子菜单"""
    while True:
        map_rule = game.current_map()
        can_rest = map_rule["safe_zone"]
        rest_hint = "（安全区，可以休息）" if can_rest else "（非安全区，无法休息）"
        lines = [
            f"当前 {game.time_text()}｜{map_rule['name']} {rest_hint}",
            f"生命 {game.player['hp']}/{game.player['max_hp']}"
            f"  体力 {game.player['stamina']}",
            "",
            "  1. 休息 —— 推进到次日清晨，恢复生命体力",
            "  2. 保存进度",
            "  3. 返回主菜单",
            "  4. 退出游戏",
            "",
            "输入编号操作",
        ]
        msg(*lines)
        render_hub(game)

        choice = ask_number()
        if choice == 1:
            if not can_rest:
                game.last_message = "此处危机四伏，不宜休息。请前往城镇、客栈等安全区域。"
            else:
                game.rest()
            show_result(game)
            press_enter()
        elif choice == 2:
            game.save()
            game.last_message = "进度已保存。"
            show_result(game)
            press_enter()
        elif choice == 3:
            return
        elif choice == 4:
            game.save()
            print("  进度已保存。旅途暂告一段落。")
            exit(0)


# ═══════════════════════════════════════════════════════════════
# 主循环
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    game = GameEngine()
    print("斗破苍穹：沉浸式回合制 RPG")
    if SAVE_PATH.exists() and input("检测到存档，是否读取？ y/n：").strip().lower() == "y":
        game.load()
    else:
        name = input("请输入主角姓名，直接回车则为萧炎：").strip()
        game.new_game(name or None)

    msg("欢迎来到斗气大陆。你的传奇，由此开始。")

    while True:
        if game.pending_schedule_node() is not None:
            resolve_required_schedule(game)
            continue

        render_hub(game)
        command = parse_main_command(input("> "))

        if command == "q":
            print("  旅途暂告一段落。")
            break
        elif command == "1":
            menu_character(game)
        elif command == "2":
            menu_items(game)
        elif command == "3":
            menu_skills(game)
        elif command == "4":
            menu_cultivation(game)
        elif command == "5":
            exploration_menu(game)
        elif command == "6":
            _travel_menu(game)
        elif command == "7":
            menu_story(game)
        elif command == "8":
            menu_system(game)
        else:
            msg("请输入菜单编号 1-8，或 q 退出。")


if __name__ == "__main__":
    main()
