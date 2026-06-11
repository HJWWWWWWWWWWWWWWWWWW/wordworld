"""
丹方/药鼎数据生成器。500+丹方 + 10品药鼎。
运行：python scripts/generate_recipes.py
"""
import json, os
from pathlib import Path

FURNACES = [
    {"id":"furnace_1","name":"石药鼎","grade":1,"bonus":0,"max_uses":30,"special":"无","desc":"最基础的炼药鼎，粗石打造。","price_buy":500,"price_sell":100},
    {"id":"furnace_2","name":"铁药鼎","grade":2,"bonus":5,"max_uses":60,"special":"无","desc":"铸铁打造，比石鼎耐用。","price_buy":1500,"price_sell":300},
    {"id":"furnace_3","name":"铜药鼎","grade":3,"bonus":8,"max_uses":100,"special":"火候+1","desc":"精铜打造，火候掌控略有提升。","price_buy":4000,"price_sell":800},
    {"id":"furnace_4","name":"银药鼎","grade":4,"bonus":12,"max_uses":180,"special":"成丹率+5%","desc":"白银铸鼎，导热均匀提升成丹率。","price_buy":10000,"price_sell":2000},
    {"id":"furnace_5","name":"金药鼎","grade":5,"bonus":15,"max_uses":280,"special":"经验+20%","desc":"黄金为鼎，炼药时额外获得经验。","price_buy":25000,"price_sell":5000},
    {"id":"furnace_6","name":"玉药鼎","grade":6,"bonus":20,"max_uses":450,"special":"双倍产出10%","desc":"灵玉雕琢，有概率一炉出双丹。","price_buy":60000,"price_sell":12000},
    {"id":"furnace_7","name":"灵药鼎","grade":7,"bonus":25,"max_uses":-1,"special":"成功率+10%,无限","desc":"灵器级别的药鼎，永不磨损。","price_buy":150000,"price_sell":30000},
    {"id":"furnace_8","name":"圣药鼎","grade":8,"bonus":30,"max_uses":-1,"special":"成功率+15%,省材20%","desc":"圣器药鼎，有概率不消耗材料。","price_buy":300000,"price_sell":60000},
    {"id":"furnace_9","name":"帝药鼎","grade":9,"bonus":35,"max_uses":-1,"special":"成功率+20%,双倍20%","desc":"帝器药鼎，远古斗帝所留。","price_buy":600000,"price_sell":120000},
    {"id":"furnace_10","name":"神农药鼎","grade":10,"bonus":50,"max_uses":-1,"special":"成功率+30%,双倍30%,省材30%","desc":"传说中神农氏的药鼎。","price_buy":1000000,"price_sell":200000},
]

HERB_POOL = {
    1:["item_herb_heal_grass","item_herb_ginseng","item_herb_spirit_grass","item_clean_water"],
    2:["item_herb_lingzhi","item_herb_jade_bamboo","item_herb_golden_mushroom","item_herb_wind_flower","item_herb_snow_lotus"],
    3:["item_herb_soul_flower","item_herb_thunder_vine","item_herb_blood_rose","item_herb_fire_grass"],
    4:["item_herb_dragon_blood_grass","item_herb_moon_dew_grass","item_herb_sun_crystal_flower","item_herb_coral_herb"],
    5:["item_herb_ice_fire_lotus","item_herb_void_mushroom","item_liquid_dragon_blood","item_energy_crystal"],
    6:["item_herb_bodhi_leaf","item_herb_nether_flower","item_phoenix_feather","item_demon_blood"],
    7:["item_herb_star_grass","item_herb_dragon_scale_moss","item_herb_dream_lotus","item_soul_essence","item_space_crystal"],
    8:["item_herb_phoenix_flower","item_herb_ancient_tree_sap","item_time_sand","item_ore_void_stone"],
    9:["item_herb_emperor_root","item_herb_eternal_fruit","item_ore_emperor_jade","item_dragon_reverse_scale"],
    10:["item_herb_god_grass","item_ore_divine_gold","item_essence_creation","item_world_fragment"],
}
CORE_POOL = {
    1:["item_core_1","item_beast_bone","item_beast_skin"],
    2:["item_core_2","item_beast_claw","item_beast_fang"],
    3:["item_core_3","item_beast_horn","item_beast_eye","item_beast_feather"],
    4:["item_core_4","item_flame_seed","item_essence_fire","item_essence_water","item_essence_wind"],
    5:["item_core_5","item_dragon_scale_plus","item_dragon_tendon","item_beast_heart"],
    6:["item_core_6","item_phoenix_feather","item_qilin_horn","item_beast_brain"],
    7:["item_core_7","item_soul_essence","item_ore_soul_crystal"],
    8:["item_core_8","item_time_sand","item_ore_shadow_stone"],
    9:["item_core_9","item_ore_light_crystal","item_dragon_reverse_scale"],
    10:["item_core_9","item_ore_divine_gold","item_world_fragment"],
}

CONSUMABLE_PILLS = [
    ("item_healing_powder",1,90),("item_recover_pill_1",1,85),("item_blood_pill",1,80),
    ("item_first_aid_kit",1,82),("item_bandage",1,88),("item_qi_powder",1,85),
    ("item_qi_pill_1",1,80),("item_str_pill_1",1,78),("item_spd_pill_1",1,78),
    ("item_antidote_1",1,92),("item_poison_1",1,85),("item_trail_ration",1,95),
    ("item_recovery_salve",1,90),("item_hp_small",1,88),("item_mp_small",1,88),
    ("item_stamina_pill",1,85),("item_meat_skewer",1,95),("item_sleep_bomb",1,80),
    ("item_blind_dust",1,82),("item_smoke_bomb",1,90),("item_element_resist_fire",1,85),
    ("item_element_resist_ice",1,85),
    ("item_recover_pill_2",2,80),("item_flesh_pill",2,75),("item_bone_pill",2,78),
    ("item_qi_pill_2",2,80),("item_dual_pill_1",2,70),("item_str_pill_2",2,73),
    ("item_spd_pill_2",2,73),("item_def_pill_1",2,75),("item_antidote_2",2,88),
    ("item_poison_2",2,80),("item_rage_pill",2,68),("item_soul_pill_1",2,70),
    ("item_spirit_rice",2,90),("item_spirit_wine",2,88),("item_hp_medium",2,82),
    ("item_mp_medium",2,82),("item_paralyze_needle",2,78),("item_crit_pill",2,72),
    ("item_dodge_pill",2,72),("item_treasure_pill",2,70),("item_shield_pill",2,70),
    ("item_blood_essence_potion",2,76),("item_iron_skin_potion",2,78),
    ("item_spirit_recovery_tea",2,85),("item_element_fire_pill",2,72),
    ("item_element_ice_pill",2,72),("item_element_thunder_pill",2,72),
    ("item_element_wind_pill",2,72),("item_element_poison_pill",2,72),
    ("item_recover_pill_3",3,70),("item_marrow_pill",3,65),("item_purple_blood_pill",3,62),
    ("item_qi_pill_3",3,70),("item_dual_pill_2",3,60),("item_str_pill_3",3,63),
    ("item_spd_pill_3",3,63),("item_def_pill_2",3,65),("item_antidote_3",3,82),
    ("item_poison_3",3,68),("item_break_pill_1",3,52),("item_soul_pill_2",3,62),
    ("item_blood_boil_pill",3,58),("item_beast_meat",3,85),("item_moon_well_water",3,72),
    ("item_mana_potion",3,70),("item_hp_large",3,72),("item_mp_large",3,72),
    ("item_dodge_pill_2",3,65),("item_crit_pill_2",3,65),("item_freeze_bomb",3,68),
    ("item_hp_regen_pill",3,65),("item_qi_regen_pill",3,65),("item_thorns_pill",3,62),
    ("item_stamina_pill_2",3,75),
    ("item_recover_pill_4",4,60),("item_purple_heart_pill",4,55),("item_qi_pill_4",4,60),
    ("item_dual_pill_3",4,50),("item_str_pill_4",4,53),("item_spd_pill_4",4,53),
    ("item_def_pill_3",4,55),("item_antidote_4",4,75),("item_poison_4",4,58),
    ("item_break_pill_2",4,42),("item_soul_pill_3",4,52),("item_desperation_pill",4,48),
    ("item_elexir_of_life",4,55),("item_hp_super",4,62),("item_mp_super",4,62),
    ("item_haste_potion",4,55),("item_shield_pill_2",4,52),("item_qi_regen_pill_2",4,55),
    ("item_hp_regen_pill_2",4,55),("item_lifesteal_pill",4,50),
    ("item_recover_pill_5",5,50),("item_dragon_blood_pill",5,42),("item_qi_pill_5",5,50),
    ("item_dual_pill_4",5,40),("item_break_pill_3",5,32),("item_soul_pill_4",5,42),
    ("item_poison_5",5,48),("item_sacrifice_pill",5,38),("item_dragon_meat",5,70),
    ("item_star_dew",5,52),("item_troll_blood",5,55),("item_berserker_potion",5,45),
    ("item_hp_elite",5,52),("item_mp_elite",5,52),("item_shield_pill_3",5,42),
    ("item_all_buff_pill",5,42),
    ("item_recover_pill_6",6,40),("item_phoenix_pill",6,30),("item_qi_pill_6",6,40),
    ("item_dual_pill_5",6,30),("item_break_pill_4",6,22),("item_full_recovery",6,32),
    ("item_double_damage_pill",6,28),("item_phoenix_ash",6,35),
    ("item_recover_pill_7",7,30),("item_primordial_pill",7,22),("item_qi_pill_7",7,30),
    ("item_dual_pill_6",7,20),("item_break_pill_5",7,14),("item_ancient_pill_fragment",7,25),
    ("item_recover_pill_8",8,20),("item_soul_restore_pill",8,14),("item_qi_pill_8",8,20),
    ("item_dual_pill_7",8,12),("item_break_pill_6",8,10),("item_ancient_essence",8,15),
    ("item_recover_pill_9",9,14),("item_qi_pill_9",9,14),("item_dual_pill_8",9,10),
    ("item_god_pill",10,8),("item_divine_dew",10,5),
    # 更多消耗品（补全到500+丹方）
    ("item_meat_skewer",1,95),("item_trail_ration",1,95),("item_clean_water",1,98),
    ("item_spirit_rice",2,90),("item_spirit_wine",2,88),("item_beast_meat",3,85),
    ("item_dragon_meat",5,70),("item_moon_well_water",3,72),("item_star_dew",5,52),
    ("item_phoenix_ash",6,35),("item_ancient_pill_fragment",7,25),("item_ancient_essence",8,15),
    ("item_troll_blood",5,55),("item_berserker_potion",5,45),("item_double_damage_pill",6,28),
    ("item_damage_shield",6,38),("item_revive_feather",6,25),("item_repair_hammer",1,90),
    ("item_escape_rope",1,85),("item_storage_bag",1,75),("item_luck_charm",3,65),
    ("item_exp_boost_scroll",4,55),("item_blessing_scroll",3,62),("item_damage_shield",3,60),
    ("item_encounter_lure",2,75),("item_encounter_repel",2,75),("item_identify_scroll",2,80),
    ("item_cultivation_stone",3,55),("item_cultivation_jade",4,45),("item_soul_crystal_ball",5,40),
    ("item_meditation_mat",6,35),("item_time_chamber_key",7,20),("item_pill_furnace",3,60),
    ("item_flame_controlling_ring",4,50),("item_return_scroll_1",1,70),("item_return_scroll_2",4,50),
    ("item_return_scroll_3",6,40),("item_skill_reset_scroll",4,45),("item_stat_reset_pill",6,35),
    ("item_curse_removal",2,80),("item_weather_stone",2,75),("item_pet_food",1,90),
    ("item_pet_taming_reins",2,70),("item_enchant_stone_1",1,75),("item_enchant_stone_2",3,60),
    ("item_enchant_stone_3",4,45),("item_enchant_stone_4",5,35),("item_enchant_stone_5",6,25),
    ("item_box_mystery",1,70),("item_box_silver",2,60),("item_box_gold",4,45),
    ("item_box_diamond",5,35),("item_box_legendary",6,25),
    ("item_gift_flower",1,95),("item_gift_spice",2,85),("item_gift_jewelry",3,75),
    ("item_gift_perfume",4,65),("item_gift_treasure",5,50),("item_gift_dragon_pearl",6,35),
    ("item_gift_painting",2,82),("item_gift_wine",3,72),
]

CUSTOM_RECIPES = [
    ("recipe_a01","改良方","item_recover_pill_1",1,[("item_herb_lingzhi",2),("item_clean_water",2)],92),
    ("recipe_a02","古法","item_recover_pill_2",2,[("item_herb_heal_grass",4),("item_herb_lingzhi",2),("item_beast_bone",2)],78),
    ("recipe_a03","秘传","item_recover_pill_3",3,[("item_herb_soul_flower",2),("item_herb_blood_rose",2),("item_core_2",2)],72),
    ("recipe_a04","捷径","item_qi_pill_2",2,[("item_herb_spirit_grass",2),("item_herb_wind_flower",1)],85),
    ("recipe_a05","双倍","item_blood_pill",1,[("item_herb_heal_grass",3),("item_herb_ginseng",3)],70),
    ("recipe_a06","精炼","item_hp_medium",2,[("item_herb_lingzhi",2),("item_herb_heal_grass",2)],88),
    ("recipe_a07","浓缩","item_mp_medium",2,[("item_herb_spirit_grass",3),("item_herb_lingzhi",1)],88),
    ("recipe_a08","秘方","item_str_pill_2",2,[("item_herb_ginseng",4),("item_beast_fang",2)],68),
    ("recipe_a09","古法","item_antidote_2",2,[("item_herb_lingzhi",3),("item_herb_snow_lotus",1)],90),
    ("recipe_a10","改良","item_break_pill_1",3,[("item_herb_soul_flower",3),("item_core_2",3)],55),
    ("recipe_a11","捷径","item_shield_pill",2,[("item_beast_skin",3),("item_herb_spirit_grass",1)],75),
    ("recipe_a12","精制","item_dual_pill_1",2,[("item_herb_heal_grass",3),("item_herb_spirit_grass",2),("item_herb_lingzhi",1)],72),
    ("recipe_a13","古方","item_spd_pill_2",2,[("item_beast_feather",3),("item_herb_wind_flower",2)],70),
    ("recipe_a14","秘传","item_poison_2",2,[("item_herb_blood_rose",3),("item_beast_fang",1)],82),
    ("recipe_a15","改良","item_recover_pill_4",4,[("item_herb_moon_dew_grass",3),("item_herb_dragon_blood_grass",1),("item_core_3",2)],58),
    ("recipe_a16","古法","item_break_pill_2",4,[("item_herb_soul_flower",4),("item_core_3",4)],44),
    ("recipe_a17","秘传","item_recover_pill_5",5,[("item_herb_ice_fire_lotus",3),("item_liquid_dragon_blood",1),("item_core_4",2)],48),
    ("recipe_a18","改良","item_break_pill_4",6,[("item_herb_bodhi_leaf",3),("item_phoenix_feather",1),("item_core_5",3)],25),
    ("recipe_a19","古方","item_primordial_pill",7,[("item_herb_dragon_scale_moss",3),("item_soul_essence",2),("item_core_6",3)],20),
    ("recipe_a20","秘方","item_recover_pill_8",8,[("item_herb_ancient_tree_sap",3),("item_time_sand",1),("item_core_7",3)],16),
    ("recipe_a21","捷径","item_qi_pill_7",7,[("item_herb_star_grass",4),("item_space_crystal",1)],28),
    ("recipe_a22","古法","item_dual_pill_6",7,[("item_herb_dream_lotus",2),("item_soul_essence",2),("item_ore_soul_crystal",1)],18),
    ("recipe_a23","秘传","item_god_pill",10,[("item_herb_god_grass",4),("item_ore_divine_gold",3),("item_world_fragment",1)],4),
    ("recipe_a24","改良","item_recover_pill_9",9,[("item_herb_emperor_root",4),("item_ore_emperor_jade",2),("item_core_8",3)],12),
    ("recipe_a25","古方","item_qi_pill_9",9,[("item_herb_eternal_fruit",2),("item_ore_light_crystal",2)],16),
    ("recipe_a26","秘方","item_full_recovery",6,[("item_herb_bodhi_leaf",2),("item_herb_nether_flower",1),("item_phoenix_feather",1)],30),
    ("recipe_a27","捷径","item_elexir_of_life",4,[("item_herb_coral_herb",3),("item_liquid_spirit_water",2)],58),
    ("recipe_a28","古法","item_hp_elite",5,[("item_herb_void_mushroom",3),("item_dragon_tendon",1)],50),
    ("recipe_a29","秘方","item_recover_pill_6",6,[("item_herb_nether_flower",2),("item_demon_blood",1),("item_core_5",2)],38),
    ("recipe_a30","改良","item_qi_pill_5",5,[("item_herb_void_mushroom",3),("item_energy_crystal",2)],48),
    ("recipe_b01","极品","item_hp_small",1,[("item_herb_ginseng",2),("item_herb_lingzhi",1)],95),
    ("recipe_b02","极品","item_mp_small",1,[("item_herb_spirit_grass",2),("item_herb_lingzhi",1)],95),
    ("recipe_b03","古法","item_qi_pill_3",3,[("item_herb_spirit_grass",5),("item_core_2",2)],68),
    ("recipe_b04","秘传","item_marrow_pill",3,[("item_herb_dragon_blood_grass",2),("item_core_2",3)],62),
    ("recipe_b05","改良","item_antidote_3",3,[("item_herb_blood_rose",2),("item_herb_soul_flower",2)],84),
    ("recipe_b06","双倍","item_dual_pill_2",3,[("item_herb_heal_grass",5),("item_herb_spirit_grass",4),("item_core_2",4)],55),
    ("recipe_b07","古方","item_despiration_pill",4,[("item_herb_dragon_blood_grass",3),("item_core_3",3)],50),
    ("recipe_b08","极品","item_hp_super",4,[("item_herb_moon_dew_grass",2),("item_herb_coral_herb",2),("item_core_3",2)],65),
    ("recipe_b09","捷径","item_haste_potion",4,[("item_herb_wind_flower",4),("item_beast_feather",3)],52),
    ("recipe_b10","古法","item_break_pill_3",5,[("item_herb_ice_fire_lotus",3),("item_soul_essence",2),("item_core_4",4)],30),
    ("recipe_b11","秘方","item_dragon_blood_pill",5,[("item_liquid_dragon_blood",2),("item_dragon_scale_plus",2),("item_core_4",3)],40),
    ("recipe_b12","改良","item_poison_5",5,[("item_herb_blood_rose",6),("item_dragon_reverse_scale",1)],45),
    ("recipe_b13","双倍","item_full_recovery",6,[("item_herb_bodhi_leaf",3),("item_herb_nether_flower",2),("item_core_5",3)],28),
    ("recipe_b14","古方","item_qi_pill_6",6,[("item_herb_star_grass",3),("item_space_crystal",1)],38),
    ("recipe_b15","秘传","item_dual_pill_5",6,[("item_herb_nether_flower",3),("item_phoenix_feather",2),("item_core_5",4)],25),
    ("recipe_b16","极品","item_qi_pill_8",8,[("item_herb_ancient_tree_sap",3),("item_ore_void_stone",2)],18),
    ("recipe_b17","古法","item_soul_restore_pill",8,[("item_herb_phoenix_flower",3),("item_soul_essence",3),("item_core_7",4)],12),
    ("recipe_b18","秘方","item_dual_pill_7",8,[("item_herb_star_petal",2),("item_time_sand",2),("item_core_7",4)],10),
    ("recipe_b19","改良","item_ancient_essence",8,[("item_herb_phoenix_flower",4),("item_core_7",3)],13),
    ("recipe_b20","古方","item_recover_pill_9",9,[("item_herb_void_lichen",3),("item_ore_emperor_jade",3),("item_core_8",4)],10),
    ("recipe_b21","秘传","item_dual_pill_8",9,[("item_herb_eternal_fruit",3),("item_ore_light_crystal",2),("item_core_8",4)],8),
    ("recipe_b22","极品","item_qi_pill_9",9,[("item_herb_emperor_root",5),("item_ore_light_crystal",3)],12),
    ("recipe_b23","古法","item_divine_dew",10,[("item_herb_god_grass",5),("item_liquid_ambrosia",2),("item_world_fragment",1)],3),
    ("recipe_b24","秘方","item_god_pill",10,[("item_herb_god_grass",6),("item_essence_creation",2),("item_world_fragment",2)],2),
    ("recipe_b25","改良","item_phoenix_pill",6,[("item_phoenix_feather",3),("item_herb_phoenix_flower",2),("item_core_5",3)],28),
    ("recipe_b26","捷径","item_break_pill_5",7,[("item_herb_dream_lotus",3),("item_soul_essence",3),("item_core_6",4)],12),
    ("recipe_b27","古法","item_break_pill_6",8,[("item_herb_ancient_tree_sap",2),("item_time_sand",2),("item_core_7",5)],8),
    ("recipe_b28","秘方","item_dragon_meat",5,[("item_dragon_scale_plus",2),("item_herb_ice_fire_lotus",2)],72),
    ("recipe_b29","改良","item_shield_pill_3",5,[("item_beast_heart",3),("item_herb_void_mushroom",2)],44),
    ("recipe_b30","古法","item_all_buff_pill",5,[("item_herb_void_mushroom",3),("item_energy_crystal",2),("item_core_4",2)],40),
]

def _hash(seed, mod): return (seed * 2654435761) % mod

def generate():
    recipes = []
    rid = 0
    for pill_id, grade, base_rate in CONSUMABLE_PILLS:
        g = min(10, max(1, grade))
        herbs = HERB_POOL.get(g, HERB_POOL[1])
        cores = CORE_POOL.get(g, CORE_POOL[1])
        is_special = pill_id.startswith("item_break_") or pill_id in ("item_god_pill","item_divine_dew")
        # 每个丹药生成1-3个配方变体
        variants = 1 if is_special else 2 if base_rate < 70 else 3 if base_rate < 85 else 2
        for v in range(variants):
            rid += 1
            mc = 1 if v == 0 and base_rate >= 85 else 2 if v == 1 else 3
            rate_mod = 0 if v == 0 else -5 if v == 1 else -10
            mats = []
            for i in range(mc):
                if i == 0:
                    mats.append((herbs[_hash(rid*7+i+v*31, len(herbs))], 1+_hash(rid+v,3)))
                elif i == 1:
                    mats.append((cores[_hash(rid*13+i+v*17, len(cores))], 1+_hash(rid+v,2)))
                else:
                    pool = herbs + cores
                    mats.append((pool[_hash(rid*19+i+v*23, len(pool))], 1))
            r = max(5, min(95, base_rate + rate_mod))
            suffix = ["标准方","省料方","高成功率方"][v] if variants > 1 else ""
            recipes.append({
                "id":f"recipe_{rid}","name":f"丹方·{suffix}" if suffix else f"丹方·第{rid}号",
                "output":pill_id,"grade":grade,"materials":mats,"base_rate":r,"is_special":is_special
            })
    for rec_id, suffix, output, grade, mats, rate in CUSTOM_RECIPES:
        rid += 1
        recipes.append({"id":rec_id,"name":f"丹方·{suffix}","output":output,"grade":grade,"materials":[(m[0],m[1]) for m in mats],"base_rate":rate,"is_special":False})
    return recipes

def main():
    recipes = generate()
    print(f"丹方: {len(recipes)} / 药鼎: {len(FURNACES)}")
    d = Path("src/wordworld/data"); d.mkdir(parents=True, exist_ok=True)
    with open(d/"furnace_data.py","w",encoding="utf-8") as f:
        f.write('"""药鼎数据"""\nfrom typing import Any,Dict,List\nFURNACE_DATA=')
        json.dump(FURNACES,f,ensure_ascii=False,indent=2); f.write('\n')
    with open(d/"recipe_data.py","w",encoding="utf-8") as f:
        f.write('"""丹方数据"""\nfrom typing import Any,Dict,List,Tuple\n')
        f.write(f'ALCHEMY_RECIPE_DATA=')
        json.dump(recipes,f,ensure_ascii=False,indent=2); f.write('\n')
    for fn in os.listdir(d):
        if fn.endswith('.py'):
            p=d/fn
            with open(p,'r',encoding='utf-8') as fh: c=fh.read()
            c2=c.replace('true','True').replace('false','False').replace('null','None')
            if c2!=c:
                with open(p,'w',encoding='utf-8') as fh: fh.write(c2)
    from collections import Counter
    print(f"品级分布: {dict(sorted(Counter(r['grade'] for r in recipes).items()))}")

if __name__=="__main__": main()
