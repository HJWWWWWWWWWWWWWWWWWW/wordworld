import json
import contextlib
import io
import re
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from wordworld.core import engine as engine_module
from wordworld.core.engine import GameEngine
from wordworld.ui import console as main


class LatestStoryTests(unittest.TestCase):
    def test_latest_workbook_story_is_loaded(self) -> None:
        game = GameEngine()

        self.assertEqual(len(game.events_list), 1904)
        self.assertEqual(game.current_event()["id"], "evt_chapter_0001")
        self.assertEqual(game.current_event()["title"], "第一章 陨落的天才")
        self.assertEqual(game.events["evt_chapter_1904"]["kind"], "ending")

    def test_story_phase_uses_goal_instead_of_chapter_text(self) -> None:
        game = GameEngine()
        game.player["level"] = 2
        game.player["training_wins"] = 1
        for _ in range(3):
            game.player["adventure_points"] = game.story_requirement()
            self.assertTrue(game.advance_story())

        self.assertEqual(game.player["story_stage"], 1)
        self.assertEqual(game.current_story_phase()["title"], "退婚与三年之约")
        self.assertGreater(game.player["reputation"], 0)

    def test_level_progression_uses_latest_attribute_rules(self) -> None:
        game = GameEngine()
        game.player["exp"] = 19

        game.apply_effects("exp:+1")

        self.assertEqual(game.player["level"], 2)
        self.assertEqual(game.player["douqi"], 8)
        self.assertEqual(game.player["atk"], 10)

    def test_story_uses_a_small_number_of_key_phases(self) -> None:
        game = GameEngine()

        self.assertEqual(len(engine_module.STORY_PHASES), 38)
        self.assertEqual(game.current_story_phase()["title"], "天才陨落")
        self.assertNotIn("斗之力，三段", game.current_story_phase()["background"])

    def test_all_core_arcs_are_covered_and_have_subnodes(self) -> None:
        phases = engine_module.STORY_PHASES
        titles = {phase["title"] for phase in phases}
        expected = {
            "退婚与三年之约",
            "炼药师大会",
            "塔戈尔沙漠与青莲地心火",
            "三年之约决战",
            "迦南学院外院",
            "陨落心炎与天焚炼气塔",
            "营救药老",
            "丹会与三千焱炎火",
            "远古遗迹",
            "古族成人礼与天墓",
            "莽荒古域与菩提古树",
            "净莲妖火",
            "药典与药族灭族战",
            "古帝洞府",
            "双帝之战",
            "五帝破空",
        }

        self.assertTrue(expected.issubset(titles))
        self.assertTrue(all(len(phase["subnodes"]) >= 2 for phase in phases))

    def test_all_21_plot_milestones_map_to_real_phase_subnodes(self) -> None:
        phases = {phase["title"]: phase for phase in engine_module.STORY_PHASES}

        self.assertEqual(len(engine_module.PLOT_MILESTONE_COVERAGE), 21)
        for milestone, (phase_title, subnode_title) in (
            engine_module.PLOT_MILESTONE_COVERAGE.items()
        ):
            self.assertIn(phase_title, phases, milestone)
            self.assertIn(
                subnode_title,
                {node["title"] for node in phases[phase_title]["subnodes"]},
                milestone,
            )

    def test_critical_story_bridges_map_to_real_phase_subnodes(self) -> None:
        phases = {phase["title"]: phase for phase in engine_module.STORY_PHASES}

        for bridge, (phase_title, subnode_title) in (
            engine_module.CRITICAL_BRIDGE_COVERAGE.items()
        ):
            self.assertIn(phase_title, phases, bridge)
            self.assertIn(
                subnode_title,
                {node["title"] for node in phases[phase_title]["subnodes"]},
                bridge,
            )

    def test_plot_milestones_follow_actual_story_sequence(self) -> None:
        phase_indexes = {
            phase["title"]: index
            for index, phase in enumerate(engine_module.STORY_PHASES)
        }
        mapped_indexes = [
            phase_indexes[engine_module.PLOT_MILESTONE_COVERAGE[name][0]]
            for name in engine_module.PLOT_MILESTONE_SEQUENCE
        ]

        self.assertEqual(mapped_indexes, sorted(mapped_indexes))

    def test_previously_misaligned_bridges_are_in_the_correct_order(self) -> None:
        titles = [phase["title"] for phase in engine_module.STORY_PHASES]

        def before(first: str, second: str) -> None:
            self.assertLess(titles.index(first), titles.index(second))

        before("退婚与三年之约", "戒中导师")
        before("塔戈尔沙漠与青莲地心火", "炼药师大会")
        before("黑角域入侵内院", "重返加玛与云岚宗大战")
        before("重返加玛与云岚宗大战", "重返黑角域")
        before("重返黑角域", "再探天焚炼气塔")
        before("再探天焚炼气塔", "进入中州")
        before("丹会与三千焱炎火", "营救药老")
        before("进入中州", "建立天府联盟")
        before("药典与药族灭族战", "古帝洞府")
        before("重返加玛与云岚宗大战", "出云帝国与毒宗之战")
        before("龙岛与龙皇血脉", "古族成人礼与天墓")
        before("古族成人礼与天墓", "玄黄要塞与西北大陆大战")
        before("玄黄要塞与西北大陆大战", "莽荒古域与菩提古树")
        before("营救药老", "远古遗迹")
        before("远古遗迹", "复活药老与重建星陨阁")
        before("建立天府联盟", "古龙岛三岛大战")
        before("古龙岛三岛大战", "血洗魂殿人殿")
        before("血洗魂殿人殿", "净莲妖火")
        before("净莲妖火", "魂殿殿主与北龙王终战")

    def test_story_order_matches_actual_chapter_anchors(self) -> None:
        phase_indexes = {
            phase["id"]: index for index, phase in enumerate(engine_module.STORY_PHASES)
        }
        anchors = engine_module.STORY_CHAPTER_ANCHORS
        ordered_ids = sorted(anchors, key=anchors.get)
        mapped_indexes = [phase_indexes[phase_id] for phase_id in ordered_ids]

        self.assertEqual(mapped_indexes, sorted(mapped_indexes))

    def test_story_requirements_never_decrease(self) -> None:
        requirements = [
            phase["requirement"] for phase in engine_module.STORY_PHASES
        ]

        self.assertEqual(requirements, sorted(requirements))

    def test_bodhi_story_grants_the_achievement_item(self) -> None:
        phase = next(
            phase
            for phase in engine_module.STORY_PHASES
            if phase["id"] == "bodhi_tree"
        )

        self.assertIn("item:+item_bodhi_heart", phase["effect"])

    def test_story_item_and_relationship_references_exist(self) -> None:
        game = GameEngine()
        item_pattern = re.compile(r"item:\+?([^,]+)")
        relation_pattern = re.compile(r"rel:([^:=,]+)")

        for phase in engine_module.STORY_PHASES:
            texts = [phase["condition"], phase["effect"]]
            for node in phase["subnodes"]:
                texts.extend([node["condition"], node["effect"]])
            for text in texts:
                for item_id in item_pattern.findall(text):
                    self.assertIn(item_id, game.item_rules, f"{phase['title']}：{item_id}")
                for reference in relation_pattern.findall(text):
                    self.assertIn(
                        reference.rstrip(">"),
                        game.relationship_index,
                        f"{phase['title']}：{reference}",
                    )

    def test_story_flag_dependencies_are_created_before_they_are_required(self) -> None:
        known_flags = set()
        flag_pattern = re.compile(r"flag:([^=,]+)=1")

        for phase in engine_module.STORY_PHASES:
            for flag in flag_pattern.findall(phase["condition"]):
                self.assertIn(flag, known_flags, f"{phase['title']} 阶段前置：{flag}")
            for node in phase["subnodes"]:
                for flag in flag_pattern.findall(node["condition"]):
                    self.assertIn(
                        flag,
                        known_flags,
                        f"{phase['title']} / {node['title']} 前置：{flag}",
                    )
                known_flags.update(flag_pattern.findall(node["effect"]))
            known_flags.update(flag_pattern.findall(phase["effect"]))

    def test_every_phase_and_subnode_can_be_resolved_without_broken_references(self) -> None:
        game = GameEngine()
        for key in game.attribute_rules:
            game.player[key] = min(10000, game.attribute_rules[key]["max"])
        game.player["reputation"] = 1000
        game.player["training_wins"] = 10
        game.player["flags"] = list(game.flag_defaults)
        for relation_id, rule in game.relationship_rules.items():
            game.player["relationships"][relation_id] = rule["max_value"]

        while game.current_story_phase() is not None:
            if game.pending_schedule_node():
                game.resolve_schedule_node()
            game.player["adventure_points"] = 100
            self.assertTrue(game.advance_story(), game.last_message)

        self.assertTrue(game.is_finished())
        self.assertIn("story_finished", game.player["flags"])

    def test_story_menu_shows_background_card_not_novel_text(self) -> None:
        output = io.StringIO()
        with patch("builtins.input", side_effect=["", "5", "2", "q"]):
            with contextlib.redirect_stdout(output):
                main.main()

        text = output.getvalue()
        self.assertIn("背景：", text)
        self.assertIn("目标：", text)
        self.assertNotIn("“斗之力，三段！”", text)


class RelationshipTests(unittest.TestCase):
    def test_new_game_uses_latest_relationship_initial_values(self) -> None:
        game = GameEngine()

        self.assertEqual(game.relation_value("npc_xun_er"), 60)
        self.assertEqual(game.relation_value("faction_hun>faction_xiao"), -100)

    def test_relation_change_is_clamped_and_supports_v4_syntax(self) -> None:
        game = GameEngine()

        game.apply_effects("rel:npc_xun_er:+100")

        self.assertEqual(game.relation_value("npc_xun_er"), 100)
        self.assertTrue(game.check_conditions("rel:npc_xun_er>=90"))
        self.assertEqual(game.relation_stage("npc_xun_er"), "相守")

    def test_on_reach_effect_only_triggers_once(self) -> None:
        game = GameEngine()

        game.apply_effects("rel:npc_xun_er:+30")
        game.apply_effects("rel:npc_xun_er:-1")
        game.apply_effects("rel:npc_xun_er:+1")

        self.assertIn("xuner_bond", game.player["flags"])
        self.assertEqual(len(game.player["relationship_triggers"]), 1)

    def test_load_migrates_old_save_to_latest_story(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "save.json"
            save_path.write_text(
                json.dumps(
                    {
                        "name": "旧存档角色",
                        "attack": 12,
                        "gold": 33,
                        "current_event": "start",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with patch("wordworld.core.engine.SAVE_PATH", save_path):
                loaded = GameEngine()
                self.assertTrue(loaded.load())

            self.assertEqual(loaded.player["name"], "旧存档角色")
            self.assertEqual(loaded.player["atk"], 12)
            self.assertEqual(loaded.player["silver"], 33)
            self.assertEqual(loaded.player["current_event"], "evt_chapter_0001")

    def test_load_keeps_the_same_story_phase_after_new_phases_are_inserted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "save.json"
            save_path.write_text(
                json.dumps({"story_stage": 20}, ensure_ascii=False),
                encoding="utf-8",
            )

            with patch("wordworld.core.engine.SAVE_PATH", save_path):
                loaded = GameEngine()
                self.assertTrue(loaded.load())

            self.assertEqual(loaded.player["story_phase_id"], "demon_flame")
            self.assertEqual(loaded.current_story_phase()["id"], "demon_flame")

    def test_save_records_stable_story_phase_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "save.json"
            game = GameEngine()
            game.player["story_stage"] = next(
                index
                for index, phase in enumerate(engine_module.STORY_PHASES)
                if phase["id"] == "demon_flame"
            )

            with patch("wordworld.core.engine.SAVE_PATH", save_path):
                game.save()

            saved = json.loads(save_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["story_phase_id"], "demon_flame")


class RpgLoopTests(unittest.TestCase):
    def test_workbook_rpg_configs_are_loaded(self) -> None:
        game = GameEngine()

        self.assertGreaterEqual(len(game.maps), 50)
        self.assertGreaterEqual(len(game.encounters), 70)
        self.assertGreaterEqual(len(game.enemies), 20)
        self.assertIn("skill_bajibang", game.skills)

    def test_exploration_spends_stamina_and_grants_adventure_progress(self) -> None:
        game = GameEngine()
        stamina = game.player["stamina"]

        encounter = game.explore()
        self.assertIsNotNone(encounter)
        self.assertLess(game.player["stamina"], stamina)
        self.assertTrue(game.choose_encounter_option(1))
        self.assertGreaterEqual(game.player["adventure_points"], 1)

    def test_turn_based_training_combat_can_be_won(self) -> None:
        game = GameEngine()
        game.player["atk"] = 100
        game.begin_training_combat()

        result = game.combat_action("attack")

        self.assertEqual(result, "won")
        self.assertIsNone(game.combat)
        self.assertGreaterEqual(game.player["adventure_points"], 2)

    def test_story_requires_adventure_progress(self) -> None:
        game = GameEngine()

        self.assertFalse(game.advance_story())
        game.player["level"] = 2
        game.player["adventure_points"] = game.story_requirement()
        self.assertTrue(game.advance_story())
        self.assertEqual(game.current_story_phase()["id"], "fallen_genius")
        self.assertEqual(game.current_story_subnode()["title"], "族内试炼翻身")

    def test_story_milestone_unlocks_world_state(self) -> None:
        game = GameEngine()
        game.player["story_stage"] = 1
        game.player["story_substage"] = 2
        game.player["reputation"] = 5
        game.player["adventure_points"] = game.story_requirement()
        self.assertTrue(game.advance_story())

        self.assertIn("three_year_pact", game.player["flags"])
        self.assertNotIn("云岚宗", [map_rule["name"] for map_rule in game.available_maps()])

    def test_maps_unlock_by_story_stage_not_level(self) -> None:
        game = GameEngine()
        game.player["level"] = 99
        game.player["alchemy"] = 99
        game.player["flags"].extend(["three_year_pact", "joined_canaan"])

        self.assertFalse(game.is_map_unlocked("map_canaan"))
        self.assertFalse(game.travel("map_canaan"))
        self.assertIn("推进至“迦南学院外院”开放", game.last_message)

        game.player["story_stage"] = next(
            index
            for index, phase in enumerate(engine_module.STORY_PHASES)
            if phase["id"] == "canaan_outer"
        )

        self.assertTrue(game.is_map_unlocked("map_canaan"))

    def test_every_map_has_a_story_unlock_stage(self) -> None:
        game = GameEngine()
        phase_ids = {phase["id"] for phase in engine_module.STORY_PHASES}

        self.assertEqual(set(game.maps), set(engine_module.MAP_STORY_UNLOCKS))
        self.assertTrue(set(engine_module.MAP_STORY_UNLOCKS.values()).issubset(phase_ids))

    def test_cultivation_before_yao_lao_wakes_only_gains_soul_and_adventure(self) -> None:
        game = GameEngine()
        initial = {
            key: game.player[key]
            for key in ("level", "exp", "douqi", "soul", "adventure_points")
        }

        self.assertTrue(game.cultivate())

        self.assertEqual(game.player["level"], initial["level"])
        self.assertEqual(game.player["exp"], initial["exp"])
        self.assertEqual(game.player["douqi"], initial["douqi"])
        self.assertGreater(game.player["soul"], initial["soul"])
        self.assertEqual(game.player["adventure_points"], initial["adventure_points"] + 1)

    def test_cultivation_after_yao_lao_wakes_can_gain_exp_and_douqi(self) -> None:
        game = GameEngine()
        game.player["flags"].append("ring_awakened")
        initial_exp = game.player["exp"]
        initial_douqi = game.player["douqi"]

        self.assertTrue(game.cultivate())

        self.assertGreater(game.player["exp"], initial_exp)
        self.assertGreater(game.player["douqi"], initial_douqi)

    def test_starting_skill_is_usable_in_combat(self) -> None:
        game = GameEngine()
        game.begin_training_combat()

        result = game.combat_action("skill", "skill_bajibang")

        self.assertIn(result, {"continue", "won"})
        self.assertLess(game.player["douqi"], 3)

    def test_auto_battle_does_not_use_finisher_on_healthy_enemy(self) -> None:
        game = GameEngine()
        game.player["known_skills"].append("skill_buddha_lotus")
        game.player["douqi"] = 100
        game.begin_training_combat()

        action, skill_id = game.choose_auto_combat_action()

        self.assertNotEqual(skill_id, "skill_buddha_lotus")
        self.assertIn(action, {"attack", "skill"})

    def test_auto_battle_uses_finisher_and_critical_on_low_health_enemy(self) -> None:
        game = GameEngine()
        game.player["known_skills"] = ["skill_buddha_lotus"]
        game.player["douqi"] = 100
        game.begin_training_combat()
        game.combat["max_hp"] = 200
        game.combat["hp"] = 55
        game.combat["def"] = 20

        action, skill_id = game.choose_auto_combat_action()
        result = game.combat_action(action, skill_id)

        self.assertEqual((action, skill_id), ("skill", "skill_buddha_lotus"))
        self.assertIn(result, {"continue", "won"})
        self.assertIn("触发暴击", game.last_message)

    def test_auto_battle_uses_healing_item_when_health_is_low(self) -> None:
        game = GameEngine()
        game.player["items"].append("item_elixir")
        game.player["hp"] = 5
        game.begin_training_combat()

        action, item_id = game.choose_auto_combat_action()

        self.assertEqual((action, item_id), ("item", "item_elixir"))

    def test_combat_healing_and_damage_do_not_overflow(self) -> None:
        game = GameEngine()
        game.player["items"].append("item_spirit_restoring_pill")
        game.player["hp"] = game.player["max_hp"] - 1
        game.begin_training_combat()

        game.combat_action("item", "item_spirit_restoring_pill")
        self.assertLessEqual(game.player["hp"], game.player["max_hp"])
        self.assertIn("恢复 1 点生命", game.last_message)

        game.player["atk"] = 1000
        game.combat["hp"] = 2
        result = game.combat_action("attack")
        self.assertEqual(result, "won")
        self.assertIn("造成 2 点伤害", game.last_message)

    def test_auto_battle_runs_until_the_battle_ends(self) -> None:
        game = GameEngine()
        game.player["atk"] = 100
        game.begin_training_combat()

        result = game.auto_battle()

        self.assertEqual(result, "won")
        self.assertIsNone(game.combat)
        self.assertIn("自动战斗开始", game.last_message)


class TimeScheduleTests(unittest.TestCase):
    def test_actions_advance_day_period_and_rest_reaches_morning(self) -> None:
        game = GameEngine()

        self.assertEqual(game.time_text(), "第1日 清晨")
        game.cultivate()
        self.assertEqual(game.time_text(), "第1日 午后")
        game.rest()
        self.assertEqual(game.time_text(), "第2日 清晨")

    def test_trial_node_blocks_actions_and_applies_failure(self) -> None:
        game = GameEngine()
        old_reputation = game.player["reputation"]

        game.advance_time(8)

        self.assertEqual(game.pending_schedule_node()["id"], "xiao_clan_trial")
        self.assertFalse(game.cultivate())
        self.assertFalse(game.resolve_schedule_node())
        self.assertLess(game.player["reputation"], old_reputation)

    def test_trial_success_rewards_preparation(self) -> None:
        game = GameEngine()
        game.player["level"] = 2
        game.player["training_wins"] = 1

        game.advance_time(8)

        self.assertTrue(game.resolve_schedule_node())
        self.assertIn("item_elixir", game.player["items"])
        self.assertGreater(game.player["reputation"], 0)

    def test_night_exploration_costs_more_and_rewards_more_progress(self) -> None:
        game = GameEngine()
        game.player["time_period"] = 2
        stamina = game.player["stamina"]

        game.explore()
        game.choose_encounter_option(game.encounter_options()[0][0])

        self.assertEqual(stamina - game.player["stamina"], 5)
        self.assertGreaterEqual(game.player["adventure_points"], 2)


class ConsoleInputTests(unittest.TestCase):
    def test_menu_number_accepts_full_width_and_menu_text(self) -> None:
        self.assertEqual(main.parse_menu_number("１"), 1)
        self.assertEqual(main.parse_menu_number("2. 移动区域"), 2)
        self.assertEqual(main.parse_menu_number("三"), 3)

    def test_main_command_accepts_action_names(self) -> None:
        self.assertEqual(main.parse_main_command("探索区域"), "1")
        self.assertEqual(main.parse_main_command("查看 状态"), "7")
        self.assertEqual(main.parse_main_command("存档"), "9")
        self.assertEqual(main.parse_main_command("退出"), "q")


if __name__ == "__main__":
    unittest.main()
