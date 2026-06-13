"""
技能/功法/源火数据生成器。
运行：python scripts/generate_skills.py
输出：src/wordworld/data/{flame,technique,skill_book,skill_elements_full,elemental_rules}.py
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ═══════════════════════════════════════════════════════════════════
# 23 种源火（原著完整排行榜）
# ═══════════════════════════════════════════════════════════════════
HEAVENLY_FLAMES = [
    (1,  "帝炎",           "divine",   "古帝的本命火焰，源火榜第一，可焚尽万物。"),
    (2,  "虚无吞炎",       "divine",   "源火榜第二，可吞噬一切化为虚无，诞生灵智。"),
    (3,  "净世白莲火",       "emperor",  "源火榜第三，可净化万物杂质，妖莲形态。"),
    (4,  "金乌焚天火",     "emperor",  "源火榜第四，云族传承之火，金光焚天。"),
    (5,  "生灵之焱",       "saint",    "源火榜第五，蕴含磅礴生机，火焰如生命之树。"),
    (6,  "八荒破灭焱",     "saint",    "源火榜第六，可破灭八方，毁灭之力。"),
    (7,  "九幽金祖火",     "mystic",   "源火榜第七，九幽之下孕育的金色火焰。"),
    (8,  "红莲业火",       "mystic",   "源火榜第八，业火焚罪、红莲净世。"),
    (9,  "三千星空火",     "heaven",   "源火榜第九，又名三千星空焱炎火。"),
    (10, "九幽风炎",       "heaven",   "源火榜第十，风炎交融的奇火。"),
    (11, "玄冥冷火",       "earth",    "源火榜第十一，玄炉老人的本命火焰，极寒之焰。"),
    (12, "九龙雷罡火",     "earth",    "源火榜第十二，九龙环绕、雷火齐鸣。"),
    (13, "龟灵地火",       "treasure", "源火榜第十三，地心孕育的龟形火焰。"),
    (14, "陨心源火",       "treasure", "源火榜第十四，透明无色、直攻内心。"),
    (15, "海心焰",         "spirit",   "源火榜第十五，深海之心孕育的奇焰。"),
    (16, "火山石焰",       "spirit",   "源火榜第十六，火山口万年不灭的暗红火焰。"),
    (17, "风雷怒焱",       "spirit",   "源火榜第十七，风雷交加而成的紫青火焰。"),
    (18, "青莲源火",     "refined",  "源火榜第十八，林烬获得的第一种源火。"),
    (19, "龙凤焱",         "refined",  "源火榜第十九，龙血凤骨诞生的双色火焰。"),
    (20, "六道轮回焱",     "iron",     "源火榜第二十，传说来自六道轮回。"),
    (21, "万兽灵火",       "iron",     "源火榜第二十一，万兽灵魂燃烧的火焰。"),
    (22, "玄黄炎",         "iron",     "源火榜第二十二，玄黄之气凝聚而成。"),
    (23, "幽冥毒火",       "iron",     "源火榜第二十三，蕴含剧毒的诡异绿焰。"),
]

# ═══════════════════════════════════════════════════════════════════
# 功法体系（每元素20种 = 100种+）
# ═══════════════════════════════════════════════════════════════════
TECHNIQUE_TEMPLATES = {
    "火": [
        ("焚天诀","atk:+8,fire_power:+15%","以烈焰灵力强化火属性攻击力。"),
        ("炎阳真解","atk:+5,hp:+30","炎阳之力淬炼肉身，攻守兼备。"),
        ("烈火焚心经","fire_power:+20%,crit_rate:+5%","引烈火入心，火系暴击率提升。"),
        ("朱雀涅槃功","hp:+50,hp_regen:+3","朱雀血脉传承，徐徐回血。"),
        ("地火淬体诀","def:+8,fire_resist:+15%","地心之火淬炼筋骨，增强防御。"),
        ("炎帝心经","atk:+12,fire_power:+25%","远古炎帝所创，火中称尊。"),
        ("紫焰锻魂法","soul:+8,fire_power:+10%","紫焰锻炼灵魂，灵魂力与火焰双修。"),
        ("熔岩霸体诀","def:+10,hp:+40","熔岩覆盖周身，肉身如钢铁。"),
        ("星火燎原诀","fire_power:+18%,spd:+5","星星之火可以燎原，速度与火焰并行。"),
        ("龙炎真法","atk:+10,fire_combo:+1","龙族控火秘法，火系连击+1。"),
        ("九阳焚天功","atk:+15,hp:-20","九阳聚顶，以血换攻。"),
        ("赤帝火皇功","fire_power:+30%","赤帝独门心法，极致火攻。"),
        ("离火归元诀","douqi_max:+30,fire_power:+12%","离火归元，灵力上限大增。"),
        ("火凤涅槃经","hp:+60,revive_chance:+5%","火凤涅槃，低概率自动复活。"),
        ("烈焰金身功","def:+12,thorns:10","烈焰护体金身，反弹10%伤害。"),
        ("丹火养气法","douqi_max:+40,douqi_regen:+5","丹火养气，灵力自生不息。"),
        ("狂焰战法","atk:+18,def:-8","狂焰附体，全力猛攻。"),
        ("天火炼神诀","soul:+12,fire_power:+15%","天火炼神，灵魂蜕变。"),
        ("不灭火种法","hp_regen:+5,fire_power:+10%","体内种下不灭火种。"),
        ("万火归宗诀","fire_power:+35%,all_resist:+5%","万火朝宗，火系大成之境。"),
    ],
    "冰": [
        ("冰心诀","def:+8,ice_power:+15%","心如冰清，增强冰系威力与防御。"),
        ("寒冰真气法","ice_power:+20%,spd:-5","寒冰真气凝聚，威力增但速度略降。"),
        ("玄冰锻体功","def:+12,hp:+30","玄冰之气淬体，冰肌玉骨。"),
        ("冰凤天翔诀","spd:+10,ice_power:+12%","冰凤展翅，身法与冰系双修。"),
        ("北冥寒功","atk:+10,ice_penetration:+15%","北冥之寒，冰系穿透力增加。"),
        ("霜雪葬花功","ice_power:+25%,freeze_chance:+8%","霜雪纷飞，冰冻概率大幅提升。"),
        ("万年冰髓法","hp:+80,ice_resist:+20%","万年冰髓入体，生命与冰抗大增。"),
        ("寒魄炼魂诀","soul:+10,ice_power:+10%","寒魄炼魂，灵魂与冰系双修。"),
        ("冰皇不灭体","def:+15,ice_armor:+20","冰皇之体，开场获得冰甲护盾。"),
        ("极寒领域功","ice_power:+18%,enemy_spd:-10%","极寒领域展开，敌人速度降低。"),
        ("冰晶玉骨诀","def:+8,hp_regen:+4","冰晶护骨，生命缓慢回复。"),
        ("雪女之舞法","spd:+12,dodge_rate:+8%","雪女曼舞，闪避率提升。"),
        ("寒渊归墟功","ice_power:+30%,hp:-30","寒渊之力，以命换攻。"),
        ("霜龙吐息诀","atk:+12,ice_power:+15%","霜龙吐息，冰系攻防一体。"),
        ("冰封王座经","def:+10,freeze_duration:+1","冰封之力，冻结时间延长。"),
        ("玄霜碎玉功","atk:+14,def:+4","玄霜碎玉，攻击为主防御为辅。"),
        ("太阴寒月法","douqi_max:+35,ice_power:+15%","太阴月华，灵力与寒冰双修。"),
        ("千山暮雪诀","ice_power:+22%,all_resist:+5%","千山暮雪，冰系小成。"),
        ("永冻之铠法","def:+18,spd:-10","永冻铠甲，极致防御降低速度。"),
        ("冰祖归宗功","ice_power:+35%,ice_combo:+1","冰祖传承，冰系连击+1。"),
    ],
    "雷": [
        ("雷霆真解","atk:+10,thunder_power:+15%","引雷霆入体，雷系攻击力大增。"),
        ("紫电天罡诀","spd:+12,thunder_power:+10%","紫电附体，雷速如电。"),
        ("雷神锻体功","atk:+8,def:+8","九天雷神锻体之法，攻防并重。"),
        ("奔雷心法","thunder_power:+20%,spd:+8","奔雷之势，雷威与速度并行。"),
        ("天罚雷诀","atk:+15,thunder_penetration:+20%","天罚之雷，穿透力无与伦比。"),
        ("九霄雷动功","spd:+15,thunder_power:+15%","九霄云外雷动九天，极速雷法。"),
        ("雷帝霸体诀","atk:+18,def:+12,hp:+20","雷帝霸体，全面强化。"),
        ("紫雷锻魂法","soul:+10,thunder_power:+10%","紫雷锻魂，灵魂与雷系双修。"),
        ("雷龙翻天诀","atk:+14,thunder_combo:+1","雷龙翻腾，雷系连击+1。"),
        ("五雷正法","thunder_power:+25%,crit_rate:+8%","五雷轰顶，暴击率大幅提升。"),
        ("雷池淬体功","def:+14,thunder_resist:+20%","雷池淬体，大幅增强雷抗与防御。"),
        ("电光石火诀","spd:+20,thunder_power:+8%","电光石火，极致速度。"),
        ("霹雳碎虚功","atk:+20,def:-10","霹雳碎虚，以防御换攻击。"),
        ("万雷朝宗法","thunder_power:+35%","万雷朝宗，雷系极致。"),
        ("雷凰天翔诀","spd:+10,dodge_rate:+10%","雷凰天翔，闪避与速度双增。"),
        ("雷霆万钧经","atk:+12,stun_chance:+5%","雷霆万钧，攻击附带眩晕概率。"),
        ("雷元归一功","douqi_max:+30,thunder_power:+12%","雷元归一，灵力上限大增。"),
        ("灭世雷罚法","atk:+25,hp:-40","灭世雷罚，以命换极致攻击。"),
        ("雷音贯耳诀","soul:+12,thunder_power:+15%","雷音贯耳，灵魂与雷双修。"),
        ("混沌雷祖功","thunder_power:+30%,all_resist:+8%","混沌雷祖，雷系大成。"),
    ],
    "风": [
        ("疾风真解","spd:+8,wind_power:+15%","疾风之力，风系威力与速度。"),
        ("风云变幻诀","spd:+12,dodge_rate:+5%","风云变幻，身法大增。"),
        ("飓风碎虚功","atk:+10,wind_power:+18%","飓风碎虚，风系攻击力。"),
        ("天风锻体法","spd:+6,def:+6,hp:+20","以天风锻体，全面小幅提升。"),
        ("御风术","spd:+15,dodge_rate:+10%","御风而行，极致闪避速度。"),
        ("风神诀","wind_power:+25%,spd:+10","风神传承，风威与速度。"),
        ("青鸾天翔功","spd:+12,wind_power:+12%","青鸾展翅，风系双修。"),
        ("暴风眼心法","wind_power:+20%,crit_rate:+8%","暴风眼中，暴击率大增。"),
        ("罡风裂天诀","atk:+16,wind_penetration:+15%","罡风裂天，穿透力极强。"),
        ("流风回雪功","def:+10,dodge_rate:+12%","流风回雪，防御与闪避。"),
        ("虚空风遁法","spd:+18,escape_bonus:+20%","虚空风遁，逃跑与速度。"),
        ("九幽风煞诀","atk:+14,wind_power:+18%","九幽之风，暗藏煞气。"),
        ("清风明月功","hp_regen:+5,douqi_regen:+5","清风明月，双回复。"),
        ("风魔乱舞诀","atk:+12,spd:+12,def:-10","风魔乱舞，速度攻击增、防御降。"),
        ("天罡风体术","def:+12,wind_resist:+20%","天罡风体，防御与风抗。"),
        ("大荒风祖功","wind_power:+35%,spd:+8","大荒风祖，风系极致。"),
        ("扶摇直上诀","spd:+20,wind_power:+10%","扶摇九万里，速度至上。"),
        ("裂空风暴法","atk:+20,wind_combo:+1","裂空风暴，风系连击+1。"),
        ("无影无形功","dodge_rate:+20%,spd:+8","无影无形，极致闪避。"),
        ("风行天下诀","wind_power:+30%,all_spd:+10%","风行天下，风系大成。"),
    ],
    "木": [
        ("青木长生功","hp:+60,hp_regen:+8","青木之气滋养肉身，生命回复大幅提升。"),
        ("万木逢春诀","wood_power:+15%,heal_bonus:+20%","万木逢春，治疗类技能效果增强。"),
        ("枯木回春法","hp:+40,revive_chance:+5%","枯木亦能回春，低概率战斗复活。"),
        ("翠木灵心经","soul:+10,wood_power:+10%","翠木灵心，灵魂与木系双修。"),
        ("古树盘根功","def:+15,immobilize_resist:+20%","如古树盘根，定身抗性大增。"),
        ("藤蔓缠身诀","atk:+10,wood_bind_chance:+15%","藤蔓缠绕，攻击附带束缚概率。"),
        ("森林之息法","douqi_max:+40,wood_power:+12%","森林吐息，灵力上限大增。"),
        ("木皇不灭体","hp:+100,hp_regen:+5","木皇之体，生命与回复双增。"),
        ("灵芝养气功","douqi_regen:+5,hp_regen:+4","灵芝养气，双回复速度提升。"),
        ("花雨纷飞诀","spd:+10,dodge_rate:+10%","花雨纷飞，闪避与速度双增。"),
        ("生命之树功","hp:+120,atk:-5","生命之树，极致生命牺牲攻击。"),
        ("荆棘光环诀","def:+12,thorns_damage:+20","荆棘光环，反弹伤害增强。"),
        ("柳絮随风法","spd:+15,wood_power:+8%","柳絮随风，速度与木系双修。"),
        ("竹影清风功","dodge_rate:+12%,spd:+8","竹影清风，闪避与速度。"),
        ("毒蔓吞噬诀","wood_power:+20%,poison_resist:+25%","毒蔓吞噬，毒抗与木攻双修。"),
        ("万物生长法","hp_regen:+10,douqi_regen:+5","万物生长，双回复速度极致。"),
        ("古榕遮天功","def:+18,wood_power:+10%","古榕遮天，防御与木攻。"),
        ("木祖归宗诀","wood_power:+35%,wood_combo:+1","木祖传承，木系连击+1。"),
        ("生生不息诀","hp_regen:+8,all_resist:+5%","生生不息，全抗与回复。"),
        ("世界树之心","hp:+150,wood_power:+25%","世界树之心，木系大成。"),
    ],
    "土": [
        ("厚土载物功","def:+15,hp:+40","厚土载物，防御与生命双增。"),
        ("山岳不动诀","def:+20,spd:-10","山岳不动，极致防御牺牲速度。"),
        ("大地之力法","atk:+12,earth_power:+15%","大地之力，土系攻击力。"),
        ("磐石护体功","def:+10,earth_resist:+25%","磐石护体，土系抗性大增。"),
        ("流沙陷阵诀","spd:+10,earth_slow_chance:+15%","流沙陷阵，攻击附带减速概率。"),
        ("石魔霸体诀","atk:+15,def:+15,spd:-15","石魔霸体，攻防双增速度大减。"),
        ("地动山摇功","atk:+18,earth_power:+20%","地动山摇，土系攻击极致。"),
        ("岩龙真法","atk:+14,def:+10","岩龙真法，攻防一体。"),
        ("沙暴葬天诀","earth_power:+25%,acc:-5%","沙暴葬天，威力增但命中略降。"),
        ("矿脉吸灵功","douqi_max:+30,earth_power:+12%","矿脉吸灵，灵力与土攻。"),
        ("陨石坠天诀","atk:+25,def:-10","陨石坠天，以防御换攻击。"),
        ("地心淬体法","def:+18,hp:+50","地心淬体，防御与生命。"),
        ("丘陵起伏功","spd:+8,dodge_rate:+8%","丘陵起伏，闪避与速度。"),
        ("土皇霸体诀","def:+16,hp:+60","土皇霸体，极致防御生命。"),
        ("化石为泥功","earth_power:+18%,enemy_def:-10%","化石为泥，降低敌人防御。"),
        ("金刚石体术","def:+25,earth_resist:+30%","金刚石体，顶级防御。"),
        ("地震波诀","atk:+16,earth_shock_chance:+10%","地震波，攻击附带震荡。"),
        ("岩壁守护法","def:+12,shield_start:+50","岩壁守护，开场获得护盾。"),
        ("大地归元功","douqi_max:+50,earth_power:+15%","大地归元，灵力与土攻。"),
        ("土祖归宗诀","earth_power:+35%,earth_combo:+1","土祖传承，土系连击+1。"),
    ],
    "毒": [
        ("毒经真解","poison_power:+15%,atk:+5","毒经入门，毒系威力。"),
        ("七彩毒经","poison_power:+25%,poison_stacks:+1","小医仙所创，毒层数+1。"),
        ("万毒心法","poison_power:+20%,def:+5","万毒归心，毒系攻防。"),
        ("蛇蝎锻体功","def:+10,poison_resist:+20%","蛇蝎锻体，百毒不侵。"),
        ("五毒真诀","atk:+12,poison_power:+15%","五毒俱全，毒系攻击。"),
        ("天毒霸体诀","hp:+60,poison_power:+10%","天毒霸体，生命与毒攻。"),
        ("幽冥毒功","poison_power:+30%,poison_dmg:+50%","幽冥之毒，毒伤大幅提升。"),
        ("化骨绵掌功","atk:+8,poison_penetration:+20%","化骨绵毒，穿透防御。"),
        ("毒龙噬心诀","atk:+16,poison_power:+18%","毒龙噬心，攻击与毒双修。"),
        ("碧磷蛇皇功","poison_power:+22%,spd:+8","碧磷蛇皇，速度与毒攻。"),
        ("千蛛万毒功","def:+12,thorns_poison:+15","千蛛万毒，反弹毒伤。"),
        ("毒姬魅影诀","spd:+12,dodge_rate:+8%","毒姬魅影，闪避与速度。"),
        ("腐骨噬魂法","poison_power:+35%,hp:-20","腐骨噬魂，以命换毒。"),
        ("百毒不侵体","def:+15,poison_resist:+30%","百毒不侵，极致抗毒。"),
        ("毒帝传承功","poison_power:+40%","毒帝传承，毒系极致。"),
        ("蝎尾淬毒诀","atk:+10,crit_poison:+8%","蝎尾淬毒，暴击附带中毒。"),
        ("毒沼归墟法","poison_power:+18%,enemy_spd:-8%","毒沼领域，敌人减速。"),
        ("蛇皇不灭体","hp:+80,poison_power:+10%","蛇皇不灭，生命与毒攻。"),
        ("毒元归一功","douqi_max:+35,poison_power:+12%","毒元归一，灵力大增。"),
        ("万毒归宗诀","poison_power:+35%,poison_combo:+1","万毒归宗，毒系连击+1。"),
    ],
}

# ═══════════════════════════════════════════════════════════════════
# 各元素专属技能（每元素30个 = 150个）
# ═══════════════════════════════════════════════════════════════════
ELEMENT_SKILLS = {
    "火": [
        ("skill_fire_1","烈焰拳",8,5,"以火焰包裹拳头的近身攻击。"),
        ("skill_fire_2","炎爆术",15,10,"凝聚火元素在前方引爆。"),
        ("skill_fire_3","烈火燎原",22,15,"大范围火焰攻击，灼烧地面。"),
        ("skill_fire_4","火龙咆哮",28,20,"火焰化为龙形吞噬敌人。"),
        ("skill_fire_5","天火坠",35,25,"召唤天火从天而降。"),
        ("skill_fire_6","炎帝之怒",45,30,"炎帝传承的终极火焰技。"),
        ("skill_fire_7","火凤展翅",30,22,"火焰化为凤凰形态。"),
        ("skill_fire_8","流星火雨",38,28,"召唤流星般密集的火球。"),
        ("skill_fire_9","焚天煮海",50,35,"火焰威能可焚天煮海。"),
        ("skill_fire_10","烈焰冲击",12,8,"火元素凝聚后直线冲击。"),
        ("skill_fire_11","炎环爆",18,12,"以自身为中心释放火焰环。"),
        ("skill_fire_12","地火喷涌",25,18,"引地心之火喷涌而出。"),
        ("skill_fire_13","火舌缠绕",16,10,"火焰如舌缠绕敌人。"),
        ("skill_fire_14","烈焰风暴拳",20,14,"拳风带火，连环打击。"),
        ("skill_fire_15","焚血狂战",40,28,"燃烧精血换取极致火伤。"),
        ("skill_fire_16","星火焚原",32,22,"星星之火，瞬间燎原。"),
        ("skill_fire_17","岩浆爆裂",35,25,"召唤地底岩浆喷发。"),
        ("skill_fire_18","火神之锤",42,30,"火焰凝聚成巨锤砸下。"),
        ("skill_fire_19","炎狱封印",28,20,"火焰牢笼封印敌人行动。"),
        ("skill_fire_20","万火朝宗",55,40,"万火归宗，火系终极奥义。"),
        ("skill_fire_21","赤焰斩",10,6,"火焰凝聚剑气的斩击。"),
        ("skill_fire_22","爆裂火球",14,9,"触碰即爆的火球术。"),
        ("skill_fire_23","火焰漩涡",24,16,"将敌人卷入火焰漩涡。"),
        ("skill_fire_24","灼热射线",20,14,"高度凝聚的火焰射线。"),
        ("skill_fire_25","热浪滔天",30,22,"释放滔天热浪冲击全体敌人。"),
        ("skill_fire_26","焚诀·吞噬",48,35,"以源火决催动吞噬源火之力。"),
        ("skill_fire_27","火云盖顶",26,18,"火焰云层覆盖战场持续灼烧。"),
        ("skill_fire_28","烈阳坠",38,26,"如烈日坠落般的毁灭打击。"),
        ("skill_fire_29","怒火焚身",34,24,"将愤怒化为烈焰焚烧敌人。"),
        ("skill_fire_30","古帝炎",60,45,"古帝传承的至高火焰一击。"),
    ],
    "冰": [
        ("skill_ice_1","冰锥术",8,5,"凝聚冰锥刺向敌人。"),
        ("skill_ice_2","寒冰箭",12,8,"冰元素凝聚的箭矢。"),
        ("skill_ice_3","冰封术",10,10,"冰冻敌人使其无法行动。"),
        ("skill_ice_4","暴风雪",22,15,"召唤暴风雪覆盖战场。"),
        ("skill_ice_5","冰墙术",5,12,"冰墙阻挡伤害。"),
        ("skill_ice_6","冰霜新星",18,14,"以自身为中心释放冰环。"),
        ("skill_ice_7","绝对零度",40,28,"极限低温冰封万物的领域。"),
        ("skill_ice_8","寒冰风暴",28,20,"冰刃与暴风结合的毁灭风暴。"),
        ("skill_ice_9","冰龙息",35,25,"冰龙吐息冻结一切。"),
        ("skill_ice_10","玄冰斩",14,9,"凝聚冰刃的斩击。"),
        ("skill_ice_11","冰晶护体",5,8,"冰晶覆盖全身提升防御。"),
        ("skill_ice_12","霜冻射线",16,11,"极寒射线冻结触碰之物。"),
        ("skill_ice_13","冰棺封印",20,16,"冰棺封印敌人两回合。"),
        ("skill_ice_14","万年冰髓",45,30,"释放万年冰髓的极寒之力。"),
        ("skill_ice_15","冰凤展翼",32,22,"冰凤形态的攻击。"),
        ("skill_ice_16","碎冰飞溅",25,16,"击碎冰层造成溅射伤害。"),
        ("skill_ice_17","寒渊裂",38,26,"撕裂大地释放深渊寒气。"),
        ("skill_ice_18","冰刃风暴",30,20,"无数冰刃旋转切割。"),
        ("skill_ice_19","永冻领域",42,30,"展开永冻领域持续减速敌人。"),
        ("skill_ice_20","冰帝裁决",55,40,"冰帝传承的至高一击。"),
        ("skill_ice_21","冰凌锥",10,7,"多重冰锥同时发射。"),
        ("skill_ice_22","寒气侵袭",13,9,"寒气渗透敌人防御。"),
        ("skill_ice_23","凝冰化剑",18,12,"将空气水分凝为冰剑。"),
        ("skill_ice_24","冰河时代",50,35,"召唤冰河覆盖整个战场。"),
        ("skill_ice_25","霜龙摆尾",26,18,"霜龙巨尾横扫。"),
        ("skill_ice_26","冰封王座",48,32,"冰封王座之力碾压敌人。"),
        ("skill_ice_27","寒冰地狱",44,30,"将敌人拖入寒冰地狱。"),
        ("skill_ice_28","冰心彻骨",22,16,"寒气直击骨髓。"),
        ("skill_ice_29","雪葬",36,24,"以大雪埋葬敌人。"),
        ("skill_ice_30","万冰归宗",58,42,"万冰归宗冰系至强一击。"),
    ],
    "雷": [
        ("skill_thunder_1","雷电术",10,6,"基础雷电攻击。"),
        ("skill_thunder_2","落雷",14,9,"从天空召唤落雷。"),
        ("skill_thunder_3","雷链",18,12,"连锁雷电跳跃多个目标。"),
        ("skill_thunder_4","雷霆一击",24,16,"凝聚雷霆的重击。"),
        ("skill_thunder_5","雷神之锤",32,22,"雷神巨锤的毁灭一击。"),
        ("skill_thunder_6","紫电狂雷",38,26,"紫色雷电的狂暴攻击。"),
        ("skill_thunder_7","九天神雷",48,32,"九天之上的神雷降世。"),
        ("skill_thunder_8","雷龙出海",42,28,"雷电化龙横扫战场。"),
        ("skill_thunder_9","雷霆万钧",35,24,"万钧雷霆覆盖全场。"),
        ("skill_thunder_10","雷闪",8,10,"雷电般快速突刺。"),
        ("skill_thunder_11","静电领域",15,14,"展开静电场持续伤害。"),
        ("skill_thunder_12","雷音震",20,15,"雷音震动造成内伤。"),
        ("skill_thunder_13","闪电风暴",28,20,"闪电风暴肆虐战场。"),
        ("skill_thunder_14","雷帝之怒",50,35,"雷帝愤怒的终极一击。"),
        ("skill_thunder_15","紫雷破",22,14,"紫色雷电穿透防御。"),
        ("skill_thunder_16","天罚之雷",45,30,"天罚雷霆的审判。"),
        ("skill_thunder_17","奔雷斩",16,10,"雷电缠绕的斩击。"),
        ("skill_thunder_18","雷狱",40,28,"雷电牢狱囚禁敌人。"),
        ("skill_thunder_19","雷光拳",12,7,"雷电包裹拳头的攻击。"),
        ("skill_thunder_20","万雷天引",55,40,"引万雷之力至强攻击。"),
        ("skill_thunder_21","电光一闪",11,7,"快如闪电的突袭。"),
        ("skill_thunder_22","雷鸣爆弹",26,18,"压缩雷电的爆弹。"),
        ("skill_thunder_23","雷击术",9,6,"指尖释放雷电。"),
        ("skill_thunder_24","雷霆战车",34,24,"雷电战车碾压。"),
        ("skill_thunder_25","紫电清霜",30,20,"紫电与清霜交织。"),
        ("skill_thunder_26","雷暴漩涡",36,26,"雷电漩涡吞噬敌人。"),
        ("skill_thunder_27","轰雷贯耳",28,20,"雷霆炸响震撼灵魂。"),
        ("skill_thunder_28","裂天雷",44,30,"裂天碎地的狂暴雷霆。"),
        ("skill_thunder_29","惊雷破晓",38,26,"惊雷划破长夜的一击。"),
        ("skill_thunder_30","雷祖归宗",60,45,"雷祖传承的至高奥义。"),
    ],
    "风": [
        ("skill_wind_1","风刃",7,4,"锐利的风之刃。"),
        ("skill_wind_2","疾风斩",12,8,"风元素凝聚的斩击。"),
        ("skill_wind_3","飓风术",18,12,"召唤小型飓风攻击。"),
        ("skill_wind_4","风卷残云",24,16,"狂风席卷的大范围攻击。"),
        ("skill_wind_5","裂风爪",16,10,"风元素凝聚为利爪。"),
        ("skill_wind_6","风之枪",14,9,"风凝聚为长枪投掷。"),
        ("skill_wind_7","天翔风斩",28,20,"从空中俯冲的风之斩击。"),
        ("skill_wind_8","暴风眼",35,25,"暴风眼的毁灭之力。"),
        ("skill_wind_9","风神怒",45,30,"风神之怒的大范围攻击。"),
        ("skill_wind_10","轻风步",5,6,"风元素加速本回合速度翻倍。"),
        ("skill_wind_11","龙卷风",30,22,"巨大龙卷席卷战场。"),
        ("skill_wind_12","风雷动",32,24,"风雷合一的快速攻击。"),
        ("skill_wind_13","裂空斩",38,26,"撕裂空间的风之斩击。"),
        ("skill_wind_14","风之屏障",5,10,"风墙阻挡攻击。"),
        ("skill_wind_15","无影风杀",40,28,"无形无影的风之暗杀。"),
        ("skill_wind_16","九天罡风",50,35,"九天罡风降临。"),
        ("skill_wind_17","风之翼斩",22,14,"风翼化刃的攻击。"),
        ("skill_wind_18","真空波",20,14,"真空状态的切割波。"),
        ("skill_wind_19","乱流绞杀",34,24,"多重气流绞杀敌人。"),
        ("skill_wind_20","风帝霸斩",55,40,"风帝传承的至高一击。"),
        ("skill_wind_21","微风拂面",3,3,"微风骚扰最低消耗。"),
        ("skill_wind_22","风暴突袭",26,18,"风暴推进的突袭攻击。"),
        ("skill_wind_23","呼啸狂风",20,15,"狂风呼啸大范围攻击。"),
        ("skill_wind_24","气刃乱舞",15,10,"多重气刃乱舞。"),
        ("skill_wind_25","风穴吸掌",18,14,"风穴吸附拉扯敌人。"),
        ("skill_wind_26","罡风裂岳",42,28,"罡风裂山碎岳。"),
        ("skill_wind_27","穿云梭风",28,20,"穿透云层的极速攻击。"),
        ("skill_wind_28","幻风残影",24,16,"残影迷惑敌人的风技。"),
        ("skill_wind_29","碎风破",36,24,"击碎一切逆风的攻击。"),
        ("skill_wind_30","万风归元",58,42,"万风归元风系至强一击。"),
    ],
    "木": [
        ("skill_wood_1","藤蔓鞭",7,4,"以木元素凝聚藤蔓抽打。"),
        ("skill_wood_2","飞叶快刀",10,6,"叶片化为利刃飞出。"),
        ("skill_wood_3","缠绕术",8,8,"藤蔓缠绕限制敌人行动。"),
        ("skill_wood_4","生命汲取",15,12,"吸取敌人的生命力恢复自身。"),
        ("skill_wood_5","万木森罗",22,16,"召唤万木攻击全场。"),
        ("skill_wood_6","春风吹又生",5,15,"以木之生机大幅回复自身HP。"),
        ("skill_wood_7","荆棘光环",12,14,"以荆棘护体反弹部分伤害。"),
        ("skill_wood_8","花开顷刻",20,18,"花朵绽放瞬间的爆发攻击。"),
        ("skill_wood_9","古树之怒",35,25,"唤醒古树愤怒的至强一击。"),
        ("skill_wood_10","森林之息",8,12,"森林吐息恢复HP和灵力。"),
        ("skill_wood_11","枯木逢春",15,10,"枯木新生，伤害与自愈并存。"),
        ("skill_wood_12","毒藤缠绕",18,14,"带毒的藤蔓缠绕，中毒并束缚。"),
        ("skill_wood_13","巨木撞击",25,18,"召唤巨木冲撞敌人。"),
        ("skill_wood_14","叶刃风暴",30,22,"万千叶片化为利刃风暴。"),
        ("skill_wood_15","生命种子",10,10,"种下生命种子持续回复。"),
        ("skill_wood_16","竹剑穿心",12,8,"竹剑般锐利的穿刺攻击。"),
        ("skill_wood_17","翠木屏障",6,12,"翠木化墙吸收伤害。"),
        ("skill_wood_18","千藤万蔓",28,20,"千条藤蔓同时攻击。"),
        ("skill_wood_19","生根发芽",14,12,"根系深入大地恢复体力。"),
        ("skill_wood_20","木灵守护",8,16,"木灵守护大幅提升防御。"),
        ("skill_wood_21","松涛万壑",32,24,"松涛如雷的大范围攻击。"),
        ("skill_wood_22","花草旋风",18,14,"花草形成的旋风攻击。"),
        ("skill_wood_23","树界降临",40,30,"召唤树界降临镇压全场。"),
        ("skill_wood_24","桃花瘴",20,16,"桃花迷雾，迷惑并伤害敌人。"),
        ("skill_wood_25","木遁之术",5,10,"木遁闪避，本回合闪避大幅提升。"),
        ("skill_wood_26","灵芝复苏",12,18,"灵芝之力大幅回复生命。"),
        ("skill_wood_27","柳枝轻拂",8,6,"柳枝轻拂的快速攻击。"),
        ("skill_wood_28","参天巨木击",38,28,"参天巨木的碾压一击。"),
        ("skill_wood_29","森林赞歌",15,20,"森林赞歌全队回复。"),
        ("skill_wood_30","木祖之怒",55,40,"木祖传承的至高一击。"),
    ],
    "土": [
        ("skill_earth_1","落石术",8,5,"召唤石块砸向敌人。"),
        ("skill_earth_2","地刺",12,8,"从地面突起石刺攻击。"),
        ("skill_earth_3","岩壁",5,12,"升起岩壁阻挡伤害。"),
        ("skill_earth_4","地震",18,14,"震动大地造成范围伤害。"),
        ("skill_earth_5","流沙",10,10,"流沙漩涡限制敌人速度。"),
        ("skill_earth_6","岩石炮",22,16,"凝聚岩石发射出去。"),
        ("skill_earth_7","陨石天降",35,25,"从天而降的陨石攻击。"),
        ("skill_earth_8","石魔之拳",28,20,"岩石巨拳的重击。"),
        ("skill_earth_9","大地之怒",45,30,"大地的愤怒至强一击。"),
        ("skill_earth_10","地裂斩",16,10,"撕裂大地的斩击。"),
        ("skill_earth_11","土墙术",8,10,"土墙阻挡敌人。"),
        ("skill_earth_12","沙尘暴",24,18,"沙尘暴覆盖战场降低命中。"),
        ("skill_earth_13","金刚石身",6,15,"金刚石附体大幅提升防御。"),
        ("skill_earth_14","泥石流",20,14,"泥石流冲击敌人。"),
        ("skill_earth_15","山崩地裂",40,28,"山崩地裂的毁灭攻击。"),
        ("skill_earth_16","岩龙卷",30,22,"岩石龙卷风席卷战场。"),
        ("skill_earth_17","石化凝视",14,12,"石化凝视有概率定身敌人。"),
        ("skill_earth_18","大地铠甲",8,14,"大地铠甲提升防御。"),
        ("skill_earth_19","重力术",12,15,"增加重力降低敌人速度。"),
        ("skill_earth_20","土灵守护",10,16,"土灵守护吸收伤害。"),
        ("skill_earth_21","岩石风暴",34,24,"岩石组成的风暴。"),
        ("skill_earth_22","地动波",18,14,"地动波传导式攻击。"),
        ("skill_earth_23","流星石雨",38,26,"流星般的石雨降下。"),
        ("skill_earth_24","泰山压顶",32,22,"泰山般的重压攻击。"),
        ("skill_earth_25","地缚术",10,10,"地缚定身敌人一回合。"),
        ("skill_earth_26","震山锤",26,18,"震动山岳的锤击。"),
        ("skill_earth_27","裂地掌",22,16,"裂地碎石的掌击。"),
        ("skill_earth_28","大地熔炉",36,26,"大地为炉熔炼敌人。"),
        ("skill_earth_29","天崩地裂",50,35,"天地崩裂的终极一击。"),
        ("skill_earth_30","土祖之怒",58,42,"土祖传承的至高一击。"),
    ],
    "毒": [
        ("skill_poison_1","毒液喷射",8,5,"喷射腐蚀性毒液。"),
        ("skill_poison_2","毒雾",10,8,"释放毒雾笼罩敌人。"),
        ("skill_poison_3","剧毒之牙",14,10,"毒牙般的穿刺攻击。"),
        ("skill_poison_4","化骨绵掌",20,14,"毒掌拍击持续腐蚀。"),
        ("skill_poison_5","万毒噬心",35,25,"万种毒素同时发作。"),
        ("skill_poison_6","七彩毒瘴",28,20,"七色毒瘴覆盖全场。"),
        ("skill_poison_7","蛇皇毒涎",24,16,"碧磷蛇皇的毒涎攻击。"),
        ("skill_poison_8","瘟疫散播",18,14,"传播瘟疫类毒素。"),
        ("skill_poison_9","幽冥毒火",32,22,"以毒催动火焰。"),
        ("skill_poison_10","毒龙钻",40,28,"毒龙形态的螺旋攻击。"),
        ("skill_poison_11","腐骨蚀魂",45,30,"腐蚀骨骼与灵魂的至毒。"),
        ("skill_poison_12","麻痹毒针",12,8,"带麻痹效果的毒针。"),
        ("skill_poison_13","毒液炸弹",22,15,"爆炸扩散毒液。"),
        ("skill_poison_14","蝎尾针",16,10,"蝎尾毒针伤害加中毒。"),
        ("skill_poison_15","腐蚀酸雨",30,22,"降下腐蚀性的酸雨。"),
        ("skill_poison_16","毒姬之吻",26,18,"毒姬传承的致命之吻。"),
        ("skill_poison_17","蜘蛛网毒",14,10,"蛛网缠缚附带毒素。"),
        ("skill_poison_18","蛇群召唤",34,24,"召唤毒蛇群攻击。"),
        ("skill_poison_19","万蛊噬身",42,30,"万蛊入体极致折磨。"),
        ("skill_poison_20","毒帝裁决",55,40,"毒帝传承的至高一击。"),
        ("skill_poison_21","毒烟术",10,7,"释放有毒烟雾。"),
        ("skill_poison_22","腐叶飞花",18,12,"毒淬花叶暗器。"),
        ("skill_poison_23","蚣蝮之毒",24,16,"蚣蝮魔兽的剧毒。"),
        ("skill_poison_24","碧磷紫焰",36,26,"碧磷蛇皇的紫焰毒攻。"),
        ("skill_poison_25","千毒万蛊阵",48,32,"千种毒物布置的阵法。"),
        ("skill_poison_26","毒血沸腾",28,20,"注入毒血使敌人内乱。"),
        ("skill_poison_27","蛤蟆毒气",14,9,"蛤蟆类毒兽喷吐攻击。"),
        ("skill_poison_28","灭魂毒咒",50,35,"连灵魂都能毒杀的咒术。"),
        ("skill_poison_29","葬花毒海",38,28,"以毒花埋葬敌人。"),
        ("skill_poison_30","万毒归宗",60,42,"万毒归宗毒系至强。"),
    ],
}

# 双属性技能 21个
CROSS_ELEMENT_SKILLS = [
    {"id":"skill_fire_storm","name":"烈焰风暴","element":"火","sub":"风","atk":25,"cost":18,"desc":"风助火势，火焰化为风暴。双属性：火+风。"},
    {"id":"skill_inferno_cyclone","name":"焚天旋风","element":"火","sub":"风","atk":30,"cost":22,"desc":"火借风势旋风所到尽化焦土。双属性：火+风。"},
    {"id":"skill_fire_tornado","name":"火龙卷","element":"火","sub":"风","atk":20,"cost":14,"desc":"火焰缠绕旋风形成火龙卷。双属性：火+风。"},
    {"id":"skill_thunder_flame","name":"雷炎爆","element":"雷","sub":"火","atk":28,"cost":20,"desc":"雷霆引燃烈焰双属性爆发。双属性：雷+火。"},
    {"id":"skill_lightning_inferno","name":"雷火炼狱","element":"雷","sub":"火","atk":35,"cost":25,"desc":"雷电与火焰交织的炼狱。双属性：雷+火。"},
    {"id":"skill_storm_flame","name":"雷火双重击","element":"雷","sub":"火","atk":22,"cost":16,"desc":"雷与火同时轰击目标。双属性：雷+火。"},
    {"id":"skill_blizzard","name":"暴风雪","element":"冰","sub":"风","atk":24,"cost":18,"desc":"风卷寒冰封锁一切。双属性：冰+风。"},
    {"id":"skill_frozen_storm","name":"冰风暴","element":"冰","sub":"风","atk":30,"cost":22,"desc":"寒风与冰刃结合的风暴。双属性：冰+风。"},
    {"id":"skill_frost_cyclone","name":"霜冻旋风","element":"冰","sub":"风","atk":18,"cost":14,"desc":"携带冰霜的旋风冻结敌人。双属性：冰+风。"},
    {"id":"skill_thunder_frost","name":"雷冰破","element":"雷","sub":"冰","atk":26,"cost":19,"desc":"雷击破冰双重冲击。双属性：雷+冰。"},
    {"id":"skill_ice_lightning","name":"冰雷闪","element":"雷","sub":"冰","atk":32,"cost":23,"desc":"冰中蕴雷触之即发。双属性：雷+冰。"},
    {"id":"skill_frost_bolt","name":"冰霜雷矢","element":"雷","sub":"冰","atk":20,"cost":15,"desc":"冰晶包裹的雷电箭矢。双属性：雷+冰。"},
    {"id":"skill_poison_mist","name":"毒雾风暴","element":"毒","sub":"风","atk":22,"cost":17,"desc":"毒雾借风势扩散大面积中毒。双属性：毒+风。"},
    {"id":"skill_venom_gale","name":"毒岚狂风","element":"毒","sub":"风","atk":28,"cost":21,"desc":"含剧毒的狂风席卷战场。双属性：毒+风。"},
    {"id":"skill_pestilence","name":"瘟疫之风","element":"毒","sub":"风","atk":16,"cost":13,"desc":"携带瘟疫的邪风。双属性：毒+风。"},
    {"id":"skill_poison_flame","name":"毒焰焚身","element":"毒","sub":"火","atk":27,"cost":20,"desc":"蕴含剧毒的火焰双折磨。双属性：毒+火。"},
    {"id":"skill_venom_inferno","name":"毒火炼狱","element":"毒","sub":"火","atk":34,"cost":24,"desc":"毒与火交织的炼狱之刑。双属性：毒+火。"},
    {"id":"skill_toxic_blaze","name":"毒炎爆","element":"毒","sub":"火","atk":20,"cost":15,"desc":"剧毒火焰的爆炸性释放。双属性：毒+火。"},
    {"id":"skill_venom_lightning","name":"毒雷亟","element":"雷","sub":"毒","atk":25,"cost":18,"desc":"携带剧毒的雷电轰击。双属性：雷+毒。"},
    {"id":"skill_toxic_thunder","name":"毒雷噬","element":"雷","sub":"毒","atk":31,"cost":22,"desc":"毒与雷融合麻痹中毒并存。双属性：雷+毒。"},
    {"id":"skill_thunder_poison","name":"雷毒双煞","element":"雷","sub":"毒","atk":38,"cost":27,"desc":"雷毒双煞降临至强一击。双属性：雷+毒。"},
    # 木+火
    {"id":"skill_wood_fire","name":"薪火爆燃","element":"木","sub":"火","atk":26,"cost":19,"desc":"木生火势，爆燃一击。双属性：木+火。"},
    {"id":"skill_blaze_bloom","name":"烈焰花开","element":"火","sub":"木","atk":28,"cost":20,"desc":"火中开花，双重伤害。双属性：火+木。"},
    # 木+土
    {"id":"skill_root_quake","name":"根裂大地","element":"木","sub":"土","atk":24,"cost":18,"desc":"根系裂石穿土而出。双属性：木+土。"},
    {"id":"skill_forest_earthquake","name":"林地震动","element":"土","sub":"木","atk":30,"cost":22,"desc":"森林大地同时震动。双属性：土+木。"},
    # 土+火
    {"id":"skill_magma_eruption","name":"岩浆爆裂","element":"土","sub":"火","atk":33,"cost":24,"desc":"地底岩浆喷涌而出。双属性：土+火。"},
    {"id":"skill_volcano_fist","name":"火山拳","element":"火","sub":"土","atk":29,"cost":21,"desc":"火山喷发般的拳劲。双属性：火+土。"},
    # 木+风
    {"id":"skill_leaf_storm","name":"叶暴风","element":"木","sub":"风","atk":22,"cost":16,"desc":"万千叶片随风化为利刃。双属性：木+风。"},
    {"id":"skill_pollen_gale","name":"花粉飓风","element":"风","sub":"木","atk":20,"cost":14,"desc":"携带催眠花粉的飓风。双属性：风+木。"},
    # 土+冰
    {"id":"skill_frozen_earth","name":"冻土崩裂","element":"冰","sub":"土","atk":26,"cost":19,"desc":"冻土崩裂的毁灭式攻击。双属性：冰+土。"},
    {"id":"skill_ice_rock","name":"冰岩坠","element":"土","sub":"冰","atk":28,"cost":20,"desc":"冰封岩石从天而降。双属性：土+冰。"},
]

# 通用/辅助技能 40个
UTILITY_SKILLS = [
    ("skill_util_1","恢复术",0,8,"消耗灵力恢复生命。","heal:60"),
    ("skill_util_2","大恢复术",0,15,"大量恢复生命。","heal:150"),
    ("skill_util_3","圣疗术",0,25,"神圣之力大幅恢复生命。","heal:350"),
    ("skill_util_4","生命之泉",0,30,"召唤生命之泉持续恢复。","heal:500,regen:30,3"),
    ("skill_util_5","回气术",0,10,"恢复灵力的法门。","douqi_restore:80"),
    ("skill_util_6","聚气归元",0,20,"大量恢复灵力。","douqi_restore:200"),
    ("skill_util_7","灵力泉涌",0,35,"灵力如泉涌般恢复。","douqi_restore:500"),
    ("skill_util_8","净化术",0,8,"驱散负面状态。","cleanse"),
    ("skill_util_9","护盾术",0,12,"生成灵力护盾吸收伤害。","shield:150"),
    ("skill_util_10","大护盾术",0,22,"生成强力护盾。","shield:400"),
    ("skill_util_11","力量增幅",0,10,"临时提升攻击力。","buff:atk,15,3"),
    ("skill_util_12","防御增幅",0,10,"临时提升防御力。","buff:def,15,3"),
    ("skill_util_13","速度增幅",0,10,"临时提升速度。","buff:spd,15,3"),
    ("skill_util_14","战吼",0,12,"激励自身全属性微量提升。","buff:all,5,3"),
    ("skill_util_15","金刚不坏",0,25,"大幅提升防御数回合。","buff:def,30,5"),
    ("skill_util_16","嗜血术",0,15,"攻击附带吸血效果。","buff:lifesteal,20,3"),
    ("skill_util_17","荆棘术",0,12,"受到伤害时反弹。","buff:thorns,25,3"),
    ("skill_util_18","潜行术",0,10,"大幅提升闪避率。","buff:dodge,30,2"),
    ("skill_util_19","致命专注",0,15,"提升暴击率。","buff:crit,30,3"),
    ("skill_util_20","冥想",0,5,"进入冥想恢复HP和灵力。","heal:30,douqi_restore:30"),
    ("skill_util_21","急救",0,5,"快速包扎恢复少量生命。","heal:40"),
    ("skill_util_22","气疗术",0,8,"灵力温养经脉。","heal:80,douqi_restore:20"),
    ("skill_util_23","解毒术",0,6,"解除中毒状态。","cure_poison"),
    ("skill_util_24","清醒术",0,6,"解除睡眠混乱。","cure_mental"),
    ("skill_util_25","铁壁",0,8,"本回合防御大幅提升。","buff:def,50,1"),
    ("skill_util_26","蓄力重击",0,20,"蓄力后释放强力一击。","charge_attack:2.5"),
    ("skill_util_27","反击架势",0,10,"受到攻击时自动反击。","counter:80,3"),
    ("skill_util_28","元素共鸣",0,15,"激活元素之力强化下个元素技。","buff:element_power,30,2"),
    ("skill_util_29","灵力燃烧",0,10,"燃烧灵力换取攻击提升。","douqi_to_atk:50"),
    ("skill_util_30","牺牲",0,5,"消耗生命换取大量灵力。","hp_to_douqi:100"),
    ("skill_util_31","灵魂链接",0,20,"链接灵魂恢复生命和灵力。","heal:200,douqi_restore:100"),
    ("skill_util_32","时空扭曲",0,30,"扭曲时空获得额外回合。","extra_turn"),
    ("skill_util_33","封印术",0,18,"封印敌人技能一回合。","seal:1"),
    ("skill_util_34","吸星大法",0,22,"吸取敌人灵力为己用。","douqi_drain:100"),
    ("skill_util_35","生命汲取",0,20,"吸取敌人生命。","hp_drain:150"),
    ("skill_util_36","分身术",0,15,"制造分身大幅提升闪避。","buff:dodge,50,1"),
    ("skill_util_37","破甲术",0,12,"降低敌人防御。","debuff:def,20,3"),
    ("skill_util_38","迟缓术",0,10,"降低敌人速度。","debuff:spd,20,3"),
    ("skill_util_39","虚弱诅咒",0,15,"降低敌人攻击力。","debuff:atk,20,3"),
    ("skill_util_40","破魔",0,18,"驱散敌人的增益状态。","dispel_enemy"),
]


def generate_all() -> Dict[str, Any]:
    output = {}

    # 1. 源火
    flames = []
    for rank, name, tier, desc in HEAVENLY_FLAMES:
        fid = f"item_flame_{rank}"
        flames.append({"id":fid,"name":name,"type":"heavenly_flame","tier":tier,
                        "effect":"special","desc":f"源火榜第{rank}。{desc}",
                        "price_buy":max(1000,50000//max(1,rank//2)),
                        "price_sell":max(500,25000//max(1,rank//2)),"rank":rank})
    output["flames"] = flames

    # 2. 功法
    techniques = []
    for elem, techs in TECHNIQUE_TEMPLATES.items():
        for name, effect, desc in techs:
            techniques.append({"id":f"tech_{elem}_{name}","name":f"《{name}》","type":"technique",
                                "tier":"refined","element":elem,"effect":effect,
                                "desc":f"[{elem}系功法] {desc}","price_buy":500,"price_sell":250})
    output["techniques"] = techniques

    # 3. 技能书
    books = []
    for elem, skills in ELEMENT_SKILLS.items():
        for sid, name, atk_bonus, cost, desc in skills:
            books.append({"id":f"book_{sid}","name":f"《{name}》","type":"book",
                           "tier":"spirit" if atk_bonus<20 else "treasure" if atk_bonus<35 else "earth",
                           "element":elem,"skill_id":sid,"skill_name":name,
                           "atk_bonus":atk_bonus,"cost":cost,"desc":f"[{elem}系] {desc}",
                           "price_buy":atk_bonus*30,"price_sell":atk_bonus*15})
    for s in CROSS_ELEMENT_SKILLS:
        books.append({"id":f"book_{s['id']}","name":f"《{s['name']}》","type":"book",
                       "tier":"treasure" if s["atk"]<30 else "earth",
                       "element":s["element"],"sub_element":s["sub"],
                       "skill_id":s["id"],"skill_name":s["name"],
                       "atk_bonus":s["atk"],"cost":s["cost"],"desc":s["desc"],
                       "price_buy":s["atk"]*40,"price_sell":s["atk"]*20,"cross":True})
    for sid, name, atk_bonus, cost, desc, effect in UTILITY_SKILLS:
        books.append({"id":f"book_{sid}","name":f"《{name}》","type":"book",
                       "tier":"refined" if cost<15 else "spirit",
                       "element":"无","skill_id":sid,"skill_name":name,
                       "atk_bonus":atk_bonus,"cost":cost,"desc":f"[辅助] {desc}",
                       "effect":effect,"price_buy":max(100,cost*30),"price_sell":max(50,cost*15)})
    output["skill_books"] = books

    # 4. 技能元素映射
    skill_elements = {}
    for elem, skills in ELEMENT_SKILLS.items():
        for sid, *_ in skills:
            skill_elements[sid] = elem
    for s in CROSS_ELEMENT_SKILLS:
        skill_elements[s["id"]] = s["element"]
        skill_elements[f"{s['id']}_sub"] = s["sub"]
    output["skill_elements"] = skill_elements

    # 5. 元素规则
    elemental_rules = {
        # 七元素克制链：火→木→土→雷→冰→风→毒→火
        "counter":{
            "火":"木","木":"土","土":"雷","雷":"冰","冰":"风","风":"毒","毒":"火"
        },
        "advantage":{
            "木":"火","土":"木","雷":"土","冰":"雷","风":"冰","毒":"风","火":"毒"
        },
        "same_element_combo":{"2":1.15,"3":1.30,"4":1.50,"5":1.75},
        "cross_element_effects":{
            "火+风":{"name":"烈焰风暴","mult":1.4},
            "风+火":{"name":"风火连天","mult":1.3},
            "火+雷":{"name":"雷火交加","mult":1.5},
            "雷+火":{"name":"烈焰雷霆","mult":1.4},
            "冰+风":{"name":"暴风雪","mult":1.35},
            "风+冰":{"name":"寒风刺骨","mult":1.25},
            "冰+雷":{"name":"雷冰双极","mult":1.45},
            "雷+冰":{"name":"冰雷闪","mult":1.35},
            "毒+风":{"name":"毒岚","mult":1.3},
            "风+毒":{"name":"毒雾扩散","mult":1.2},
            "毒+火":{"name":"毒焰","mult":1.5},
            "火+毒":{"name":"焚毒","mult":1.35},
            "雷+毒":{"name":"雷毒噬","mult":1.4},
            "木+火":{"name":"薪火相传","mult":1.45},
            "火+木":{"name":"焚木生辉","mult":1.35},
            "木+土":{"name":"根深蒂固","mult":1.3},
            "土+木":{"name":"沃土生木","mult":1.25},
            "土+火":{"name":"熔岩爆发","mult":1.5},
            "火+土":{"name":"烈火炼金","mult":1.4},
            "冰+木":{"name":"霜冻森林","mult":1.3},
            "木+冰":{"name":"冰封万木","mult":1.25},
            "雷+木":{"name":"雷击古木","mult":1.35},
            "木+雷":{"name":"木引天雷","mult":1.3},
            "毒+土":{"name":"毒染大地","mult":1.35},
            "土+毒":{"name":"毒沼陷阱","mult":1.3},
            "风+土":{"name":"飞沙走石","mult":1.35},
            "土+风":{"name":"沙尘风暴","mult":1.3},
            "风+木":{"name":"风卷残叶","mult":1.25},
            "木+风":{"name":"春风化雨","mult":1.2},
            "冰+土":{"name":"冻土荒原","mult":1.3},
            "土+冰":{"name":"冰封大地","mult":1.25},
            "雷+土":{"name":"雷击大地","mult":1.4},
        },
    }
    output["elemental_rules"] = elemental_rules

    return output


def main():
    data = generate_all()
    d = Path("src/wordworld/data")
    d.mkdir(parents=True, exist_ok=True)

    files = [
        ("flame_data.py", "flames", "HEAVENLY_FLAMES_FULL"),
        ("technique_data.py", "techniques", "TECHNIQUE_DATA"),
        ("skill_book_data.py", "skill_books", "SKILL_BOOK_DATA"),
        ("skill_elements_full.py", "skill_elements", "SKILL_ELEMENTS_FULL"),
        ("elemental_rules.py", "elemental_rules", "ELEMENTAL_RULES"),
    ]
    for fname, key, varname in files:
        with open(d / fname, "w", encoding="utf-8") as f:
            f.write('"""Auto-generated data."""\nfrom typing import Any, Dict, List\n\n')
            f.write(f'{varname} = ')
            json.dump(data[key], f, ensure_ascii=False, indent=2)
            f.write('\n')

    from collections import Counter
    print(f"源火: {len(data['flames'])} 种")
    print(f"功法: {len(data['techniques'])} 种 ({dict(Counter(t['element'] for t in data['techniques']))})")
    print(f"技能书: {len(data['skill_books'])} 种 ({dict(Counter(b['element'] for b in data['skill_books']))})")
    print(f"技能元素映射: {len(data['skill_elements'])} 个")
    print(f"跨元素组合: {len(data['elemental_rules']['cross_element_effects'])} 组")


if __name__ == "__main__":
    main()
