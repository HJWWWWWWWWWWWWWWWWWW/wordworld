from typing import Optional

from wordworld.core.engine import GameEngine
from wordworld.config.paths import SAVE_PATH


def line() -> None:
    print("=" * 72)


def ask_number(prompt: str = "> ") -> Optional[int]:
    raw = input(prompt).strip().lower()
    if raw in {"q", "b"}:
        return None
    try:
        return int(raw)
    except ValueError:
        print("请输入有效数字，或输入 b 返回。")
        return -1


def show_result(game: GameEngine) -> None:
    if game.last_message:
        print(f"\n【行动结果】{game.last_message}")


def combat_loop(game: GameEngine) -> None:
    while game.combat is not None:
        line()
        print("【回合战斗】")
        print(game.combat_text())
        print("\n1. 普通攻击  2. 施展斗技  3. 防御  4. 使用丹药  5. 逃跑  6. 本场自动战斗")
        choice = ask_number()
        if choice is None:
            choice = 5
        if choice == 1:
            game.combat_action("attack")
        elif choice == 2:
            skills = game.combat_skills()
            if not skills:
                print("尚未掌握可用斗技。")
                continue
            print("\n选择斗技：")
            for index, skill in enumerate(skills, start=1):
                print(f"{index}. {skill['name']}（{skill['rank']}）- {skill['description']}")
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
            print("没有这个战斗行动。")
            continue
        show_result(game)


def encounter_loop(game: GameEngine) -> None:
    encounter = game.active_encounter
    if encounter is None:
        show_result(game)
        return
    line()
    print("【探索奇遇】")
    print(encounter["text"])
    options = game.encounter_options()
    for index, option in options:
        print(f"{index}. {option['text']}")
    choice = ask_number()
    if choice is None:
        game.active_encounter = None
        game.last_message = "你谨慎地离开了现场。"
        return
    game.choose_encounter_option(choice)
    show_result(game)
    if game.combat is not None:
        combat_loop(game)


def travel_menu(game: GameEngine) -> None:
    maps = game.available_maps()
    line()
    print("【区域移动】")
    for index, map_rule in enumerate(maps, start=1):
        current = "（当前）" if map_rule["id"] == game.current_map()["id"] else ""
        danger = "安全区域" if map_rule["safe_zone"] else "危险区域"
        print(
            f"{index}. {map_rule['name']}{current}｜剧情已开放｜推荐等级 {map_rule['recommend_level']}"
            f"｜{danger}｜{map_rule['description']}"
        )
    choice = ask_number()
    if choice is not None and 1 <= choice <= len(maps):
        game.travel(maps[choice - 1]["id"])


def inventory_menu(game: GameEngine) -> None:
    while True:
        line()
        print("【行囊】")
        items = game.player.get("items", [])
        if not items:
            print("行囊空空。")
            return
        for index, item_id in enumerate(items, start=1):
            rule = game.item_rules.get(item_id, {})
            print(f"{index}. {game.item_name(item_id)}｜{rule.get('description', '')}")
        print("输入编号使用道具，输入 b 返回。")
        choice = ask_number()
        if choice is None:
            return
        if 1 <= choice <= len(items):
            game.use_item(items[choice - 1])
            show_result(game)


def story_mission(game: GameEngine) -> None:
    phase = game.current_story_phase()
    if phase is None:
        print("主要目标已经全部完成。")
        return
    requirement = game.story_requirement()
    line()
    print(f"【关键目标】{phase['title']}")
    print(f"推进需求：冒险阅历 {requirement}｜当前 {game.player['adventure_points']}")
    print(f"\n背景：{phase['background']}")
    print(f"目标：{phase['objective']}")
    print(f"风险：{phase['risk']}")
    print("\n阶段子节点：")
    current = game.current_story_subnode()
    for index, subnode in enumerate(phase["subnodes"], start=1):
        if index <= game.player["story_substage"]:
            marker = "已完成"
        elif subnode is current:
            marker = "当前"
        else:
            marker = "未开始"
        print(
            f"  {index}. [{marker}] {subnode['title']}：{subnode['objective']}"
            f"（条件：{subnode['condition']}）"
        )
    if current:
        print(f"\n当前行动：完成子节点“{current['title']}”")
    else:
        print(f"\n阶段结算条件：{phase['condition']}")
    print("\n1. 尝试推进当前节点  2. 暂时离开")
    choice = ask_number()
    if choice == 1:
        game.advance_story()
        show_result(game)


def resolve_required_schedule(game: GameEngine) -> None:
    node = game.pending_schedule_node()
    if node is None:
        return
    line()
    print("【强制日程节点】")
    print(game.schedule_text(node))
    input("\n时间已到，按回车参加并结算。")
    game.resolve_schedule_node()
    show_result(game)


def show_hub(game: GameEngine) -> None:
    map_rule = game.current_map()
    line()
    phase = "夜间" if game.is_night() else "白天"
    print(f"【{game.time_text()}｜{phase}｜{map_rule['name']}】{map_rule['description']}")
    print(
        f"{game.player['name']}｜{game.realm_name()} Lv.{game.player['level']}｜"
        f"生命 {game.player['hp']}/{game.player['max_hp']}｜"
        f"斗气 {game.player['douqi']}｜体力 {game.player['stamina']}｜"
        f"冒险阅历 {game.player['adventure_points']}"
    )
    phase = game.current_story_phase()
    print(f"当前目标：{phase['title'] if phase else '所有关键目标已完成'}")
    subnode = game.current_story_subnode()
    if subnode:
        print(f"当前子节点：{subnode['title']}｜{subnode['objective']}")
    node = game.next_schedule_node()
    if node:
        goals = game.schedule_text(node).splitlines()[-1]
        print(
            f"临近日程：{game.schedule_text(node).splitlines()[0]}"
            f"｜{game.schedule_countdown_text(node)}｜{goals}"
        )
    print("\n1. 探索区域  2. 移动区域  3. 修炼  4. 切磋")
    print("5. 推进主线  6. 休息  7. 查看状态  8. 行囊  9. 保存  q. 退出")


def main() -> None:
    game = GameEngine()
    print("斗破苍穹：沉浸式回合制 RPG")
    if SAVE_PATH.exists() and input("检测到存档，是否读取？ y/n：").strip().lower() == "y":
        game.load()
    else:
        name = input("请输入主角姓名，直接回车则为萧炎：").strip()
        game.new_game(name or None)

    while True:
        if game.pending_schedule_node() is not None:
            resolve_required_schedule(game)
            continue
        show_hub(game)
        command = input("\n> ").strip().lower()
        if command == "q":
            print("旅途暂告一段落。")
            break
        if command == "1":
            game.explore()
            encounter_loop(game)
        elif command == "2":
            travel_menu(game)
            show_result(game)
        elif command == "3":
            game.cultivate()
            show_result(game)
        elif command == "4":
            game.begin_training_combat()
            combat_loop(game)
        elif command == "5":
            story_mission(game)
        elif command == "6":
            game.rest()
            show_result(game)
        elif command == "7":
            line()
            print(game.status_text())
        elif command == "8":
            inventory_menu(game)
        elif command == "9":
            game.save()
            print("进度已保存。")
        else:
            print("请输入菜单中的行动编号。")


if __name__ == "__main__":
    main()
