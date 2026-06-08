import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from wordworld.data.workbook import load_game_data
from wordworld.config.paths import SAVE_PATH, WORKBOOK_PATH


LEGACY_STAT_ALIASES = {
    "attack": "atk",
    "defense": "def",
    "gold": "silver",
    "neili": "douqi",
}

COMPARISON_PATTERN = re.compile(r"^(.+?)(>=|<=|==|!=|>|<)(-?\d+)$")
RELATION_EFFECT_PATTERN = re.compile(r"^rel:([^:=]+):([+-]\d+)$")
RELATION_SET_PATTERN = re.compile(r"^rel:([^:=]+)=(-?\d+)$")
ON_REACH_PATTERN = re.compile(r"^(rel:.+?(?:>=|<=|==|!=|>|<)-?\d+):(.*)$")
EXP_FORMULA_PATTERN = re.compile(r"^level\*(\d+)$")

LEVEL_SKILL_MILESTONES = {
    10: "skill_alchemy",
    20: "skill_wind_thunder",
    30: "skill_flame",
    40: "skill_healing",
    50: "skill_gold_flame",
}

TIME_PERIODS = ["清晨", "午后", "傍晚", "深夜"]

# 自动战斗中的终结类斗技只会在敌方生命不高于该比例时使用。
FINISHER_SKILLS = {
    "skill_buddha_lotus": 0.30,
    "skill_great_silence_finger": 0.30,
    "skill_huangquan_finger": 0.30,
    "skill_annihilate_sky_seal": 0.30,
}

# 上一版存档只保存数字阶段。该列表用于把旧数字位置迁移到稳定阶段 ID。
LEGACY_STORY_PHASE_IDS_V2 = [
    "fallen_genius", "three_year_pact", "ring_awakening", "wutan_growth",
    "mountain_training", "desert_flame", "alchemy_conference", "yunlan_duel",
    "canaan_outer", "canaan_inner", "fallen_heart", "black_corner_war",
    "yunlan_war", "zhongzhou_arrival", "dan_meeting_flame", "save_mentor",
    "ancient_ruins", "gu_clan_tomb", "bodhi_tree", "tianfu_alliance",
    "demon_flame", "medicine_ceremony", "ancient_clan_war", "ancient_emperor",
    "final_war", "five_emperors",
]


def _story_phase(
    phase_id: str,
    title: str,
    background: str,
    objective: str,
    risk: str,
    requirement: int,
    condition: str,
    effect: str,
    subnodes: List[Tuple[str, str, str, str]],
) -> Dict[str, Any]:
    return {
        "id": phase_id,
        "title": title,
        "background": background,
        "objective": objective,
        "risk": risk,
        "requirement": requirement,
        "condition": condition,
        "effect": effect,
        "subnodes": [
            {
                "title": node_title,
                "objective": node_objective,
                "condition": node_condition,
                "effect": node_effect,
            }
            for node_title, node_objective, node_condition, node_effect in subnodes
        ],
    }


# 主线必须按因果顺序显式排列，禁止再通过列表插入拼接时间线。
STORY_PHASES = [
    _story_phase("fallen_genius", "天才陨落", "斗气持续衰退，族内试炼迫近。", "稳住根基并重新证明自己。", "失败会失去族内资源与信任。", 2, "level>=2", "reputation:+3,rel:npc_xiao_zhan:+3", [
        ("查明斗气衰退", "观察身体与戒指的异常。", "soul>=5", "soul:+1"),
        ("族内试炼翻身", "在演武场重新证明实力。", "training_wins>=1", "reputation:+3"),
    ]),
    _story_phase("three_year_pact", "退婚与三年之约", "云岚宗登门退婚，萧家尊严受到挑战。", "维护家族尊严并立下三年之约。", "软弱回应会让萧家声望受损。", 3, "reputation>=5", "flag:three_year_pact=1,rel:npc_nalan_yanran:-10", [
        ("应对退婚", "在大厅冲突中维护萧家尊严。", "reputation>=5", "rel:npc_xiao_zhan:+5"),
        ("立下三年之约", "公开承担未来决战的责任。", "level>=3", "flag:three_year_pact=1,reputation:+5"),
    ]),
    _story_phase("ring_awakening", "戒中导师", "退婚风波后，戒中的神秘灵魂终于现身。", "建立师徒关系并获得成长道路。", "无法取得信任会失去关键指导。", 3, "soul>=6,flag:three_year_pact=1", "flag:ring_awakened=1,rel:npc_yao_lao:+10,douqi:+5", [
        ("药老现身", "确认斗气流失的真正原因。", "soul>=6", "flag:ring_awakened=1"),
        ("学习炼药与焚决", "建立师徒信任并选择成长路线。", "adventure_points>=3", "rel:npc_yao_lao:+10,alchemy:+3"),
    ]),
    _story_phase("wutan_growth", "乌坦城成长", "离开家族前，你需要功法、资金与实战经验。", "解决坊市冲突并完成离家准备。", "基础不足会使后续历练举步维艰。", 4, "level>=4", "flag:left_wutan=1,reputation:+5", [
        ("经营坊市资源", "通过炼药、交易或探索筹集资源。", "silver>=20", "alchemy:+2"),
        ("解决家族冲突", "保护萧家利益并赢得成人认可。", "training_wins>=2", "reputation:+5"),
        ("告别家族", "准备独自踏上历练之路。", "adventure_points>=5", "flag:left_wutan=1"),
    ]),
    _story_phase("mountain_training", "魔兽山脉历练", "魔兽山脉中有药材、强敌与新的伙伴。", "完成独立生存训练并穿越山脉。", "缺乏实战会无法深入沙漠。", 5, "level>=6,flag:left_wutan=1", "rel:npc_xiao_yixian:+10,exp:+50", [
        ("青山镇立足", "建立补给点并了解山脉情报。", "adventure_points>=6", "reputation:+3"),
        ("结识小医仙", "共同探索遗迹并建立信任。", "reputation>=10", "rel:npc_xiao_yixian:+10"),
        ("面对厄难毒体", "帮助伙伴控制危险体质。", "rel:npc_xiao_yixian>=35", "flag:poison_companion=1"),
    ]),
    _story_phase("desert_flame", "塔戈尔沙漠与青莲地心火", "异火线索指向蛇人族领地。", "深入沙漠并夺取青莲地心火。", "异火争夺失败会严重拖慢成长。", 6, "level>=10", "item:+item_green_lotus_flame,rel:npc_cai_lin:+15,douqi:+20", [
        ("保护青鳞", "解决石漠城危机并保护青鳞。", "reputation>=10", "rel:npc_qing_lin:+10"),
        ("寻找青莲地心火", "追踪地穴中的异火线索。", "soul>=12", "flag:green_lotus_found=1"),
        ("美杜莎神殿争夺", "在多方冲突中取得异火并保留转圜余地。", "level>=10,rel:npc_cai_lin>=-40", "rel:npc_cai_lin:+10"),
    ]),
    _story_phase("alchemy_conference", "炼药师大会", "返回加玛帝国后，炼药师大会成为积累声望的关键机会。", "通过考核、解决丹王势力威胁并夺得大会认可。", "失败会失去帝都盟友与公开声望。", 7, "alchemy>=12,soul>=12", "reputation:+10,alchemy:+5,item:+item_elixir", [
        ("取得炼药师资格", "通过公会测试并获得参赛身份。", "alchemy>=10", "reputation:+3"),
        ("处理纳兰家烙毒", "以异火与炼药能力换取关键人脉。", "soul>=12", "reputation:+4"),
        ("赢得炼药师大会", "在大会决赛中挫败敌对炼药师。", "alchemy>=12", "alchemy:+5,reputation:+8"),
    ]),
    _story_phase("yunlan_duel", "三年之约决战", "约定期限已至，你必须登上云岚宗。", "击败纳兰嫣然并从宗门追击中脱身。", "失败会让三年努力失去意义。", 8, "level>=15,flag:three_year_pact=1", "flag:rival_resolved=1,flag:yunlan_hostile=1,reputation:+20", [
        ("登上云岚宗", "突破宗门压力并抵达决战场。", "level>=15", "reputation:+5"),
        ("击败纳兰嫣然", "兑现三年之约。", "flag:three_year_pact=1", "rel:npc_nalan_yanran:+20,reputation:+10"),
        ("再上云岚宗击杀云棱", "处理萧家遇袭的直接责任人。", "reputation>=20", "flag:yunleng_defeated=1"),
        ("逃离加玛帝国", "在云山追击下保全自己并前往黑角域。", "soul>=15", "flag:first_yunlan_escape=1"),
    ]),
    _story_phase("canaan_outer", "迦南学院外院", "离开加玛帝国后，你终于前往迦南学院。", "完成入院与外院成长，为进入内院做准备。", "无法进入内院会错失核心修炼资源。", 9, "level>=18", "flag:joined_canaan=1,reputation:+8", [
        ("穿越黑角域", "通过黑域大平原与拍卖争夺抵达学院。", "adventure_points>=10,flag:first_yunlan_escape=1", "flag:first_black_corner_crossing=1"),
        ("抵达迦南学院", "完成迟到后的入院考验。", "level>=18", "flag:joined_canaan=1"),
        ("建立新生队伍", "与同伴形成可靠的小队。", "reputation>=25", "reputation:+5"),
        ("通过内院选拔赛", "赢得进入内院的资格。", "training_wins>=3", "flag:entered_inner_academy=1"),
    ]),
    _story_phase("canaan_inner", "内院磐门与强榜", "内院资源竞争激烈，新生必须抱团立足。", "建立磐门并在强榜大赛中取得资格。", "没有自己的势力将持续受到压制。", 10, "flag:entered_inner_academy=1,reputation>=25", "flag:pan_gate_founded=1,reputation:+10", [
        ("建立磐门", "团结新生并建立稳定据点。", "reputation>=25", "flag:pan_gate_founded=1"),
        ("结识紫研", "通过内院任务与紫研建立信任。", "adventure_points>=12", "rel:npc_ziyan:+10"),
        ("挑战强榜大赛", "取得进入天焚炼气塔核心区域的资格。", "training_wins>=4", "flag:strong_rank_won=1"),
    ]),
    _story_phase("fallen_heart", "陨落心炎与天焚炼气塔", "天焚炼气塔异动，陨落心炎即将失控。", "守住内院并收服陨落心炎。", "异火失控会摧毁内院。", 11, "level>=25,flag:strong_rank_won=1", "item:+item_fallen_heart_flame,douqi:+30", [
        ("调查炼气塔异动", "确认陨落心炎暴动征兆。", "soul>=20", "flag:fallen_heart_unstable=1"),
        ("深入塔底", "在封印崩溃前抵达异火本体。", "level>=25", "exp:+80"),
        ("收服陨落心炎", "承受异火炼体并返回内院。", "flag:fallen_heart_unstable=1", "item:+item_fallen_heart_flame"),
    ]),
    _story_phase("black_corner_war", "黑角域入侵内院", "韩枫联合黑角域势力进攻内院，试图夺走陨落心炎。", "守住内院并击退韩枫与黑盟。", "学院失守会让异火和盟友落入韩枫手中。", 12, "level>=28,flag:pan_gate_founded=1", "flag:han_feng_escaped=1,flag:soul_hall_exposed=1,reputation:+15", [
        ("集结学院盟友", "组织内院力量抵挡黑盟入侵。", "reputation>=35", "reputation:+5"),
        ("击退韩枫与黑盟", "保住学院并摧毁韩枫肉身。", "level>=28", "flag:han_feng_hostile=1"),
        ("发现魂殿接应", "确认韩枫灵魂被魂殿救走。", "soul>=25", "flag:han_feng_escaped=1,flag:soul_hall_exposed=1"),
    ]),
    _story_phase("yunlan_war", "重返加玛与云岚宗大战", "父亲失踪、萧家遭难，线索指向云岚宗与魂殿。", "救援萧家、击败云山并重建故土秩序。", "拖延会让萧家与盟友被逐个击破。", 13, "level>=30,flag:first_yunlan_escape=1", "flag:yan_alliance_founded=1,reputation:+20", [
        ("追查父亲失踪", "确认萧家危机与魂殿介入。", "reputation>=35", "flag:xiao_family_crisis=1"),
        ("击败云山，药老被掳", "终结云岚宗威胁，但魂殿护法趁乱掳走药老。", "level>=30,flag:yunlan_hostile=1", "flag:yunlan_defeated=1,flag:yao_lao_captured=1"),
        ("建立炎盟", "联合加玛帝国盟友保护萧家。", "reputation>=45", "flag:yan_alliance_founded=1"),
    ]),
    _story_phase("poison_sect_war", "出云帝国与毒宗之战", "炎盟刚刚建立，毒宗、金雁宗与慕兰谷便入侵加玛帝国。", "守住炎盟、重逢小医仙并解决厄难毒体危机。", "联盟初战失败会让故土再次陷入战乱。", 14, "level>=33,flag:yan_alliance_founded=1", "flag:northwest_stabilized=1,rel:npc_xiao_yixian:+15,reputation:+15", [
        ("守卫加玛帝国", "带领炎盟击退三宗联军。", "reputation>=50", "flag:yan_alliance_defended=1"),
        ("重逢毒宗宗主", "确认小医仙身份并避免双方死战。", "rel:npc_xiao_yixian>=40", "rel:npc_xiao_yixian:+10"),
        ("暂时封印厄难毒体", "寻找毒丹之法，暂时压制小医仙的毒体。", "alchemy>=20,flag:poison_companion=1", "flag:poison_body_sealed=1"),
    ]),
    _story_phase("return_black_corner", "重返黑角域", "魂殿线索与韩枫逃亡方向都指向黑角域。", "清算魔炎谷、擒获韩枫并取得魂殿情报。", "缺少情报便无法定位药老。", 15, "level>=35,flag:han_feng_escaped=1", "flag:han_feng_captured=1,flag:mentor_prison_known=1,reputation:+15", [
        ("清算魔炎谷", "摧毁黑角域中敌对势力的核心据点。", "reputation>=55", "flag:demon_flame_valley_defeated=1"),
        ("擒获韩枫灵魂", "击败韩枫与魂殿接应者。", "level>=35,flag:han_feng_escaped=1", "flag:han_feng_captured=1"),
        ("取得药老关押情报", "从韩枫与魂殿护法处取得关键线索。", "soul>=30", "flag:mentor_prison_known=1"),
    ]),
    _story_phase("revisit_tower", "再探天焚炼气塔", "黑角域清算后，炼气塔底的岩浆世界仍隐藏着异火和古帝线索。", "再入塔底、救出天火尊者并发现古帝洞府线索。", "忽略塔底秘密会让终局线索断裂。", 16, "level>=36,flag:han_feng_captured=1", "flag:ancient_emperor_clue_found=1,reputation:+8", [
        ("返回迦南学院", "安置萧门与磐门并准备再入塔底。", "reputation>=58", "reputation:+3"),
        ("救出天火尊者", "深入岩浆世界并帮助残魂脱困。", "soul>=32", "flag:tianhuo_rescued=1"),
        ("发现古帝玉线索", "确认岩浆世界与古帝洞府存在联系。", "flag:tianhuo_rescued=1", "flag:ancient_emperor_clue_found=1"),
    ]),
    _story_phase("zhongzhou_arrival", "进入中州", "药老被魂殿掳走，新的线索指向强者云集的中州。", "在中州立足、寻找星陨阁并追查魂殿。", "没有据点与情报便无法展开营救。", 16, "level>=36,flag:mentor_prison_known=1", "flag:star_pavilion_found=1,reputation:+15", [
        ("穿越空间虫洞", "抵达中州并适应新的强敌环境。", "level>=35", "exp:+100"),
        ("四方阁立威", "通过风雷阁冲突建立中州声望。", "training_wins>=5", "reputation:+10"),
        ("找到风尊者与星陨阁", "联系药老旧友并建立营救据点。", "reputation>=50", "flag:star_pavilion_found=1,rel:npc_feng_zunzhe:+15"),
    ]),
    _story_phase("ye_ice_valley", "叶城与冰河谷", "中州丹塔选拔将近，小医仙的厄难毒体也引来冰河谷追杀。", "帮助叶家取得资格，并彻底解决厄难毒体。", "毒体失控会危及小医仙与周围所有人。", 17, "level>=38,flag:poison_body_sealed=1", "flag:poison_body_resolved=1,reputation:+12", [
        ("帮助叶家通过考核", "取得参加丹会的正式资格。", "alchemy>=28", "flag:dan_meeting_qualified=1"),
        ("迎战冰河谷", "保护小医仙并击退冰河谷追兵。", "level>=38,rel:npc_xiao_yixian>=50", "reputation:+5"),
        ("凝聚毒丹", "彻底控制厄难毒体而非继续封印。", "alchemy>=30,flag:poison_body_sealed=1", "flag:poison_body_resolved=1"),
    ]),
    _story_phase("dan_meeting_flame", "丹会与三千焱炎火", "丹塔大会能提供声望、盟友与接近三千焱炎火的机会。", "赢得丹会并收服星域异火。", "失败会失去营救药老的重要支援。", 18, "level>=40,alchemy>=30,soul>=30,flag:dan_meeting_qualified=1", "item:+item_three_thousand_flame,alchemy:+15,reputation:+20", [
        ("通过丹会选拔", "证明炼药与灵魂能力。", "alchemy>=30,soul>=30", "reputation:+10"),
        ("赢得丹会", "在顶尖炼药师竞争中夺得名次。", "alchemy>=35", "flag:dan_meeting_won=1"),
        ("进入星域收服异火", "处理魂殿干扰并取得三千焱炎火。", "level>=40,flag:dan_meeting_won=1", "item:+item_three_thousand_flame"),
    ]),
    _story_phase("save_mentor", "营救药老", "魂殿囚禁着药老，营救时机终于成熟。", "突袭亡魂山脉并救回药老灵魂。", "失败将失去导师和对抗魂殿的核心盟友。", 19, "level>=45,flag:star_pavilion_found=1,rel:npc_yao_lao>=60", "flag:yao_lao_rescued=1,rel:npc_yao_lao:+20,reputation:+20", [
        ("突袭魂殿分殿", "依靠丹塔与星陨阁情报展开营救。", "reputation>=60", "flag:yao_lao_rescued=1"),
        ("撤回星陨阁", "保护重伤的药老灵魂撤离。", "soul>=40,flag:yao_lao_rescued=1", "flag:mentor_soul_secured=1"),
        ("准备复活材料", "确认重塑躯体仍缺少斗圣骸骨。", "alchemy>=40", "flag:saint_bones_needed=1"),
    ]),
    _story_phase("ancient_ruins", "远古遗迹", "远古遗迹现世，其中的斗圣骸骨是复活药老的关键。", "探索遗迹、取得龙凰本源果与斗圣骸骨。", "无法取得骸骨便不能为药老重塑躯体。", 20, "level>=48,soul>=35,flag:saint_bones_needed=1", "item:+item_earth_skill,flag:saint_bones_acquired=1,soul:+10", [
        ("定位遗迹入口", "识别空间波动并准备探索队伍。", "soul>=35", "exp:+50"),
        ("重逢青鳞", "在遗迹中与青鳞会合并应对远古天蛇力量。", "rel:npc_qing_lin>=35", "rel:npc_qing_lin:+10"),
        ("取得龙凰本源果", "为紫研后续的龙皇血脉觉醒准备机缘。", "level>=48", "flag:dragon_phoenix_fruit_acquired=1"),
        ("夺取斗圣骸骨", "击退争夺者并带回重塑躯体的核心材料。", "reputation>=70", "item:+item_earth_skill,flag:saint_bones_acquired=1"),
    ]),
    _story_phase("revive_mentor", "复活药老与重建星陨阁", "斗圣骸骨已经到手，可以为药老重塑躯体。", "复活药老并将星陨阁建设为长期据点。", "拖延会让魂殿再次找到虚弱的药老。", 21, "alchemy>=42,flag:saint_bones_acquired=1,flag:mentor_soul_secured=1", "flag:yao_lao_revived=1,flag:star_pavilion_rebuilt=1,reputation:+20", [
        ("炼制斗圣躯体", "使用斗圣骸骨与异火完成躯体炼制。", "alchemy>=42,flag:saint_bones_acquired=1", "flag:saint_body_refined=1"),
        ("药老复活", "让药老灵魂与新躯体完成融合。", "soul>=45,flag:saint_body_refined=1", "flag:yao_lao_revived=1,rel:npc_yao_lao:+15"),
        ("重建星陨阁", "将临时营救据点发展为长期势力。", "reputation>=75", "flag:star_pavilion_rebuilt=1"),
    ]),
    _story_phase("flower_sect", "花宗与云韵传承", "花宗传承纷争将云韵卷入危机，也影响中州盟友格局。", "帮助云韵取得花宗传承并争取花宗支持。", "花宗落入敌对势力会削弱未来联盟。", 22, "level>=50,flag:star_pavilion_rebuilt=1", "flag:flower_sect_allied=1,rel:npc_yun_yun:+15,reputation:+10", [
        ("赶往花宗", "响应云韵求援并查明宗主传承争议。", "reputation>=75", "rel:npc_yun_yun:+5"),
        ("击败花宗敌手", "保护云韵完成传承。", "level>=50", "exp:+120"),
        ("争取花宗支持", "让花宗成为星陨阁的盟友。", "rel:npc_yun_yun>=30", "flag:flower_sect_allied=1"),
    ]),
    _story_phase("dragon_island_legacy", "龙岛与龙皇血脉", "龙凰本源果被送往分裂的古龙岛，紫研需要完成血脉觉醒。", "帮助紫研觉醒龙皇血脉并稳住东龙岛。", "紫研失败会让太虚古龙族继续分裂。", 23, "level>=50,rel:npc_ziyan>=35,flag:dragon_phoenix_fruit_acquired=1", "flag:dragon_emperor_awakened=1,rel:npc_ziyan:+15,reputation:+10", [
        ("抵达东龙岛", "穿越虚空并确认古龙族分裂局势。", "soul>=40", "flag:east_dragon_island_reached=1"),
        ("守护龙凰晶层", "在三岛压力下保护紫研完成炼化。", "level>=50", "rel:npc_ziyan:+10"),
        ("见证龙皇觉醒", "帮助紫研继承龙皇血脉。", "rel:npc_ziyan>=40", "flag:dragon_emperor_awakened=1"),
    ]),
    _story_phase("gu_clan_tomb", "古族成人礼与天墓", "古族成人礼与天墓开启提供了接触萧族先祖的机会。", "赢得古族认可并获得萧玄传承。", "失败会削弱古族联盟与血脉成长。", 24, "level>=52,rel:npc_xun_er>=60", "rel:npc_gu_yuan:+20,douqi:+50", [
        ("参加古族成人礼", "在远古种族面前证明实力。", "reputation>=75", "rel:npc_gu_yuan:+10"),
        ("进入天墓", "与同伴穿越能量风暴。", "level>=50", "exp:+150"),
        ("接受萧玄传承", "恢复萧族血脉并理解先祖使命。", "soul>=45", "flag:xiao_bloodline_awakened=1,douqi:+30"),
    ]),
    _story_phase("northwest_fortress_war", "玄黄要塞与西北大陆大战", "魂殿联军进攻西北大陆，炎盟与萧家在玄黄要塞陷入苦战。", "返回故土、守住要塞并稳定西北联盟。", "故土失守会让天府联盟失去根基。", 25, "level>=54,flag:yan_alliance_founded=1", "flag:northwest_front_secured=1,reputation:+18", [
        ("赶回玄黄要塞", "响应炎盟求援并集结故土盟友。", "reputation>=82", "flag:northwest_reinforced=1"),
        ("守卫萧家与炎盟", "击退魂殿联军对西北大陆的进攻。", "level>=54", "reputation:+10"),
        ("稳定西北战线", "重新整合加玛、出云与蛇人族力量。", "flag:northwest_stabilized=1", "flag:northwest_front_secured=1"),
    ]),
    _story_phase("bodhi_tree", "莽荒古域与菩提古树", "菩提古树现世，进入莽荒古域还需面对兽潮与各方争夺。", "穿越莽荒古域、突破幻境并取得菩提心。", "心境不足会永远迷失。", 25, "level>=55,soul>=45", "item:+item_bodhi_heart,item:+item_bodhi_seed,soul:+20", [
        ("穿越莽荒古域兽潮", "与盟友突破古域入口和兽潮阻拦。", "reputation>=80", "exp:+100"),
        ("争夺古树入口", "与各方势力竞争进入资格。", "reputation>=80", "exp:+100"),
        ("突破菩提幻境", "分辨幻象并保持自我。", "soul>=45", "soul:+10"),
        ("取得菩提心", "吸收古树核心机缘并完成境界突破。", "level>=55", "item:+item_bodhi_heart,item:+item_bodhi_seed"),
    ]),
    _story_phase("tianfu_alliance", "建立天府联盟", "魂殿全面施压，单一势力已无法抵抗。", "联合星陨阁、丹塔、炎盟与伙伴势力。", "联盟失败会让各方被逐个击破。", 26, "flag:star_pavilion_rebuilt=1,flag:yan_alliance_founded=1,reputation>=90", "flag:tianfu_alliance_founded=1,reputation:+20", [
        ("调查灵族消失", "确认远古种族正在遭受魂族秘密袭击。", "soul>=50", "flag:ancient_clan_disappearances=1"),
        ("整合星陨阁与炎盟", "统一两地情报与资源网络。", "reputation>=90", "reputation:+5"),
        ("争取丹塔与伙伴势力", "让中州盟友加入共同防线。", "alchemy>=45,rel:npc_ziyan>=35", "reputation:+10"),
        ("建立天府联盟", "形成能够正面对抗魂殿的联盟。", "flag:star_pavilion_rebuilt=1", "flag:tianfu_alliance_founded=1"),
    ]),
    _story_phase("nether_spring", "九幽黄泉与妖暝", "建立天府联盟后，需要争取九幽地冥蟒族并强化彩鳞血脉。", "救出妖暝、取得妖圣精血并争取魔兽盟友。", "缺少魔兽盟友会让联盟侧翼空虚。", 27, "level>=58,flag:tianfu_alliance_founded=1", "flag:nether_python_allied=1,rel:npc_cai_lin:+15,reputation:+10", [
        ("深入九幽黄泉", "帮助彩鳞寻找血脉突破机缘。", "rel:npc_cai_lin>=20", "rel:npc_cai_lin:+10"),
        ("救出妖暝", "推翻九幽地冥蟒族中的篡位者。", "level>=58", "flag:yaoming_restored=1"),
        ("争取魔兽盟友", "让九幽地冥蟒族加入天府联盟。", "flag:yaoming_restored=1", "flag:nether_python_allied=1"),
    ]),
    _story_phase("dragon_island_war", "古龙岛三岛大战", "三大龙王拒绝承认紫研，古龙族战争爆发。", "帮助紫研击败三岛联军，但北龙王趁乱逃脱。", "北龙王仍会成为后续隐患。", 28, "level>=60,flag:dragon_emperor_awakened=1", "flag:north_dragon_escaped=1,rel:npc_ziyan:+15,reputation:+15", [
        ("重返古龙岛", "响应紫研求援并集结东龙岛力量。", "rel:npc_ziyan>=45", "reputation:+5"),
        ("迎战三大龙王", "打破三岛联军并保护紫研。", "level>=60", "exp:+200"),
        ("北龙王逃脱", "结束三岛大战并追踪北龙王去向。", "flag:dragon_emperor_awakened=1", "flag:north_dragon_escaped=1"),
    ]),
    _story_phase("soul_hall_war", "血洗魂殿人殿", "天府联盟成立后，双方开始争夺中州主动权。", "摧毁魂殿核心分殿并夺回灵魂本源。", "若魂殿仍掌握灵魂本源，联盟将持续受制。", 29, "level>=62,flag:tianfu_alliance_founded=1", "flag:soul_hall_weakened=1,soul:+15,reputation:+20", [
        ("血洗魂殿人殿", "摧毁魂殿灵魂收集据点。", "reputation>=105", "flag:soul_hall_core_exposed=1"),
        ("夺回灵魂本源", "释放被囚灵魂并强化自身灵魂境界。", "soul>=55,flag:soul_hall_core_exposed=1", "soul:+15"),
        ("逼退魂殿殿主", "迫使魂殿收缩，但殿主仍未被彻底击败。", "level>=62", "flag:soul_hall_weakened=1"),
    ]),
    _story_phase("demon_flame", "净莲妖火", "残图汇聚，净莲妖火空间开启。", "突破妖火幻境并完成收服。", "失败会被妖火控制。", 30, "level>=64,soul>=55,flag:soul_hall_weakened=1", "item:+item_purifying_demon_flame,douqi:+80", [
        ("集齐妖火残图", "借助联盟情报定位妖火空间。", "soul>=50", "flag:demon_flame_map=1"),
        ("突破妖火幻境", "抵抗净莲妖圣留下的幻境。", "soul>=55", "soul:+10"),
        ("收服净莲妖火", "与盟友共同压制妖火本体。", "level>=60", "item:+item_purifying_demon_flame"),
    ]),
    _story_phase("post_demon_wars", "魂殿殿主与北龙王终战", "净莲妖火之后，魂殿殿主与逃亡的北龙王先后发动反扑。", "击败两名强敌并完成古龙族统一。", "残余强敌会破坏大陆联盟。", 31, "level>=66,flag:north_dragon_escaped=1,flag:soul_hall_weakened=1", "flag:soul_hall_defeated=1,flag:dragon_clan_unified=1,reputation:+20", [
        ("击败魂殿殿主", "终结魂殿在中州的公开统治。", "level>=66,flag:soul_hall_weakened=1", "flag:soul_hall_defeated=1"),
        ("追击北龙王", "阻止北龙王利用化龙魔阵反扑。", "rel:npc_ziyan>=50,flag:north_dragon_escaped=1", "exp:+200"),
        ("统一太虚古龙族", "彻底结束古龙族分裂。", "flag:north_dragon_escaped=1", "flag:dragon_clan_unified=1"),
    ]),
    _story_phase("medicine_ceremony", "药典与药族灭族战", "药族举办药典，魂族随后发动灭族袭击。", "通过药典、救援药族幸存者并确认魂族计划。", "药族覆灭会让魂族夺得更多血脉与帝玉。", 32, "alchemy>=50,soul>=55", "alchemy:+20,flag:medicine_clan_survivors_saved=1,reputation:+20", [
        ("完成药典考验", "展现高阶炼药与灵魂控制。", "alchemy>=50,soul>=55", "alchemy:+10"),
        ("应对药族灭族战", "在魂族袭击中保护药族幸存者。", "level>=65", "flag:hun_clan_hostile=1"),
        ("救出药族幸存者", "将幸存力量带回联盟并保存药族传承。", "reputation>=110", "flag:medicine_clan_survivors_saved=1"),
    ]),
    _story_phase("ancient_clan_war", "远古种族联盟战", "魂族开始夺取各族帝玉，远古种族面临覆灭。", "协调古族、古龙族与盟友，并救回被囚的父亲。", "联盟破裂会让魂族打开古帝洞府。", 33, "flag:dragon_clan_unified=1,flag:hun_clan_hostile=1", "flag:ancient_alliance=1,rel:npc_xiao_zhan:+20,reputation:+25", [
        ("确认魂族夺玉计划", "整合药族幸存者与古族情报。", "flag:medicine_clan_survivors_saved=1", "flag:emperor_jade_crisis=1"),
        ("再入天墓", "借助萧玄残魂将灵魂境界提升至帝境。", "flag:xiao_bloodline_awakened=1,soul>=65", "flag:emperor_soul_awakened=1,soul:+20"),
        ("营救萧战", "在魂族大战中救回被囚多年的父亲。", "flag:xiao_family_crisis=1,level>=68", "flag:xiao_zhan_rescued=1,rel:npc_xiao_zhan:+20"),
        ("协调远古种族盟友", "争取古族与统一后的太虚古龙族共同作战。", "rel:npc_gu_yuan>=30,flag:dragon_clan_unified=1", "flag:ancient_alliance=1"),
    ]),
    _story_phase("ancient_emperor", "古帝洞府", "魂族打开古帝洞府，成帝传承成为最后争夺。", "进入洞府并阻止魂族独占传承。", "失败会让魂天帝完成最终突破。", 34, "level>=70,flag:ancient_alliance=1", "flag:ancient_emperor_jade=1,item:+item_tuoshe_jade,douqi:+100", [
        ("追入古帝洞府", "集结联盟进入洞府空间。", "flag:ancient_alliance=1", "flag:ancient_emperor_jade=1"),
        ("争夺帝品雏丹", "阻止魂族夺取成帝关键。", "level>=70", "douqi:+50"),
        ("魂天帝夺丹成帝", "在争夺失败后应对魂天帝完成突破的危机。", "level>=72", "flag:soul_emperor_ascended=1"),
        ("接受古帝传承", "获得迎战魂天帝的最后力量。", "flag:emperor_soul_awakened=1", "flag:emperor_legacy=1,douqi:+100"),
    ]),
    _story_phase("final_war", "双帝之战", "魂天帝突破，大陆已无退路。", "集结联军并完成最终决战。", "失败意味着大陆秩序覆灭。", 35, "level>=80,flag:emperor_legacy=1", "flag:soul_emperor_defeated=1,reputation:+100", [
        ("集结大陆联军", "让所有盟友进入最终战场。", "reputation>=120,flag:ancient_alliance=1", "reputation:+20"),
        ("突破斗帝", "以古帝传承与异火完成最终突破。", "level>=80,flag:emperor_legacy=1", "flag:xiao_emperor_awakened=1"),
        ("迎战魂天帝", "封印魂天帝并终结魂族战争。", "flag:xiao_emperor_awakened=1", "flag:soul_emperor_defeated=1"),
    ]),
    _story_phase("five_emperors", "五帝破空", "大战结束后，大陆恢复秩序，新的世界通道出现。", "安置盟友、留下传承并开启新纪元。", "若没有完成战后安排，胜利仍会留下隐患。", 36, "flag:soul_emperor_defeated=1", "flag:story_finished=1,item:+item_emperor_flame", [
        ("重建大陆秩序", "处理战后势力与家族安置。", "reputation>=150", "reputation:+20"),
        ("留下斗帝传承", "让新的修炼道路延续。", "flag:xiao_emperor_awakened=1", "item:+item_emperor_flame"),
        ("五帝破空", "与重要伙伴前往新的世界。", "flag:ancient_alliance=1", "flag:story_finished=1"),
    ]),
]


# 工作簿里程碑必须映射到真实节点，并按实际剧情先后排列。
PLOT_MILESTONE_SEQUENCE = [
    "退婚", "三年之约", "青莲地心火争夺", "炼药师大会", "内院选拔赛",
    "强榜大赛", "陨落心炎与天焚炼气塔", "黑角域大战", "云岚宗大战",
    "丹会", "三千焱炎火", "营救药老", "远古遗迹", "古族成人礼",
    "天墓与萧玄", "菩提古树", "净莲妖火", "药典", "古帝洞府",
    "双帝之战", "五帝破空",
]

PLOT_MILESTONE_COVERAGE = {
    "退婚": ("退婚与三年之约", "应对退婚"),
    "三年之约": ("退婚与三年之约", "立下三年之约"),
    "青莲地心火争夺": ("塔戈尔沙漠与青莲地心火", "美杜莎神殿争夺"),
    "炼药师大会": ("炼药师大会", "赢得炼药师大会"),
    "内院选拔赛": ("迦南学院外院", "通过内院选拔赛"),
    "强榜大赛": ("内院磐门与强榜", "挑战强榜大赛"),
    "陨落心炎与天焚炼气塔": ("陨落心炎与天焚炼气塔", "收服陨落心炎"),
    "黑角域大战": ("黑角域入侵内院", "击退韩枫与黑盟"),
    "云岚宗大战": ("重返加玛与云岚宗大战", "击败云山，药老被掳"),
    "丹会": ("丹会与三千焱炎火", "赢得丹会"),
    "三千焱炎火": ("丹会与三千焱炎火", "进入星域收服异火"),
    "营救药老": ("营救药老", "突袭魂殿分殿"),
    "远古遗迹": ("远古遗迹", "夺取斗圣骸骨"),
    "古族成人礼": ("古族成人礼与天墓", "参加古族成人礼"),
    "天墓与萧玄": ("古族成人礼与天墓", "接受萧玄传承"),
    "菩提古树": ("莽荒古域与菩提古树", "取得菩提心"),
    "净莲妖火": ("净莲妖火", "收服净莲妖火"),
    "药典": ("药典与药族灭族战", "完成药典考验"),
    "古帝洞府": ("古帝洞府", "追入古帝洞府"),
    "双帝之战": ("双帝之战", "迎战魂天帝"),
    "五帝破空": ("五帝破空", "五帝破空"),
}

# 不属于工作簿 21 个里程碑名称，但对剧情因果闭环不可省略的桥梁。
CRITICAL_BRIDGE_COVERAGE = {
    "药老被魂殿掳走": ("重返加玛与云岚宗大战", "击败云山，药老被掳"),
    "出云帝国战争": ("出云帝国与毒宗之战", "守卫加玛帝国"),
    "厄难毒体稳定": ("叶城与冰河谷", "凝聚毒丹"),
    "紫研觉醒龙皇血脉": ("龙岛与龙皇血脉", "见证龙皇觉醒"),
    "太虚古龙统一": ("魂殿殿主与北龙王终战", "统一太虚古龙族"),
    "魂殿决战": ("魂殿殿主与北龙王终战", "击败魂殿殿主"),
    "药族灭族战": ("药典与药族灭族战", "应对药族灭族战"),
    "营救萧战": ("远古种族联盟战", "营救萧战"),
    "获得菩提心": ("莽荒古域与菩提古树", "取得菩提心"),
    "重返黑角域": ("重返黑角域", "擒获韩枫灵魂"),
    "叶城与冰河谷": ("叶城与冰河谷", "迎战冰河谷"),
    "药老复活": ("复活药老与重建星陨阁", "药老复活"),
    "花宗传承": ("花宗与云韵传承", "争取花宗支持"),
    "九幽黄泉": ("九幽黄泉与妖暝", "救出妖暝"),
    "首次穿越黑角域": ("迦南学院外院", "穿越黑角域"),
    "再探天焚炼气塔": ("再探天焚炼气塔", "发现古帝玉线索"),
    "玄黄要塞大战": ("玄黄要塞与西北大陆大战", "守卫萧家与炎盟"),
    "灵族消失": ("建立天府联盟", "调查灵族消失"),
    "再入天墓帝境灵魂": ("远古种族联盟战", "再入天墓"),
    "魂天帝夺丹成帝": ("古帝洞府", "魂天帝夺丹成帝"),
}

# 取自章节索引的实际发生位置，用于防止中段剧情再次错位。
STORY_CHAPTER_ANCHORS = {
    "yunlan_duel": 329,
    "canaan_outer": 378,
    "fallen_heart": 582,
    "black_corner_war": 589,
    "yunlan_war": 668,
    "poison_sect_war": 735,
    "return_black_corner": 811,
    "revisit_tower": 896,
    "zhongzhou_arrival": 941,
    "ye_ice_valley": 1052,
    "dan_meeting_flame": 1220,
    "save_mentor": 1310,
    "ancient_ruins": 1378,
    "revive_mentor": 1439,
    "flower_sect": 1447,
    "dragon_island_legacy": 1461,
    "gu_clan_tomb": 1473,
    "northwest_fortress_war": 1566,
    "bodhi_tree": 1597,
    "tianfu_alliance": 1665,
    "nether_spring": 1692,
    "dragon_island_war": 1721,
    "soul_hall_war": 1737,
    "demon_flame": 1750,
    "post_demon_wars": 1778,
    "medicine_ceremony": 1815,
    "ancient_clan_war": 1838,
    "ancient_emperor": 1870,
    "final_war": 1901,
    "five_emperors": 1904,
}

# 地图只随剧情开放。推荐等级仅用于提示危险，不参与解锁判断。
MAP_STORY_UNLOCKS = {
    "map_wutan": "fallen_genius",
    "map_jia_ma": "fallen_genius",
    "map_miteer_auction": "wutan_growth",
    "map_magic_mountains": "mountain_training",
    "map_qingshan": "mountain_training",
    "map_tager": "desert_flame",
    "map_jia_ma_capital": "alchemy_conference",
    "map_alchemist_guild": "alchemy_conference",
    "map_yunlan": "yunlan_duel",
    "map_peace_town": "canaan_outer",
    "map_black_corner": "canaan_outer",
    "map_canaan": "canaan_outer",
    "map_canaan_inner": "canaan_inner",
    "map_skyfire_tower": "fallen_heart",
    "map_feng_city": "black_corner_war",
    "map_black_emperor_city": "return_black_corner",
    "map_zhongzhou": "zhongzhou_arrival",
    "map_tianbei_city": "zhongzhou_arrival",
    "map_wind_lightning_pavilion": "zhongzhou_arrival",
    "map_huangquan_pavilion": "zhongzhou_arrival",
    "map_wanjian_pavilion": "zhongzhou_arrival",
    "map_burning_flame_valley": "zhongzhou_arrival",
    "map_ye_city": "ye_ice_valley",
    "map_ice_river_valley": "ye_ice_valley",
    "map_dan_region": "dan_meeting_flame",
    "map_sacred_dan_city": "dan_meeting_flame",
    "map_dan_tower": "dan_meeting_flame",
    "map_soul_mountains": "save_mentor",
    "map_soul_hall": "save_mentor",
    "map_star_pavilion": "save_mentor",
    "map_star_realm": "revive_mentor",
    "map_ancient_ruins": "ancient_ruins",
    "map_beast_region": "ancient_ruins",
    "map_flower_sect": "flower_sect",
    "map_dragon_island": "dragon_island_legacy",
    "map_east_dragon_island": "dragon_island_legacy",
    "map_ancient_dragon_island": "dragon_island_legacy",
    "map_ancient_sacred_city": "gu_clan_tomb",
    "map_ancient_realm": "gu_clan_tomb",
    "map_heaven_tomb": "gu_clan_tomb",
    "map_wilderness": "bodhi_tree",
    "map_bodhi_tree": "bodhi_tree",
    "map_space_trade_fair": "bodhi_tree",
    "map_west_dragon_island": "dragon_island_war",
    "map_south_dragon_island": "dragon_island_war",
    "map_north_dragon_island": "dragon_island_war",
    "map_demon_flame_space": "demon_flame",
    "map_yao_realm": "medicine_ceremony",
    "map_soul_realm": "ancient_clan_war",
    "map_hun_clan_space": "ancient_clan_war",
    "map_emperor_cave": "ancient_emperor",
    "map_double_emperor": "final_war",
}

SCHEDULE_NODES = [
    {
        "id": "xiao_clan_trial",
        "day": 3,
        "period": 0,
        "title": "萧家族内试炼",
        "description": "族内长老将在演武场检验年轻一辈。你必须证明自己没有彻底失去锋芒。",
        "goals": {"level": 2, "training_wins": 1},
        "success_text": "你在试炼中稳住阵脚，赢得了父亲与族人的认可。",
        "success_effect": "exp:+30,reputation:+5,rel:npc_xiao_zhan:+5,item:+item_elixir",
        "failure_text": "准备不足令你在众目睽睽之下落败，族内质疑声愈发刺耳。",
        "failure_effect": "reputation:-5,rel:npc_xiao_zhan:-10,hp:-20",
    },
    {
        "id": "black_ring_deadline",
        "day": 7,
        "period": 2,
        "title": "后山之约",
        "description": "夕阳落下前，你必须带着足够的历练前往后山，查明黑色戒指的异动。",
        "goals": {"story_stage": 2, "adventure_points": 3},
        "success_text": "你如约抵达后山，戒指中传来一道苍老声音，新的道路由此展开。",
        "success_effect": "flag:ring_awakened=1,soul:+5,douqi:+5",
        "failure_text": "你错过了戒指最强烈的一次波动，只能付出更多时间重新寻找线索。",
        "failure_effect": "soul:-2,reputation:-2",
    },
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


class GameEngine:
    def __init__(self, workbook_path: Path = WORKBOOK_PATH) -> None:
        data = load_game_data(workbook_path)
        self.events_list: List[Dict[str, Any]] = data["events"]
        self.events: Dict[str, Dict[str, Any]] = {
            event["id"]: event for event in self.events_list
        }
        self.start_event: str = data["start_event"]
        self.attribute_rules: Dict[str, Dict[str, Any]] = data["attributes"]
        self.flag_defaults: Dict[str, int] = data["flag_defaults"]
        self.npc_names: Dict[str, str] = data["npc_names"]
        relationship_list: List[Dict[str, Any]] = data["relationships"]
        self.relationship_rules: Dict[str, Dict[str, Any]] = {
            rule["id"]: rule for rule in relationship_list
        }
        self.relationship_index = self._build_relationship_index(relationship_list)
        self.level_progression: List[Dict[str, Any]] = data["level_progression"]
        self.maps: Dict[str, Dict[str, Any]] = data["maps"]
        self.encounters: List[Dict[str, Any]] = data["encounters"]
        self.enemies: Dict[str, Dict[str, Any]] = data["enemies"]
        self.item_rules: Dict[str, Dict[str, Any]] = data["items"]
        self.skills: Dict[str, Dict[str, Any]] = data["skills"]
        self.realms: List[Dict[str, Any]] = data["realms"]
        self.active_encounter: Optional[Dict[str, Any]] = None
        self.combat: Optional[Dict[str, Any]] = None
        self.player: Dict[str, Any] = self._create_new_player()
        self.last_message: str = ""

    def new_game(self, name: Optional[str] = None) -> None:
        self.player = self._create_new_player()
        if name:
            self.player["name"] = name
        self.last_message = "斗气大陆的故事由此开始。"

    def save(self) -> None:
        self._sync_story_phase_id()
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SAVE_PATH.open("w", encoding="utf-8") as file:
            json.dump(self.player, file, ensure_ascii=False, indent=2)

    def load(self) -> bool:
        if not SAVE_PATH.exists():
            return False
        self.player = load_json(SAVE_PATH)
        self._ensure_player_state()
        self.last_message = "存档已读取，并已迁移到最新剧情数据。"
        return True

    def _create_new_player(self) -> Dict[str, Any]:
        player: Dict[str, Any] = {
            rule_id: rule["initial"] for rule_id, rule in self.attribute_rules.items()
        }
        player.update(
            {
                "name": self.npc_names.get("player", "萧炎"),
                "max_hp": self.attribute_rules["hp"]["initial"],
                "flags": [
                    flag_id
                    for flag_id, default in self.flag_defaults.items()
                    if default
                ],
                "items": [],
                "visited": {},
                "relationships": {},
                "relationship_triggers": [],
                "active_statuses": [],
                "current_event": self.start_event,
                "last_map": "map_wutan",
                "adventure_points": 0,
                "story_stage": 0,
                "story_phase_id": STORY_PHASES[0]["id"],
                "story_substage": 0,
                "known_skills": ["skill_bajibang", "skill_flame_mantra"],
                "day": 1,
                "time_period": 0,
                "completed_schedule_nodes": [],
                "pending_schedule_node": "",
                "training_wins": 0,
            }
        )
        self._ensure_player_state(player)
        return player

    def _ensure_player_state(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player

        nested_player = player.get("player")
        if isinstance(nested_player, dict):
            player.setdefault("name", nested_player.get("name", "萧炎"))
            attributes = nested_player.get("attributes", {})
            if isinstance(attributes, dict):
                for key, value in attributes.items():
                    player.setdefault(key, value)

        for legacy_key, current_key in LEGACY_STAT_ALIASES.items():
            if current_key not in player and legacy_key in player:
                player[current_key] = player[legacy_key]
        for attribute_id, rule in self.attribute_rules.items():
            player.setdefault(attribute_id, rule["initial"])

        flags = player.get("flags", [])
        if isinstance(flags, dict):
            player["flags"] = [key for key, value in flags.items() if int(value)]
        else:
            player.setdefault("flags", [])
        for flag_id, default in self.flag_defaults.items():
            if default and flag_id not in player["flags"]:
                player["flags"].append(flag_id)

        if "items" not in player:
            inventory = player.get("inventory", {})
            if isinstance(inventory, dict):
                player["items"] = [
                    item_id for item_id, count in inventory.items() if int(count) > 0
                ]
            else:
                player["items"] = []

        player.setdefault("name", self.npc_names.get("player", "萧炎"))
        player.setdefault(
            "max_hp", max(self.attribute_rules["hp"]["initial"], player["hp"])
        )
        player.setdefault("visited", {})
        player.setdefault("relationships", {})
        player.setdefault("relationship_triggers", [])
        player.setdefault("active_statuses", [])
        player.setdefault("last_map", "map_wutan")
        player.setdefault("adventure_points", 0)
        if "story_phase_id" in player:
            phase_id = player["story_phase_id"]
            matching_stage = next(
                (
                    index
                    for index, phase in enumerate(STORY_PHASES)
                    if phase["id"] == phase_id
                ),
                len(STORY_PHASES) if not phase_id else None,
            )
            if matching_stage is not None:
                player["story_stage"] = matching_stage
        else:
            old_stage = int(player.get("story_stage", player.get("story_steps", 0)))
            if 0 <= old_stage < len(LEGACY_STORY_PHASE_IDS_V2):
                old_phase_id = LEGACY_STORY_PHASE_IDS_V2[old_stage]
                player["story_stage"] = next(
                    (
                        index
                        for index, phase in enumerate(STORY_PHASES)
                        if phase["id"] == old_phase_id
                    ),
                    min(len(STORY_PHASES), old_stage),
                )
            else:
                player["story_stage"] = min(len(STORY_PHASES), old_stage)
            player["story_phase_id"] = (
                STORY_PHASES[player["story_stage"]]["id"]
                if player["story_stage"] < len(STORY_PHASES)
                else ""
            )
        player.setdefault("story_substage", 0)
        player.setdefault("known_skills", ["skill_bajibang", "skill_flame_mantra"])
        player.setdefault("day", 1)
        player.setdefault("time_period", 0)
        player.setdefault("completed_schedule_nodes", [])
        player.setdefault("pending_schedule_node", "")
        player.setdefault("training_wins", 0)
        self._check_schedule_nodes(player)
        if player.get("current_event") not in self.events:
            player["current_event"] = self.start_event
        self._ensure_relationship_state(player)
        self._clamp_player_stats(player)
        self._apply_level_progression(player)

    def _ensure_relationship_state(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player
        values = player.setdefault("relationships", {})
        for relation_id, rule in self.relationship_rules.items():
            values.setdefault(relation_id, int(rule.get("initial_value", 0)))

    @staticmethod
    def _build_relationship_index(
        relationship_list: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        index: Dict[str, str] = {}
        for rule in relationship_list:
            relation_id = rule["id"]
            source = rule["source"]
            target = rule["target"]
            index[relation_id] = relation_id
            index[f"{source}>{target}"] = relation_id
            if source == "player":
                index[target] = relation_id
            if rule.get("bidirectional"):
                index[f"{target}>{source}"] = relation_id
        return index

    def relation_rule(self, reference: str) -> Dict[str, Any]:
        relation_id = self.relationship_index.get(reference)
        if relation_id is None:
            raise KeyError(f"未定义的关系：{reference}")
        return self.relationship_rules[relation_id]

    def relation_value(self, reference: str) -> int:
        rule = self.relation_rule(reference)
        return int(self.player["relationships"][rule["id"]])

    def relation_stage(self, reference: str) -> str:
        rule = self.relation_rule(reference)
        value = self.relation_value(reference)
        stage = "未定义"
        thresholds = []
        for item in rule.get("stage_rule", "").split("|"):
            if not item:
                continue
            threshold, name = item.split(":", 1)
            thresholds.append((int(threshold), name))
        for threshold, name in sorted(thresholds):
            if value >= threshold:
                stage = name
        return stage

    def set_relation_value(
        self, reference: str, value: int, evaluate_triggers: bool = True
    ) -> List[str]:
        rule = self.relation_rule(reference)
        relation_id = rule["id"]
        old_value = self.relation_value(reference)
        new_value = max(
            int(rule.get("min_value", -100)),
            min(int(rule.get("max_value", 100)), int(value)),
        )
        self.player["relationships"][relation_id] = new_value
        target_name = self.npc_names.get(rule["target"], rule["target"])
        logs = [f"关系 {target_name} {old_value}->{new_value}"]
        if evaluate_triggers:
            logs.extend(self._apply_on_reach_effect(rule))
        return logs

    def change_relation_value(
        self, reference: str, delta: int, evaluate_triggers: bool = True
    ) -> List[str]:
        return self.set_relation_value(
            reference,
            self.relation_value(reference) + delta,
            evaluate_triggers=evaluate_triggers,
        )

    def _apply_on_reach_effect(self, rule: Dict[str, Any]) -> List[str]:
        expression = rule.get("on_reach_effect")
        if not expression:
            return []
        match = ON_REACH_PATTERN.match(expression)
        if not match or not self._check_condition_token(match.group(1)):
            return []
        trigger_id = f"{rule['id']}:{expression}"
        triggered: List[str] = self.player["relationship_triggers"]
        if trigger_id in triggered:
            return []
        triggered.append(trigger_id)
        return self.apply_effects(match.group(2), evaluate_relationship_triggers=False)

    def current_event(self) -> Dict[str, Any]:
        event_id = self.player.get("current_event", self.start_event)
        if event_id not in self.events:
            event_id = self.start_event
            self.player["current_event"] = event_id
        return self.events[event_id]

    def mark_visited(self, event_id: str) -> None:
        visited = self.player.setdefault("visited", {})
        visited[event_id] = visited.get(event_id, 0) + 1

    @staticmethod
    def _compare(left: int, operator: str, right: int) -> bool:
        return {
            ">": left > right,
            ">=": left >= right,
            "<": left < right,
            "<=": left <= right,
            "==": left == right,
            "!=": left != right,
        }[operator]

    @staticmethod
    def _canonical_stat(key: str) -> str:
        return LEGACY_STAT_ALIASES.get(key, key)

    def _check_condition_token(self, token: str) -> bool:
        token = token.strip()
        if not token:
            return True
        if token.startswith("item:"):
            return token[5:] in self.player.get("items", [])
        if token.startswith("flag:"):
            name, expected = token[5:].split("=", 1)
            actual = 1 if name in self.player.get("flags", []) else 0
            return actual == int(expected)

        match = COMPARISON_PATTERN.match(token)
        if not match:
            raise ValueError(f"不支持的条件表达式：{token}")
        key, operator, raw_value = match.groups()
        if key.startswith("rel:"):
            actual = self.relation_value(key[4:])
        else:
            actual = int(self.player.get(self._canonical_stat(key), 0))
        return self._compare(actual, operator, int(raw_value))

    def check_conditions(self, conditions: Optional[Any]) -> bool:
        if not conditions:
            return True
        if isinstance(conditions, str):
            return all(
                self._check_condition_token(token) for token in conditions.split(",")
            )

        player = self.player
        for stat, value in conditions.get("stat_min", {}).items():
            if player.get(self._canonical_stat(stat), 0) < value:
                return False
        for stat, value in conditions.get("stat_max", {}).items():
            if player.get(self._canonical_stat(stat), 0) > value:
                return False
        for flag in conditions.get("has_flags", []):
            if flag not in player.get("flags", []):
                return False
        for flag in conditions.get("not_flags", []):
            if flag in player.get("flags", []):
                return False
        for item in conditions.get("has_items", []):
            if item not in player.get("items", []):
                return False
        for item in conditions.get("not_items", []):
            if item in player.get("items", []):
                return False
        return True

    def available_options(
        self, event: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[int, Dict[str, Any]]]:
        event = event or self.current_event()
        if not self.check_conditions(event.get("conditions")):
            return []
        result = []
        for index, option in enumerate(event.get("options", []), start=1):
            if self.check_conditions(option.get("conditions")):
                result.append((index, option))
        return result

    def _apply_effect_token(
        self, token: str, evaluate_relationship_triggers: bool
    ) -> List[str]:
        token = token.strip()
        if not token:
            return []

        match = RELATION_EFFECT_PATTERN.match(token)
        if match:
            return self.change_relation_value(
                match.group(1),
                int(match.group(2)),
                evaluate_triggers=evaluate_relationship_triggers,
            )
        match = RELATION_SET_PATTERN.match(token)
        if match:
            return self.set_relation_value(
                match.group(1),
                int(match.group(2)),
                evaluate_triggers=evaluate_relationship_triggers,
            )
        if token.startswith("item:+"):
            item = token[6:]
            if item not in self.player["items"]:
                self.player["items"].append(item)
            return [f"获得道具：{self.item_name(item)}"]
        if token.startswith("item:-"):
            item = token[6:]
            if item in self.player["items"]:
                self.player["items"].remove(item)
            return [f"失去道具：{self.item_name(item)}"]
        if token.startswith("flag:"):
            name, raw_value = token[5:].split("=", 1)
            flags = self.player["flags"]
            if int(raw_value) and name not in flags:
                flags.append(name)
            elif not int(raw_value) and name in flags:
                flags.remove(name)
            return [f"剧情开关 {name}={raw_value}"]
        if token.startswith("status:+"):
            status = token[8:]
            if status not in self.player["active_statuses"]:
                self.player["active_statuses"].append(status)
            return [f"获得状态：{status}"]
        if token.startswith("status:-"):
            status = token[8:]
            if status in self.player["active_statuses"]:
                self.player["active_statuses"].remove(status)
            return [f"移除状态：{status}"]

        key, raw_value = token.split(":", 1)
        key = self._canonical_stat(key)
        if key not in self.attribute_rules:
            raise ValueError(f"不支持的效果表达式：{token}")
        value = int(raw_value)
        self.player[key] = self.player.get(key, 0) + value
        sign = "+" if value >= 0 else ""
        return [f"{self.attribute_rules[key]['name']} {sign}{value}"]

    def apply_effects(
        self,
        effects: Optional[Any],
        evaluate_relationship_triggers: bool = True,
    ) -> List[str]:
        if not effects:
            return []
        if isinstance(effects, str):
            logs: List[str] = []
            for token in effects.split(","):
                logs.extend(
                    self._apply_effect_token(token, evaluate_relationship_triggers)
                )
            self._clamp_player_stats()
            logs.extend(self._apply_level_progression())
            return logs

        logs: List[str] = []
        for key, value in effects.items():
            canonical_key = self._canonical_stat(key)
            if canonical_key in self.attribute_rules:
                self.player[canonical_key] = self.player.get(canonical_key, 0) + value
                logs.append(f"{self.attribute_rules[canonical_key]['name']} {value:+d}")
        self._clamp_player_stats()
        logs.extend(self._apply_level_progression())
        return logs

    def _clamp_player_stats(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player
        for attribute_id, rule in self.attribute_rules.items():
            value = int(player.get(attribute_id, rule["initial"]))
            player[attribute_id] = max(rule["min"], min(rule["max"], value))

    def _progression_rule(self, level: int) -> Optional[Dict[str, Any]]:
        for rule in self.level_progression:
            if rule["min_level"] <= level <= rule["max_level"]:
                return rule
        return None

    @staticmethod
    def _required_exp(level: int, formula: str) -> Optional[int]:
        match = EXP_FORMULA_PATTERN.match(formula)
        return level * int(match.group(1)) if match else None

    def _apply_level_progression(
        self, player: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        player = player if player is not None else self.player
        logs: List[str] = []
        while True:
            level = int(player.get("level", 1))
            rule = self._progression_rule(level)
            if rule is None:
                break
            required_exp = self._required_exp(level, rule["exp_formula"])
            if required_exp is None or int(player.get("exp", 0)) < required_exp:
                break

            player["level"] = level + 1
            for attribute_id, gain in rule["gains"].items():
                player[attribute_id] = player.get(attribute_id, 0) + gain
                if attribute_id == "hp":
                    player["max_hp"] = player.get("max_hp", player["hp"]) + gain
            self._clamp_player_stats(player)
            logs.append(f"境界等级提升至 {level + 1}")
            skill_id = LEVEL_SKILL_MILESTONES.get(level + 1)
            if skill_id and skill_id not in player["known_skills"]:
                player["known_skills"].append(skill_id)
                logs.append(f"领悟斗技：{self.skills[skill_id]['name']}")
        return logs

    def eligible_random_events(self) -> List[Dict[str, Any]]:
        return [
            event
            for event in self.events_list
            if event.get("pool") not in {"", "main"}
            and self.check_conditions(event.get("conditions"))
        ]

    def choose_random_event_id(self) -> str:
        candidates = self.eligible_random_events()
        if not candidates:
            return self.player.get("current_event", self.start_event)
        weights = [max(1, int(event.get("weight", 1))) for event in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]["id"]

    def resolve_next(self, option: Dict[str, Any]) -> str:
        next_id = option.get("next", "")
        if not next_id:
            return self.player.get("current_event", self.start_event)
        if next_id == "random":
            return self.choose_random_event_id()
        if "|" in next_id:
            branches = []
            for branch in next_id.split("|"):
                event_id, weight = branch.rsplit(":", 1)
                branches.append((event_id, max(1, int(weight))))
            return random.choices(
                [branch[0] for branch in branches],
                weights=[branch[1] for branch in branches],
                k=1,
            )[0]
        return next_id

    def choose_option(self, visible_option_number: int) -> bool:
        event = self.current_event()
        option_map = {index: option for index, option in self.available_options(event)}
        if visible_option_number not in option_map:
            self.last_message = "无效选择，或当前条件尚未满足。"
            return False

        self.mark_visited(event["id"])
        option = option_map[visible_option_number]
        logs = self.apply_effects(option.get("effects"))
        next_id = self.resolve_next(option)
        if next_id in self.events:
            self.player["current_event"] = next_id
        else:
            logs.append(f"暂不支持的跳转：{next_id}")
        self.last_message = "；".join(logs) if logs else "继续前行。"
        return True

    def realm_name(self) -> str:
        level = int(self.player.get("level", 1))
        for realm in self.realms:
            if realm["min_level"] <= level <= realm["max_level"]:
                return realm["name"]
        return "未知境界"

    def current_map(self) -> Dict[str, Any]:
        return self.maps.get(self.player.get("last_map", ""), self.maps["map_wutan"])

    def time_text(self) -> str:
        return f"第{self.player['day']}日 {TIME_PERIODS[self.player['time_period']]}"

    def is_night(self) -> bool:
        return int(self.player["time_period"]) >= 2

    def pending_schedule_node(self) -> Optional[Dict[str, Any]]:
        node_id = self.player.get("pending_schedule_node", "")
        return next((node for node in SCHEDULE_NODES if node["id"] == node_id), None)

    def next_schedule_node(self) -> Optional[Dict[str, Any]]:
        completed = set(self.player.get("completed_schedule_nodes", []))
        return next((node for node in SCHEDULE_NODES if node["id"] not in completed), None)

    def schedule_text(self, node: Dict[str, Any]) -> str:
        goals = []
        for key, required in node["goals"].items():
            names = {
                "level": "等级",
                "training_wins": "切磋胜场",
                "story_steps": "主线进度",
                "story_stage": "关键阶段",
                "adventure_points": "冒险阅历",
            }
            goals.append(f"{names.get(key, key)} {self.player.get(key, 0)}/{required}")
        return (
            f"{node['title']}｜第{node['day']}日 {TIME_PERIODS[node['period']]}\n"
            f"{node['description']}\n目标：" + "、".join(goals)
        )

    def schedule_countdown_text(self, node: Dict[str, Any]) -> str:
        node_time = (node["day"] - 1) * len(TIME_PERIODS) + node["period"]
        remaining = max(0, node_time - self._absolute_time())
        days, periods = divmod(remaining, len(TIME_PERIODS))
        parts = []
        if days:
            parts.append(f"{days}日")
        if periods:
            parts.append(f"{periods}个时段")
        return "剩余" + ("".join(parts) if parts else "时间已到")

    def _can_take_free_action(self) -> bool:
        if self.pending_schedule_node() is None:
            return True
        self.last_message = "当前有必须处理的日程节点，无法进行其他行动。"
        return False

    def _absolute_time(self, player: Optional[Dict[str, Any]] = None) -> int:
        player = player if player is not None else self.player
        return (int(player["day"]) - 1) * len(TIME_PERIODS) + int(player["time_period"])

    def _check_schedule_nodes(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player
        if player.get("pending_schedule_node"):
            return
        completed = set(player.get("completed_schedule_nodes", []))
        current_time = self._absolute_time(player)
        for node in SCHEDULE_NODES:
            node_time = (node["day"] - 1) * len(TIME_PERIODS) + node["period"]
            if node["id"] not in completed and current_time >= node_time:
                player["pending_schedule_node"] = node["id"]
                return

    def advance_time(self, periods: int = 1) -> None:
        absolute = self._absolute_time() + max(0, periods)
        self.player["day"] = absolute // len(TIME_PERIODS) + 1
        self.player["time_period"] = absolute % len(TIME_PERIODS)
        self._check_schedule_nodes()

    def resolve_schedule_node(self) -> bool:
        node = self.pending_schedule_node()
        if node is None:
            self.last_message = "当前没有必须处理的日程。"
            return False
        success = all(
            int(self.player.get(key, 0)) >= required
            for key, required in node["goals"].items()
        )
        result_text = node["success_text"] if success else node["failure_text"]
        effects = node["success_effect"] if success else node["failure_effect"]
        logs = self.apply_effects(effects)
        self.player["completed_schedule_nodes"].append(node["id"])
        self.player["pending_schedule_node"] = ""
        self.last_message = (
            f"{'达标' if success else '未达标'}：{result_text}"
            + ("；" + "；".join(logs) if logs else "")
        )
        self._check_schedule_nodes()
        return success

    def available_maps(self) -> List[Dict[str, Any]]:
        return [map_rule for map_rule in self.maps.values() if self.is_map_unlocked(map_rule["id"])]

    def is_map_unlocked(self, map_id: str) -> bool:
        phase_id = MAP_STORY_UNLOCKS.get(map_id)
        if phase_id is None:
            return False
        required_stage = next(
            (
                index
                for index, phase in enumerate(STORY_PHASES)
                if phase["id"] == phase_id
            ),
            len(STORY_PHASES),
        )
        return int(self.player.get("story_stage", 0)) >= required_stage

    def map_unlock_text(self, map_id: str) -> str:
        phase_id = MAP_STORY_UNLOCKS.get(map_id)
        phase = next((phase for phase in STORY_PHASES if phase["id"] == phase_id), None)
        return f"推进至“{phase['title']}”开放" if phase else "尚无开放剧情"

    def travel(self, map_id: str) -> bool:
        if not self._can_take_free_action():
            return False
        map_rule = self.maps.get(map_id)
        if map_rule is None or not self.is_map_unlocked(map_id):
            self.last_message = (
                f"该区域尚未开放。{self.map_unlock_text(map_id)}"
                if map_rule is not None
                else "不存在该区域。"
            )
            return False
        if self.player["time_period"] == 3 and not map_rule["safe_zone"]:
            self.last_message = "深夜无法安全前往危险区域，请等到天亮。"
            return False
        self.player["last_map"] = map_id
        self.active_encounter = None
        self.advance_time()
        self.last_message = f"你抵达了{map_rule['name']}。{map_rule['description']}"
        return True

    def rest(self) -> None:
        if not self._can_take_free_action():
            return
        self.player["hp"] = self.player["max_hp"]
        self.player["stamina"] = self.attribute_rules["stamina"]["initial"]
        periods = len(TIME_PERIODS) - int(self.player["time_period"])
        self.advance_time(periods)
        self.last_message = f"你休整到{self.time_text()}，生命与体力已经恢复。"

    def cultivate(self) -> bool:
        if not self._can_take_free_action():
            return False
        if self.player["stamina"] < 10:
            self.last_message = "体力不足，先休息再修炼。"
            return False
        self.player["stamina"] -= 10
        soul_gain = 2 if self.is_night() else 1
        self.player["adventure_points"] += 1
        if "ring_awakened" not in self.player["flags"]:
            logs = self.apply_effects(f"soul:+{soul_gain}")
            action_text = "药老尚未苏醒，你只能感知戒指异动、锤炼灵魂。"
        else:
            logs = self.apply_effects(f"exp:+10,douqi:+2,soul:+{soul_gain}")
            action_text = "你依照药老指导运转斗气，完成了一轮修炼。"
        self.advance_time()
        self.last_message = action_text + "；获得冒险阅历 +1"
        if logs:
            self.last_message += "；" + "；".join(logs)
        return True

    def explore(self) -> Optional[Dict[str, Any]]:
        if not self._can_take_free_action():
            return None
        map_rule = self.current_map()
        night_cost = 2 if self.is_night() else 0
        cost = map_rule["stamina_cost"] + night_cost
        if self.player["stamina"] < cost:
            self.last_message = "体力不足，无法继续探索。"
            return None
        self.player["stamina"] -= cost
        candidates = [
            encounter
            for encounter in self.encounters
            if encounter["map_id"] == map_rule["id"]
            and self.check_conditions(encounter.get("conditions"))
        ]
        if not candidates:
            self.player["adventure_points"] += 1
            self.advance_time()
            self.last_message = f"你探索了{map_rule['name']}，但没有特别发现。"
            return None
        self.active_encounter = random.choices(
            candidates,
            weights=[max(1, encounter["weight"]) for encounter in candidates],
            k=1,
        )[0]
        self.last_message = self.active_encounter["text"]
        return self.active_encounter

    def encounter_options(self) -> List[Tuple[int, Dict[str, Any]]]:
        if self.active_encounter is None:
            return []
        return [
            (index, option)
            for index, option in enumerate(self.active_encounter["options"], start=1)
            if self.check_conditions(option.get("conditions"))
        ]

    def choose_encounter_option(self, option_number: int) -> bool:
        option_map = {index: option for index, option in self.encounter_options()}
        if option_number not in option_map:
            self.last_message = "当前无法选择该行动。"
            return False
        option = option_map[option_number]
        logs = self.apply_effects(option.get("effects"))
        next_id = option.get("next", "")
        encounter_text = self.active_encounter["text"] if self.active_encounter else ""
        self.active_encounter = None
        self.player["adventure_points"] += 1
        if self.is_night():
            self.player["adventure_points"] += 1
            logs.append("夜间探索额外获得 1 点冒险阅历")
        if next_id.startswith("combat:"):
            self.combat_time_cost = 1
            self.begin_combat(next_id[7:])
            if logs:
                self.last_message = "；".join(logs) + "；" + self.last_message
        else:
            self.advance_time()
            self.last_message = "；".join(logs) if logs else f"你处理了这次遭遇：{encounter_text}"
        return True

    def begin_training_combat(self) -> bool:
        if not self._can_take_free_action():
            return False
        level = int(self.player["level"])
        self.combat_time_cost = 1
        self.combat_is_training = True
        self.combat = {
            "enemy_id": "training_opponent",
            "name": "萧家陪练弟子",
            "level": level,
            "hp": 30 + level * 8,
            "max_hp": 30 + level * 8,
            "atk": 5 + level * 2,
            "def": 2 + level,
            "spd": 5 + level,
            "exp_reward": 10 + level * 4,
            "drop_table": "",
            "round": 1,
            "defending": False,
            "can_escape": True,
        }
        self.last_message = "陪练弟子摆开架势，回合战斗开始。"
        return True

    def begin_combat(self, enemy_id: str) -> bool:
        enemy = self.enemies.get(enemy_id)
        if enemy is None:
            self.last_message = f"未找到敌人配置：{enemy_id}"
            return False
        level = int(self.player["level"])
        enemy_level = max(level, min(enemy["level"], level + 4))
        hp = max(35, min(enemy["hp"], 35 + enemy_level * 18))
        self.combat = {
            "enemy_id": enemy_id,
            "name": enemy["name"],
            "level": enemy_level,
            "hp": hp,
            "max_hp": hp,
            "atk": max(5, min(enemy["atk"], 7 + enemy_level * 3)),
            "def": max(1, min(enemy["def"], 3 + enemy_level * 2)),
            "spd": max(4, min(enemy["spd"], 6 + enemy_level * 2)),
            "exp_reward": max(10, min(enemy["exp_reward"], 12 + enemy_level * 8)),
            "drop_table": enemy["drop_table"],
            "round": 1,
            "defending": False,
            "can_escape": enemy["type"] not in {"boss", "final_boss"},
        }
        self.combat_is_training = False
        self.last_message = f"{enemy['name']}挡住了去路，回合战斗开始。"
        return True

    def combat_text(self) -> str:
        if self.combat is None:
            return ""
        return (
            f"第{self.combat['round']}回合｜{self.combat['name']} "
            f"生命 {self.combat['hp']}/{self.combat['max_hp']}\n"
            f"{self.player['name']} 生命 {self.player['hp']}｜斗气 {self.player['douqi']}"
        )

    def combat_skills(self) -> List[Dict[str, Any]]:
        return [
            self.skills[skill_id]
            for skill_id in self.player.get("known_skills", [])
            if skill_id in self.skills
        ]

    @staticmethod
    def _skill_attack_bonus(effect: str) -> int:
        for token in effect.split(","):
            if token.startswith("atk:+"):
                return int(token[5:])
        return 0

    def _skill_cost(self, skill: Dict[str, Any]) -> int:
        return max(2, 2 + self._skill_attack_bonus(skill["effect"]) // 15)

    def _estimated_attack_damage(self, bonus: int = 0, multiplier: float = 1.0) -> int:
        if self.combat is None:
            return 0
        return max(1, int((self.player["atk"] + bonus) * multiplier) - self.combat["def"])

    @staticmethod
    def _effect_gain(effect: str, stat: str) -> int:
        prefix = f"{stat}:+"
        for token in effect.split(","):
            if token.startswith(prefix):
                return int(token[len(prefix):])
        return 0

    def _combat_healing_items(self) -> List[Tuple[str, int, int]]:
        missing_hp = max(0, int(self.player["max_hp"]) - int(self.player["hp"]))
        missing_douqi = max(
            0,
            int(self.attribute_rules["douqi"]["max"]) - int(self.player["douqi"]),
        )
        candidates = []
        for item_id in self.player.get("items", []):
            item = self.item_rules.get(item_id, {})
            hp_gain = self._effect_gain(item.get("use_effect", ""), "hp")
            douqi_gain = self._effect_gain(item.get("use_effect", ""), "douqi")
            if hp_gain > 0 and missing_hp > 0 and self.check_conditions(item.get("use_condition")):
                effective = min(hp_gain, missing_hp) + min(douqi_gain, missing_douqi)
                candidates.append((item_id, effective, max(0, hp_gain - missing_hp)))
        return sorted(candidates, key=lambda value: (-value[1], value[2]))

    def choose_auto_combat_action(self) -> Tuple[str, Optional[str]]:
        if self.combat is None:
            return "none", None

        hp_ratio = self.player["hp"] / max(1, self.player["max_hp"])
        enemy_ratio = self.combat["hp"] / max(1, self.combat["max_hp"])
        enemy_damage = max(1, self.combat["atk"] - self.player["def"])
        healing_items = self._combat_healing_items()

        if healing_items and (hp_ratio <= 0.40 or self.player["hp"] <= enemy_damage * 2):
            return "item", healing_items[0][0]
        if not healing_items and self.player["hp"] <= enemy_damage:
            return "defend", None

        normal_damage = self._estimated_attack_damage()
        if normal_damage >= self.combat["hp"]:
            return "attack", None

        usable_skills = []
        for skill in self.combat_skills():
            bonus = self._skill_attack_bonus(skill["effect"])
            if bonus <= 0:
                continue
            cost = self._skill_cost(skill)
            if self.player["douqi"] < cost:
                continue
            finisher_threshold = FINISHER_SKILLS.get(skill["id"])
            if finisher_threshold is not None and enemy_ratio > finisher_threshold:
                continue
            damage = self._estimated_attack_damage(bonus, 1.25)
            # 保留最后一轮普通攻击所需的斗气余量，避免高消耗技能无意义溢伤。
            score = min(damage, self.combat["hp"]) / cost
            if damage >= self.combat["hp"]:
                score += 100
            if finisher_threshold is not None:
                score += 20
            usable_skills.append((score, skill["id"]))

        if usable_skills:
            return "skill", max(usable_skills)[1]
        if hp_ratio <= 0.30 and self.combat["hp"] > normal_damage * 2:
            return "defend", None
        return "attack", None

    def auto_battle(self, max_rounds: int = 200) -> str:
        if self.combat is None:
            self.last_message = "当前没有正在进行的战斗。"
            return "none"
        battle_logs = ["自动战斗开始"]
        result = "continue"
        for _ in range(max_rounds):
            action, target = self.choose_auto_combat_action()
            if action == "none":
                break
            result = self.combat_action(action, target)
            battle_logs.append(self.last_message)
            if result != "continue":
                break
        if result == "continue":
            battle_logs.append("自动战斗达到回合上限，已暂停")
        self.last_message = "；".join(log for log in battle_logs if log)
        return result

    def combat_action(self, action: str, skill_id: Optional[str] = None) -> str:
        if self.combat is None:
            return "none"
        combat = self.combat
        logs: List[str] = []
        combat["defending"] = False

        if action == "escape":
            chance = 0.35 + max(0, self.player["spd"] - combat["spd"]) * 0.02
            if combat["can_escape"] and random.random() < min(0.9, chance):
                self.combat = None
                self.advance_time(getattr(self, "combat_time_cost", 0))
                self.last_message = "你抓住空隙脱离了战斗。"
                return "escaped"
            logs.append("你试图撤退，但被对方拦下")
        elif action == "item":
            item_id = skill_id or "item_elixir"
            item = self.item_rules.get(item_id, {})
            hp_gain = self._effect_gain(item.get("use_effect", ""), "hp")
            douqi_gain = self._effect_gain(item.get("use_effect", ""), "douqi")
            if item_id not in self.player["items"] or hp_gain <= 0:
                self.last_message = "背包中没有可用丹药。"
                return "invalid"
            self.player["items"].remove(item_id)
            actual_heal = min(hp_gain, max(0, self.player["max_hp"] - self.player["hp"]))
            actual_douqi = min(
                douqi_gain,
                max(0, self.attribute_rules["douqi"]["max"] - self.player["douqi"]),
            )
            self.player["hp"] += actual_heal
            self.player["douqi"] += actual_douqi
            self._clamp_player_stats()
            logs.append(f"你服下{self.item_name(item_id)}，恢复 {actual_heal} 点生命")
            if actual_douqi:
                logs.append(f"恢复 {actual_douqi} 点斗气")
        elif action == "defend":
            combat["defending"] = True
            logs.append("你凝聚斗气防守")
        else:
            bonus = 0
            multiplier = 1.0
            if action == "skill":
                skill = self.skills.get(skill_id or "")
                if skill is None:
                    self.last_message = "尚未掌握该斗技。"
                    return "invalid"
                cost = self._skill_cost(skill)
                if self.player["douqi"] < cost:
                    self.last_message = "斗气不足，无法施展该斗技。"
                    return "invalid"
                self.player["douqi"] -= cost
                bonus = self._skill_attack_bonus(skill["effect"])
                multiplier = 1.25
                logs.append(f"你施展了{skill['name']}")
                finisher_threshold = FINISHER_SKILLS.get(skill["id"])
                enemy_ratio = combat["hp"] / max(1, combat["max_hp"])
                if finisher_threshold is not None and enemy_ratio <= finisher_threshold:
                    multiplier *= 2
                    logs.append("斗技命中虚弱破绽，触发暴击")
            damage = max(
                1,
                int((self.player["atk"] + bonus) * multiplier)
                - combat["def"]
                + random.randint(-2, 3),
            )
            actual_damage = min(damage, combat["hp"])
            combat["hp"] = max(0, combat["hp"] - actual_damage)
            logs.append(f"对{combat['name']}造成 {actual_damage} 点伤害")

        if combat["hp"] <= 0:
            logs.extend(self._finish_combat_win())
            self.last_message = "；".join(logs)
            return "won"

        enemy_damage = max(
            1,
            combat["atk"] - self.player["def"] + random.randint(-2, 3),
        )
        if combat["defending"]:
            enemy_damage = max(1, enemy_damage // 2)
        self.player["hp"] = max(0, self.player["hp"] - enemy_damage)
        logs.append(f"{combat['name']}反击，造成 {enemy_damage} 点伤害")
        combat["round"] += 1
        if self.player["hp"] <= 0:
            self.player["hp"] = max(1, self.attribute_rules["hp"]["initial"] // 3)
            self.player["stamina"] = 0
            self.player["last_map"] = "map_wutan"
            self.combat = None
            self.advance_time(getattr(self, "combat_time_cost", 0))
            logs.append("你失去意识，被送回乌坦城休养")
            self.last_message = "；".join(logs)
            return "lost"
        self.last_message = "；".join(logs)
        return "continue"

    def _finish_combat_win(self) -> List[str]:
        if self.combat is None:
            return []
        combat = self.combat
        logs = [f"你击败了{combat['name']}"]
        logs.extend(self.apply_effects(f"exp:+{combat['exp_reward']},reputation:+1"))
        self.player["adventure_points"] += 2
        if getattr(self, "combat_is_training", False):
            self.player["training_wins"] += 1
        if combat["drop_table"]:
            drops = combat["drop_table"].split("|")
            for drop in drops:
                parts = drop.split(":")
                if len(parts) == 3 and random.randint(1, 100) <= int(parts[2]):
                    if parts[0] == "item":
                        item_id = parts[1]
                        if item_id not in self.player["items"]:
                            self.player["items"].append(item_id)
                        logs.append(f"获得{self.item_name(item_id)}")
                    elif parts[0] in self.attribute_rules:
                        logs.extend(self.apply_effects(f"{parts[0]}:+{parts[1]}"))
        self.combat = None
        self.advance_time(getattr(self, "combat_time_cost", 0))
        return logs

    def story_requirement(self) -> int:
        phase = self.current_story_phase()
        if phase is None:
            return 0
        if self.current_story_subnode() is not None:
            return max(1, int(phase["requirement"]) // 2)
        return int(phase["requirement"])

    def _sync_story_phase_id(self) -> None:
        stage = int(self.player.get("story_stage", 0))
        self.player["story_phase_id"] = (
            STORY_PHASES[stage]["id"] if stage < len(STORY_PHASES) else ""
        )

    def current_story_phase(self) -> Optional[Dict[str, Any]]:
        stage = int(self.player.get("story_stage", 0))
        return STORY_PHASES[stage] if stage < len(STORY_PHASES) else None

    def current_story_subnode(self) -> Optional[Dict[str, Any]]:
        phase = self.current_story_phase()
        if phase is None:
            return None
        substage = int(self.player.get("story_substage", 0))
        return phase["subnodes"][substage] if substage < len(phase["subnodes"]) else None

    def advance_story(self) -> bool:
        if not self._can_take_free_action():
            return False
        phase = self.current_story_phase()
        if phase is None:
            self.last_message = "主要目标已经全部完成。"
            return False
        requirement = self.story_requirement()
        if self.player["adventure_points"] < requirement:
            self.last_message = (
                f"还缺少 {requirement - self.player['adventure_points']} 点冒险阅历。"
                "请通过探索、修炼或战斗积累。"
            )
            return False
        subnode = self.current_story_subnode()
        if subnode is not None:
            if not self.check_conditions(subnode.get("condition")):
                self.last_message = (
                    f"子节点“{subnode['title']}”尚未达成：{subnode['condition']}。"
                    "完成方式可以自由选择。"
                )
                return False
            self.player["adventure_points"] -= requirement
            self.player["story_substage"] += 1
            logs = self.apply_effects(subnode.get("effect"))
            self.last_message = f"子节点完成：{subnode['title']}"
            if logs:
                self.last_message += "；" + "；".join(logs)
            self.advance_time()
            return True
        if not self.check_conditions(phase.get("condition")):
            self.last_message = (
                f"尚未达到“{phase['title']}”的目标条件：{phase['condition']}。"
                "你可以自由探索、修炼和建立关系后再来。"
            )
            return False
        self.player["adventure_points"] -= requirement
        self.player["story_stage"] += 1
        self.player["story_substage"] = 0
        self._sync_story_phase_id()
        logs = self.apply_effects(phase.get("effect"))
        self.last_message = f"关键目标完成：{phase['title']}"
        if logs:
            self.last_message += "；" + "；".join(logs)
        self.advance_time()
        return True

    def item_name(self, item_id: str) -> str:
        return self.item_rules.get(item_id, {}).get("name", item_id)

    def use_item(self, item_id: str) -> bool:
        if item_id not in self.player["items"]:
            self.last_message = "背包中没有该道具。"
            return False
        item = self.item_rules.get(item_id)
        if item is None or not item.get("use_effect"):
            self.last_message = "该道具当前不能直接使用。"
            return False
        if not self.check_conditions(item.get("use_condition")):
            self.last_message = "尚未满足该道具的使用条件。"
            return False
        self.player["items"].remove(item_id)
        logs = self.apply_effects(item["use_effect"])
        self.last_message = f"使用{item['name']}；" + "；".join(logs)
        return True

    def is_ending(self) -> bool:
        return self.current_story_phase() is None

    def is_finished(self) -> bool:
        return self.is_ending()

    def status_text(self) -> str:
        core_attributes = [
            "level",
            "exp",
            "hp",
            "douqi",
            "atk",
            "def",
            "spd",
            "silver",
            "reputation",
            "alchemy",
            "soul",
        ]
        attribute_text = "｜".join(
            f"{self.attribute_rules[key]['name']} {self.player[key]}"
            for key in core_attributes
            if key in self.attribute_rules
        )
        relationships = []
        for rule in self.relationship_rules.values():
            if not rule.get("visible", False):
                continue
            if rule.get("pre_condition") and not self.check_conditions(
                rule["pre_condition"]
            ):
                continue
            target = rule["target"]
            target_name = self.npc_names.get(target, target)
            relationships.append(
                f"{target_name} {self.relation_value(target)}"
                f"({self.relation_stage(target)})"
            )
        relationship_text = "、".join(relationships) or "无"
        items = "、".join(self.player.get("items", [])) or "无"
        flags = "、".join(self.player.get("flags", [])) or "无"
        node = self.next_schedule_node()
        schedule = (
            f"\n日程：{node['title']}（{self.schedule_countdown_text(node)}）"
            if node
            else ""
        )
        return (
            f"{self.player['name']}｜{self.realm_name()}｜{attribute_text}\n"
            f"{self.time_text()}｜所在区域：{self.current_map()['name']}｜"
            f"冒险阅历 {self.player['adventure_points']}"
            f"｜关键阶段 {self.player['story_stage']}/{len(STORY_PHASES)}"
            f"｜阶段子节点 {self.player['story_substage']}/"
            f"{len(self.current_story_phase()['subnodes']) if self.current_story_phase() else 0}\n"
            f"道具：{items}\n开关：{flags}\n关系：{relationship_text}{schedule}"
        )
