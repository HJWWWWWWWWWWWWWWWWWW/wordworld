"""
数据生成器：生成 500+ 装备和 500+ 道具的 Python 数据文件。
运行：python scripts/generate_items.py
输出：src/wordworld/data/equipment_data.py 和 item_data.py
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ═══════════════════════════════════════════════════════════════════
# 境界分层
# ═══════════════════════════════════════════════════════════════════
TIERS = [
    ("iron",    "铁器",  (1, 9),   4,  3,  8,  50),
    ("refined", "精铁",  (10, 19), 9,  6,  15, 40),
    ("spirit",  "灵器",  (20, 29), 15, 10, 24, 30),
    ("treasure","宝器",  (30, 39), 22, 14, 34, 25),
    ("earth",   "地阶",  (40, 49), 30, 18, 44, 18),
    ("heaven",  "天阶",  (50, 59), 38, 22, 54, 12),
    ("mystic",  "玄阶",  (60, 69), 48, 26, 66, 8),
    ("saint",   "圣阶",  (70, 79), 58, 30, 78, 5),
    ("emperor", "帝阶",  (80, 89), 68, 34, 90, 3),
    ("divine",  "神阶",  (90, 100),80, 40, 105,1),
]

RARITIES = [
    ("common",    "普通", 1.0),
    ("uncommon",  "精良", 1.3),
    ("rare",      "稀有", 1.7),
    ("epic",      "史诗", 2.2),
    ("legendary", "传说", 3.0),
]

# ═══════════════════════════════════════════════════════════════════
# 武器命名表
# ═══════════════════════════════════════════════════════════════════
WEAPON_TYPES = {
    "sword": {
        "category": "剑",
        "names": ["铁剑","青锋剑","寒光剑","紫电剑","龙渊剑","太阿剑","承影剑",
                  "纯钧剑","鱼肠剑","巨阙剑","湛卢剑","赤霄剑","霜华剑","流云剑",
                  "惊鸿剑","游龙剑","七星剑","断水剑","无影剑","破风剑","裂石剑"],
        "rare_names": ["玄铁重剑","冰魄寒光剑","紫薇软剑","碧血照丹青",
                       "诛仙剑","戮仙剑","陷仙剑","绝仙剑","墨眉","天问剑"],
        "epic_names": ["魂灭之剑","龙皇之剑","焚天之剑","虚空之剑",
                       "星辰之剑","太虚之剑","不朽之剑"],
        "legendary_names": ["古帝之剑","万火之王剑","混沌开天剑"],
    },
    "blade": {
        "category": "刀",
        "names": ["铁刀","横刀","斩马刀","断岳刀","裂天刀","虎牙刀","龙雀刀",
                  "凤翅刀","破军刀","碎星刀","血刃","狂风刀","惊雷刀",
                  "偃月刀","绣春刀","雁翎刀","苗刀","环首刀","斩铁刀","青龙刀"],
        "rare_names": ["屠龙刀","血饮狂刀","虎魄刀","鸣鸿刀","大夏龙雀",
                       "寒月刀","新亭侯刀","毒匕寒月刃"],
        "epic_names": ["噬魂之刀","灭世之刀","苍穹之刃","混沌之刃",
                       "万魂斩","星辰裂"],
        "legendary_names": ["古帝战刀","无尽之刃","破天之刃"],
    },
    "spear": {
        "category": "枪",
        "names": ["长枪","银枪","破阵枪","穿云枪","点钢枪","钩镰枪",
                  "龙胆枪","梅花枪","凤嘴枪","芦叶枪","透甲枪","飞燕枪",
                  "穿心枪","梨花枪","丈八蛇矛","虎头湛金枪","绿沉枪",
                  "五虎断魂枪","霸王枪","沥泉枪"],
        "rare_names": ["方天画戟·枪","蟠龙金枪","紫电银枪","神威烈水枪",
                       "帝道之枪","三尖两刃枪"],
        "epic_names": ["破天之枪","屠龙之枪","虚无法枪","星辰之枪",
                       "混沌战枪"],
        "legendary_names": ["古帝神枪","裁决之枪"],
    },
    "ruler": {
        "category": "尺",
        "names": ["铁尺","玄铁尺","精铁尺","量天尺","断山尺","镇魂尺",
                  "玄重尺","墨玉尺","紫金尺","寒铁尺","风云尺","撼地尺",
                  "定海尺","铁骨尺","断念尺","镇岳尺"],
        "rare_names": ["玄重龙尺","黑曜裁决尺","幽冥镇魂尺","万象天引尺",
                       "天罚之尺"],
        "epic_names": ["虚空之尺","混沌量天尺","万魂镇岳尺"],
        "legendary_names": ["古帝玄尺","天罚裁决尺"],
    },
    "staff": {
        "category": "杖",
        "names": ["木杖","铁杖","灵木杖","龙骨杖","魂木杖","紫檀杖",
                  "降龙杖","伏虎杖","千钧杖","盘龙杖","风雷杖","星辰杖",
                  "玄冰杖","烈焰杖","碧波杖","青木杖","淬魂杖","虎头杖"],
        "rare_names": ["万兽之杖","幽冥鬼杖","圣光裁决杖","自然之杖",
                       "元素掌控者","灵魂低语者"],
        "epic_names": ["世界树之杖","混沌魔杖","虚空法杖","星辰之杖"],
        "legendary_names": ["古帝权杖","万象归宗之杖"],
    },
    "fan": {
        "category": "扇",
        "names": ["纸扇","铁扇","竹扇","玉骨扇","山河扇","秋风扇",
                  "鹤羽扇","凤羽扇","阴阳扇","乾坤扇","风云扇","紫霞扇",
                  "碧波扇","烟雨扇","寒梅扇","凌波扇","金翎扇","七宝扇"],
        "rare_names": ["山河社稷扇","天罡北斗扇","紫薇星辰扇",
                       "五火七禽扇","阴阳两仪扇"],
        "epic_names": ["焚天之扇","混沌之扇","虚空之扇"],
        "legendary_names": ["古帝之扇","万象天引扇"],
    },
    "bow": {
        "category": "弓",
        "names": ["猎弓","短弓","长弓","穿云弓","落日弓","追风弓",
                  "惊鸿弓","射日弓","逐月弓","破天弓","寒冰弓","烈焰弓",
                  "裂风弓","碎星弓","落雁弓","追魂弓","开山弓","龙筋弓"],
        "rare_names": ["射日神弓","苍穹裂风弓","星辰落月弓",
                       "冰火双极弓","万钧破天弓"],
        "epic_names": ["混沌之弓","虚空之弓","灭世之弓"],
        "legendary_names": ["古帝神弓","落日星辰弓"],
    },
    "halberd": {
        "category": "戟",
        "names": ["短戟","方天戟","破军戟","青龙戟","白虎戟","朱雀戟",
                  "玄武戟","画杆戟","月牙戟","三叉戟","虎威戟","龙鳞戟",
                  "裂地戟","断魂戟","破阵戟","铁脊戟","飞将戟"],
        "rare_names": ["方天画戟","天龙破城戟","雷神之戟",
                       "银剪戟","蟠龙金戟"],
        "epic_names": ["混沌战戟","虚空之戟","灭世方天戟"],
        "legendary_names": ["古帝神戟","裁决之戟"],
    },
    "whip": {
        "category": "鞭",
        "names": ["软鞭","铁鞭","竹节鞭","虎尾鞭","龙筋鞭","雷鞭",
                  "风鞭","银丝鞭","金丝鞭","紫藤鞭","寒铁鞭","烈火鞭",
                  "蛇骨鞭","九节鞭","追魂鞭","断岳鞭"],
        "rare_names": ["九天雷鞭","龙筋追魂鞭","冰火双极鞭",
                       "星辰锁链","万兽之鞭"],
        "epic_names": ["虚空之鞭","混沌之鞭","灭世雷鞭"],
        "legendary_names": ["古帝神鞭","万法归宗鞭"],
    },
    "claw": {
        "category": "爪",
        "names": ["铁爪","精铁爪","裂风爪","碎金爪","虎牙爪","龙爪",
                  "鹰爪","熊爪","狼爪","幽冥爪","破甲爪","擒龙爪",
                  "寒冰爪","烈焰爪","追魂爪","裂骨爪"],
        "rare_names": ["龙之怒爪","幽冥鬼爪","九天雷爪",
                       "冰霜龙爪","裂天之爪"],
        "epic_names": ["虚空之爪","混沌之爪","噬魂龙爪"],
        "legendary_names": ["古帝龙爪","苍穹裂空爪"],
    },
}

# ═══════════════════════════════════════════════════════════════════
# 防具命名表
# ═══════════════════════════════════════════════════════════════════
ARMOR_TYPES = {
    "robe": {
        "category": "袍",
        "names": ["布袍","棉袍","丝袍","绸袍","灵绸袍","天丝袍",
                  "云锦袍","彩霞袍","紫云袍","青霜袍","白鹤袍","金缕袍",
                  "月华袍","星河袍","碧落袍","烟霞袍","流云袍","鹤氅袍"],
        "rare_names": ["九天玄女袍","星辰织锦袍","万象天引袍",
                       "太虚归元袍","混沌天丝袍"],
        "epic_names": ["虚空之袍","不朽之袍"],
        "legendary_names": ["古帝圣袍"],
    },
    "armor": {
        "category": "甲",
        "names": ["皮甲","铁甲","锁子甲","明光铠","鱼鳞甲","山文甲",
                  "乌锤甲","玄铁甲","金刚甲","玄武甲","麒麟甲","龙鳞甲",
                  "狻猊铠","狴犴铠","饕餮铠","貔貅铠","朱雀甲","白虎甲"],
        "rare_names": ["不灭战甲","万兽之王铠","星辰陨铁甲",
                       "龙血战甲","混沌玄甲"],
        "epic_names": ["虚空战甲","不朽之甲"],
        "legendary_names": ["古帝神甲"],
    },
    "cloak": {
        "category": "斗篷",
        "names": ["麻布斗篷","粗布斗篷","棉布斗篷","隐风斗篷","潜行斗篷",
                  "夜幕斗篷","迷雾斗篷","暗影斗篷","星辰斗篷","虚空斗篷",
                  "疾风斗篷","幻影斗篷","黑羽斗篷","鸦羽斗篷","幽灵斗篷",
                  "月影斗篷"],
        "rare_names": ["暗夜王者斗篷","星辰隐匿斗篷","虚空行者斗篷",
                       "风之主宰斗篷"],
        "epic_names": ["混沌斗篷","不朽斗篷"],
        "legendary_names": ["古帝神篷"],
    },
    "belt": {
        "category": "腰带",
        "names": ["布带","皮带","麻绳带","兽筋带","虎皮带","犀皮带",
                  "蟒皮带","龙筋带","玉带","金缕带","银丝带","紫金带",
                  "玄铁带","灵玉带","星辰带","蛟龙带"],
        "rare_names": ["龙筋玉带","虚空之缚","星辰束带",
                       "万兽之王带","混沌之束"],
        "epic_names": ["虚空腰带","不朽束带"],
        "legendary_names": ["古帝圣带"],
    },
    "boots": {
        "category": "靴",
        "names": ["布靴","草鞋","皮靴","鹿皮靴","犀皮靴","踏云靴",
                  "追风靴","凌云靴","登云靴","飞云靴","逐日靴","流星靴",
                  "御风靴","腾云靴","缩地靴","浮光靴"],
        "rare_names": ["追星逐月靴","踏雪无痕靴","九天凌云靴",
                       "虚空行者靴","万界穿梭靴"],
        "epic_names": ["混沌之靴","不朽之靴"],
        "legendary_names": ["古帝神靴"],
    },
    "helmet": {
        "category": "盔",
        "names": ["铁盔","皮盔","铜盔","银盔","金盔","紫金冠",
                  "凤翅冠","麒麟冠","龙首盔","虎头冠","鹰盔","玄铁盔",
                  "狻猊冠","獬豸冠"],
        "rare_names": ["不灭之冠","星辰之盔","龙血之冠",
                       "万兽王冠","混沌头盔"],
        "epic_names": ["虚空之冠","不朽之冠"],
        "legendary_names": ["古帝圣冠"],
    },
}

# ═══════════════════════════════════════════════════════════════════
# 饰品命名表
# ═══════════════════════════════════════════════════════════════════
ACCESSORY_TYPES = {
    "ring": {
        "category": "戒指",
        "names": ["铁戒","铜戒","银戒","金戒","玉戒","纳戒",
                  "灵戒","魂戒","星辰戒","日月戒","虚空戒","寒冰戒",
                  "烈焰戒","碧波戒","紫电戒","青木戒","空间戒"],
        "rare_names": ["虚空之戒","万火之王戒","星辰之源戒",
                       "混沌之戒","不朽之戒"],
        "epic_names": ["古帝之戒"],
        "legendary_names": ["创世之戒"],
    },
    "pendant": {
        "category": "吊坠",
        "names": ["石坠","铜坠","银坠","金坠","玉坠","灵玉坠",
                  "魂玉坠","星辰坠","月华坠","日光坠","紫晶坠",
                  "蓝宝石坠","碧玉坠","琥珀坠","玛瑙坠","水晶坠"],
        "rare_names": ["星辰之心坠","月神之泪坠","虚空之源坠",
                       "混沌之眼坠","不朽之心坠"],
        "epic_names": ["古帝之坠"],
        "legendary_names": ["万象归宗坠"],
    },
    "jade": {
        "category": "宝玉",
        "names": ["粗玉","青玉","白玉","黄玉","紫玉","墨玉",
                  "温玉","寒玉","灵玉","魂玉","养魂玉","镇魂玉",
                  "星辰玉","日月玉","血玉","冰玉","火玉","龙纹玉","凤纹玉"],
        "rare_names": ["万魂归宗玉","星辰之源玉","虚空之玉",
                       "混沌之玉","不朽之玉"],
        "epic_names": ["古帝之玉"],
        "legendary_names": ["创世之玉"],
    },
    "amulet": {
        "category": "护符",
        "names": ["木符","石符","铜符","银符","金符","玉符",
                  "灵符","魂符","镇魂符","护身符","平安符","长生符",
                  "金刚符","清心符","辟邪符","聚灵符","招财符","如意符"],
        "rare_names": ["万法不侵符","星辰护体符","虚空之符",
                       "混沌之符","不朽之符"],
        "epic_names": ["古帝之符"],
        "legendary_names": ["创世之符"],
    },
    "bracelet": {
        "category": "手镯",
        "names": ["铜镯","银镯","金镯","玉镯","灵玉镯",
                  "紫金镯","星辰镯","月光镯","日光镯","碧波镯",
                  "寒冰镯","烈焰镯","龙纹镯","凤纹镯","麒麟镯","如意镯"],
        "rare_names": ["虚空之镯","星辰之源镯","混沌之镯",
                       "不朽之镯"],
        "epic_names": ["古帝之镯"],
        "legendary_names": ["创世之镯"],
    },
}

# ═══════════════════════════════════════════════════════════════════
# 消耗品设计（参考原著丹药体系）
# ═══════════════════════════════════════════════════════════════════
CONSUMABLES: List[Dict[str, Any]] = [
    # ── 回复类（HP）──
    {"id":"item_healing_powder","name":"止血散","type":"consumable","tier":"iron",
     "effect":"hp:+30","desc":"最基础的伤药，佣兵常备。","price_buy":10,"price_sell":5},
    {"id":"item_recover_pill_1","name":"回春丹","type":"consumable","tier":"iron",
     "effect":"hp:+50","desc":"一品丹药，治愈轻微伤势。","price_buy":20,"price_sell":10},
    {"id":"item_blood_pill","name":"补血丹","type":"consumable","tier":"iron",
     "effect":"hp:+80","desc":"补充气血的基础丹药。","price_buy":30,"price_sell":15},
    {"id":"item_first_aid_kit","name":"急救包","type":"consumable","tier":"iron",
     "effect":"hp:+100","desc":"佣兵随身携带的急救包裹。","price_buy":35,"price_sell":17},
    {"id":"item_bandage","name":"金创药膏","type":"consumable","tier":"iron",
     "effect":"hp:+40","desc":"外敷药膏，止血生肌。","price_buy":12,"price_sell":6},
    {"id":"item_recover_pill_2","name":"续命丹","type":"consumable","tier":"refined",
     "effect":"hp:+120","desc":"二品丹药，可续断骨、愈重伤。","price_buy":50,"price_sell":25},
    {"id":"item_flesh_pill","name":"生肌丹","type":"consumable","tier":"refined",
     "effect":"hp:+180","desc":"促进血肉再生的二品丹药。","price_buy":70,"price_sell":35},
    {"id":"item_bone_pill","name":"接骨丹","type":"consumable","tier":"refined",
     "effect":"hp:+150","desc":"专治骨折筋断的二品丹药。","price_buy":60,"price_sell":30},
    {"id":"item_recover_pill_3","name":"大还丹","type":"consumable","tier":"spirit",
     "effect":"hp:+280,douqi:+20","desc":"三品丹药，武林中人梦寐以求的疗伤圣药。","price_buy":120,"price_sell":60},
    {"id":"item_marrow_pill","name":"洗髓丹","type":"consumable","tier":"spirit",
     "effect":"hp:+350","desc":"三品丹药，洗筋伐髓，重塑根骨。","price_buy":150,"price_sell":75},
    {"id":"item_purple_blood_pill","name":"紫血大还丹","type":"consumable","tier":"spirit",
     "effect":"hp:+400","desc":"三品丹药中的上品，紫色丹纹。","price_buy":180,"price_sell":90},
    {"id":"item_recover_pill_4","name":"九转还魂丹","type":"consumable","tier":"treasure",
     "effect":"hp:+500,douqi:+40","desc":"四品丹药，只要还有一口气就能救回来。","price_buy":250,"price_sell":125},
    {"id":"item_purple_heart_pill","name":"紫心破障丹","type":"consumable","tier":"treasure",
     "effect":"hp:+600","desc":"四品丹药，紫色丹心蕴含磅礴生机。","price_buy":300,"price_sell":150},
    {"id":"item_recover_pill_5","name":"生生造化丹","type":"consumable","tier":"earth",
     "effect":"hp:+800,douqi:+80","desc":"五品丹药，生死人肉白骨的传闻并非虚言。","price_buy":500,"price_sell":250},
    {"id":"item_dragon_blood_pill","name":"龙血丹","type":"consumable","tier":"earth",
     "effect":"hp:+1000","desc":"五品丹药，蕴含一丝龙族血脉之力。","price_buy":600,"price_sell":300},
    {"id":"item_recover_pill_6","name":"天魂融血丹","type":"consumable","tier":"heaven",
     "effect":"hp:+1500,douqi:+150","desc":"六品丹药，以天魂为引，融血为基。","price_buy":1000,"price_sell":500},
    {"id":"item_phoenix_pill","name":"凤血涅槃丹","type":"consumable","tier":"heaven",
     "effect":"hp:+2000","desc":"六品丹药，凤凰涅槃、浴火重生之意。","price_buy":1200,"price_sell":600},
    {"id":"item_recover_pill_7","name":"造化生生丹","type":"consumable","tier":"mystic",
     "effect":"hp:+3000,douqi:+300","desc":"七品丹药，夺天地之造化。","price_buy":2500,"price_sell":1250},
    {"id":"item_primordial_pill","name":"阴阳玄龙丹","type":"consumable","tier":"mystic",
     "effect":"hp:+3500","desc":"七品丹药，玄炉老人成名之作，蕴含阴阳二气。","price_buy":3000,"price_sell":1500},
    {"id":"item_recover_pill_8","name":"菩提大还丹","type":"consumable","tier":"saint",
     "effect":"hp:+5000,douqi:+500","desc":"八品丹药，需菩提子为引。","price_buy":5000,"price_sell":2500},
    {"id":"item_soul_restore_pill","name":"魂元归位丹","type":"consumable","tier":"saint",
     "effect":"hp:+6000","desc":"八品丹药，可修补受损的灵魂本源。","price_buy":6000,"price_sell":3000},
    {"id":"item_recover_pill_9","name":"九转玄丹","type":"consumable","tier":"emperor",
     "effect":"hp:+8000,douqi:+800","desc":"九品丹药，每一次转火都是天地异象。","price_buy":10000,"price_sell":5000},
    {"id":"item_god_pill","name":"帝品雏丹","type":"consumable","tier":"divine",
     "effect":"hp:+15000,douqi:+1500","desc":"接近帝品丹药的存在，威能莫测。","price_buy":25000,"price_sell":12500},

    # ── 回气类（灵力）──
    {"id":"item_qi_powder","name":"聚气散","type":"consumable","tier":"iron",
     "effect":"douqi:+30","desc":"加快灵力凝聚的基础药散。","price_buy":15,"price_sell":7},
    {"id":"item_qi_pill_1","name":"回气丹","type":"consumable","tier":"iron",
     "effect":"douqi:+60","desc":"一品回气丹药。","price_buy":30,"price_sell":15},
    {"id":"item_qi_pill_2","name":"养气丹","type":"consumable","tier":"refined",
     "effect":"douqi:+120","desc":"二品丹药，滋养气旋。","price_buy":60,"price_sell":30},
    {"id":"item_qi_pill_3","name":"三纹青灵丹","type":"consumable","tier":"spirit",
     "effect":"douqi:+200","desc":"三品丹药，丹身三道青纹，药力精纯。","price_buy":120,"price_sell":60},
    {"id":"item_qi_pill_4","name":"聚气化晶丹","type":"consumable","tier":"treasure",
     "effect":"douqi:+350","desc":"四品丹药，可化气为晶储存体内。","price_buy":250,"price_sell":125},
    {"id":"item_qi_pill_5","name":"灵力凝丹","type":"consumable","tier":"earth",
     "effect":"douqi:+600","desc":"五品丹药，将天地元气凝为实质。","price_buy":500,"price_sell":250},
    {"id":"item_qi_pill_6","name":"天罡聚气丹","type":"consumable","tier":"heaven",
     "effect":"douqi:+1000","desc":"六品丹药，引天罡之气入体。","price_buy":1000,"price_sell":500},
    {"id":"item_qi_pill_7","name":"虚空引气丹","type":"consumable","tier":"mystic",
     "effect":"douqi:+1800","desc":"七品丹药，自虚空中牵引能量。","price_buy":2500,"price_sell":1250},
    {"id":"item_qi_pill_8","name":"星辰灵力丹","type":"consumable","tier":"saint",
     "effect":"douqi:+3000","desc":"八品丹药，蕴含星辰之力。","price_buy":5000,"price_sell":2500},
    {"id":"item_qi_pill_9","name":"帝气归元丹","type":"consumable","tier":"emperor",
     "effect":"douqi:+5000","desc":"九品丹药，可容纳帝之本源。","price_buy":10000,"price_sell":5000},

    # ── 双重回复 ──
    {"id":"item_dual_pill_1","name":"双灵丹","type":"consumable","tier":"refined",
     "effect":"hp:+100,douqi:+50","desc":"同时恢复气血与灵力的二品丹药。","price_buy":80,"price_sell":40},
    {"id":"item_dual_pill_2","name":"阴阳双生丹","type":"consumable","tier":"spirit",
     "effect":"hp:+250,douqi:+150","desc":"三品丹药，阴阳调和，性命双修。","price_buy":200,"price_sell":100},
    {"id":"item_dual_pill_3","name":"天地双元丹","type":"consumable","tier":"treasure",
     "effect":"hp:+450,douqi:+300","desc":"四品丹药，纳天地之气于一体。","price_buy":400,"price_sell":200},
    {"id":"item_dual_pill_4","name":"龙虎双形丹","type":"consumable","tier":"earth",
     "effect":"hp:+800,douqi:+500","desc":"五品丹药，龙虎交汇，气力双增。","price_buy":800,"price_sell":400},
    {"id":"item_dual_pill_5","name":"日月同辉丹","type":"consumable","tier":"heaven",
     "effect":"hp:+1500,douqi:+1000","desc":"六品丹药，日月精华凝于一炉。","price_buy":1800,"price_sell":900},
    {"id":"item_dual_pill_6","name":"混沌归元丹","type":"consumable","tier":"mystic",
     "effect":"hp:+3000,douqi:+2000","desc":"七品丹药，混沌之力归一。","price_buy":4000,"price_sell":2000},
    {"id":"item_dual_pill_7","name":"万象归宗丹","type":"consumable","tier":"saint",
     "effect":"hp:+5000,douqi:+3500","desc":"八品丹药，万法归宗，万源归一。","price_buy":8000,"price_sell":4000},
    {"id":"item_dual_pill_8","name":"帝道无极丹","type":"consumable","tier":"emperor",
     "effect":"hp:+8000,douqi:+6000","desc":"九品丹药，帝道无极，生生不息。","price_buy":15000,"price_sell":7500},

    # ── 属性增益类 ──
    {"id":"item_str_pill_1","name":"力量丹","type":"consumable","tier":"iron",
     "effect":"atk:+5","desc":"短时间内提升攻击力。","price_buy":40,"price_sell":20},
    {"id":"item_str_pill_2","name":"金刚丹","type":"consumable","tier":"refined",
     "effect":"atk:+12,def:+5","desc":"二品丹药，肉身如金刚。","price_buy":80,"price_sell":40},
    {"id":"item_str_pill_3","name":"龙力丹","type":"consumable","tier":"spirit",
     "effect":"atk:+20","desc":"三品丹药，借龙族之力强化肉身。","price_buy":150,"price_sell":75},
    {"id":"item_str_pill_4","name":"霸体丹","type":"consumable","tier":"treasure",
     "effect":"atk:+30,def:+15","desc":"四品丹药，短时间内肉身无敌。","price_buy":300,"price_sell":150},
    {"id":"item_spd_pill_1","name":"疾风丹","type":"consumable","tier":"iron",
     "effect":"spd:+5","desc":"提升身法速度。","price_buy":30,"price_sell":15},
    {"id":"item_spd_pill_2","name":"追风丹","type":"consumable","tier":"refined",
     "effect":"spd:+12","desc":"二品丹药，疾如追风。","price_buy":70,"price_sell":35},
    {"id":"item_spd_pill_3","name":"雷闪丹","type":"consumable","tier":"spirit",
     "effect":"spd:+20","desc":"三品丹药，动如雷霆。","price_buy":140,"price_sell":70},
    {"id":"item_spd_pill_4","name":"缩地丹","type":"consumable","tier":"treasure",
     "effect":"spd:+30","desc":"四品丹药，一步十里。","price_buy":280,"price_sell":140},
    {"id":"item_soul_pill_1","name":"醒神丹","type":"consumable","tier":"refined",
     "effect":"soul:+5","desc":"提升灵魂感知力。","price_buy":100,"price_sell":50},
    {"id":"item_soul_pill_2","name":"养魂丹","type":"consumable","tier":"spirit",
     "effect":"soul:+12","desc":"三品丹药，滋养灵魂本源。","price_buy":200,"price_sell":100},
    {"id":"item_soul_pill_3","name":"凝魂丹","type":"consumable","tier":"treasure",
     "effect":"soul:+25","desc":"四品丹药，凝聚灵魂之力。","price_buy":400,"price_sell":200},
    {"id":"item_soul_pill_4","name":"魂元丹","type":"consumable","tier":"earth",
     "effect":"soul:+40","desc":"五品丹药，大幅强化灵魂。","price_buy":800,"price_sell":400},
    {"id":"item_def_pill_1","name":"铁骨丹","type":"consumable","tier":"refined",
     "effect":"def:+8","desc":"淬炼筋骨，提升防御。","price_buy":70,"price_sell":35},
    {"id":"item_def_pill_2","name":"玄武丹","type":"consumable","tier":"spirit",
     "effect":"def:+18","desc":"三品丹药，身如玄武。","price_buy":160,"price_sell":80},
    {"id":"item_def_pill_3","name":"不灭丹","type":"consumable","tier":"treasure",
     "effect":"def:+30","desc":"四品丹药，肉身难灭。","price_buy":350,"price_sell":175},

    # ── 突破辅助类 ──
    {"id":"item_break_pill_1","name":"破境丹","type":"consumable","tier":"spirit",
     "effect":"progress:+20","desc":"三品丹药，提升突破概率。","price_buy":300,"price_sell":150},
    {"id":"item_break_pill_2","name":"破障丹","type":"consumable","tier":"treasure",
     "effect":"progress:+35","desc":"四品丹药，破除修炼障碍。","price_buy":600,"price_sell":300},
    {"id":"item_break_pill_3","name":"冲关丹","type":"consumable","tier":"earth",
     "effect":"progress:+50","desc":"五品丹药，辅助冲击瓶颈。","price_buy":1200,"price_sell":600},
    {"id":"item_break_pill_4","name":"天劫渡厄丹","type":"consumable","tier":"heaven",
     "effect":"progress:+70","desc":"六品丹药，渡天劫时保命底牌。","price_buy":3000,"price_sell":1500},
    {"id":"item_break_pill_5","name":"圣劫涅槃丹","type":"consumable","tier":"mystic",
     "effect":"progress:+100","desc":"七品丹药，以此丹辅助突破，九死一生亦无悔。","price_buy":8000,"price_sell":4000},
    {"id":"item_break_pill_6","name":"帝道丹","type":"consumable","tier":"saint",
     "effect":"progress:+150","desc":"八品丹药，传闻只有远古八族能够炼制。","price_buy":20000,"price_sell":10000},

    # ── 特殊丹药 ──
    {"id":"item_antidote_1","name":"解毒丹","type":"consumable","tier":"iron",
     "effect":"cure:poison","desc":"解除常见毒素。","price_buy":25,"price_sell":12},
    {"id":"item_antidote_2","name":"百毒解","type":"consumable","tier":"refined",
     "effect":"cure:poison","desc":"二品解药，解百毒。","price_buy":60,"price_sell":30},
    {"id":"item_antidote_3","name":"万毒清","type":"consumable","tier":"spirit",
     "effect":"cure:poison","desc":"三品解药，万毒可清。","price_buy":150,"price_sell":75},
    {"id":"item_antidote_4","name":"七彩毒经解","type":"consumable","tier":"treasure",
     "effect":"cure:poison","desc":"以小医仙毒经为基，克制七彩毒瘴。","price_buy":350,"price_sell":175},
    {"id":"item_poison_1","name":"毒粉","type":"consumable","tier":"iron",
     "effect":"inflict_poison:1,30","desc":"涂抹于武器上的基础毒药（中毒1层，每回合30伤害）。","price_buy":20,"price_sell":10},
    {"id":"item_poison_2","name":"化骨散","type":"consumable","tier":"refined",
     "effect":"inflict_poison:2,60","desc":"二品毒药，可化骨肉为脓水。","price_buy":80,"price_sell":40},
    {"id":"item_poison_3","name":"七蛇毒","type":"consumable","tier":"spirit",
     "effect":"inflict_poison:3,100","desc":"三品毒药，七种蛇毒混合炼制。","price_buy":200,"price_sell":100},
    {"id":"item_poison_4","name":"七彩毒瘴","type":"consumable","tier":"treasure",
     "effect":"inflict_poison:4,200","desc":"四品毒药，来自出云帝国七彩毒经。","price_buy":500,"price_sell":250},
    {"id":"item_poison_5","name":"万毒噬心散","type":"consumable","tier":"earth",
     "effect":"inflict_poison:5,400","desc":"五品毒药，万毒噬心，神仙难救。","price_buy":1200,"price_sell":600},

    # ── 爆发类 ──
    {"id":"item_rage_pill","name":"狂化丹","type":"consumable","tier":"refined",
     "effect":"atk:+20,def:-10","desc":"激发潜能，换取瞬间的狂暴力量。","price_buy":100,"price_sell":50},
    {"id":"item_blood_boil_pill","name":"沸血丹","type":"consumable","tier":"spirit",
     "effect":"atk:+35,hp:-50","desc":"燃烧精血换取爆发力。","price_buy":200,"price_sell":100},
    {"id":"item_desperation_pill","name":"绝命丹","type":"consumable","tier":"treasure",
     "effect":"atk:+60,hp:-120","desc":"绝境中燃烧全部生机。","price_buy":400,"price_sell":200},
    {"id":"item_sacrifice_pill","name":"祭魂丹","type":"consumable","tier":"earth",
     "effect":"atk:+100,soul:-10","desc":"以灵魂之力祭献换取无上力量。","price_buy":1000,"price_sell":500},

    # ── 额外回复药剂 ──
    {"id":"item_elexir_of_life","name":"生命之泉","type":"consumable","tier":"treasure",
     "effect":"hp:+700","desc":"精灵族秘制的圣水。","price_buy":350,"price_sell":175},
    {"id":"item_phoenix_ash","name":"凤凰灰烬","type":"consumable","tier":"heaven",
     "effect":"hp:+2500","desc":"凤凰涅槃后留下的灰烬，蕴含重生之力。","price_buy":1500,"price_sell":750},
    {"id":"item_moon_well_water","name":"月井之水","type":"consumable","tier":"spirit",
     "effect":"hp:+200,douqi:+100","desc":"月光下收集的灵水。","price_buy":100,"price_sell":50},
    {"id":"item_star_dew","name":"星辰露","type":"consumable","tier":"earth",
     "effect":"hp:+600,douqi:+300","desc":"星辉凝露，药性温和而持久。","price_buy":700,"price_sell":350},
    {"id":"item_ancient_pill_fragment","name":"古丹碎片","type":"consumable","tier":"mystic",
     "effect":"hp:+4000","desc":"远古丹药的碎片，药力依然惊人。","price_buy":3500,"price_sell":1750},
    {"id":"item_blood_essence_potion","name":"精血药剂","type":"consumable","tier":"refined",
     "effect":"hp:+80,douqi:+40","desc":"以魔兽精血炼制的回复剂。","price_buy":65,"price_sell":32},
    {"id":"item_mana_potion","name":"魔力药剂","type":"consumable","tier":"spirit",
     "effect":"douqi:+180","desc":"蓝色发光的魔法药剂。","price_buy":110,"price_sell":55},
    {"id":"item_berserker_potion","name":"狂战士药剂","type":"consumable","tier":"earth",
     "effect":"atk:+45,def:-20","desc":"以理智换力量的禁药。","price_buy":900,"price_sell":450},
    {"id":"item_iron_skin_potion","name":"铁皮药剂","type":"consumable","tier":"refined",
     "effect":"def:+15","desc":"让皮肤坚硬如铁的药剂。","price_buy":75,"price_sell":37},
    {"id":"item_haste_potion","name":"急速药剂","type":"consumable","tier":"treasure",
     "effect":"spd:+25","desc":"让身形快如闪电。","price_buy":260,"price_sell":130},
    {"id":"item_double_damage_pill","name":"狂战丹","type":"consumable","tier":"heaven",
     "effect":"atk:+80,hp:-200","desc":"以生命力换取毁灭性力量。","price_buy":2000,"price_sell":1000},
    {"id":"item_recovery_salve","name":"疗伤药膏","type":"consumable","tier":"iron",
     "effect":"hp:+20","desc":"外敷用的廉价药膏。","price_buy":8,"price_sell":4},
    {"id":"item_spirit_recovery_tea","name":"还神茶","type":"consumable","tier":"refined",
     "effect":"douqi:+80","desc":"安宁心神的灵茶。","price_buy":45,"price_sell":22},
    {"id":"item_emergency_pill","name":"急救丹","type":"consumable","tier":"treasure",
     "effect":"hp:+400,douqi:+200","desc":"佣兵公会配发的战斗急救药。","price_buy":320,"price_sell":160},
    {"id":"item_troll_blood","name":"巨魔之血","type":"consumable","tier":"earth",
     "effect":"hp:+500","desc":"巨魔心脏中提取的鲜血。","price_buy":550,"price_sell":275},
    {"id":"item_ancient_essence","name":"远古精华","type":"consumable","tier":"saint",
     "effect":"hp:+4000,douqi:+2000","desc":"从远古遗迹中提炼的能量精华。","price_buy":12000,"price_sell":6000},
    {"id":"item_divine_dew","name":"神露","type":"consumable","tier":"divine",
     "effect":"hp:+10000,douqi:+10000","desc":"据说来自神界的甘露。","price_buy":50000,"price_sell":25000},
    # 更多消耗品变体
    {"id":"item_hp_small","name":"小回复药","type":"consumable","tier":"iron","effect":"hp:+25","desc":"最便宜的回复药水。","price_buy":8,"price_sell":4},
    {"id":"item_hp_medium","name":"中回复药","type":"consumable","tier":"refined","effect":"hp:+80","desc":"标准品质的回复药水。","price_buy":40,"price_sell":20},
    {"id":"item_hp_large","name":"大回复药","type":"consumable","tier":"spirit","effect":"hp:+200","desc":"高品质的回复药水。","price_buy":100,"price_sell":50},
    {"id":"item_hp_super","name":"超级回复药","type":"consumable","tier":"treasure","effect":"hp:+500","desc":"顶级的回复药水。","price_buy":300,"price_sell":150},
    {"id":"item_hp_elite","name":"精英回复药","type":"consumable","tier":"earth","effect":"hp:+1000","desc":"专为强者炼制的回复药。","price_buy":800,"price_sell":400},
    {"id":"item_mp_small","name":"小回气药","type":"consumable","tier":"iron","effect":"douqi:+20","desc":"最便宜的回气药水。","price_buy":10,"price_sell":5},
    {"id":"item_mp_medium","name":"中回气药","type":"consumable","tier":"refined","effect":"douqi:+60","desc":"标准品质的回气药水。","price_buy":50,"price_sell":25},
    {"id":"item_mp_large","name":"大回气药","type":"consumable","tier":"spirit","effect":"douqi:+150","desc":"高品质的回气药水。","price_buy":120,"price_sell":60},
    {"id":"item_mp_super","name":"超级回气药","type":"consumable","tier":"treasure","effect":"douqi:+400","desc":"顶级的回气药水。","price_buy":350,"price_sell":175},
    {"id":"item_mp_elite","name":"精英回气药","type":"consumable","tier":"earth","effect":"douqi:+800","desc":"专为强者炼制的回气药。","price_buy":900,"price_sell":450},
    {"id":"item_stamina_pill","name":"精力丹","type":"consumable","tier":"iron","effect":"stamina:+20","desc":"恢复体力的丹药。","price_buy":25,"price_sell":12},
    {"id":"item_stamina_pill_2","name":"活力丹","type":"consumable","tier":"spirit","effect":"stamina:+50","desc":"大幅恢复体力的丹药。","price_buy":80,"price_sell":40},
    {"id":"item_full_recovery","name":"全回复药","type":"consumable","tier":"heaven","effect":"hp:+3000,douqi:+2000,stamina:+50","desc":"全面恢复状态的灵药。","price_buy":5000,"price_sell":2500},
    {"id":"item_crit_pill","name":"会心丹","type":"consumable","tier":"refined","effect":"crit_rate:+10","desc":"临时提升暴击率。","price_buy":90,"price_sell":45},
    {"id":"item_crit_pill_2","name":"致命丹","type":"consumable","tier":"spirit","effect":"crit_rate:+25","desc":"大幅提升暴击率。","price_buy":200,"price_sell":100},
    {"id":"item_dodge_pill","name":"闪避丹","type":"consumable","tier":"refined","effect":"dodge_rate:+10","desc":"临时提升闪避率。","price_buy":90,"price_sell":45},
    {"id":"item_dodge_pill_2","name":"幻影丹","type":"consumable","tier":"spirit","effect":"dodge_rate:+25","desc":"大幅提升闪避率。","price_buy":200,"price_sell":100},
    {"id":"item_hp_regen_pill","name":"回春露","type":"consumable","tier":"spirit","effect":"hp_regen:20,5","desc":"每回合恢复20HP，持续5回合。","price_buy":180,"price_sell":90},
    {"id":"item_hp_regen_pill_2","name":"长生露","type":"consumable","tier":"treasure","effect":"hp_regen:50,5","desc":"每回合恢复50HP，持续5回合。","price_buy":400,"price_sell":200},
    {"id":"item_qi_regen_pill","name":"回气露","type":"consumable","tier":"spirit","effect":"douqi_regen:10,5","desc":"每回合恢复10灵力，持续5回合。","price_buy":150,"price_sell":75},
    {"id":"item_qi_regen_pill_2","name":"聚气露","type":"consumable","tier":"treasure","effect":"douqi_regen:25,5","desc":"每回合恢复25灵力，持续5回合。","price_buy":350,"price_sell":175},
    {"id":"item_element_fire_pill","name":"火元丹","type":"consumable","tier":"spirit","effect":"element_boost:fire","desc":"临时强化火属性灵技威力。","price_buy":180,"price_sell":90},
    {"id":"item_element_ice_pill","name":"冰元丹","type":"consumable","tier":"spirit","effect":"element_boost:ice","desc":"临时强化冰属性灵技威力。","price_buy":180,"price_sell":90},
    {"id":"item_element_thunder_pill","name":"雷元丹","type":"consumable","tier":"spirit","effect":"element_boost:thunder","desc":"临时强化雷属性灵技威力。","price_buy":180,"price_sell":90},
    {"id":"item_element_wind_pill","name":"风元丹","type":"consumable","tier":"spirit","effect":"element_boost:wind","desc":"临时强化风属性灵技威力。","price_buy":180,"price_sell":90},
    {"id":"item_element_poison_pill","name":"毒元丹","type":"consumable","tier":"spirit","effect":"element_boost:poison","desc":"临时强化毒属性灵技威力。","price_buy":180,"price_sell":90},
    {"id":"item_shield_pill","name":"护体丹","type":"consumable","tier":"refined","effect":"shield:100","desc":"生成100点护盾吸收伤害。","price_buy":120,"price_sell":60},
    {"id":"item_shield_pill_2","name":"金刚护体丹","type":"consumable","tier":"treasure","effect":"shield:300","desc":"生成300点护盾吸收伤害。","price_buy":350,"price_sell":175},
    {"id":"item_shield_pill_3","name":"不灭护体丹","type":"consumable","tier":"earth","effect":"shield:800","desc":"生成800点护盾吸收伤害。","price_buy":1000,"price_sell":500},
    {"id":"item_thorns_pill","name":"荆棘丹","type":"consumable","tier":"spirit","effect":"thorns:30","desc":"受到伤害时反弹30%伤害。","price_buy":250,"price_sell":125},
    {"id":"item_lifesteal_pill","name":"嗜血丹","type":"consumable","tier":"treasure","effect":"lifesteal:20","desc":"攻击时吸取20%伤害为生命。","price_buy":500,"price_sell":250},
    {"id":"item_all_buff_pill","name":"全效丹","type":"consumable","tier":"earth","effect":"atk:+15,def:+10,spd:+10","desc":"全面提升战斗属性。","price_buy":600,"price_sell":300},
    {"id":"item_treasure_pill","name":"聚宝丹","type":"consumable","tier":"refined","effect":"luck:+20","desc":"临时提升掉落品质。","price_buy":100,"price_sell":50},
    {"id":"item_element_resist_fire","name":"耐火药剂","type":"consumable","tier":"iron","effect":"resist:fire","desc":"抵御火焰伤害。","price_buy":30,"price_sell":15},
    {"id":"item_element_resist_ice","name":"抗寒药剂","type":"consumable","tier":"iron","effect":"resist:ice","desc":"抵御冰霜伤害。","price_buy":30,"price_sell":15},
    {"id":"item_sleep_bomb","name":"催眠弹","type":"consumable","tier":"refined","effect":"sleep:3","desc":"使敌人陷入3回合睡眠。","price_buy":80,"price_sell":40},
    {"id":"item_blind_dust","name":"致盲粉","type":"consumable","tier":"iron","effect":"blind:2","desc":"降低敌人命中率2回合。","price_buy":25,"price_sell":12},
    {"id":"item_freeze_bomb","name":"冷冻弹","type":"consumable","tier":"spirit","effect":"freeze:2","desc":"使敌人陷入2回合冰冻。","price_buy":150,"price_sell":75},
    {"id":"item_paralyze_needle","name":"麻痹针","type":"consumable","tier":"refined","effect":"paralyze:1","desc":"使敌人陷入1回合麻痹。","price_buy":60,"price_sell":30},
    {"id":"item_smoke_bomb","name":"烟雾弹","type":"consumable","tier":"iron","effect":"escape:100","desc":"战斗中必定成功逃脱。","price_buy":50,"price_sell":25},

    # ── 日常回复（客栈物资）──
    {"id":"item_trail_ration","name":"干粮","type":"consumable","tier":"iron",
     "effect":"hp:+15","desc":"佣兵行囊里的粗粮饼。","price_buy":5,"price_sell":2},
    {"id":"item_clean_water","name":"净水","type":"consumable","tier":"iron",
     "effect":"hp:+10","desc":"一壶清水。","price_buy":3,"price_sell":1},
    {"id":"item_meat_skewer","name":"烤肉","type":"consumable","tier":"iron",
     "effect":"hp:+25","desc":"刚出炉的魔兽肉串。","price_buy":8,"price_sell":4},
    {"id":"item_spirit_rice","name":"灵米","type":"consumable","tier":"refined",
     "effect":"hp:+40,douqi:+10","desc":"以灵气灌溉的稻米。","price_buy":20,"price_sell":10},
    {"id":"item_spirit_wine","name":"灵酒","type":"consumable","tier":"refined",
     "effect":"hp:+60,douqi:+30","desc":"灵药酿制的琼浆。","price_buy":40,"price_sell":20},
    {"id":"item_beast_meat","name":"魔兽精肉","type":"consumable","tier":"spirit",
     "effect":"hp:+100","desc":"三阶以上魔兽的精华部位。","price_buy":50,"price_sell":25},
    {"id":"item_dragon_meat","name":"龙肉干","type":"consumable","tier":"earth",
     "effect":"hp:+300","desc":"远虚空龙族后裔的血肉。","price_buy":300,"price_sell":150},
]

# ═══════════════════════════════════════════════════════════════════
# 材料类
# ═══════════════════════════════════════════════════════════════════
MATERIALS: List[Dict[str, Any]] = [
    # ── 药材 ──
    {"id":"item_herb_ginseng","name":"人参","type":"material","tier":"iron",
     "effect":"material","desc":"百年份的野山参。","price_buy":20,"price_sell":10},
    {"id":"item_herb_lingzhi","name":"灵芝","type":"material","tier":"iron",
     "effect":"material","desc":"生于灵气充沛之地的菌中之王。","price_buy":25,"price_sell":12},
    {"id":"item_herb_heal_grass","name":"凝血草","type":"material","tier":"iron",
     "effect":"material","desc":"捣碎敷在伤口上可快速止血。","price_buy":10,"price_sell":5},
    {"id":"item_herb_spirit_grass","name":"聚灵草","type":"material","tier":"refined",
     "effect":"material","desc":"天生聚灵，炼药常用辅料。","price_buy":30,"price_sell":15},
    {"id":"item_herb_soul_flower","name":"养魂花","type":"material","tier":"spirit",
     "effect":"material","desc":"可滋养灵魂力量的奇花。","price_buy":60,"price_sell":30},
    {"id":"item_herb_dragon_blood_grass","name":"龙血草","type":"material","tier":"treasure",
     "effect":"material","desc":"传闻是龙血洒落大地而生。","price_buy":120,"price_sell":60},
    {"id":"item_herb_ice_fire_lotus","name":"冰火双叶莲","type":"material","tier":"earth",
     "effect":"material","desc":"冰火同株，奇药中的奇药。","price_buy":250,"price_sell":125},
    {"id":"item_herb_bodhi_leaf","name":"菩提叶","type":"material","tier":"heaven",
     "effect":"material","desc":"菩提古树落下的叶片。","price_buy":500,"price_sell":250},
    {"id":"item_herb_star_grass","name":"星辰草","type":"material","tier":"mystic",
     "effect":"material","desc":"只在星辉洒落之地生长的奇草。","price_buy":1000,"price_sell":500},
    {"id":"item_herb_phoenix_flower","name":"涅槃花","type":"material","tier":"saint",
     "effect":"material","desc":"传说凤凰涅槃之地才能寻得。","price_buy":2500,"price_sell":1250},
    {"id":"item_herb_emperor_root","name":"帝皇参","type":"material","tier":"emperor",
     "effect":"material","desc":"千年成形，蕴含帝之本源。","price_buy":5000,"price_sell":2500},
    {"id":"item_herb_god_grass","name":"不死神草","type":"material","tier":"divine",
     "effect":"material","desc":"古籍记载的神物，可令人起死回生。","price_buy":15000,"price_sell":7500},
    {"id":"item_herb_jade_bamboo","name":"玉髓竹","type":"material","tier":"refined",
     "effect":"material","desc":"竹节中空含玉髓，炼丹佳品。","price_buy":35,"price_sell":17},
    {"id":"item_herb_golden_mushroom","name":"金线菇","type":"material","tier":"refined",
     "effect":"material","desc":"表面有金色纹路的珍稀菌菇。","price_buy":40,"price_sell":20},
    {"id":"item_herb_thunder_vine","name":"雷击藤","type":"material","tier":"spirit",
     "effect":"material","desc":"被天雷击中却不死的古藤。","price_buy":70,"price_sell":35},
    {"id":"item_herb_blood_rose","name":"血玫瑰","type":"material","tier":"spirit",
     "effect":"material","desc":"生长于古战场的血色玫瑰。","price_buy":65,"price_sell":32},
    {"id":"item_herb_moon_dew_grass","name":"月华露草","type":"material","tier":"treasure",
     "effect":"material","desc":"只在月圆之夜凝结露珠的灵草。","price_buy":140,"price_sell":70},
    {"id":"item_herb_sun_crystal_flower","name":"日晶花","type":"material","tier":"treasure",
     "effect":"material","desc":"花瓣如水晶般透明，只在正午绽放。","price_buy":160,"price_sell":80},
    {"id":"item_herb_void_mushroom","name":"虚空菇","type":"material","tier":"earth",
     "effect":"material","desc":"生长在空间裂缝附近的奇异菌类。","price_buy":300,"price_sell":150},
    {"id":"item_herb_nether_flower","name":"幽冥花","type":"material","tier":"heaven",
     "effect":"material","desc":"生长于极阴之地的黑色花朵。","price_buy":600,"price_sell":300},
    {"id":"item_herb_dragon_scale_moss","name":"龙鳞苔","type":"material","tier":"mystic",
     "effect":"material","desc":"形似龙鳞的奇异苔藓。","price_buy":1200,"price_sell":600},
    {"id":"item_herb_ancient_tree_sap","name":"古树灵液","type":"material","tier":"saint",
     "effect":"material","desc":"万年古树分泌的金黄灵液。","price_buy":3000,"price_sell":1500},
    {"id":"item_herb_eternal_fruit","name":"长生果","type":"material","tier":"emperor",
     "effect":"material","desc":"三千年一开花三千年一结果的天地奇珍。","price_buy":8000,"price_sell":4000},
    {"id":"item_herb_snow_lotus","name":"雪莲花","type":"material","tier":"refined",
     "effect":"material","desc":"生长于极寒之巅的圣洁之花。","price_buy":45,"price_sell":22},
    {"id":"item_herb_fire_grass","name":"炎阳草","type":"material","tier":"spirit",
     "effect":"material","desc":"只在火山口附近生长的红色灵草。","price_buy":55,"price_sell":27},
    {"id":"item_herb_coral_herb","name":"深海珊瑚草","type":"material","tier":"treasure",
     "effect":"material","desc":"来自深海万丈的珊瑚状灵草。","price_buy":180,"price_sell":90},

    # ── 矿石 ──
    {"id":"item_ore_iron","name":"铁矿石","type":"material","tier":"iron",
     "effect":"material","desc":"最基础的锻造材料。","price_buy":5,"price_sell":2},
    {"id":"item_ore_copper","name":"铜矿石","type":"material","tier":"iron",
     "effect":"material","desc":"比铁更坚韧的基础矿石。","price_buy":8,"price_sell":4},
    {"id":"item_ore_silver_ore","name":"银矿石","type":"material","tier":"refined",
     "effect":"material","desc":"蕴含微弱灵气的银矿。","price_buy":20,"price_sell":10},
    {"id":"item_ore_gold_ore","name":"金矿石","type":"material","tier":"refined",
     "effect":"material","desc":"金黄色的灵矿。","price_buy":30,"price_sell":15},
    {"id":"item_ore_black_iron","name":"黑铁","type":"material","tier":"spirit",
     "effect":"material","desc":"沉于寒潭深处的玄铁。","price_buy":50,"price_sell":25},
    {"id":"item_ore_cold_iron","name":"寒铁","type":"material","tier":"spirit",
     "effect":"material","desc":"触之冰寒刺骨的稀有铁矿。","price_buy":60,"price_sell":30},
    {"id":"item_ore_spirit_jade","name":"灵玉原石","type":"material","tier":"treasure",
     "effect":"material","desc":"蕴含灵气的玉石原矿。","price_buy":100,"price_sell":50},
    {"id":"item_ore_meteor_iron","name":"陨铁","type":"material","tier":"treasure",
     "effect":"material","desc":"天外陨石中提炼的奇铁。","price_buy":150,"price_sell":75},
    {"id":"item_ore_dragon_crystal","name":"龙晶矿","type":"material","tier":"earth",
     "effect":"material","desc":"龙族巢穴附近才能找到的晶矿。","price_buy":300,"price_sell":150},
    {"id":"item_ore_star_iron","name":"星陨铁","type":"material","tier":"heaven",
     "effect":"material","desc":"星辰坠落形成的奇铁。","price_buy":600,"price_sell":300},
    {"id":"item_ore_soul_crystal","name":"魂晶","type":"material","tier":"mystic",
     "effect":"material","desc":"可储存灵魂力量的晶体。","price_buy":1200,"price_sell":600},
    {"id":"item_ore_void_stone","name":"虚空石","type":"material","tier":"saint",
     "effect":"material","desc":"空间裂缝中凝结的特殊矿石。","price_buy":3000,"price_sell":1500},
    {"id":"item_ore_emperor_jade","name":"帝玉","type":"material","tier":"emperor",
     "effect":"material","desc":"蕴含帝之本源的至高灵玉。","price_buy":8000,"price_sell":4000},
    {"id":"item_ore_divine_gold","name":"神金","type":"material","tier":"divine",
     "effect":"material","desc":"传说中的神级材料。","price_buy":20000,"price_sell":10000},

    # ── 魔核 ──
    {"id":"item_core_1","name":"一阶魔核","type":"material","tier":"iron",
     "effect":"material","desc":"一阶魔兽体内凝结的能量核心。","price_buy":15,"price_sell":7},
    {"id":"item_core_2","name":"二阶魔核","type":"material","tier":"refined",
     "effect":"material","desc":"二阶魔兽的能量核心。","price_buy":40,"price_sell":20},
    {"id":"item_core_3","name":"三阶魔核","type":"material","tier":"spirit",
     "effect":"material","desc":"三阶魔兽的能量核心，呈淡青色。","price_buy":100,"price_sell":50},
    {"id":"item_core_4","name":"四阶魔核","type":"material","tier":"treasure",
     "effect":"material","desc":"四阶魔兽的能量核心，呈深蓝色。","price_buy":250,"price_sell":125},
    {"id":"item_core_5","name":"五阶魔核","type":"material","tier":"earth",
     "effect":"material","desc":"五阶魔兽的能量核心，紫光流转。","price_buy":600,"price_sell":300},
    {"id":"item_core_6","name":"六阶魔核","type":"material","tier":"heaven",
     "effect":"material","desc":"六阶魔兽的能量核心，金光灿灿。","price_buy":1500,"price_sell":750},
    {"id":"item_core_7","name":"七阶魔核","type":"material","tier":"mystic",
     "effect":"material","desc":"七阶魔兽的能量核心，七彩光辉。","price_buy":4000,"price_sell":2000},
    {"id":"item_core_8","name":"八阶魔核","type":"material","tier":"saint",
     "effect":"material","desc":"八阶魔兽的能量核心，蕴含空间法则碎片。","price_buy":10000,"price_sell":5000},
    {"id":"item_core_9","name":"九阶魔核","type":"material","tier":"emperor",
     "effect":"material","desc":"九阶魔兽的能量核心，已化为实质结晶。","price_buy":25000,"price_sell":12500},

    # ── 兽材 ──
    {"id":"item_beast_skin","name":"兽皮","type":"material","tier":"iron",
     "effect":"material","desc":"普通魔兽的毛皮。","price_buy":10,"price_sell":5},
    {"id":"item_beast_bone","name":"兽骨","type":"material","tier":"iron",
     "effect":"material","desc":"魔兽遗留的坚骨。","price_buy":12,"price_sell":6},
    {"id":"item_beast_claw","name":"兽爪","type":"material","tier":"refined",
     "effect":"material","desc":"锋利的魔兽利爪。","price_buy":25,"price_sell":12},
    {"id":"item_beast_fang","name":"兽牙","type":"material","tier":"refined",
     "effect":"material","desc":"魔兽的尖锐獠牙。","price_buy":30,"price_sell":15},
    {"id":"item_beast_horn","name":"兽角","type":"material","tier":"spirit",
     "effect":"material","desc":"高阶魔兽的角。","price_buy":80,"price_sell":40},
    {"id":"item_beast_eye","name":"魔兽之眼","type":"material","tier":"spirit",
     "effect":"material","desc":"蕴含魔力的兽眼。","price_buy":70,"price_sell":35},
    {"id":"item_beast_feather","name":"灵禽羽","type":"material","tier":"spirit",
     "effect":"material","desc":"灵禽身上脱落的羽毛。","price_buy":50,"price_sell":25},
    {"id":"item_beast_blood_essence_plus","name":"兽血精华","type":"material","tier":"treasure",
     "effect":"material","desc":"精炼后的魔兽血液精华。","price_buy":200,"price_sell":100},
    {"id":"item_dragon_scale_plus","name":"真龙鳞","type":"material","tier":"earth",
     "effect":"material","desc":"龙族后裔脱落的鳞片。","price_buy":500,"price_sell":250},
    {"id":"item_dragon_tendon","name":"龙筋","type":"material","tier":"earth",
     "effect":"material","desc":"龙族后裔的筋腱，坚韧无比。","price_buy":600,"price_sell":300},
    {"id":"item_phoenix_feather","name":"凤羽","type":"material","tier":"heaven",
     "effect":"material","desc":"沾染凤血的奇羽。","price_buy":2000,"price_sell":1000},
    {"id":"item_qilin_horn","name":"麒麟角","type":"material","tier":"mystic",
     "effect":"material","desc":"远古麒麟遗落的角。","price_buy":5000,"price_sell":2500},
    {"id":"item_dragon_reverse_scale","name":"龙之逆鳞","type":"material","tier":"saint",
     "effect":"material","desc":"触之即死的龙族逆鳞。","price_buy":15000,"price_sell":7500},

    # ── 其他材料 ──
    {"id":"item_soul_fragment","name":"灵魂碎片","type":"material","tier":"spirit",
     "effect":"material","desc":"逝者残留的灵魂能量。","price_buy":200,"price_sell":100},
    {"id":"item_flame_seed","name":"源火种子","type":"material","tier":"treasure",
     "effect":"material","desc":"源火的微弱火种。","price_buy":500,"price_sell":250},
    {"id":"item_space_crystal","name":"空间结晶","type":"material","tier":"mystic",
     "effect":"material","desc":"可用于炼制纳戒的空间属性晶体。","price_buy":3000,"price_sell":1500},
    {"id":"item_time_sand","name":"时之沙","type":"material","tier":"saint",
     "effect":"material","desc":"据说来自时间法则的具象化。","price_buy":8000,"price_sell":4000},
    {"id":"item_demon_blood","name":"恶魔之血","type":"material","tier":"heaven",
     "effect":"material","desc":"黑渊高阶成员体内提炼的黑血。","price_buy":800,"price_sell":400},
    {"id":"item_soul_essence","name":"灵魂本源","type":"material","tier":"mystic",
     "effect":"material","desc":"极为珍贵的灵魂系材料。","price_buy":4000,"price_sell":2000},
    # 更多材料
    {"id":"item_fabric_silk","name":"天蚕丝","type":"material","tier":"refined",
     "effect":"material","desc":"天蚕吐出的坚韧丝线。","price_buy":35,"price_sell":17},
    {"id":"item_fabric_cloud_silk","name":"云锦","type":"material","tier":"spirit",
     "effect":"material","desc":"以云霞之气编织的锦缎。","price_buy":90,"price_sell":45},
    {"id":"item_fabric_dragon_silk","name":"龙绡","type":"material","tier":"earth",
     "effect":"material","desc":"龙族以龙息编织的神奇织物。","price_buy":400,"price_sell":200},
    {"id":"item_leather_tough","name":"韧皮","type":"material","tier":"iron",
     "effect":"material","desc":"鞣制过的魔兽皮革。","price_buy":18,"price_sell":9},
    {"id":"item_leather_basilisk","name":"蛇蜥皮","type":"material","tier":"refined",
     "effect":"material","desc":"蛇蜥类魔兽的厚皮。","price_buy":45,"price_sell":22},
    {"id":"item_leather_wyvern","name":"飞龙皮","type":"material","tier":"earth",
     "effect":"material","desc":"亚龙种魔兽的珍贵皮革。","price_buy":350,"price_sell":175},
    {"id":"item_wood_ironwood","name":"铁木","type":"material","tier":"iron",
     "effect":"material","desc":"坚硬如铁的木材。","price_buy":12,"price_sell":6},
    {"id":"item_wood_spirit_oak","name":"灵橡木","type":"material","tier":"refined",
     "effect":"material","desc":"蕴含灵气的橡木。","price_buy":30,"price_sell":15},
    {"id":"item_wood_ancient_pine","name":"古松木","type":"material","tier":"spirit",
     "effect":"material","desc":"千年古松的木心。","price_buy":75,"price_sell":37},
    {"id":"item_wood_bodhi_branch","name":"菩提枝","type":"material","tier":"heaven",
     "effect":"material","desc":"菩提古树的一截枝干。","price_buy":1500,"price_sell":750},
    {"id":"item_wood_world_tree","name":"世界树枝","type":"material","tier":"saint",
     "effect":"material","desc":"传说中支撑世界的古树枝条。","price_buy":10000,"price_sell":5000},
    {"id":"item_essence_fire","name":"火元素精华","type":"material","tier":"spirit",
     "effect":"material","desc":"纯粹火元素凝聚的结晶。","price_buy":120,"price_sell":60},
    {"id":"item_essence_water","name":"水元素精华","type":"material","tier":"spirit",
     "effect":"material","desc":"纯粹水元素凝聚的结晶。","price_buy":120,"price_sell":60},
    {"id":"item_essence_wind","name":"风元素精华","type":"material","tier":"spirit",
     "effect":"material","desc":"纯粹风元素凝聚的结晶。","price_buy":120,"price_sell":60},
    {"id":"item_essence_earth","name":"土元素精华","type":"material","tier":"spirit",
     "effect":"material","desc":"纯粹土元素凝聚的结晶。","price_buy":120,"price_sell":60},
    {"id":"item_essence_thunder","name":"雷元素精华","type":"material","tier":"treasure",
     "effect":"material","desc":"纯粹雷元素凝聚的结晶。","price_buy":250,"price_sell":125},
    {"id":"item_beast_tendon","name":"韧筋","type":"material","tier":"iron",
     "effect":"material","desc":"从魔兽腿部取出的坚韧筋腱。","price_buy":15,"price_sell":7},
    {"id":"item_beast_wing","name":"翼膜","type":"material","tier":"refined",
     "effect":"material","desc":"飞行魔兽的翼膜。","price_buy":40,"price_sell":20},
    {"id":"item_beast_tail","name":"蝎尾","type":"material","tier":"spirit",
     "effect":"material","desc":"蝎类魔兽的毒尾。","price_buy":85,"price_sell":42},
    {"id":"item_beast_venom_gland","name":"毒腺","type":"material","tier":"treasure",
     "effect":"material","desc":"毒系魔兽的毒液腺体。","price_buy":220,"price_sell":110},
    {"id":"item_beast_heart","name":"魔兽心脏","type":"material","tier":"earth",
     "effect":"material","desc":"高阶魔兽的强大心脏。","price_buy":450,"price_sell":225},
    {"id":"item_beast_brain","name":"魂兽脑核","type":"material","tier":"heaven",
     "effect":"material","desc":"灵魂系魔兽的脑核。","price_buy":1200,"price_sell":600},
    {"id":"item_energy_crystal","name":"能量水晶","type":"material","tier":"treasure",
     "effect":"material","desc":"可储存大量灵力的水晶。","price_buy":300,"price_sell":150},
    {"id":"item_runestone","name":"符文石","type":"material","tier":"spirit",
     "effect":"material","desc":"刻有远古符文的石头。","price_buy":100,"price_sell":50},
    {"id":"item_enchant_dust","name":"附魔粉尘","type":"material","tier":"treasure",
     "effect":"material","desc":"用于附魔的魔法粉尘。","price_buy":280,"price_sell":140},
    {"id":"item_world_fragment","name":"世界碎片","type":"material","tier":"divine",
     "effect":"material","desc":"世界破碎后残留的碎片。","price_buy":50000,"price_sell":25000},
    {"id":"item_herb_mystic_mushroom","name":"仙灵菇","type":"material","tier":"earth",
     "effect":"material","desc":"只在灵气极度浓郁处生长的仙菇。","price_buy":280,"price_sell":140},
    {"id":"item_herb_blood_grass","name":"血精草","type":"material","tier":"spirit",
     "effect":"material","desc":"以妖兽鲜血浇灌的灵草。","price_buy":65,"price_sell":32},
    {"id":"item_herb_wind_flower","name":"风语花","type":"material","tier":"refined",
     "effect":"material","desc":"能被微风唤起铃音的奇花。","price_buy":38,"price_sell":19},
    {"id":"item_herb_sunflower_essence","name":"向阳花精","type":"material","tier":"treasure",
     "effect":"material","desc":"终日面朝太阳的花朵精华。","price_buy":170,"price_sell":85},
    {"id":"item_herb_shadow_root","name":"暗影根","type":"material","tier":"heaven",
     "effect":"material","desc":"生长在永恒暗影中的根茎。","price_buy":550,"price_sell":275},
    {"id":"item_herb_dream_lotus","name":"梦莲","type":"material","tier":"mystic",
     "effect":"material","desc":"只在梦境与现实交界处绽放的莲花。","price_buy":1500,"price_sell":750},
    {"id":"item_herb_star_petal","name":"星瓣草","type":"material","tier":"saint",
     "effect":"material","desc":"花瓣上天然生有星辰纹路的灵草。","price_buy":3500,"price_sell":1750},
    {"id":"item_herb_void_lichen","name":"虚空苔","type":"material","tier":"emperor",
     "effect":"material","desc":"在虚空中生长的奇异苔藓。","price_buy":7000,"price_sell":3500},
    {"id":"item_ore_mithril","name":"秘银矿","type":"material","tier":"refined",
     "effect":"material","desc":"轻如羽毛、坚如钢铁的秘银。","price_buy":55,"price_sell":27},
    {"id":"item_ore_adamantite","name":"精金矿","type":"material","tier":"spirit",
     "effect":"material","desc":"传说中最坚硬的金属矿。","price_buy":120,"price_sell":60},
    {"id":"item_ore_orichalcum","name":"山铜","type":"material","tier":"treasure",
     "effect":"material","desc":"散发着金色光泽的传奇金属。","price_buy":300,"price_sell":150},
    {"id":"item_ore_blood_iron","name":"血纹铁","type":"material","tier":"earth",
     "effect":"material","desc":"矿脉中有血色纹路的奇铁。","price_buy":400,"price_sell":200},
    {"id":"item_ore_thunder_iron","name":"雷纹钢","type":"material","tier":"heaven",
     "effect":"material","desc":"被天雷轰击后形成的特殊钢材。","price_buy":800,"price_sell":400},
    {"id":"item_ore_frost_crystal","name":"冰霜水晶","type":"material","tier":"mystic",
     "effect":"material","desc":"万年不化的冰晶核心。","price_buy":2000,"price_sell":1000},
    {"id":"item_ore_flame_crystal","name":"烈焰水晶","type":"material","tier":"mystic",
     "effect":"material","desc":"火山核心孕育的火焰晶体。","price_buy":2000,"price_sell":1000},
    {"id":"item_ore_shadow_stone","name":"暗影石","type":"material","tier":"saint",
     "effect":"material","desc":"能吸收一切光线的黑石。","price_buy":5000,"price_sell":2500},
    {"id":"item_ore_light_crystal","name":"圣光水晶","type":"material","tier":"emperor",
     "effect":"material","desc":"永不熄灭的光明之源。","price_buy":10000,"price_sell":5000},
    {"id":"item_liquid_spirit_water","name":"灵泉水","type":"material","tier":"iron",
     "effect":"material","desc":"蕴含灵气的山泉之水。","price_buy":8,"price_sell":4},
    {"id":"item_liquid_mana_spring","name":"魔力泉","type":"material","tier":"refined",
     "effect":"material","desc":"能恢复魔力的泉水。","price_buy":35,"price_sell":17},
    {"id":"item_liquid_dragon_blood","name":"龙血","type":"material","tier":"earth",
     "effect":"material","desc":"真正的龙族血液。","price_buy":2000,"price_sell":1000},
    {"id":"item_liquid_phoenix_tear","name":"凤凰泪","type":"material","tier":"heaven",
     "effect":"material","desc":"据说凤凰悲伤时流下的泪珠。","price_buy":3000,"price_sell":1500},
    {"id":"item_liquid_ambrosia","name":"神之甘露","type":"material","tier":"divine",
     "effect":"material","desc":"神灵享用的琼浆玉液。","price_buy":20000,"price_sell":10000},
    {"id":"item_liquid_elixir_base","name":"丹液","type":"material","tier":"spirit",
     "effect":"material","desc":"炼制高级丹药的基础液体。","price_buy":90,"price_sell":45},
    {"id":"item_powder_iron","name":"铁粉","type":"material","tier":"iron",
     "effect":"material","desc":"精细研磨的铁粉。","price_buy":5,"price_sell":2},
    {"id":"item_powder_silver","name":"银粉","type":"material","tier":"refined",
     "effect":"material","desc":"精细研磨的银粉。","price_buy":25,"price_sell":12},
    {"id":"item_powder_gold","name":"金粉","type":"material","tier":"spirit",
     "effect":"material","desc":"精细研磨的金粉。","price_buy":80,"price_sell":40},
    {"id":"item_powder_gem","name":"宝石粉","type":"material","tier":"treasure",
     "effect":"material","desc":"精细研磨的宝石粉末。","price_buy":200,"price_sell":100},
    {"id":"item_powder_diamond","name":"钻石粉","type":"material","tier":"earth",
     "effect":"material","desc":"精细研磨的钻石粉末。","price_buy":500,"price_sell":250},
    {"id":"item_essence_life","name":"生命精华","type":"material","tier":"treasure",
     "effect":"material","desc":"蕴含着磅礴生命力的浓缩精华。","price_buy":400,"price_sell":200},
    {"id":"item_essence_creation","name":"创世之尘","type":"material","tier":"divine",
     "effect":"material","desc":"传说中创造世界所用的原始尘埃。","price_buy":100000,"price_sell":50000},
    {"id":"item_scroll_paper","name":"空白卷轴","type":"material","tier":"iron",
     "effect":"material","desc":"用于制作卷轴的空白羊皮纸。","price_buy":10,"price_sell":5},
    {"id":"item_scroll_ink","name":"魔法墨水","type":"material","tier":"refined",
     "effect":"material","desc":"用于书写魔法卷轴的特殊墨水。","price_buy":40,"price_sell":20},
    {"id":"item_scroll_enchant_paper","name":"附魔纸","type":"material","tier":"spirit",
     "effect":"material","desc":"经过魔力处理的特殊纸张。","price_buy":70,"price_sell":35},
    {"id":"item_pigment_red","name":"朱砂","type":"material","tier":"iron",
     "effect":"material","desc":"炼丹制符常用。","price_buy":15,"price_sell":7},
    {"id":"item_pigment_blue","name":"蓝晶粉","type":"material","tier":"refined",
     "effect":"material","desc":"蓝色结晶研磨的粉末。","price_buy":30,"price_sell":15},
    {"id":"item_pigment_purple","name":"紫金粉","type":"material","tier":"spirit",
     "effect":"material","desc":"紫金研磨的珍贵粉末。","price_buy":100,"price_sell":50},
    {"id":"item_catalyst_1","name":"催化粉","type":"material","tier":"iron",
     "effect":"material","desc":"加速丹药成型的催化剂。","price_buy":20,"price_sell":10},
    {"id":"item_catalyst_2","name":"活性催化液","type":"material","tier":"refined",
     "effect":"material","desc":"提升丹药品质的催化剂。","price_buy":60,"price_sell":30},
    {"id":"item_catalyst_3","name":"极品催化剂","type":"material","tier":"treasure",
     "effect":"material","desc":"炼药师梦寐以求的催化材料。","price_buy":300,"price_sell":150},
]

# ═══════════════════════════════════════════════════════════════════
# 特殊道具
# ═══════════════════════════════════════════════════════════════════
SPECIAL_ITEMS: List[Dict[str, Any]] = [
    # ── 源火（原著排行榜）──
    {"id":"item_flame_1","name":"帝炎","type":"heavenly_flame","tier":"divine",
     "effect":"special","desc":"源火榜第一，古帝的本命火焰。","price_buy":100000,"price_sell":50000},
    {"id":"item_flame_2","name":"虚无吞炎","type":"heavenly_flame","tier":"divine",
     "effect":"special","desc":"源火榜第二，可吞噬万物化为虚无。","price_buy":90000,"price_sell":45000},
    {"id":"item_flame_3","name":"净世白莲火","type":"heavenly_flame","tier":"emperor",
     "effect":"special","desc":"源火榜第三，可净化一切杂质。","price_buy":80000,"price_sell":40000},
    {"id":"item_flame_4","name":"金乌焚天火","type":"heavenly_flame","tier":"emperor",
     "effect":"special","desc":"源火榜第四，云族传承之火。","price_buy":70000,"price_sell":35000},
    {"id":"item_flame_5","name":"生灵之焱","type":"heavenly_flame","tier":"saint",
     "effect":"special","desc":"源火榜第五，蕴含磅礴生机。","price_buy":60000,"price_sell":30000},
    {"id":"item_flame_6","name":"八荒破灭焱","type":"heavenly_flame","tier":"saint",
     "effect":"special","desc":"源火榜第六，可破灭一切。","price_buy":50000,"price_sell":25000},
    {"id":"item_flame_7","name":"九幽金祖火","type":"heavenly_flame","tier":"mystic",
     "effect":"special","desc":"源火榜第七，九幽之下孕育的金色火焰。","price_buy":45000,"price_sell":22500},
    {"id":"item_flame_8","name":"红莲业火","type":"heavenly_flame","tier":"mystic",
     "effect":"special","desc":"源火榜第八，业火焚罪、红莲净世。","price_buy":40000,"price_sell":20000},
    {"id":"item_flame_9","name":"三千星空火","type":"heavenly_flame","tier":"heaven",
     "effect":"special","desc":"源火榜第九，又名三千星空火。","price_buy":35000,"price_sell":17500},
    {"id":"item_flame_10","name":"九幽风炎","type":"heavenly_flame","tier":"heaven",
     "effect":"special","desc":"源火榜第十，风炎交融的奇火。","price_buy":30000,"price_sell":15000},
    {"id":"item_flame_11","name":"玄冥冷火","type":"heavenly_flame","tier":"earth",
     "effect":"special","desc":"源火榜第十一，玄炉老人的本命火焰。","price_buy":25000,"price_sell":12500},
    {"id":"item_flame_12","name":"九龙雷罡火","type":"heavenly_flame","tier":"earth",
     "effect":"special","desc":"源火榜第十二，九龙环绕、雷火齐鸣。","price_buy":22000,"price_sell":11000},
    {"id":"item_flame_13","name":"龟灵地火","type":"heavenly_flame","tier":"treasure",
     "effect":"special","desc":"源火榜第十三，地心孕育的龟形火焰。","price_buy":18000,"price_sell":9000},
    {"id":"item_flame_14","name":"陨心源火","type":"heavenly_flame","tier":"treasure",
     "effect":"special","desc":"源火榜第十四，透明无色、直攻内心。","price_buy":16000,"price_sell":8000},
    {"id":"item_flame_15","name":"海心焰","type":"heavenly_flame","tier":"spirit",
     "effect":"special","desc":"源火榜第十五，深海之心孕育的奇焰。","price_buy":12000,"price_sell":6000},
    {"id":"item_flame_16","name":"火山石焰","type":"heavenly_flame","tier":"spirit",
     "effect":"special","desc":"源火榜排名第十六，火山口万年不灭的火焰。","price_buy":10000,"price_sell":5000},

    # ── 功法书 ──
    {"id":"item_skill_book_1","name":"源火决·残卷","type":"book","tier":"refined",
     "effect":"learn_skill","desc":"玄炉老人传授的神秘功法残卷，可吞噬源火进化。","price_buy":0,"price_sell":0},
    {"id":"item_skill_book_2","name":"八荒崩·手札","type":"book","tier":"refined",
     "effect":"learn_skill","desc":"记载地阶灵技八荒崩的修炼手札。","price_buy":800,"price_sell":400},
    {"id":"item_skill_book_3","name":"焰分噬浪尺","type":"book","tier":"spirit",
     "effect":"learn_skill","desc":"地阶灵技——焰分噬浪尺的修炼法门。","price_buy":2000,"price_sell":1000},
    {"id":"item_skill_book_4","name":"三千雷动","type":"book","tier":"treasure",
     "effect":"learn_skill","desc":"地阶身法灵技——三千雷动。","price_buy":5000,"price_sell":2500},
    {"id":"item_skill_book_5","name":"大天造化掌","type":"book","tier":"earth",
     "effect":"learn_skill","desc":"天阶灵技——大天造化掌。","price_buy":15000,"price_sell":7500},
    {"id":"item_skill_book_6","name":"金刚琉璃身","type":"book","tier":"heaven",
     "effect":"learn_skill","desc":"天阶炼体灵技——金刚琉璃身。","price_buy":25000,"price_sell":12500},
    {"id":"item_skill_book_7","name":"黄泉天怒","type":"book","tier":"mystic",
     "effect":"learn_skill","desc":"天阶灵魂灵技——黄泉天怒。","price_buy":50000,"price_sell":25000},

    # ── 修炼宝物 ──
    {"id":"item_cultivation_stone","name":"聚灵石","type":"special","tier":"spirit",
     "effect":"cultivation_boost","desc":"放置于身旁可加速灵力修炼。","price_buy":500,"price_sell":250},
    {"id":"item_cultivation_jade","name":"修炼玉简","type":"special","tier":"treasure",
     "effect":"cultivation_boost","desc":"记录前辈修炼心得的玉简。","price_buy":1000,"price_sell":500},
    {"id":"item_soul_crystal_ball","name":"魂晶球","type":"special","tier":"earth",
     "effect":"soul_boost","desc":"测试并锻炼灵魂力量的晶球。","price_buy":3000,"price_sell":1500},
    {"id":"item_meditation_mat","name":"悟道蒲团","type":"special","tier":"heaven",
     "effect":"cultivation_boost","desc":"坐于其上修炼事半功倍。","price_buy":5000,"price_sell":2500},
    {"id":"item_time_chamber_key","name":"时之密匙","type":"special","tier":"mystic",
     "effect":"time_cultivation","desc":"开启时间密室的钥匙，其中一日抵外界数日。","price_buy":20000,"price_sell":10000},
    {"id":"item_pill_furnace","name":"炼药鼎","type":"special","tier":"spirit",
     "effect":"alchemy_boost","desc":"炼药师炼药时的必备工具。","price_buy":800,"price_sell":400},
    {"id":"item_flame_controlling_ring","name":"控火之环","type":"special","tier":"treasure",
     "effect":"flame_control","desc":"帮助炼药师精确控制火焰温度的法器。","price_buy":2000,"price_sell":1000},

    # ── 关系礼物 ──
    {"id":"item_gift_flower","name":"幽香花束","type":"special","tier":"iron",
     "effect":"gift","desc":"精心采集的山野鲜花。","price_buy":15,"price_sell":7},
    {"id":"item_gift_spice","name":"灵茶","type":"special","tier":"refined",
     "effect":"gift","desc":"用灵泉冲泡的上等茶叶。","price_buy":50,"price_sell":25},
    {"id":"item_gift_jewelry","name":"精致首饰","type":"special","tier":"spirit",
     "effect":"gift","desc":"以灵玉雕琢的精美首饰。","price_buy":200,"price_sell":100},
    {"id":"item_gift_perfume","name":"凝香露","type":"special","tier":"treasure",
     "effect":"gift","desc":"以百花精华炼制的香水。","price_buy":500,"price_sell":250},
    {"id":"item_gift_treasure","name":"夜明珠","type":"special","tier":"earth",
     "effect":"gift","desc":"拳头大小的夜明珠。","price_buy":2000,"price_sell":1000},
    {"id":"item_gift_dragon_pearl","name":"龙珠","type":"special","tier":"heaven",
     "effect":"gift","desc":"龙族体内凝结的宝珠。","price_buy":10000,"price_sell":5000},
    {"id":"item_gift_painting","name":"名家字画","type":"special","tier":"refined",
     "effect":"gift","desc":"出自名家的字画。","price_buy":80,"price_sell":40},
    {"id":"item_gift_wine","name":"陈年佳酿","type":"special","tier":"spirit",
     "effect":"gift","desc":"百年陈酿，酒香醇厚。","price_buy":150,"price_sell":75},

    # ── 特殊功能道具 ──
    {"id":"item_return_scroll_1","name":"传送卷轴·青石城","type":"special","tier":"iron",
     "effect":"teleport:map_wutan","desc":"撕碎后立即传送到青石城。","price_buy":100,"price_sell":50},
    {"id":"item_return_scroll_2","name":"传送卷轴·迦南学院","type":"special","tier":"treasure",
     "effect":"teleport:map_canaan","desc":"撕碎后立即传送到迦南学院。","price_buy":500,"price_sell":250},
    {"id":"item_return_scroll_3","name":"传送卷轴·中州","type":"special","tier":"heaven",
     "effect":"teleport:map_zhongzhou","desc":"撕碎后立即传送到中州。","price_buy":2000,"price_sell":1000},
    {"id":"item_repair_hammer","name":"修理锤","type":"special","tier":"iron",
     "effect":"repair_equipment","desc":"铁匠的修理工具。","price_buy":30,"price_sell":15},
    {"id":"item_identify_scroll","name":"鉴定卷轴","type":"special","tier":"refined",
     "effect":"identify","desc":"鉴定未知物品的属性。","price_buy":80,"price_sell":40},
    {"id":"item_luck_charm","name":"幸运符","type":"special","tier":"spirit",
     "effect":"luck_boost","desc":"据说能提升好运的灵符。","price_buy":300,"price_sell":150},
    {"id":"item_exp_boost_scroll","name":"经验增幅卷轴","type":"special","tier":"treasure",
     "effect":"exp_boost","desc":"使用后战斗经验翻倍（持续10场战斗）。","price_buy":800,"price_sell":400},
    {"id":"item_storage_bag","name":"储物袋","type":"special","tier":"iron",
     "effect":"expand_inventory","desc":"空间储物袋，扩大背包容量。","price_buy":200,"price_sell":100},
    {"id":"item_escape_rope","name":"脱逃绳索","type":"special","tier":"iron",
     "effect":"escape_combat","desc":"战斗中必定成功逃跑（一次性）。","price_buy":150,"price_sell":75},
    {"id":"item_encounter_lure","name":"诱敌香","type":"special","tier":"refined",
     "effect":"force_encounter","desc":"点燃后散发出吸引魔兽的香气。","price_buy":60,"price_sell":30},
    {"id":"item_encounter_repel","name":"驱兽香","type":"special","tier":"refined",
     "effect":"avoid_encounter","desc":"点燃后驱散附近的魔兽。","price_buy":80,"price_sell":40},
    {"id":"item_mystery_box","name":"神秘宝盒","type":"special","tier":"spirit",
     "effect":"random_reward","desc":"不知里面装了什么的神秘盒子。","price_buy":200,"price_sell":100},
    {"id":"item_treasure_map","name":"藏宝图","type":"special","tier":"treasure",
     "effect":"treasure_hunt","desc":"指向某个隐藏宝藏的古老地图。","price_buy":1000,"price_sell":500},
    {"id":"item_dungeon_map_1","name":"秘境入口图","type":"special","tier":"spirit",
     "effect":"reveal_dungeon","desc":"标注某个修炼秘境入口的古图。","price_buy":300,"price_sell":150},
    {"id":"item_dungeon_map_2","name":"远古秘境图","type":"special","tier":"mystic",
     "effect":"reveal_dungeon","desc":"标注远古秘境位置的残图。","price_buy":5000,"price_sell":2500},
    {"id":"item_skill_reset_scroll","name":"遗忘卷轴","type":"special","tier":"treasure",
     "effect":"reset_skills","desc":"以魔力书写的卷轴，可遗忘一项灵技。","price_buy":1000,"price_sell":500},
    {"id":"item_stat_reset_pill","name":"洗点丹","type":"special","tier":"heaven",
     "effect":"reset_stats","desc":"重置属性分配（尚未开放的稀有丹药）。","price_buy":5000,"price_sell":2500},
    {"id":"item_name_color_dye","name":"称号染料","type":"special","tier":"iron",
     "effect":"cosmetic","desc":"改变称号颜色的染料。","price_buy":100,"price_sell":50},
    {"id":"item_pet_food","name":"魔兽食物","type":"special","tier":"iron",
     "effect":"pet_food","desc":"用于喂养驯服魔兽的食物。","price_buy":20,"price_sell":10},
    {"id":"item_pet_taming_reins","name":"驯兽绳","type":"special","tier":"refined",
     "effect":"tame_beast","desc":"用于驯服低阶魔兽的绳索。","price_buy":150,"price_sell":75},
    {"id":"item_blessing_scroll","name":"祝福卷轴","type":"special","tier":"spirit",
     "effect":"temp_buff:all","desc":"获得持续一段时间的全属性小幅提升。","price_buy":400,"price_sell":200},
    {"id":"item_curse_removal","name":"净化卷轴","type":"special","tier":"refined",
     "effect":"remove_curse","desc":"解除身上的诅咒效果。","price_buy":120,"price_sell":60},
    {"id":"item_revive_feather","name":"重生之羽","type":"special","tier":"heaven",
     "effect":"auto_revive","desc":"战斗中被击败时自动复活一次。","price_buy":8000,"price_sell":4000},
    {"id":"item_damage_shield","name":"护盾符","type":"special","tier":"spirit",
     "effect":"damage_shield","desc":"生成抵挡一次攻击的灵力护盾。","price_buy":250,"price_sell":125},
    {"id":"item_weather_stone","name":"晴天石","type":"special","tier":"refined",
     "effect":"change_weather","desc":"驱散恶劣天气的奇石。","price_buy":90,"price_sell":45},
    {"id":"item_enchant_stone_1","name":"初级强化石","type":"special","tier":"iron",
     "effect":"enchant:1","desc":"为装备附加微弱属性。","price_buy":60,"price_sell":30},
    {"id":"item_enchant_stone_2","name":"中级强化石","type":"special","tier":"spirit",
     "effect":"enchant:2","desc":"为装备附加中等属性。","price_buy":200,"price_sell":100},
    {"id":"item_enchant_stone_3","name":"高级强化石","type":"special","tier":"treasure",
     "effect":"enchant:3","desc":"为装备附加强大属性。","price_buy":600,"price_sell":300},
    {"id":"item_enchant_stone_4","name":"顶级强化石","type":"special","tier":"earth",
     "effect":"enchant:4","desc":"为装备附加极限属性。","price_buy":2000,"price_sell":1000},
    {"id":"item_enchant_stone_5","name":"神级强化石","type":"special","tier":"heaven",
     "effect":"enchant:5","desc":"传说中的神级强化石。","price_buy":10000,"price_sell":5000},
    {"id":"item_box_mystery","name":"神秘宝箱","type":"special","tier":"iron",
     "effect":"random_reward","desc":"不知道里面有什么的神秘宝箱。","price_buy":50,"price_sell":25},
    {"id":"item_box_silver","name":"银宝箱","type":"special","tier":"refined",
     "effect":"random_reward","desc":"银光闪闪的宝箱。","price_buy":150,"price_sell":75},
    {"id":"item_box_gold","name":"金宝箱","type":"special","tier":"treasure",
     "effect":"random_reward","desc":"金光灿烂的宝箱。","price_buy":500,"price_sell":250},
    {"id":"item_box_diamond","name":"钻石宝箱","type":"special","tier":"earth",
     "effect":"random_reward","desc":"镶满钻石的华丽宝箱。","price_buy":2000,"price_sell":1000},
    {"id":"item_box_legendary","name":"传说宝箱","type":"special","tier":"heaven",
     "effect":"random_reward","desc":"只在传说中出现的宝箱。","price_buy":10000,"price_sell":5000},
]

# ═══════════════════════════════════════════════════════════════════
# 关键道具
# ═══════════════════════════════════════════════════════════════════
KEY_ITEMS: List[Dict[str, Any]] = [
    # ── 钥匙 ──
    {"id":"item_key_copper","name":"铜钥匙","type":"key","tier":"iron",
     "effect":"key","desc":"最常见的铜质钥匙。","price_buy":20,"price_sell":10},
    {"id":"item_key_iron","name":"铁钥匙","type":"key","tier":"refined",
     "effect":"key","desc":"精铁铸造的钥匙。","price_buy":50,"price_sell":25},
    {"id":"item_key_silver","name":"银钥匙","type":"key","tier":"spirit",
     "effect":"key","desc":"白银铸成的精致钥匙。","price_buy":150,"price_sell":75},
    {"id":"item_key_gold","name":"金钥匙","type":"key","tier":"treasure",
     "effect":"key","desc":"纯金打造的贵重钥匙。","price_buy":400,"price_sell":200},
    {"id":"item_key_jade","name":"玉钥匙","type":"key","tier":"earth",
     "effect":"key","desc":"灵玉雕琢的特殊钥匙。","price_buy":1000,"price_sell":500},
    {"id":"item_key_crystal","name":"水晶钥匙","type":"key","tier":"heaven",
     "effect":"key","desc":"透明无瑕的水晶钥匙。","price_buy":3000,"price_sell":1500},
    {"id":"item_key_soul","name":"魂之钥匙","type":"key","tier":"mystic",
     "effect":"key","desc":"以灵魂之力凝聚的虚无之钥。","price_buy":8000,"price_sell":4000},
    {"id":"item_key_ancient","name":"远古密钥","type":"key","tier":"saint",
     "effect":"key","desc":"远古遗迹的通行凭证。","price_buy":20000,"price_sell":10000},
    {"id":"item_key_emperor","name":"帝之密钥","type":"key","tier":"emperor",
     "effect":"key","desc":"灵帝遗留的至高密钥。","price_buy":50000,"price_sell":25000},

    # ── 剧情相关（任务物品）──
    {"id":"item_quest_token_1","name":"林家族徽","type":"quest","tier":"iron",
     "effect":"quest","desc":"林家的族徽，青石城林家的身份证明。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_2","name":"炼药师徽章","type":"quest","tier":"refined",
     "effect":"quest","desc":"炼药师公会的认证徽章。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_3","name":"内院选拔令","type":"quest","tier":"spirit",
     "effect":"quest","desc":"迦南学院内院选拔资格令牌。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_4","name":"暗角域通行证","type":"quest","tier":"treasure",
     "effect":"quest","desc":"进入暗角域核心区域的通行证。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_5","name":"丹阁认证","type":"quest","tier":"earth",
     "effect":"quest","desc":"丹阁炼药师等级认证文书。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_6","name":"古界令","type":"quest","tier":"heaven",
     "effect":"quest","desc":"云族发放的通行令牌。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_7","name":"黑渊令牌","type":"quest","tier":"mystic",
     "effect":"quest","desc":"从黑渊使者身上缴获的令牌。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_8","name":"远古八族盟约","type":"quest","tier":"saint",
     "effect":"quest","desc":"远古八族共同签署的盟约文书。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_9","name":"古帝玉·残片","type":"quest","tier":"emperor",
     "effect":"quest","desc":"源帝玉的碎片之一，蕴含帝之本源。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_10","name":"净世白莲火·残图","type":"quest","tier":"heaven",
     "effect":"quest","desc":"标注净世白莲火位置的地图残片。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_11","name":"玄炉老人之戒","type":"quest","tier":"iron",
     "effect":"quest","desc":"母亲留给林烬的黑色戒指，玄炉老人灵魂栖身之所。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_12","name":"玄重尺","type":"quest","tier":"refined",
     "effect":"quest","desc":"玄炉老人赠予林烬的修炼用重尺，重逾千斤。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_13","name":"七彩毒经","type":"quest","tier":"treasure",
     "effect":"quest","desc":"小医仙的七彩毒经手抄本。","price_buy":0,"price_sell":0},
    {"id":"item_quest_token_14","name":"天火三玄变·手札","type":"quest","tier":"earth",
     "effect":"quest","desc":"林玄所创的秘法手札残篇。","price_buy":0,"price_sell":0},

    # ── 地图类 ──
    {"id":"item_map_wutan","name":"青石城地图","type":"quest","tier":"iron",
     "effect":"reveal_map","desc":"标注青石城各区域的位置。","price_buy":10,"price_sell":5},
    {"id":"item_map_magic_beast","name":"魔兽山脉地图","type":"quest","tier":"refined",
     "effect":"reveal_map","desc":"标注魔兽山脉安全路线。","price_buy":30,"price_sell":15},
    {"id":"item_map_desert","name":"赤沙荒漠地图","type":"quest","tier":"spirit",
     "effect":"reveal_map","desc":"标注沙漠绿洲和蛇人族领地。","price_buy":100,"price_sell":50},
    {"id":"item_map_canaan","name":"迦南学院地图","type":"quest","tier":"treasure",
     "effect":"reveal_map","desc":"标注迦南学院内外院布局。","price_buy":200,"price_sell":100},
    {"id":"item_map_black_corner","name":"暗角域地图","type":"quest","tier":"earth",
     "effect":"reveal_map","desc":"标注暗角域各大势力范围。","price_buy":500,"price_sell":250},
    {"id":"item_map_zhongzhou","name":"中州地图","type":"quest","tier":"heaven",
     "effect":"reveal_map","desc":"标注中州各大势力范围。","price_buy":2000,"price_sell":1000},
    {"id":"item_map_ancient","name":"远古遗迹地图","type":"quest","tier":"mystic",
     "effect":"reveal_map","desc":"标注远古遗迹的入口位置。","price_buy":5000,"price_sell":2500},
    {"id":"item_map_dragon_island","name":"龙岛海图","type":"quest","tier":"saint",
     "effect":"reveal_map","desc":"标注虚空龙族所在的龙岛航线。","price_buy":15000,"price_sell":7500},
    {"id":"item_map_ancient_emperor","name":"古帝洞府图","type":"quest","tier":"divine",
     "effect":"reveal_map","desc":"源帝洞府的藏宝图残片。","price_buy":50000,"price_sell":25000},

    # 更多钥匙
    {"id":"item_key_dungeon_1","name":"魔兽山脉秘境钥匙","type":"key","tier":"iron",
     "effect":"key","desc":"开启魔兽山脉某处秘境的钥匙。","price_buy":30,"price_sell":15},
    {"id":"item_key_dungeon_2","name":"沙漠地宫钥匙","type":"key","tier":"refined",
     "effect":"key","desc":"开启赤沙荒漠地宫的钥匙。","price_buy":80,"price_sell":40},
    {"id":"item_key_dungeon_3","name":"内院密室钥匙","type":"key","tier":"spirit",
     "effect":"key","desc":"迦南学院内院的密室钥匙。","price_buy":200,"price_sell":100},
    {"id":"item_key_dungeon_4","name":"暗角域地下城钥匙","type":"key","tier":"treasure",
     "effect":"key","desc":"暗角域地下暗市的通行钥匙。","price_buy":500,"price_sell":250},
    {"id":"item_key_dungeon_5","name":"焚炎谷秘库钥匙","type":"key","tier":"earth",
     "effect":"key","desc":"焚炎谷珍藏宝物的秘库钥匙。","price_buy":1500,"price_sell":750},
    {"id":"item_key_dungeon_6","name":"丹阁顶层钥匙","type":"key","tier":"heaven",
     "effect":"key","desc":"通往丹阁顶层的钥匙。","price_buy":5000,"price_sell":2500},
    {"id":"item_key_dungeon_7","name":"黑渊分殿钥匙","type":"key","tier":"mystic",
     "effect":"key","desc":"从黑渊护法身上缴获的分殿钥匙。","price_buy":10000,"price_sell":5000},
    {"id":"item_key_dungeon_8","name":"古帝洞府之钥","type":"key","tier":"divine",
     "effect":"key","desc":"开启源帝洞府的至高钥匙。","price_buy":100000,"price_sell":50000},

    # 更多任务物品
    {"id":"item_quest_letter_1","name":"林战家书","type":"quest","tier":"iron",
     "effect":"quest","desc":"父亲林战写给林烬的家书。","price_buy":0,"price_sell":0},
    {"id":"item_quest_letter_2","name":"玄炉老人的手札","type":"quest","tier":"refined",
     "effect":"quest","desc":"玄炉老人亲笔所写的修炼笔记。","price_buy":0,"price_sell":0},
    {"id":"item_quest_letter_3","name":"青韵的信","type":"quest","tier":"spirit",
     "effect":"quest","desc":"青岚宗宗主青韵的亲笔信。","price_buy":0,"price_sell":0},
    {"id":"item_quest_medal_1","name":"炼药师大会金牌","type":"quest","tier":"spirit",
     "effect":"quest","desc":"炼药师大会冠军的证明。","price_buy":0,"price_sell":0},
    {"id":"item_quest_medal_2","name":"内院强榜第一徽章","type":"quest","tier":"treasure",
     "effect":"quest","desc":"迦南学院内院强榜第一的荣誉。","price_buy":0,"price_sell":0},
    {"id":"item_quest_medal_3","name":"丹阁冠军勋章","type":"quest","tier":"heaven",
     "effect":"quest","desc":"中州丹阁炼药师大赛冠军勋章。","price_buy":0,"price_sell":0},
    {"id":"item_quest_trophy_1","name":"冷煜的戒指","type":"quest","tier":"treasure",
     "effect":"quest","desc":"玄炉老人逆徒冷煜的纳戒，其中或许藏有秘密。","price_buy":0,"price_sell":0},
    {"id":"item_quest_trophy_2","name":"黑渊护法的灵魂印记","type":"quest","tier":"mystic",
     "effect":"quest","desc":"击败黑渊护法后获得的战利品。","price_buy":0,"price_sell":0},
    {"id":"item_quest_trophy_3","name":"天妖凰族精血","type":"quest","tier":"heaven",
     "effect":"quest","desc":"从天妖凰族体内提炼的精血。","price_buy":0,"price_sell":0},
    {"id":"item_quest_trophy_4","name":"虚空龙族逆鳞","type":"quest","tier":"saint",
     "effect":"quest","desc":"虚空龙族王的逆鳞信物。","price_buy":0,"price_sell":0},
    {"id":"item_quest_trophy_5","name":"古帝传承之证","type":"quest","tier":"divine",
     "effect":"quest","desc":"获得源帝传承的信物。","price_buy":0,"price_sell":0},
]

# ═══════════════════════════════════════════════════════════════════
# 装备生成
# ═══════════════════════════════════════════════════════════════════

def generate_equipment() -> Dict[str, Dict[str, Any]]:
    """生成 500+ 件装备。"""
    equipment: Dict[str, Dict[str, Any]] = {}

    for tier_idx, (tier_id, tier_name, (lvl_min, lvl_max), atk_base, def_base, hp_base, _) in enumerate(TIERS):
        # ── 武器 ──
        for wtype_id, wtype_info in WEAPON_TYPES.items():
            category = wtype_info["category"]
            names = wtype_info["names"]
            rare_names = wtype_info.get("rare_names", [])
            epic_names = wtype_info.get("epic_names", [])
            legendary_names = wtype_info.get("legendary_names", [])

            for rarity_idx, (rarity_id, rarity_name, rarity_mult) in enumerate(RARITIES):
                if rarity_id == "legendary" and legendary_names:
                    name_pool = legendary_names
                elif rarity_id == "epic" and epic_names:
                    name_pool = epic_names
                elif rarity_id in ("rare", "uncommon") and rare_names:
                    name_pool = rare_names
                else:
                    name_pool = names

                count = max(1, 4 - rarity_idx)
                if tier_idx <= 2 and rarity_id in ("epic", "legendary"):
                    continue
                if tier_idx <= 4 and rarity_id == "legendary":
                    continue

                for slot_idx in range(min(count, len(name_pool))):
                    name_idx = (tier_idx * 3 + rarity_idx * 2 + slot_idx) % len(name_pool)
                    name = f"{tier_name}{name_pool[name_idx]}"
                    if rarity_id != "common":
                        name = f"[{rarity_name}] {name}"

                    eid = f"eq_{category}_{tier_id}_{rarity_id}_{slot_idx}"
                    atk_bonus = int((atk_base + tier_idx * 4) * rarity_mult)
                    def_bonus = int((def_base + tier_idx * 2) * rarity_mult)
                    hp_bonus = int((hp_base + tier_idx * 3) * rarity_mult)

                    equipment[eid] = {
                        "name": name, "slot": "weapon", "subtype": wtype_id,
                        "atk": atk_bonus, "def": max(0, def_bonus // 3),
                        "hp": hp_bonus, "tier": tier_id, "tier_name": tier_name,
                        "level_min": lvl_min, "level_max": lvl_max, "rarity": rarity_id,
                    }

        # ── 防具 ──
        for atype_id, atype_info in ARMOR_TYPES.items():
            category = atype_info["category"]
            names = atype_info["names"]
            rare_names = atype_info.get("rare_names", [])
            epic_names = atype_info.get("epic_names", [])
            legendary_names = atype_info.get("legendary_names", [])

            for rarity_idx, (rarity_id, rarity_name, rarity_mult) in enumerate(RARITIES):
                if rarity_id == "legendary" and legendary_names:
                    name_pool = legendary_names
                elif rarity_id == "epic" and epic_names:
                    name_pool = epic_names
                elif rarity_id in ("rare", "uncommon") and rare_names:
                    name_pool = rare_names
                else:
                    name_pool = names

                count = max(1, 4 - rarity_idx)
                if tier_idx <= 2 and rarity_id in ("epic", "legendary"):
                    continue
                if tier_idx <= 4 and rarity_id == "legendary":
                    continue

                for slot_idx in range(min(count, len(name_pool))):
                    name_idx = (tier_idx * 3 + rarity_idx * 2 + slot_idx) % len(name_pool)
                    name = f"{tier_name}{name_pool[name_idx]}"
                    if rarity_id != "common":
                        name = f"[{rarity_name}] {name}"

                    eid = f"eq_{category}_{tier_id}_{rarity_id}_{slot_idx}"
                    def_bonus = int((def_base + tier_idx * 3) * rarity_mult)
                    hp_bonus = int((hp_base + tier_idx * 4) * rarity_mult)

                    equipment[eid] = {
                        "name": name, "slot": "armor", "subtype": atype_id,
                        "atk": 0, "def": def_bonus, "hp": hp_bonus,
                        "tier": tier_id, "tier_name": tier_name,
                        "level_min": lvl_min, "level_max": lvl_max, "rarity": rarity_id,
                    }

        # ── 饰品 ──
        for atype_id, atype_info in ACCESSORY_TYPES.items():
            category = atype_info["category"]
            names = atype_info["names"]
            rare_names = atype_info.get("rare_names", [])
            epic_names = atype_info.get("epic_names", [])
            legendary_names = atype_info.get("legendary_names", [])

            for rarity_idx, (rarity_id, rarity_name, rarity_mult) in enumerate(RARITIES):
                if rarity_id == "legendary" and legendary_names:
                    name_pool = legendary_names
                elif rarity_id == "epic" and epic_names:
                    name_pool = epic_names
                elif rarity_id in ("rare", "uncommon") and rare_names:
                    name_pool = rare_names
                else:
                    name_pool = names

                count = max(1, 4 - rarity_idx)
                if tier_idx <= 2 and rarity_id in ("epic", "legendary"):
                    continue
                if tier_idx <= 4 and rarity_id == "legendary":
                    continue

                for slot_idx in range(min(count, len(name_pool))):
                    name_idx = (tier_idx * 3 + rarity_idx * 2 + slot_idx) % len(name_pool)
                    name = f"{tier_name}{name_pool[name_idx]}"
                    if rarity_id != "common":
                        name = f"[{rarity_name}] {name}"

                    eid = f"eq_{category}_{tier_id}_{rarity_id}_{slot_idx}"
                    atk_bonus = int((atk_base // 3 + tier_idx) * rarity_mult)
                    def_bonus = int((def_base // 2 + tier_idx) * rarity_mult)
                    hp_bonus = int((hp_base + tier_idx * 2) * rarity_mult)

                    equipment[eid] = {
                        "name": name, "slot": "accessory", "subtype": atype_id,
                        "atk": atk_bonus, "def": def_bonus, "hp": hp_bonus,
                        "tier": tier_id, "tier_name": tier_name,
                        "level_min": lvl_min, "level_max": lvl_max, "rarity": rarity_id,
                    }

    return equipment


def generate_items() -> Dict[str, Dict[str, Any]]:
    """整合所有道具。"""
    items: Dict[str, Dict[str, Any]] = {}
    for item in CONSUMABLES:
        items[item["id"]] = item
    for item in MATERIALS:
        items[item["id"]] = item
    for item in SPECIAL_ITEMS:
        items[item["id"]] = item
    for item in KEY_ITEMS:
        items[item["id"]] = item
    return items


def generate_loot_table(equipment: Dict, items: Dict) -> Dict[str, List[Tuple[str, int]]]:
    """层级掉落映射：tier_id -> [(id, weight), ...]"""
    loot: Dict[str, List[Tuple[str, int]]] = {t[0]: [] for t in TIERS}
    for eid, eq in equipment.items():
        tier = eq.get("tier", "iron")
        rarity = eq.get("rarity", "common")
        weight = {"common": 100, "uncommon": 60, "rare": 25, "epic": 8, "legendary": 1}.get(rarity, 50)
        if tier in loot:
            loot[tier].append((eid, weight))
    for iid, item_def in items.items():
        tier = item_def.get("tier", "iron")
        if tier in loot:
            itype = item_def.get("type", "")
            weight = {"consumable": 120, "material": 80, "special": 20, "key": 5, "quest": 5,
                      "heavenly_flame": 3, "book": 15, "herb": 60, "monster_core": 40}.get(itype, 50)
            loot[tier].append((iid, weight))
    return loot


# ═══════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════

def main() -> None:
    equipment = generate_equipment()
    items = generate_items()
    removed_item_ids = {
        "item_repair_hammer", "item_identify_scroll", "item_pet_food",
        "item_pet_taming_reins", "item_enchant_stone_1", "item_enchant_stone_2",
        "item_enchant_stone_3", "item_enchant_stone_4", "item_enchant_stone_5",
    }
    items = {
        item_id: item
        for item_id, item in items.items()
        if item_id not in removed_item_ids
    }
    loot = generate_loot_table(equipment, items)

    print(f"装备: {len(equipment)} 件")
    print(f"道具: {len(items)} 件")
    print(f"掉落池: {sum(len(v) for v in loot.values())} 条目")

    from collections import Counter
    rarity_count = Counter(eq["rarity"] for eq in equipment.values())
    print(f"装备稀有度分布: {dict(rarity_count)}")
    tier_count = Counter(eq["tier"] for eq in equipment.values())
    print(f"装备层级分布: {dict(tier_count)}")
    type_count = Counter(item["type"] for item in items.values())
    print(f"道具类型分布: {dict(type_count)}")

    output_dir = Path("src/wordworld/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "equipment_data.py", "w", encoding="utf-8") as f:
        f.write('"""残火长明 RPG — 装备数据（自动生成）"""\n')
        f.write('from typing import Any, Dict\n\n')
        f.write(f'# 装备数量: {len(equipment)}\n')
        f.write('EQUIPMENT_DATA: Dict[str, Dict[str, Any]] = ')
        json.dump(equipment, f, ensure_ascii=False, indent=2)
        f.write('\n')

    with open(output_dir / "item_data.py", "w", encoding="utf-8") as f:
        f.write('"""残火长明 RPG — 道具数据（自动生成）"""\n')
        f.write('from typing import Any, Dict, List, Tuple\n\n')
        f.write(f'# 道具数量: {len(items)}\n')
        f.write('ITEM_DATA: Dict[str, Dict[str, Any]] = ')
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write('\n')

    with open(output_dir / "loot_table.py", "w", encoding="utf-8") as f:
        f.write('"""残火长明 RPG — 掉落表（自动生成）"""\n')
        f.write('from typing import Dict, List, Tuple\n\n')
        f.write(f'# 层级掉落映射: tier_id -> [(item_id, weight), ...]\n')
        f.write('LOOT_TABLE: Dict[str, List[Tuple[str, int]]] = ')
        json.dump(loot, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f"\n输出到: {output_dir}")


if __name__ == "__main__":
    main()
