"""丹方数据"""
from typing import Any,Dict,List,Tuple
ALCHEMY_RECIPE_DATA=[
  {
    "id": "recipe_1",
    "name": "丹方·标准方",
    "output": "item_healing_powder",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        2
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_2",
    "name": "丹方·省料方",
    "output": "item_healing_powder",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        1
      ],
      [
        "item_beast_skin",
        2
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_3",
    "name": "丹方·标准方",
    "output": "item_recover_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_4",
    "name": "丹方·省料方",
    "output": "item_recover_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        3
      ],
      [
        "item_beast_bone",
        2
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_5",
    "name": "丹方·标准方",
    "output": "item_blood_pill",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        3
      ],
      [
        "item_core_1",
        2
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_6",
    "name": "丹方·省料方",
    "output": "item_blood_pill",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        2
      ],
      [
        "item_core_1",
        2
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_7",
    "name": "丹方·高成功率方",
    "output": "item_blood_pill",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        1
      ],
      [
        "item_core_1",
        2
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_8",
    "name": "丹方·标准方",
    "output": "item_first_aid_kit",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_core_1",
        1
      ],
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 82,
    "is_special": False
  },
  {
    "id": "recipe_9",
    "name": "丹方·省料方",
    "output": "item_first_aid_kit",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 77,
    "is_special": False
  },
  {
    "id": "recipe_10",
    "name": "丹方·高成功率方",
    "output": "item_first_aid_kit",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_core_1",
        1
      ],
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_11",
    "name": "丹方·标准方",
    "output": "item_bandage",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        3
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_12",
    "name": "丹方·省料方",
    "output": "item_bandage",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        2
      ],
      [
        "item_core_1",
        2
      ]
    ],
    "base_rate": 83,
    "is_special": False
  },
  {
    "id": "recipe_13",
    "name": "丹方·标准方",
    "output": "item_qi_powder",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        2
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_14",
    "name": "丹方·省料方",
    "output": "item_qi_powder",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        1
      ],
      [
        "item_beast_skin",
        2
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_15",
    "name": "丹方·标准方",
    "output": "item_qi_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        1
      ],
      [
        "item_beast_bone",
        2
      ],
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_16",
    "name": "丹方·省料方",
    "output": "item_qi_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        3
      ],
      [
        "item_beast_bone",
        2
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_17",
    "name": "丹方·高成功率方",
    "output": "item_qi_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        2
      ],
      [
        "item_beast_bone",
        2
      ],
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_18",
    "name": "丹方·标准方",
    "output": "item_str_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        1
      ],
      [
        "item_beast_bone",
        1
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 78,
    "is_special": False
  },
  {
    "id": "recipe_19",
    "name": "丹方·省料方",
    "output": "item_str_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 73,
    "is_special": False
  },
  {
    "id": "recipe_20",
    "name": "丹方·高成功率方",
    "output": "item_str_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_beast_bone",
        1
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_21",
    "name": "丹方·标准方",
    "output": "item_spd_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        1
      ],
      [
        "item_beast_bone",
        2
      ],
      [
        "item_clean_water",
        1
      ]
    ],
    "base_rate": 78,
    "is_special": False
  },
  {
    "id": "recipe_22",
    "name": "丹方·省料方",
    "output": "item_spd_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        3
      ],
      [
        "item_beast_bone",
        2
      ]
    ],
    "base_rate": 73,
    "is_special": False
  },
  {
    "id": "recipe_23",
    "name": "丹方·高成功率方",
    "output": "item_spd_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        2
      ],
      [
        "item_beast_bone",
        2
      ],
      [
        "item_clean_water",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_24",
    "name": "丹方·标准方",
    "output": "item_antidote_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 92,
    "is_special": False
  },
  {
    "id": "recipe_25",
    "name": "丹方·省料方",
    "output": "item_antidote_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 87,
    "is_special": False
  },
  {
    "id": "recipe_26",
    "name": "丹方·标准方",
    "output": "item_poison_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_27",
    "name": "丹方·省料方",
    "output": "item_poison_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_28",
    "name": "丹方·标准方",
    "output": "item_trail_ration",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        2
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_29",
    "name": "丹方·省料方",
    "output": "item_trail_ration",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        1
      ],
      [
        "item_beast_skin",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_30",
    "name": "丹方·标准方",
    "output": "item_recovery_salve",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_31",
    "name": "丹方·省料方",
    "output": "item_recovery_salve",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_32",
    "name": "丹方·标准方",
    "output": "item_hp_small",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_33",
    "name": "丹方·省料方",
    "output": "item_hp_small",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 83,
    "is_special": False
  },
  {
    "id": "recipe_34",
    "name": "丹方·标准方",
    "output": "item_mp_small",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_35",
    "name": "丹方·省料方",
    "output": "item_mp_small",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_beast_skin",
        1
      ]
    ],
    "base_rate": 83,
    "is_special": False
  },
  {
    "id": "recipe_36",
    "name": "丹方·标准方",
    "output": "item_stamina_pill",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_37",
    "name": "丹方·省料方",
    "output": "item_stamina_pill",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_38",
    "name": "丹方·标准方",
    "output": "item_meat_skewer",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_39",
    "name": "丹方·省料方",
    "output": "item_meat_skewer",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_40",
    "name": "丹方·标准方",
    "output": "item_sleep_bomb",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        2
      ],
      [
        "item_beast_skin",
        1
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_41",
    "name": "丹方·省料方",
    "output": "item_sleep_bomb",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        1
      ],
      [
        "item_beast_skin",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_42",
    "name": "丹方·高成功率方",
    "output": "item_sleep_bomb",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_beast_skin",
        1
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_43",
    "name": "丹方·标准方",
    "output": "item_blind_dust",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        2
      ],
      [
        "item_beast_skin",
        2
      ],
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 82,
    "is_special": False
  },
  {
    "id": "recipe_44",
    "name": "丹方·省料方",
    "output": "item_blind_dust",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        1
      ],
      [
        "item_beast_skin",
        2
      ]
    ],
    "base_rate": 77,
    "is_special": False
  },
  {
    "id": "recipe_45",
    "name": "丹方·高成功率方",
    "output": "item_blind_dust",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        3
      ],
      [
        "item_beast_skin",
        2
      ],
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_46",
    "name": "丹方·标准方",
    "output": "item_smoke_bomb",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_47",
    "name": "丹方·省料方",
    "output": "item_smoke_bomb",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_beast_skin",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_48",
    "name": "丹方·标准方",
    "output": "item_element_resist_fire",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_49",
    "name": "丹方·省料方",
    "output": "item_element_resist_fire",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_50",
    "name": "丹方·标准方",
    "output": "item_element_resist_ice",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_51",
    "name": "丹方·省料方",
    "output": "item_element_resist_ice",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_52",
    "name": "丹方·标准方",
    "output": "item_recover_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        2
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_53",
    "name": "丹方·省料方",
    "output": "item_recover_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_54",
    "name": "丹方·高成功率方",
    "output": "item_recover_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_herb_golden_mushroom",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_55",
    "name": "丹方·标准方",
    "output": "item_flesh_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_56",
    "name": "丹方·省料方",
    "output": "item_flesh_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        1
      ],
      [
        "item_beast_fang",
        2
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_57",
    "name": "丹方·高成功率方",
    "output": "item_flesh_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        3
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_58",
    "name": "丹方·标准方",
    "output": "item_bone_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 78,
    "is_special": False
  },
  {
    "id": "recipe_59",
    "name": "丹方·省料方",
    "output": "item_bone_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 73,
    "is_special": False
  },
  {
    "id": "recipe_60",
    "name": "丹方·高成功率方",
    "output": "item_bone_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        3
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_61",
    "name": "丹方·标准方",
    "output": "item_qi_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_62",
    "name": "丹方·省料方",
    "output": "item_qi_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        1
      ],
      [
        "item_beast_fang",
        2
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_63",
    "name": "丹方·高成功率方",
    "output": "item_qi_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        3
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_64",
    "name": "丹方·标准方",
    "output": "item_dual_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        2
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_herb_golden_mushroom",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_65",
    "name": "丹方·省料方",
    "output": "item_dual_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_66",
    "name": "丹方·高成功率方",
    "output": "item_dual_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_67",
    "name": "丹方·标准方",
    "output": "item_str_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        2
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 73,
    "is_special": False
  },
  {
    "id": "recipe_68",
    "name": "丹方·省料方",
    "output": "item_str_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_beast_fang",
        2
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_69",
    "name": "丹方·高成功率方",
    "output": "item_str_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 63,
    "is_special": False
  },
  {
    "id": "recipe_70",
    "name": "丹方·标准方",
    "output": "item_spd_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 73,
    "is_special": False
  },
  {
    "id": "recipe_71",
    "name": "丹方·省料方",
    "output": "item_spd_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_72",
    "name": "丹方·高成功率方",
    "output": "item_spd_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        3
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 63,
    "is_special": False
  },
  {
    "id": "recipe_73",
    "name": "丹方·标准方",
    "output": "item_def_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_74",
    "name": "丹方·省料方",
    "output": "item_def_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ],
      [
        "item_beast_fang",
        2
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_75",
    "name": "丹方·高成功率方",
    "output": "item_def_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        3
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_76",
    "name": "丹方·标准方",
    "output": "item_antidote_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_77",
    "name": "丹方·省料方",
    "output": "item_antidote_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 83,
    "is_special": False
  },
  {
    "id": "recipe_78",
    "name": "丹方·标准方",
    "output": "item_poison_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_79",
    "name": "丹方·省料方",
    "output": "item_poison_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_80",
    "name": "丹方·高成功率方",
    "output": "item_poison_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_81",
    "name": "丹方·标准方",
    "output": "item_rage_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_82",
    "name": "丹方·省料方",
    "output": "item_rage_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_beast_claw",
        2
      ]
    ],
    "base_rate": 63,
    "is_special": False
  },
  {
    "id": "recipe_83",
    "name": "丹方·标准方",
    "output": "item_soul_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        3
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_84",
    "name": "丹方·省料方",
    "output": "item_soul_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_85",
    "name": "丹方·高成功率方",
    "output": "item_soul_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_86",
    "name": "丹方·标准方",
    "output": "item_spirit_rice",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        3
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_87",
    "name": "丹方·省料方",
    "output": "item_spirit_rice",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_88",
    "name": "丹方·标准方",
    "output": "item_spirit_wine",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_89",
    "name": "丹方·省料方",
    "output": "item_spirit_wine",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 83,
    "is_special": False
  },
  {
    "id": "recipe_90",
    "name": "丹方·标准方",
    "output": "item_hp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        1
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 82,
    "is_special": False
  },
  {
    "id": "recipe_91",
    "name": "丹方·省料方",
    "output": "item_hp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        3
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 77,
    "is_special": False
  },
  {
    "id": "recipe_92",
    "name": "丹方·高成功率方",
    "output": "item_hp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_93",
    "name": "丹方·标准方",
    "output": "item_mp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 82,
    "is_special": False
  },
  {
    "id": "recipe_94",
    "name": "丹方·省料方",
    "output": "item_mp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_beast_claw",
        2
      ]
    ],
    "base_rate": 77,
    "is_special": False
  },
  {
    "id": "recipe_95",
    "name": "丹方·高成功率方",
    "output": "item_mp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_96",
    "name": "丹方·标准方",
    "output": "item_paralyze_needle",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_golden_mushroom",
        1
      ]
    ],
    "base_rate": 78,
    "is_special": False
  },
  {
    "id": "recipe_97",
    "name": "丹方·省料方",
    "output": "item_paralyze_needle",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 73,
    "is_special": False
  },
  {
    "id": "recipe_98",
    "name": "丹方·高成功率方",
    "output": "item_paralyze_needle",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        2
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_99",
    "name": "丹方·标准方",
    "output": "item_crit_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        1
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_100",
    "name": "丹方·省料方",
    "output": "item_crit_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        3
      ],
      [
        "item_beast_claw",
        2
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_101",
    "name": "丹方·高成功率方",
    "output": "item_crit_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        2
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_102",
    "name": "丹方·标准方",
    "output": "item_dodge_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_103",
    "name": "丹方·省料方",
    "output": "item_dodge_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        3
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_104",
    "name": "丹方·高成功率方",
    "output": "item_dodge_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_105",
    "name": "丹方·标准方",
    "output": "item_treasure_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        1
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_106",
    "name": "丹方·省料方",
    "output": "item_treasure_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        3
      ],
      [
        "item_beast_claw",
        2
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_107",
    "name": "丹方·高成功率方",
    "output": "item_treasure_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_108",
    "name": "丹方·标准方",
    "output": "item_shield_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_109",
    "name": "丹方·省料方",
    "output": "item_shield_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_110",
    "name": "丹方·高成功率方",
    "output": "item_shield_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_golden_mushroom",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_111",
    "name": "丹方·标准方",
    "output": "item_blood_essence_potion",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 76,
    "is_special": False
  },
  {
    "id": "recipe_112",
    "name": "丹方·省料方",
    "output": "item_blood_essence_potion",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_beast_claw",
        2
      ]
    ],
    "base_rate": 71,
    "is_special": False
  },
  {
    "id": "recipe_113",
    "name": "丹方·高成功率方",
    "output": "item_blood_essence_potion",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        2
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 66,
    "is_special": False
  },
  {
    "id": "recipe_114",
    "name": "丹方·标准方",
    "output": "item_iron_skin_potion",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        1
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 78,
    "is_special": False
  },
  {
    "id": "recipe_115",
    "name": "丹方·省料方",
    "output": "item_iron_skin_potion",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        3
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 73,
    "is_special": False
  },
  {
    "id": "recipe_116",
    "name": "丹方·高成功率方",
    "output": "item_iron_skin_potion",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        2
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_117",
    "name": "丹方·标准方",
    "output": "item_spirit_recovery_tea",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_118",
    "name": "丹方·省料方",
    "output": "item_spirit_recovery_tea",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        3
      ],
      [
        "item_beast_claw",
        2
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_119",
    "name": "丹方·标准方",
    "output": "item_element_fire_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        3
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_120",
    "name": "丹方·省料方",
    "output": "item_element_fire_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_121",
    "name": "丹方·高成功率方",
    "output": "item_element_fire_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_122",
    "name": "丹方·标准方",
    "output": "item_element_ice_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_core_2",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_123",
    "name": "丹方·省料方",
    "output": "item_element_ice_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_124",
    "name": "丹方·高成功率方",
    "output": "item_element_ice_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        1
      ],
      [
        "item_core_2",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_125",
    "name": "丹方·标准方",
    "output": "item_element_thunder_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_126",
    "name": "丹方·省料方",
    "output": "item_element_thunder_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_127",
    "name": "丹方·高成功率方",
    "output": "item_element_thunder_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_128",
    "name": "丹方·标准方",
    "output": "item_element_wind_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        3
      ],
      [
        "item_core_2",
        1
      ],
      [
        "item_herb_golden_mushroom",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_129",
    "name": "丹方·省料方",
    "output": "item_element_wind_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_130",
    "name": "丹方·高成功率方",
    "output": "item_element_wind_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_core_2",
        1
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_131",
    "name": "丹方·标准方",
    "output": "item_element_poison_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        3
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_132",
    "name": "丹方·省料方",
    "output": "item_element_poison_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_133",
    "name": "丹方·高成功率方",
    "output": "item_element_poison_pill",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        1
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_134",
    "name": "丹方·标准方",
    "output": "item_recover_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_core_3",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_135",
    "name": "丹方·省料方",
    "output": "item_recover_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_136",
    "name": "丹方·高成功率方",
    "output": "item_recover_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_137",
    "name": "丹方·标准方",
    "output": "item_marrow_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        3
      ],
      [
        "item_beast_eye",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_138",
    "name": "丹方·省料方",
    "output": "item_marrow_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        2
      ],
      [
        "item_core_3",
        2
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_139",
    "name": "丹方·标准方",
    "output": "item_purple_blood_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        2
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_herb_fire_grass",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_140",
    "name": "丹方·省料方",
    "output": "item_purple_blood_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        1
      ],
      [
        "item_beast_eye",
        2
      ]
    ],
    "base_rate": 57,
    "is_special": False
  },
  {
    "id": "recipe_141",
    "name": "丹方·标准方",
    "output": "item_qi_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        1
      ],
      [
        "item_beast_eye",
        2
      ],
      [
        "item_herb_thunder_vine",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_142",
    "name": "丹方·省料方",
    "output": "item_qi_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        3
      ],
      [
        "item_core_3",
        2
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_143",
    "name": "丹方·高成功率方",
    "output": "item_qi_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        2
      ],
      [
        "item_beast_eye",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_144",
    "name": "丹方·标准方",
    "output": "item_dual_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_145",
    "name": "丹方·省料方",
    "output": "item_dual_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_146",
    "name": "丹方·标准方",
    "output": "item_str_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 63,
    "is_special": False
  },
  {
    "id": "recipe_147",
    "name": "丹方·省料方",
    "output": "item_str_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 58,
    "is_special": False
  },
  {
    "id": "recipe_148",
    "name": "丹方·标准方",
    "output": "item_spd_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_beast_eye",
        1
      ]
    ],
    "base_rate": 63,
    "is_special": False
  },
  {
    "id": "recipe_149",
    "name": "丹方·省料方",
    "output": "item_spd_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 58,
    "is_special": False
  },
  {
    "id": "recipe_150",
    "name": "丹方·标准方",
    "output": "item_def_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_core_3",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_151",
    "name": "丹方·省料方",
    "output": "item_def_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_152",
    "name": "丹方·标准方",
    "output": "item_antidote_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 82,
    "is_special": False
  },
  {
    "id": "recipe_153",
    "name": "丹方·省料方",
    "output": "item_antidote_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 77,
    "is_special": False
  },
  {
    "id": "recipe_154",
    "name": "丹方·高成功率方",
    "output": "item_antidote_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_beast_eye",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_155",
    "name": "丹方·标准方",
    "output": "item_poison_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        3
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_herb_fire_grass",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_156",
    "name": "丹方·省料方",
    "output": "item_poison_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        2
      ],
      [
        "item_beast_eye",
        2
      ]
    ],
    "base_rate": 63,
    "is_special": False
  },
  {
    "id": "recipe_157",
    "name": "丹方·第157号",
    "output": "item_break_pill_1",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        2
      ],
      [
        "item_beast_eye",
        2
      ],
      [
        "item_herb_thunder_vine",
        1
      ]
    ],
    "base_rate": 52,
    "is_special": True
  },
  {
    "id": "recipe_158",
    "name": "丹方·标准方",
    "output": "item_soul_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_core_3",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_159",
    "name": "丹方·省料方",
    "output": "item_soul_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 57,
    "is_special": False
  },
  {
    "id": "recipe_160",
    "name": "丹方·标准方",
    "output": "item_blood_boil_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 58,
    "is_special": False
  },
  {
    "id": "recipe_161",
    "name": "丹方·省料方",
    "output": "item_blood_boil_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 53,
    "is_special": False
  },
  {
    "id": "recipe_162",
    "name": "丹方·标准方",
    "output": "item_beast_meat",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_163",
    "name": "丹方·省料方",
    "output": "item_beast_meat",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_164",
    "name": "丹方·标准方",
    "output": "item_moon_well_water",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_beast_eye",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_165",
    "name": "丹方·省料方",
    "output": "item_moon_well_water",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_166",
    "name": "丹方·高成功率方",
    "output": "item_moon_well_water",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_167",
    "name": "丹方·标准方",
    "output": "item_mana_potion",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        3
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_168",
    "name": "丹方·省料方",
    "output": "item_mana_potion",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        2
      ],
      [
        "item_beast_eye",
        2
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_169",
    "name": "丹方·高成功率方",
    "output": "item_mana_potion",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        1
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_herb_fire_grass",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_170",
    "name": "丹方·标准方",
    "output": "item_hp_large",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_171",
    "name": "丹方·省料方",
    "output": "item_hp_large",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_172",
    "name": "丹方·高成功率方",
    "output": "item_hp_large",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_core_3",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_173",
    "name": "丹方·标准方",
    "output": "item_mp_large",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        3
      ],
      [
        "item_beast_eye",
        2
      ],
      [
        "item_herb_thunder_vine",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_174",
    "name": "丹方·省料方",
    "output": "item_mp_large",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        2
      ],
      [
        "item_core_3",
        2
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_175",
    "name": "丹方·高成功率方",
    "output": "item_mp_large",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        1
      ],
      [
        "item_beast_eye",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_176",
    "name": "丹方·标准方",
    "output": "item_dodge_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_177",
    "name": "丹方·省料方",
    "output": "item_dodge_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_178",
    "name": "丹方·标准方",
    "output": "item_crit_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_179",
    "name": "丹方·省料方",
    "output": "item_crit_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_180",
    "name": "丹方·标准方",
    "output": "item_freeze_bomb",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_beast_eye",
        1
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_181",
    "name": "丹方·省料方",
    "output": "item_freeze_bomb",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 63,
    "is_special": False
  },
  {
    "id": "recipe_182",
    "name": "丹方·标准方",
    "output": "item_hp_regen_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_core_3",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_183",
    "name": "丹方·省料方",
    "output": "item_hp_regen_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_184",
    "name": "丹方·标准方",
    "output": "item_qi_regen_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_185",
    "name": "丹方·省料方",
    "output": "item_qi_regen_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_186",
    "name": "丹方·标准方",
    "output": "item_thorns_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_187",
    "name": "丹方·省料方",
    "output": "item_thorns_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 57,
    "is_special": False
  },
  {
    "id": "recipe_188",
    "name": "丹方·标准方",
    "output": "item_stamina_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_beast_eye",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_189",
    "name": "丹方·省料方",
    "output": "item_stamina_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_190",
    "name": "丹方·高成功率方",
    "output": "item_stamina_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_191",
    "name": "丹方·标准方",
    "output": "item_recover_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_essence_wind",
        2
      ],
      [
        "item_herb_moon_dew_grass",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_192",
    "name": "丹方·省料方",
    "output": "item_recover_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_essence_wind",
        2
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_193",
    "name": "丹方·标准方",
    "output": "item_purple_heart_pill",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_core_4",
        2
      ],
      [
        "item_essence_fire",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_194",
    "name": "丹方·省料方",
    "output": "item_purple_heart_pill",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_195",
    "name": "丹方·标准方",
    "output": "item_qi_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_flame_seed",
        2
      ],
      [
        "item_herb_sun_crystal_flower",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_196",
    "name": "丹方·省料方",
    "output": "item_qi_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_flame_seed",
        2
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_197",
    "name": "丹方·标准方",
    "output": "item_dual_pill_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_essence_fire",
        2
      ],
      [
        "item_essence_water",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_198",
    "name": "丹方·省料方",
    "output": "item_dual_pill_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_essence_fire",
        2
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_199",
    "name": "丹方·标准方",
    "output": "item_str_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_essence_water",
        2
      ],
      [
        "item_herb_coral_herb",
        1
      ]
    ],
    "base_rate": 53,
    "is_special": False
  },
  {
    "id": "recipe_200",
    "name": "丹方·省料方",
    "output": "item_str_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        1
      ],
      [
        "item_essence_water",
        2
      ]
    ],
    "base_rate": 48,
    "is_special": False
  },
  {
    "id": "recipe_201",
    "name": "丹方·标准方",
    "output": "item_spd_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        1
      ],
      [
        "item_essence_wind",
        2
      ],
      [
        "item_essence_wind",
        1
      ]
    ],
    "base_rate": 53,
    "is_special": False
  },
  {
    "id": "recipe_202",
    "name": "丹方·省料方",
    "output": "item_spd_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_essence_wind",
        2
      ]
    ],
    "base_rate": 48,
    "is_special": False
  },
  {
    "id": "recipe_203",
    "name": "丹方·标准方",
    "output": "item_def_pill_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_core_4",
        2
      ],
      [
        "item_core_4",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_204",
    "name": "丹方·省料方",
    "output": "item_def_pill_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_205",
    "name": "丹方·标准方",
    "output": "item_antidote_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_flame_seed",
        2
      ],
      [
        "item_herb_dragon_blood_grass",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_206",
    "name": "丹方·省料方",
    "output": "item_antidote_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_flame_seed",
        2
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_207",
    "name": "丹方·高成功率方",
    "output": "item_antidote_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_flame_seed",
        2
      ],
      [
        "item_herb_coral_herb",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_208",
    "name": "丹方·标准方",
    "output": "item_poison_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_dragon_blood_grass",
        2
      ],
      [
        "item_core_4",
        1
      ],
      [
        "item_herb_coral_herb",
        1
      ]
    ],
    "base_rate": 58,
    "is_special": False
  },
  {
    "id": "recipe_209",
    "name": "丹方·省料方",
    "output": "item_poison_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_sun_crystal_flower",
        1
      ],
      [
        "item_core_4",
        1
      ]
    ],
    "base_rate": 53,
    "is_special": False
  },
  {
    "id": "recipe_210",
    "name": "丹方·第210号",
    "output": "item_break_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_sun_crystal_flower",
        1
      ],
      [
        "item_flame_seed",
        1
      ],
      [
        "item_essence_wind",
        1
      ]
    ],
    "base_rate": 42,
    "is_special": True
  },
  {
    "id": "recipe_211",
    "name": "丹方·标准方",
    "output": "item_soul_pill_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_essence_wind",
        2
      ],
      [
        "item_essence_fire",
        1
      ]
    ],
    "base_rate": 52,
    "is_special": False
  },
  {
    "id": "recipe_212",
    "name": "丹方·省料方",
    "output": "item_soul_pill_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        1
      ],
      [
        "item_essence_wind",
        2
      ]
    ],
    "base_rate": 47,
    "is_special": False
  },
  {
    "id": "recipe_213",
    "name": "丹方·标准方",
    "output": "item_desperation_pill",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        1
      ],
      [
        "item_core_4",
        2
      ],
      [
        "item_herb_sun_crystal_flower",
        1
      ]
    ],
    "base_rate": 48,
    "is_special": False
  },
  {
    "id": "recipe_214",
    "name": "丹方·省料方",
    "output": "item_desperation_pill",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 43,
    "is_special": False
  },
  {
    "id": "recipe_215",
    "name": "丹方·标准方",
    "output": "item_elexir_of_life",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_flame_seed",
        2
      ],
      [
        "item_essence_water",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_216",
    "name": "丹方·省料方",
    "output": "item_elexir_of_life",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_flame_seed",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_217",
    "name": "丹方·标准方",
    "output": "item_hp_super",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_essence_fire",
        2
      ],
      [
        "item_herb_coral_herb",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_218",
    "name": "丹方·省料方",
    "output": "item_hp_super",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_essence_fire",
        2
      ]
    ],
    "base_rate": 57,
    "is_special": False
  },
  {
    "id": "recipe_219",
    "name": "丹方·标准方",
    "output": "item_mp_super",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_essence_water",
        2
      ],
      [
        "item_essence_wind",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_220",
    "name": "丹方·省料方",
    "output": "item_mp_super",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_essence_water",
        2
      ]
    ],
    "base_rate": 57,
    "is_special": False
  },
  {
    "id": "recipe_221",
    "name": "丹方·标准方",
    "output": "item_haste_potion",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_essence_wind",
        2
      ],
      [
        "item_core_4",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_222",
    "name": "丹方·省料方",
    "output": "item_haste_potion",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_essence_wind",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_223",
    "name": "丹方·标准方",
    "output": "item_shield_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_core_4",
        2
      ],
      [
        "item_herb_dragon_blood_grass",
        1
      ]
    ],
    "base_rate": 52,
    "is_special": False
  },
  {
    "id": "recipe_224",
    "name": "丹方·省料方",
    "output": "item_shield_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        1
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 47,
    "is_special": False
  },
  {
    "id": "recipe_225",
    "name": "丹方·标准方",
    "output": "item_qi_regen_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        1
      ],
      [
        "item_flame_seed",
        2
      ],
      [
        "item_flame_seed",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_226",
    "name": "丹方·省料方",
    "output": "item_qi_regen_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_flame_seed",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_227",
    "name": "丹方·标准方",
    "output": "item_hp_regen_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_essence_fire",
        2
      ],
      [
        "item_herb_moon_dew_grass",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_228",
    "name": "丹方·省料方",
    "output": "item_hp_regen_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_essence_fire",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_229",
    "name": "丹方·标准方",
    "output": "item_lifesteal_pill",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_essence_water",
        2
      ],
      [
        "item_essence_fire",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_230",
    "name": "丹方·省料方",
    "output": "item_lifesteal_pill",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_essence_water",
        2
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_231",
    "name": "丹方·标准方",
    "output": "item_recover_pill_5",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        1
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_232",
    "name": "丹方·省料方",
    "output": "item_recover_pill_5",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        3
      ],
      [
        "item_dragon_tendon",
        2
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_233",
    "name": "丹方·标准方",
    "output": "item_dragon_blood_pill",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        3
      ],
      [
        "item_dragon_tendon",
        2
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 42,
    "is_special": False
  },
  {
    "id": "recipe_234",
    "name": "丹方·省料方",
    "output": "item_dragon_blood_pill",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        2
      ],
      [
        "item_core_5",
        2
      ]
    ],
    "base_rate": 37,
    "is_special": False
  },
  {
    "id": "recipe_235",
    "name": "丹方·标准方",
    "output": "item_qi_pill_5",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        2
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_energy_crystal",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_236",
    "name": "丹方·省料方",
    "output": "item_qi_pill_5",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        1
      ],
      [
        "item_dragon_tendon",
        2
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_237",
    "name": "丹方·标准方",
    "output": "item_dual_pill_4",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        1
      ],
      [
        "item_dragon_tendon",
        2
      ],
      [
        "item_herb_void_mushroom",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_238",
    "name": "丹方·省料方",
    "output": "item_dual_pill_4",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_core_5",
        2
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_239",
    "name": "丹方·第239号",
    "output": "item_break_pill_3",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 32,
    "is_special": True
  },
  {
    "id": "recipe_240",
    "name": "丹方·标准方",
    "output": "item_soul_pill_4",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        1
      ],
      [
        "item_dragon_scale_plus",
        1
      ],
      [
        "item_liquid_dragon_blood",
        1
      ]
    ],
    "base_rate": 42,
    "is_special": False
  },
  {
    "id": "recipe_241",
    "name": "丹方·省料方",
    "output": "item_soul_pill_4",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        3
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 37,
    "is_special": False
  },
  {
    "id": "recipe_242",
    "name": "丹方·标准方",
    "output": "item_poison_5",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        3
      ],
      [
        "item_beast_heart",
        1
      ],
      [
        "item_herb_ice_fire_lotus",
        1
      ]
    ],
    "base_rate": 48,
    "is_special": False
  },
  {
    "id": "recipe_243",
    "name": "丹方·省料方",
    "output": "item_poison_5",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        2
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 43,
    "is_special": False
  },
  {
    "id": "recipe_244",
    "name": "丹方·标准方",
    "output": "item_sacrifice_pill",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        2
      ],
      [
        "item_dragon_scale_plus",
        1
      ],
      [
        "item_dragon_tendon",
        1
      ]
    ],
    "base_rate": 38,
    "is_special": False
  },
  {
    "id": "recipe_245",
    "name": "丹方·省料方",
    "output": "item_sacrifice_pill",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        1
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 33,
    "is_special": False
  },
  {
    "id": "recipe_246",
    "name": "丹方·标准方",
    "output": "item_dragon_meat",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        1
      ],
      [
        "item_beast_heart",
        1
      ],
      [
        "item_core_5",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_247",
    "name": "丹方·省料方",
    "output": "item_dragon_meat",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        3
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_248",
    "name": "丹方·高成功率方",
    "output": "item_dragon_meat",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        2
      ],
      [
        "item_beast_heart",
        1
      ],
      [
        "item_herb_ice_fire_lotus",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_249",
    "name": "丹方·标准方",
    "output": "item_star_dew",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        1
      ],
      [
        "item_dragon_tendon",
        2
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 52,
    "is_special": False
  },
  {
    "id": "recipe_250",
    "name": "丹方·省料方",
    "output": "item_star_dew",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_core_5",
        2
      ]
    ],
    "base_rate": 47,
    "is_special": False
  },
  {
    "id": "recipe_251",
    "name": "丹方·标准方",
    "output": "item_troll_blood",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_energy_crystal",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_252",
    "name": "丹方·省料方",
    "output": "item_troll_blood",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        2
      ],
      [
        "item_dragon_tendon",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_253",
    "name": "丹方·标准方",
    "output": "item_berserker_potion",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        2
      ],
      [
        "item_dragon_tendon",
        2
      ],
      [
        "item_herb_void_mushroom",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_254",
    "name": "丹方·省料方",
    "output": "item_berserker_potion",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        1
      ],
      [
        "item_core_5",
        2
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_255",
    "name": "丹方·标准方",
    "output": "item_hp_elite",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        1
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 52,
    "is_special": False
  },
  {
    "id": "recipe_256",
    "name": "丹方·省料方",
    "output": "item_hp_elite",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        3
      ],
      [
        "item_dragon_tendon",
        2
      ]
    ],
    "base_rate": 47,
    "is_special": False
  },
  {
    "id": "recipe_257",
    "name": "丹方·标准方",
    "output": "item_mp_elite",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        3
      ],
      [
        "item_dragon_tendon",
        2
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 52,
    "is_special": False
  },
  {
    "id": "recipe_258",
    "name": "丹方·省料方",
    "output": "item_mp_elite",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        2
      ],
      [
        "item_core_5",
        2
      ]
    ],
    "base_rate": 47,
    "is_special": False
  },
  {
    "id": "recipe_259",
    "name": "丹方·标准方",
    "output": "item_shield_pill_3",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        2
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_energy_crystal",
        1
      ]
    ],
    "base_rate": 42,
    "is_special": False
  },
  {
    "id": "recipe_260",
    "name": "丹方·省料方",
    "output": "item_shield_pill_3",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        1
      ],
      [
        "item_dragon_tendon",
        2
      ]
    ],
    "base_rate": 37,
    "is_special": False
  },
  {
    "id": "recipe_261",
    "name": "丹方·标准方",
    "output": "item_all_buff_pill",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        1
      ],
      [
        "item_dragon_tendon",
        2
      ],
      [
        "item_herb_void_mushroom",
        1
      ]
    ],
    "base_rate": 42,
    "is_special": False
  },
  {
    "id": "recipe_262",
    "name": "丹方·省料方",
    "output": "item_all_buff_pill",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_core_5",
        2
      ]
    ],
    "base_rate": 37,
    "is_special": False
  },
  {
    "id": "recipe_263",
    "name": "丹方·标准方",
    "output": "item_recover_pill_6",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        3
      ],
      [
        "item_core_6",
        2
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_264",
    "name": "丹方·省料方",
    "output": "item_recover_pill_6",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        2
      ],
      [
        "item_qilin_horn",
        2
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_265",
    "name": "丹方·标准方",
    "output": "item_phoenix_pill",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        2
      ],
      [
        "item_qilin_horn",
        2
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_266",
    "name": "丹方·省料方",
    "output": "item_phoenix_pill",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        1
      ],
      [
        "item_core_6",
        2
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_267",
    "name": "丹方·标准方",
    "output": "item_qi_pill_6",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        1
      ],
      [
        "item_core_6",
        2
      ],
      [
        "item_demon_blood",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_268",
    "name": "丹方·省料方",
    "output": "item_qi_pill_6",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        3
      ],
      [
        "item_qilin_horn",
        2
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_269",
    "name": "丹方·标准方",
    "output": "item_dual_pill_5",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        3
      ],
      [
        "item_qilin_horn",
        2
      ],
      [
        "item_herb_nether_flower",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_270",
    "name": "丹方·省料方",
    "output": "item_dual_pill_5",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        2
      ],
      [
        "item_core_6",
        2
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_271",
    "name": "丹方·第271号",
    "output": "item_break_pill_4",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        2
      ],
      [
        "item_core_6",
        2
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 22,
    "is_special": True
  },
  {
    "id": "recipe_272",
    "name": "丹方·标准方",
    "output": "item_full_recovery",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        3
      ],
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 32,
    "is_special": False
  },
  {
    "id": "recipe_273",
    "name": "丹方·省料方",
    "output": "item_full_recovery",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        2
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 27,
    "is_special": False
  },
  {
    "id": "recipe_274",
    "name": "丹方·标准方",
    "output": "item_double_damage_pill",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        2
      ],
      [
        "item_beast_brain",
        1
      ],
      [
        "item_herb_bodhi_leaf",
        1
      ]
    ],
    "base_rate": 28,
    "is_special": False
  },
  {
    "id": "recipe_275",
    "name": "丹方·省料方",
    "output": "item_double_damage_pill",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        1
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 23,
    "is_special": False
  },
  {
    "id": "recipe_276",
    "name": "丹方·标准方",
    "output": "item_phoenix_ash",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        1
      ],
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_qilin_horn",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_277",
    "name": "丹方·省料方",
    "output": "item_phoenix_ash",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        3
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_278",
    "name": "丹方·标准方",
    "output": "item_recover_pill_7",
    "grade": 7,
    "materials": [
      [
        "item_herb_dragon_scale_moss",
        3
      ],
      [
        "item_core_7",
        1
      ],
      [
        "item_space_crystal",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_279",
    "name": "丹方·省料方",
    "output": "item_recover_pill_7",
    "grade": 7,
    "materials": [
      [
        "item_space_crystal",
        2
      ],
      [
        "item_core_7",
        1
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_280",
    "name": "丹方·标准方",
    "output": "item_primordial_pill",
    "grade": 7,
    "materials": [
      [
        "item_herb_star_grass",
        2
      ],
      [
        "item_ore_soul_crystal",
        1
      ],
      [
        "item_herb_dream_lotus",
        1
      ]
    ],
    "base_rate": 22,
    "is_special": False
  },
  {
    "id": "recipe_281",
    "name": "丹方·省料方",
    "output": "item_primordial_pill",
    "grade": 7,
    "materials": [
      [
        "item_soul_essence",
        1
      ],
      [
        "item_ore_soul_crystal",
        1
      ]
    ],
    "base_rate": 17,
    "is_special": False
  },
  {
    "id": "recipe_282",
    "name": "丹方·标准方",
    "output": "item_qi_pill_7",
    "grade": 7,
    "materials": [
      [
        "item_space_crystal",
        1
      ],
      [
        "item_soul_essence",
        1
      ],
      [
        "item_herb_star_grass",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_283",
    "name": "丹方·省料方",
    "output": "item_qi_pill_7",
    "grade": 7,
    "materials": [
      [
        "item_herb_dream_lotus",
        3
      ],
      [
        "item_soul_essence",
        1
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_284",
    "name": "丹方·标准方",
    "output": "item_dual_pill_6",
    "grade": 7,
    "materials": [
      [
        "item_soul_essence",
        3
      ],
      [
        "item_core_7",
        1
      ],
      [
        "item_soul_essence",
        1
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_285",
    "name": "丹方·省料方",
    "output": "item_dual_pill_6",
    "grade": 7,
    "materials": [
      [
        "item_herb_dragon_scale_moss",
        2
      ],
      [
        "item_core_7",
        1
      ]
    ],
    "base_rate": 15,
    "is_special": False
  },
  {
    "id": "recipe_286",
    "name": "丹方·第286号",
    "output": "item_break_pill_5",
    "grade": 7,
    "materials": [
      [
        "item_herb_dream_lotus",
        2
      ],
      [
        "item_ore_soul_crystal",
        1
      ],
      [
        "item_space_crystal",
        1
      ]
    ],
    "base_rate": 14,
    "is_special": True
  },
  {
    "id": "recipe_287",
    "name": "丹方·标准方",
    "output": "item_ancient_pill_fragment",
    "grade": 7,
    "materials": [
      [
        "item_space_crystal",
        3
      ],
      [
        "item_core_7",
        2
      ],
      [
        "item_ore_soul_crystal",
        1
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_288",
    "name": "丹方·省料方",
    "output": "item_ancient_pill_fragment",
    "grade": 7,
    "materials": [
      [
        "item_herb_dream_lotus",
        2
      ],
      [
        "item_core_7",
        2
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_289",
    "name": "丹方·标准方",
    "output": "item_recover_pill_8",
    "grade": 8,
    "materials": [
      [
        "item_ore_void_stone",
        2
      ],
      [
        "item_ore_shadow_stone",
        2
      ],
      [
        "item_core_8",
        1
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_290",
    "name": "丹方·省料方",
    "output": "item_recover_pill_8",
    "grade": 8,
    "materials": [
      [
        "item_herb_ancient_tree_sap",
        1
      ],
      [
        "item_ore_shadow_stone",
        2
      ]
    ],
    "base_rate": 15,
    "is_special": False
  },
  {
    "id": "recipe_291",
    "name": "丹方·标准方",
    "output": "item_soul_restore_pill",
    "grade": 8,
    "materials": [
      [
        "item_herb_ancient_tree_sap",
        1
      ],
      [
        "item_time_sand",
        2
      ],
      [
        "item_time_sand",
        1
      ]
    ],
    "base_rate": 14,
    "is_special": False
  },
  {
    "id": "recipe_292",
    "name": "丹方·省料方",
    "output": "item_soul_restore_pill",
    "grade": 8,
    "materials": [
      [
        "item_ore_void_stone",
        3
      ],
      [
        "item_time_sand",
        2
      ]
    ],
    "base_rate": 9,
    "is_special": False
  },
  {
    "id": "recipe_293",
    "name": "丹方·标准方",
    "output": "item_qi_pill_8",
    "grade": 8,
    "materials": [
      [
        "item_ore_void_stone",
        3
      ],
      [
        "item_core_8",
        2
      ],
      [
        "item_ore_shadow_stone",
        1
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_294",
    "name": "丹方·省料方",
    "output": "item_qi_pill_8",
    "grade": 8,
    "materials": [
      [
        "item_herb_ancient_tree_sap",
        2
      ],
      [
        "item_core_8",
        2
      ]
    ],
    "base_rate": 15,
    "is_special": False
  },
  {
    "id": "recipe_295",
    "name": "丹方·标准方",
    "output": "item_dual_pill_7",
    "grade": 8,
    "materials": [
      [
        "item_herb_ancient_tree_sap",
        2
      ],
      [
        "item_ore_shadow_stone",
        2
      ],
      [
        "item_herb_phoenix_flower",
        1
      ]
    ],
    "base_rate": 12,
    "is_special": False
  },
  {
    "id": "recipe_296",
    "name": "丹方·省料方",
    "output": "item_dual_pill_7",
    "grade": 8,
    "materials": [
      [
        "item_ore_void_stone",
        1
      ],
      [
        "item_ore_shadow_stone",
        2
      ]
    ],
    "base_rate": 7,
    "is_special": False
  },
  {
    "id": "recipe_297",
    "name": "丹方·第297号",
    "output": "item_break_pill_6",
    "grade": 8,
    "materials": [
      [
        "item_ore_void_stone",
        1
      ],
      [
        "item_time_sand",
        2
      ],
      [
        "item_herb_ancient_tree_sap",
        1
      ]
    ],
    "base_rate": 10,
    "is_special": True
  },
  {
    "id": "recipe_298",
    "name": "丹方·标准方",
    "output": "item_ancient_essence",
    "grade": 8,
    "materials": [
      [
        "item_time_sand",
        2
      ],
      [
        "item_ore_shadow_stone",
        1
      ],
      [
        "item_time_sand",
        1
      ]
    ],
    "base_rate": 15,
    "is_special": False
  },
  {
    "id": "recipe_299",
    "name": "丹方·省料方",
    "output": "item_ancient_essence",
    "grade": 8,
    "materials": [
      [
        "item_herb_phoenix_flower",
        1
      ],
      [
        "item_ore_shadow_stone",
        1
      ]
    ],
    "base_rate": 10,
    "is_special": False
  },
  {
    "id": "recipe_300",
    "name": "丹方·标准方",
    "output": "item_recover_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_herb_emperor_root",
        1
      ],
      [
        "item_ore_light_crystal",
        1
      ],
      [
        "item_dragon_reverse_scale",
        1
      ]
    ],
    "base_rate": 14,
    "is_special": False
  },
  {
    "id": "recipe_301",
    "name": "丹方·省料方",
    "output": "item_recover_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_ore_emperor_jade",
        3
      ],
      [
        "item_ore_light_crystal",
        1
      ]
    ],
    "base_rate": 9,
    "is_special": False
  },
  {
    "id": "recipe_302",
    "name": "丹方·标准方",
    "output": "item_qi_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_ore_emperor_jade",
        3
      ],
      [
        "item_core_9",
        1
      ],
      [
        "item_herb_emperor_root",
        1
      ]
    ],
    "base_rate": 14,
    "is_special": False
  },
  {
    "id": "recipe_303",
    "name": "丹方·省料方",
    "output": "item_qi_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_herb_emperor_root",
        2
      ],
      [
        "item_core_9",
        1
      ]
    ],
    "base_rate": 9,
    "is_special": False
  },
  {
    "id": "recipe_304",
    "name": "丹方·标准方",
    "output": "item_dual_pill_8",
    "grade": 9,
    "materials": [
      [
        "item_herb_emperor_root",
        2
      ],
      [
        "item_dragon_reverse_scale",
        1
      ],
      [
        "item_herb_eternal_fruit",
        1
      ]
    ],
    "base_rate": 10,
    "is_special": False
  },
  {
    "id": "recipe_305",
    "name": "丹方·省料方",
    "output": "item_dual_pill_8",
    "grade": 9,
    "materials": [
      [
        "item_ore_emperor_jade",
        1
      ],
      [
        "item_dragon_reverse_scale",
        1
      ]
    ],
    "base_rate": 5,
    "is_special": False
  },
  {
    "id": "recipe_306",
    "name": "丹方·第306号",
    "output": "item_god_pill",
    "grade": 10,
    "materials": [
      [
        "item_essence_creation",
        1
      ],
      [
        "item_ore_divine_gold",
        1
      ],
      [
        "item_essence_creation",
        1
      ]
    ],
    "base_rate": 8,
    "is_special": True
  },
  {
    "id": "recipe_307",
    "name": "丹方·第307号",
    "output": "item_divine_dew",
    "grade": 10,
    "materials": [
      [
        "item_ore_divine_gold",
        2
      ],
      [
        "item_world_fragment",
        2
      ],
      [
        "item_world_fragment",
        1
      ]
    ],
    "base_rate": 5,
    "is_special": True
  },
  {
    "id": "recipe_308",
    "name": "丹方·标准方",
    "output": "item_meat_skewer",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_309",
    "name": "丹方·省料方",
    "output": "item_meat_skewer",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_310",
    "name": "丹方·标准方",
    "output": "item_trail_ration",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_311",
    "name": "丹方·省料方",
    "output": "item_trail_ration",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_beast_skin",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_312",
    "name": "丹方·标准方",
    "output": "item_clean_water",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_313",
    "name": "丹方·省料方",
    "output": "item_clean_water",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 93,
    "is_special": False
  },
  {
    "id": "recipe_314",
    "name": "丹方·标准方",
    "output": "item_spirit_rice",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        3
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_315",
    "name": "丹方·省料方",
    "output": "item_spirit_rice",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_316",
    "name": "丹方·标准方",
    "output": "item_spirit_wine",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_317",
    "name": "丹方·省料方",
    "output": "item_spirit_wine",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 83,
    "is_special": False
  },
  {
    "id": "recipe_318",
    "name": "丹方·标准方",
    "output": "item_beast_meat",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_319",
    "name": "丹方·省料方",
    "output": "item_beast_meat",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_320",
    "name": "丹方·标准方",
    "output": "item_dragon_meat",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        3
      ],
      [
        "item_dragon_scale_plus",
        1
      ],
      [
        "item_liquid_dragon_blood",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_321",
    "name": "丹方·省料方",
    "output": "item_dragon_meat",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        2
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_322",
    "name": "丹方·高成功率方",
    "output": "item_dragon_meat",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        1
      ],
      [
        "item_dragon_scale_plus",
        1
      ],
      [
        "item_dragon_tendon",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_323",
    "name": "丹方·标准方",
    "output": "item_moon_well_water",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        3
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_herb_fire_grass",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_324",
    "name": "丹方·省料方",
    "output": "item_moon_well_water",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        2
      ],
      [
        "item_beast_eye",
        2
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_325",
    "name": "丹方·高成功率方",
    "output": "item_moon_well_water",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        1
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_326",
    "name": "丹方·标准方",
    "output": "item_star_dew",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        3
      ],
      [
        "item_beast_heart",
        1
      ],
      [
        "item_core_5",
        1
      ]
    ],
    "base_rate": 52,
    "is_special": False
  },
  {
    "id": "recipe_327",
    "name": "丹方·省料方",
    "output": "item_star_dew",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        2
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 47,
    "is_special": False
  },
  {
    "id": "recipe_328",
    "name": "丹方·标准方",
    "output": "item_phoenix_ash",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        2
      ],
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_329",
    "name": "丹方·省料方",
    "output": "item_phoenix_ash",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_330",
    "name": "丹方·标准方",
    "output": "item_ancient_pill_fragment",
    "grade": 7,
    "materials": [
      [
        "item_herb_star_grass",
        1
      ],
      [
        "item_soul_essence",
        1
      ],
      [
        "item_herb_star_grass",
        1
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_331",
    "name": "丹方·省料方",
    "output": "item_ancient_pill_fragment",
    "grade": 7,
    "materials": [
      [
        "item_soul_essence",
        3
      ],
      [
        "item_soul_essence",
        1
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_332",
    "name": "丹方·标准方",
    "output": "item_ancient_essence",
    "grade": 8,
    "materials": [
      [
        "item_herb_phoenix_flower",
        3
      ],
      [
        "item_core_8",
        1
      ],
      [
        "item_herb_ancient_tree_sap",
        1
      ]
    ],
    "base_rate": 15,
    "is_special": False
  },
  {
    "id": "recipe_333",
    "name": "丹方·省料方",
    "output": "item_ancient_essence",
    "grade": 8,
    "materials": [
      [
        "item_time_sand",
        2
      ],
      [
        "item_core_8",
        1
      ]
    ],
    "base_rate": 10,
    "is_special": False
  },
  {
    "id": "recipe_334",
    "name": "丹方·标准方",
    "output": "item_troll_blood",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        2
      ],
      [
        "item_beast_heart",
        1
      ],
      [
        "item_core_5",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_335",
    "name": "丹方·省料方",
    "output": "item_troll_blood",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        1
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_336",
    "name": "丹方·标准方",
    "output": "item_berserker_potion",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        1
      ],
      [
        "item_dragon_scale_plus",
        1
      ],
      [
        "item_liquid_dragon_blood",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_337",
    "name": "丹方·省料方",
    "output": "item_berserker_potion",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        3
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_338",
    "name": "丹方·标准方",
    "output": "item_double_damage_pill",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        3
      ],
      [
        "item_beast_brain",
        1
      ],
      [
        "item_herb_bodhi_leaf",
        1
      ]
    ],
    "base_rate": 28,
    "is_special": False
  },
  {
    "id": "recipe_339",
    "name": "丹方·省料方",
    "output": "item_double_damage_pill",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        2
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 23,
    "is_special": False
  },
  {
    "id": "recipe_340",
    "name": "丹方·标准方",
    "output": "item_damage_shield",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        2
      ],
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_qilin_horn",
        1
      ]
    ],
    "base_rate": 38,
    "is_special": False
  },
  {
    "id": "recipe_341",
    "name": "丹方·省料方",
    "output": "item_damage_shield",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 33,
    "is_special": False
  },
  {
    "id": "recipe_342",
    "name": "丹方·标准方",
    "output": "item_revive_feather",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_beast_brain",
        1
      ],
      [
        "item_core_6",
        1
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_343",
    "name": "丹方·省料方",
    "output": "item_revive_feather",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        3
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_344",
    "name": "丹方·标准方",
    "output": "item_repair_hammer",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_345",
    "name": "丹方·省料方",
    "output": "item_repair_hammer",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_346",
    "name": "丹方·标准方",
    "output": "item_escape_rope",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_347",
    "name": "丹方·省料方",
    "output": "item_escape_rope",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_beast_skin",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_348",
    "name": "丹方·标准方",
    "output": "item_storage_bag",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_beast_bone",
        1
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_349",
    "name": "丹方·省料方",
    "output": "item_storage_bag",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_350",
    "name": "丹方·高成功率方",
    "output": "item_storage_bag",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        2
      ],
      [
        "item_beast_bone",
        1
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_351",
    "name": "丹方·标准方",
    "output": "item_luck_charm",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        1
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_352",
    "name": "丹方·省料方",
    "output": "item_luck_charm",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        3
      ],
      [
        "item_beast_eye",
        2
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_353",
    "name": "丹方·标准方",
    "output": "item_exp_boost_scroll",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_core_4",
        2
      ],
      [
        "item_herb_moon_dew_grass",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_354",
    "name": "丹方·省料方",
    "output": "item_exp_boost_scroll",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_355",
    "name": "丹方·标准方",
    "output": "item_blessing_scroll",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        2
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_herb_fire_grass",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_356",
    "name": "丹方·省料方",
    "output": "item_blessing_scroll",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        1
      ],
      [
        "item_beast_eye",
        2
      ]
    ],
    "base_rate": 57,
    "is_special": False
  },
  {
    "id": "recipe_357",
    "name": "丹方·标准方",
    "output": "item_damage_shield",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        1
      ],
      [
        "item_beast_eye",
        2
      ],
      [
        "item_herb_thunder_vine",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_358",
    "name": "丹方·省料方",
    "output": "item_damage_shield",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        3
      ],
      [
        "item_core_3",
        2
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_359",
    "name": "丹方·标准方",
    "output": "item_encounter_lure",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        3
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_360",
    "name": "丹方·省料方",
    "output": "item_encounter_lure",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_361",
    "name": "丹方·高成功率方",
    "output": "item_encounter_lure",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_362",
    "name": "丹方·标准方",
    "output": "item_encounter_repel",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_core_2",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_363",
    "name": "丹方·省料方",
    "output": "item_encounter_repel",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_364",
    "name": "丹方·高成功率方",
    "output": "item_encounter_repel",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        1
      ],
      [
        "item_core_2",
        1
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_365",
    "name": "丹方·标准方",
    "output": "item_identify_scroll",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_366",
    "name": "丹方·省料方",
    "output": "item_identify_scroll",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_367",
    "name": "丹方·高成功率方",
    "output": "item_identify_scroll",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_368",
    "name": "丹方·标准方",
    "output": "item_cultivation_stone",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ],
      [
        "item_herb_blood_rose",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_369",
    "name": "丹方·省料方",
    "output": "item_cultivation_stone",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_370",
    "name": "丹方·标准方",
    "output": "item_cultivation_jade",
    "grade": 4,
    "materials": [
      [
        "item_herb_sun_crystal_flower",
        2
      ],
      [
        "item_flame_seed",
        1
      ],
      [
        "item_herb_coral_herb",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_371",
    "name": "丹方·省料方",
    "output": "item_cultivation_jade",
    "grade": 4,
    "materials": [
      [
        "item_herb_dragon_blood_grass",
        1
      ],
      [
        "item_flame_seed",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_372",
    "name": "丹方·标准方",
    "output": "item_soul_crystal_ball",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        1
      ],
      [
        "item_dragon_scale_plus",
        1
      ],
      [
        "item_dragon_tendon",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_373",
    "name": "丹方·省料方",
    "output": "item_soul_crystal_ball",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        3
      ],
      [
        "item_beast_heart",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_374",
    "name": "丹方·标准方",
    "output": "item_meditation_mat",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        3
      ],
      [
        "item_beast_brain",
        1
      ],
      [
        "item_core_6",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_375",
    "name": "丹方·省料方",
    "output": "item_meditation_mat",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        2
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_376",
    "name": "丹方·标准方",
    "output": "item_time_chamber_key",
    "grade": 7,
    "materials": [
      [
        "item_herb_dream_lotus",
        2
      ],
      [
        "item_ore_soul_crystal",
        1
      ],
      [
        "item_herb_dream_lotus",
        1
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_377",
    "name": "丹方·省料方",
    "output": "item_time_chamber_key",
    "grade": 7,
    "materials": [
      [
        "item_herb_star_grass",
        1
      ],
      [
        "item_ore_soul_crystal",
        1
      ]
    ],
    "base_rate": 15,
    "is_special": False
  },
  {
    "id": "recipe_378",
    "name": "丹方·标准方",
    "output": "item_pill_furnace",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        1
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_379",
    "name": "丹方·省料方",
    "output": "item_pill_furnace",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_380",
    "name": "丹方·标准方",
    "output": "item_flame_controlling_ring",
    "grade": 4,
    "materials": [
      [
        "item_herb_dragon_blood_grass",
        3
      ],
      [
        "item_flame_seed",
        1
      ],
      [
        "item_herb_moon_dew_grass",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_381",
    "name": "丹方·省料方",
    "output": "item_flame_controlling_ring",
    "grade": 4,
    "materials": [
      [
        "item_herb_sun_crystal_flower",
        2
      ],
      [
        "item_flame_seed",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_382",
    "name": "丹方·标准方",
    "output": "item_return_scroll_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_beast_skin",
        1
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_383",
    "name": "丹方·省料方",
    "output": "item_return_scroll_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_beast_skin",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_384",
    "name": "丹方·高成功率方",
    "output": "item_return_scroll_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ],
      [
        "item_beast_skin",
        1
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_385",
    "name": "丹方·标准方",
    "output": "item_return_scroll_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_flame_seed",
        2
      ],
      [
        "item_herb_dragon_blood_grass",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_386",
    "name": "丹方·省料方",
    "output": "item_return_scroll_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_flame_seed",
        2
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_387",
    "name": "丹方·标准方",
    "output": "item_return_scroll_3",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        1
      ],
      [
        "item_core_6",
        2
      ],
      [
        "item_demon_blood",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_388",
    "name": "丹方·省料方",
    "output": "item_return_scroll_3",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        3
      ],
      [
        "item_qilin_horn",
        2
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_389",
    "name": "丹方·标准方",
    "output": "item_skill_reset_scroll",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_essence_water",
        2
      ],
      [
        "item_herb_moon_dew_grass",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_390",
    "name": "丹方·省料方",
    "output": "item_skill_reset_scroll",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_essence_water",
        2
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_391",
    "name": "丹方·标准方",
    "output": "item_stat_reset_pill",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        2
      ],
      [
        "item_core_6",
        2
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_392",
    "name": "丹方·省料方",
    "output": "item_stat_reset_pill",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        1
      ],
      [
        "item_qilin_horn",
        2
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_393",
    "name": "丹方·标准方",
    "output": "item_curse_removal",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_394",
    "name": "丹方·省料方",
    "output": "item_curse_removal",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_beast_claw",
        2
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_395",
    "name": "丹方·高成功率方",
    "output": "item_curse_removal",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        2
      ],
      [
        "item_beast_claw",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_396",
    "name": "丹方·标准方",
    "output": "item_weather_stone",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        1
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_397",
    "name": "丹方·省料方",
    "output": "item_weather_stone",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_beast_claw",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_398",
    "name": "丹方·高成功率方",
    "output": "item_weather_stone",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        2
      ],
      [
        "item_beast_claw",
        1
      ],
      [
        "item_herb_golden_mushroom",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_399",
    "name": "丹方·标准方",
    "output": "item_pet_food",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_400",
    "name": "丹方·省料方",
    "output": "item_pet_food",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        3
      ],
      [
        "item_beast_bone",
        2
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_401",
    "name": "丹方·标准方",
    "output": "item_pet_taming_reins",
    "grade": 2,
    "materials": [
      [
        "item_herb_golden_mushroom",
        3
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_402",
    "name": "丹方·省料方",
    "output": "item_pet_taming_reins",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_403",
    "name": "丹方·高成功率方",
    "output": "item_pet_taming_reins",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        1
      ],
      [
        "item_core_2",
        2
      ],
      [
        "item_herb_jade_bamboo",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_404",
    "name": "丹方·标准方",
    "output": "item_enchant_stone_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_core_1",
        1
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_405",
    "name": "丹方·省料方",
    "output": "item_enchant_stone_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_406",
    "name": "丹方·高成功率方",
    "output": "item_enchant_stone_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        1
      ],
      [
        "item_core_1",
        1
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_407",
    "name": "丹方·标准方",
    "output": "item_enchant_stone_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_thunder_vine",
        3
      ],
      [
        "item_core_3",
        2
      ],
      [
        "item_beast_feather",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_408",
    "name": "丹方·省料方",
    "output": "item_enchant_stone_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_fire_grass",
        2
      ],
      [
        "item_beast_eye",
        2
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_409",
    "name": "丹方·标准方",
    "output": "item_enchant_stone_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_essence_water",
        2
      ],
      [
        "item_essence_fire",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_410",
    "name": "丹方·省料方",
    "output": "item_enchant_stone_3",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_essence_water",
        2
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_411",
    "name": "丹方·标准方",
    "output": "item_enchant_stone_4",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        1
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_energy_crystal",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_412",
    "name": "丹方·省料方",
    "output": "item_enchant_stone_4",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        3
      ],
      [
        "item_dragon_tendon",
        2
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_413",
    "name": "丹方·标准方",
    "output": "item_enchant_stone_5",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        3
      ],
      [
        "item_qilin_horn",
        2
      ],
      [
        "item_herb_nether_flower",
        1
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_414",
    "name": "丹方·省料方",
    "output": "item_enchant_stone_5",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        2
      ],
      [
        "item_core_6",
        2
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_415",
    "name": "丹方·标准方",
    "output": "item_box_mystery",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        2
      ],
      [
        "item_beast_skin",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_416",
    "name": "丹方·省料方",
    "output": "item_box_mystery",
    "grade": 1,
    "materials": [
      [
        "item_clean_water",
        1
      ],
      [
        "item_beast_skin",
        2
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_417",
    "name": "丹方·高成功率方",
    "output": "item_box_mystery",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        3
      ],
      [
        "item_beast_skin",
        2
      ],
      [
        "item_core_1",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_418",
    "name": "丹方·标准方",
    "output": "item_box_silver",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        2
      ],
      [
        "item_beast_fang",
        1
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_419",
    "name": "丹方·省料方",
    "output": "item_box_silver",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        1
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_420",
    "name": "丹方·标准方",
    "output": "item_box_gold",
    "grade": 4,
    "materials": [
      [
        "item_herb_dragon_blood_grass",
        1
      ],
      [
        "item_flame_seed",
        1
      ],
      [
        "item_herb_sun_crystal_flower",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_421",
    "name": "丹方·省料方",
    "output": "item_box_gold",
    "grade": 4,
    "materials": [
      [
        "item_herb_sun_crystal_flower",
        3
      ],
      [
        "item_flame_seed",
        1
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_422",
    "name": "丹方·标准方",
    "output": "item_box_diamond",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        3
      ],
      [
        "item_beast_heart",
        1
      ],
      [
        "item_core_5",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_423",
    "name": "丹方·省料方",
    "output": "item_box_diamond",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        2
      ],
      [
        "item_dragon_scale_plus",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_424",
    "name": "丹方·标准方",
    "output": "item_box_legendary",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        2
      ],
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_425",
    "name": "丹方·省料方",
    "output": "item_box_legendary",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_beast_brain",
        1
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_426",
    "name": "丹方·标准方",
    "output": "item_gift_flower",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_427",
    "name": "丹方·省料方",
    "output": "item_gift_flower",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_beast_bone",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_428",
    "name": "丹方·标准方",
    "output": "item_gift_spice",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        3
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_429",
    "name": "丹方·省料方",
    "output": "item_gift_spice",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        2
      ],
      [
        "item_core_2",
        1
      ]
    ],
    "base_rate": 80,
    "is_special": False
  },
  {
    "id": "recipe_430",
    "name": "丹方·标准方",
    "output": "item_gift_jewelry",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_core_3",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_431",
    "name": "丹方·省料方",
    "output": "item_gift_jewelry",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_432",
    "name": "丹方·高成功率方",
    "output": "item_gift_jewelry",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_433",
    "name": "丹方·标准方",
    "output": "item_gift_perfume",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_core_4",
        2
      ],
      [
        "item_herb_coral_herb",
        1
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_434",
    "name": "丹方·省料方",
    "output": "item_gift_perfume",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        1
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 60,
    "is_special": False
  },
  {
    "id": "recipe_435",
    "name": "丹方·标准方",
    "output": "item_gift_treasure",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        1
      ],
      [
        "item_core_5",
        2
      ],
      [
        "item_energy_crystal",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_436",
    "name": "丹方·省料方",
    "output": "item_gift_treasure",
    "grade": 5,
    "materials": [
      [
        "item_energy_crystal",
        3
      ],
      [
        "item_dragon_tendon",
        2
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_437",
    "name": "丹方·标准方",
    "output": "item_gift_dragon_pearl",
    "grade": 6,
    "materials": [
      [
        "item_demon_blood",
        3
      ],
      [
        "item_qilin_horn",
        2
      ],
      [
        "item_herb_nether_flower",
        1
      ]
    ],
    "base_rate": 35,
    "is_special": False
  },
  {
    "id": "recipe_438",
    "name": "丹方·省料方",
    "output": "item_gift_dragon_pearl",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        2
      ],
      [
        "item_core_6",
        2
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_439",
    "name": "丹方·标准方",
    "output": "item_gift_painting",
    "grade": 2,
    "materials": [
      [
        "item_herb_wind_flower",
        2
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 82,
    "is_special": False
  },
  {
    "id": "recipe_440",
    "name": "丹方·省料方",
    "output": "item_gift_painting",
    "grade": 2,
    "materials": [
      [
        "item_herb_jade_bamboo",
        1
      ],
      [
        "item_beast_fang",
        2
      ]
    ],
    "base_rate": 77,
    "is_special": False
  },
  {
    "id": "recipe_441",
    "name": "丹方·高成功率方",
    "output": "item_gift_painting",
    "grade": 2,
    "materials": [
      [
        "item_herb_snow_lotus",
        3
      ],
      [
        "item_beast_fang",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_442",
    "name": "丹方·标准方",
    "output": "item_gift_wine",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_herb_soul_flower",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_443",
    "name": "丹方·省料方",
    "output": "item_gift_wine",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        1
      ],
      [
        "item_beast_horn",
        1
      ]
    ],
    "base_rate": 67,
    "is_special": False
  },
  {
    "id": "recipe_444",
    "name": "丹方·高成功率方",
    "output": "item_gift_wine",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_feather",
        1
      ],
      [
        "item_core_3",
        1
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_a01",
    "name": "丹方·改良方",
    "output": "item_recover_pill_1",
    "grade": 1,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_clean_water",
        2
      ]
    ],
    "base_rate": 92,
    "is_special": False
  },
  {
    "id": "recipe_a02",
    "name": "丹方·古法",
    "output": "item_recover_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_heal_grass",
        4
      ],
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_beast_bone",
        2
      ]
    ],
    "base_rate": 78,
    "is_special": False
  },
  {
    "id": "recipe_a03",
    "name": "丹方·秘传",
    "output": "item_recover_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        2
      ],
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_a04",
    "name": "丹方·捷径",
    "output": "item_qi_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_herb_wind_flower",
        1
      ]
    ],
    "base_rate": 85,
    "is_special": False
  },
  {
    "id": "recipe_a05",
    "name": "丹方·双倍",
    "output": "item_blood_pill",
    "grade": 1,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_herb_ginseng",
        3
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_a06",
    "name": "丹方·精炼",
    "output": "item_hp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        2
      ],
      [
        "item_herb_heal_grass",
        2
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_a07",
    "name": "丹方·浓缩",
    "output": "item_mp_medium",
    "grade": 2,
    "materials": [
      [
        "item_herb_spirit_grass",
        3
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 88,
    "is_special": False
  },
  {
    "id": "recipe_a08",
    "name": "丹方·秘方",
    "output": "item_str_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_ginseng",
        4
      ],
      [
        "item_beast_fang",
        2
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_a09",
    "name": "丹方·古法",
    "output": "item_antidote_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_lingzhi",
        3
      ],
      [
        "item_herb_snow_lotus",
        1
      ]
    ],
    "base_rate": 90,
    "is_special": False
  },
  {
    "id": "recipe_a10",
    "name": "丹方·改良",
    "output": "item_break_pill_1",
    "grade": 3,
    "materials": [
      [
        "item_herb_soul_flower",
        3
      ],
      [
        "item_core_2",
        3
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_a11",
    "name": "丹方·捷径",
    "output": "item_shield_pill",
    "grade": 2,
    "materials": [
      [
        "item_beast_skin",
        3
      ],
      [
        "item_herb_spirit_grass",
        1
      ]
    ],
    "base_rate": 75,
    "is_special": False
  },
  {
    "id": "recipe_a12",
    "name": "丹方·精制",
    "output": "item_dual_pill_1",
    "grade": 2,
    "materials": [
      [
        "item_herb_heal_grass",
        3
      ],
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_a13",
    "name": "丹方·古方",
    "output": "item_spd_pill_2",
    "grade": 2,
    "materials": [
      [
        "item_beast_feather",
        3
      ],
      [
        "item_herb_wind_flower",
        2
      ]
    ],
    "base_rate": 70,
    "is_special": False
  },
  {
    "id": "recipe_a14",
    "name": "丹方·秘传",
    "output": "item_poison_2",
    "grade": 2,
    "materials": [
      [
        "item_herb_blood_rose",
        3
      ],
      [
        "item_beast_fang",
        1
      ]
    ],
    "base_rate": 82,
    "is_special": False
  },
  {
    "id": "recipe_a15",
    "name": "丹方·改良",
    "output": "item_recover_pill_4",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        3
      ],
      [
        "item_herb_dragon_blood_grass",
        1
      ],
      [
        "item_core_3",
        2
      ]
    ],
    "base_rate": 58,
    "is_special": False
  },
  {
    "id": "recipe_a16",
    "name": "丹方·古法",
    "output": "item_break_pill_2",
    "grade": 4,
    "materials": [
      [
        "item_herb_soul_flower",
        4
      ],
      [
        "item_core_3",
        4
      ]
    ],
    "base_rate": 44,
    "is_special": False
  },
  {
    "id": "recipe_a17",
    "name": "丹方·秘传",
    "output": "item_recover_pill_5",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        3
      ],
      [
        "item_liquid_dragon_blood",
        1
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 48,
    "is_special": False
  },
  {
    "id": "recipe_a18",
    "name": "丹方·改良",
    "output": "item_break_pill_4",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        3
      ],
      [
        "item_phoenix_feather",
        1
      ],
      [
        "item_core_5",
        3
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_a19",
    "name": "丹方·古方",
    "output": "item_primordial_pill",
    "grade": 7,
    "materials": [
      [
        "item_herb_dragon_scale_moss",
        3
      ],
      [
        "item_soul_essence",
        2
      ],
      [
        "item_core_6",
        3
      ]
    ],
    "base_rate": 20,
    "is_special": False
  },
  {
    "id": "recipe_a20",
    "name": "丹方·秘方",
    "output": "item_recover_pill_8",
    "grade": 8,
    "materials": [
      [
        "item_herb_ancient_tree_sap",
        3
      ],
      [
        "item_time_sand",
        1
      ],
      [
        "item_core_7",
        3
      ]
    ],
    "base_rate": 16,
    "is_special": False
  },
  {
    "id": "recipe_a21",
    "name": "丹方·捷径",
    "output": "item_qi_pill_7",
    "grade": 7,
    "materials": [
      [
        "item_herb_star_grass",
        4
      ],
      [
        "item_space_crystal",
        1
      ]
    ],
    "base_rate": 28,
    "is_special": False
  },
  {
    "id": "recipe_a22",
    "name": "丹方·古法",
    "output": "item_dual_pill_6",
    "grade": 7,
    "materials": [
      [
        "item_herb_dream_lotus",
        2
      ],
      [
        "item_soul_essence",
        2
      ],
      [
        "item_ore_soul_crystal",
        1
      ]
    ],
    "base_rate": 18,
    "is_special": False
  },
  {
    "id": "recipe_a23",
    "name": "丹方·秘传",
    "output": "item_god_pill",
    "grade": 10,
    "materials": [
      [
        "item_herb_god_grass",
        4
      ],
      [
        "item_ore_divine_gold",
        3
      ],
      [
        "item_world_fragment",
        1
      ]
    ],
    "base_rate": 4,
    "is_special": False
  },
  {
    "id": "recipe_a24",
    "name": "丹方·改良",
    "output": "item_recover_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_herb_emperor_root",
        4
      ],
      [
        "item_ore_emperor_jade",
        2
      ],
      [
        "item_core_8",
        3
      ]
    ],
    "base_rate": 12,
    "is_special": False
  },
  {
    "id": "recipe_a25",
    "name": "丹方·古方",
    "output": "item_qi_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_herb_eternal_fruit",
        2
      ],
      [
        "item_ore_light_crystal",
        2
      ]
    ],
    "base_rate": 16,
    "is_special": False
  },
  {
    "id": "recipe_a26",
    "name": "丹方·秘方",
    "output": "item_full_recovery",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        2
      ],
      [
        "item_herb_nether_flower",
        1
      ],
      [
        "item_phoenix_feather",
        1
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_a27",
    "name": "丹方·捷径",
    "output": "item_elexir_of_life",
    "grade": 4,
    "materials": [
      [
        "item_herb_coral_herb",
        3
      ],
      [
        "item_liquid_spirit_water",
        2
      ]
    ],
    "base_rate": 58,
    "is_special": False
  },
  {
    "id": "recipe_a28",
    "name": "丹方·古法",
    "output": "item_hp_elite",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_dragon_tendon",
        1
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_a29",
    "name": "丹方·秘方",
    "output": "item_recover_pill_6",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        2
      ],
      [
        "item_demon_blood",
        1
      ],
      [
        "item_core_5",
        2
      ]
    ],
    "base_rate": 38,
    "is_special": False
  },
  {
    "id": "recipe_a30",
    "name": "丹方·改良",
    "output": "item_qi_pill_5",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_energy_crystal",
        2
      ]
    ],
    "base_rate": 48,
    "is_special": False
  },
  {
    "id": "recipe_b01",
    "name": "丹方·极品",
    "output": "item_hp_small",
    "grade": 1,
    "materials": [
      [
        "item_herb_ginseng",
        2
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_b02",
    "name": "丹方·极品",
    "output": "item_mp_small",
    "grade": 1,
    "materials": [
      [
        "item_herb_spirit_grass",
        2
      ],
      [
        "item_herb_lingzhi",
        1
      ]
    ],
    "base_rate": 95,
    "is_special": False
  },
  {
    "id": "recipe_b03",
    "name": "丹方·古法",
    "output": "item_qi_pill_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_spirit_grass",
        5
      ],
      [
        "item_core_2",
        2
      ]
    ],
    "base_rate": 68,
    "is_special": False
  },
  {
    "id": "recipe_b04",
    "name": "丹方·秘传",
    "output": "item_marrow_pill",
    "grade": 3,
    "materials": [
      [
        "item_herb_dragon_blood_grass",
        2
      ],
      [
        "item_core_2",
        3
      ]
    ],
    "base_rate": 62,
    "is_special": False
  },
  {
    "id": "recipe_b05",
    "name": "丹方·改良",
    "output": "item_antidote_3",
    "grade": 3,
    "materials": [
      [
        "item_herb_blood_rose",
        2
      ],
      [
        "item_herb_soul_flower",
        2
      ]
    ],
    "base_rate": 84,
    "is_special": False
  },
  {
    "id": "recipe_b06",
    "name": "丹方·双倍",
    "output": "item_dual_pill_2",
    "grade": 3,
    "materials": [
      [
        "item_herb_heal_grass",
        5
      ],
      [
        "item_herb_spirit_grass",
        4
      ],
      [
        "item_core_2",
        4
      ]
    ],
    "base_rate": 55,
    "is_special": False
  },
  {
    "id": "recipe_b07",
    "name": "丹方·古方",
    "output": "item_despiration_pill",
    "grade": 4,
    "materials": [
      [
        "item_herb_dragon_blood_grass",
        3
      ],
      [
        "item_core_3",
        3
      ]
    ],
    "base_rate": 50,
    "is_special": False
  },
  {
    "id": "recipe_b08",
    "name": "丹方·极品",
    "output": "item_hp_super",
    "grade": 4,
    "materials": [
      [
        "item_herb_moon_dew_grass",
        2
      ],
      [
        "item_herb_coral_herb",
        2
      ],
      [
        "item_core_3",
        2
      ]
    ],
    "base_rate": 65,
    "is_special": False
  },
  {
    "id": "recipe_b09",
    "name": "丹方·捷径",
    "output": "item_haste_potion",
    "grade": 4,
    "materials": [
      [
        "item_herb_wind_flower",
        4
      ],
      [
        "item_beast_feather",
        3
      ]
    ],
    "base_rate": 52,
    "is_special": False
  },
  {
    "id": "recipe_b10",
    "name": "丹方·古法",
    "output": "item_break_pill_3",
    "grade": 5,
    "materials": [
      [
        "item_herb_ice_fire_lotus",
        3
      ],
      [
        "item_soul_essence",
        2
      ],
      [
        "item_core_4",
        4
      ]
    ],
    "base_rate": 30,
    "is_special": False
  },
  {
    "id": "recipe_b11",
    "name": "丹方·秘方",
    "output": "item_dragon_blood_pill",
    "grade": 5,
    "materials": [
      [
        "item_liquid_dragon_blood",
        2
      ],
      [
        "item_dragon_scale_plus",
        2
      ],
      [
        "item_core_4",
        3
      ]
    ],
    "base_rate": 40,
    "is_special": False
  },
  {
    "id": "recipe_b12",
    "name": "丹方·改良",
    "output": "item_poison_5",
    "grade": 5,
    "materials": [
      [
        "item_herb_blood_rose",
        6
      ],
      [
        "item_dragon_reverse_scale",
        1
      ]
    ],
    "base_rate": 45,
    "is_special": False
  },
  {
    "id": "recipe_b13",
    "name": "丹方·双倍",
    "output": "item_full_recovery",
    "grade": 6,
    "materials": [
      [
        "item_herb_bodhi_leaf",
        3
      ],
      [
        "item_herb_nether_flower",
        2
      ],
      [
        "item_core_5",
        3
      ]
    ],
    "base_rate": 28,
    "is_special": False
  },
  {
    "id": "recipe_b14",
    "name": "丹方·古方",
    "output": "item_qi_pill_6",
    "grade": 6,
    "materials": [
      [
        "item_herb_star_grass",
        3
      ],
      [
        "item_space_crystal",
        1
      ]
    ],
    "base_rate": 38,
    "is_special": False
  },
  {
    "id": "recipe_b15",
    "name": "丹方·秘传",
    "output": "item_dual_pill_5",
    "grade": 6,
    "materials": [
      [
        "item_herb_nether_flower",
        3
      ],
      [
        "item_phoenix_feather",
        2
      ],
      [
        "item_core_5",
        4
      ]
    ],
    "base_rate": 25,
    "is_special": False
  },
  {
    "id": "recipe_b16",
    "name": "丹方·极品",
    "output": "item_qi_pill_8",
    "grade": 8,
    "materials": [
      [
        "item_herb_ancient_tree_sap",
        3
      ],
      [
        "item_ore_void_stone",
        2
      ]
    ],
    "base_rate": 18,
    "is_special": False
  },
  {
    "id": "recipe_b17",
    "name": "丹方·古法",
    "output": "item_soul_restore_pill",
    "grade": 8,
    "materials": [
      [
        "item_herb_phoenix_flower",
        3
      ],
      [
        "item_soul_essence",
        3
      ],
      [
        "item_core_7",
        4
      ]
    ],
    "base_rate": 12,
    "is_special": False
  },
  {
    "id": "recipe_b18",
    "name": "丹方·秘方",
    "output": "item_dual_pill_7",
    "grade": 8,
    "materials": [
      [
        "item_herb_star_petal",
        2
      ],
      [
        "item_time_sand",
        2
      ],
      [
        "item_core_7",
        4
      ]
    ],
    "base_rate": 10,
    "is_special": False
  },
  {
    "id": "recipe_b19",
    "name": "丹方·改良",
    "output": "item_ancient_essence",
    "grade": 8,
    "materials": [
      [
        "item_herb_phoenix_flower",
        4
      ],
      [
        "item_core_7",
        3
      ]
    ],
    "base_rate": 13,
    "is_special": False
  },
  {
    "id": "recipe_b20",
    "name": "丹方·古方",
    "output": "item_recover_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_herb_void_lichen",
        3
      ],
      [
        "item_ore_emperor_jade",
        3
      ],
      [
        "item_core_8",
        4
      ]
    ],
    "base_rate": 10,
    "is_special": False
  },
  {
    "id": "recipe_b21",
    "name": "丹方·秘传",
    "output": "item_dual_pill_8",
    "grade": 9,
    "materials": [
      [
        "item_herb_eternal_fruit",
        3
      ],
      [
        "item_ore_light_crystal",
        2
      ],
      [
        "item_core_8",
        4
      ]
    ],
    "base_rate": 8,
    "is_special": False
  },
  {
    "id": "recipe_b22",
    "name": "丹方·极品",
    "output": "item_qi_pill_9",
    "grade": 9,
    "materials": [
      [
        "item_herb_emperor_root",
        5
      ],
      [
        "item_ore_light_crystal",
        3
      ]
    ],
    "base_rate": 12,
    "is_special": False
  },
  {
    "id": "recipe_b23",
    "name": "丹方·古法",
    "output": "item_divine_dew",
    "grade": 10,
    "materials": [
      [
        "item_herb_god_grass",
        5
      ],
      [
        "item_liquid_ambrosia",
        2
      ],
      [
        "item_world_fragment",
        1
      ]
    ],
    "base_rate": 3,
    "is_special": False
  },
  {
    "id": "recipe_b24",
    "name": "丹方·秘方",
    "output": "item_god_pill",
    "grade": 10,
    "materials": [
      [
        "item_herb_god_grass",
        6
      ],
      [
        "item_essence_creation",
        2
      ],
      [
        "item_world_fragment",
        2
      ]
    ],
    "base_rate": 2,
    "is_special": False
  },
  {
    "id": "recipe_b25",
    "name": "丹方·改良",
    "output": "item_phoenix_pill",
    "grade": 6,
    "materials": [
      [
        "item_phoenix_feather",
        3
      ],
      [
        "item_herb_phoenix_flower",
        2
      ],
      [
        "item_core_5",
        3
      ]
    ],
    "base_rate": 28,
    "is_special": False
  },
  {
    "id": "recipe_b26",
    "name": "丹方·捷径",
    "output": "item_break_pill_5",
    "grade": 7,
    "materials": [
      [
        "item_herb_dream_lotus",
        3
      ],
      [
        "item_soul_essence",
        3
      ],
      [
        "item_core_6",
        4
      ]
    ],
    "base_rate": 12,
    "is_special": False
  },
  {
    "id": "recipe_b27",
    "name": "丹方·古法",
    "output": "item_break_pill_6",
    "grade": 8,
    "materials": [
      [
        "item_herb_ancient_tree_sap",
        2
      ],
      [
        "item_time_sand",
        2
      ],
      [
        "item_core_7",
        5
      ]
    ],
    "base_rate": 8,
    "is_special": False
  },
  {
    "id": "recipe_b28",
    "name": "丹方·秘方",
    "output": "item_dragon_meat",
    "grade": 5,
    "materials": [
      [
        "item_dragon_scale_plus",
        2
      ],
      [
        "item_herb_ice_fire_lotus",
        2
      ]
    ],
    "base_rate": 72,
    "is_special": False
  },
  {
    "id": "recipe_b29",
    "name": "丹方·改良",
    "output": "item_shield_pill_3",
    "grade": 5,
    "materials": [
      [
        "item_beast_heart",
        3
      ],
      [
        "item_herb_void_mushroom",
        2
      ]
    ],
    "base_rate": 44,
    "is_special": False
  },
  {
    "id": "recipe_b30",
    "name": "丹方·古法",
    "output": "item_all_buff_pill",
    "grade": 5,
    "materials": [
      [
        "item_herb_void_mushroom",
        3
      ],
      [
        "item_energy_crystal",
        2
      ],
      [
        "item_core_4",
        2
      ]
    ],
    "base_rate": 40,
    "is_special": False
  }
]
