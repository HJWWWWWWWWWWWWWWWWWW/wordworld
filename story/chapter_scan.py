"""
Chapter-by-chapter scan of 13.txt to find missing content.
Checks: locations, characters, items, skills, factions not yet in the game.
"""
import re, sys
sys.path.insert(0, 'src')
from wordworld.data.workbook import load_game_data

with open('story/13.txt', 'r', encoding='utf-8') as f:
    content = f.read()

data = load_game_data()

# Existing data sets
existing_maps = {m['name'] for m in data['maps'].values()}
existing_map_ids = set(data['maps'].keys())
existing_items = {item['name'] for item in data['items'].values()}
existing_npcs = set(data['npc_names'].values())
existing_npc_ids = set(data['npc_names'].keys())
existing_skills = {s['name'] for s in data['skills'].values()}
existing_enemies = {e['name'] for e in data['enemies'].values()}

output = []
output.append("=" * 80)
output.append("逐章扫描查漏补缺报告")
output.append("=" * 80)

# ── 1. CHAPTER TITLES ──
chapters = re.findall(r'第[零一二三四五六七八九十百千\d]+章\s+(.*?)\n', content)
output.append(f"\n### 章节总数: {len(chapters)}")
output.append("\n### 含地点关键词的章节标题:")
location_kw = ['城','镇','宗','阁','谷','山','域','界','岛','塔','殿','院','沙漠','帝国','平原','洞','府','池','潭','林','墟','盟']
for i, title in enumerate(chapters):
    if any(kw in title for kw in location_kw):
        output.append(f"  Ch{i+1}: {title}")

# ── 2. MISSING LOCATIONS (deeper scan) ──
output.append("\n\n### 深度地点扫描:")
scan_locations = [
    # Cities that might be missing
    ("黑印城拍卖场", "黑印城"),
    ("千药坊", "暗角域"),
    ("万药斋", "暗角域/青山镇"),
    ("林门", "迦南学院/暗角域"),
    ("磐门", "迦南学院内院"),
    ("天焚炼气塔", "迦南学院"),
    ("天心城", "中州"),  # check again
    ("化骨城", "暗角域边境"),
    ("雁城", "暗角域边境"),
    ("天涯城", "暗角域"),
    ("天擎城", "中州"),
    ("血宗", "暗角域"),
    ("暗盟", "暗角域"),
    ("八扇门", "黑印城"),
    ("风雷东阁", "中州"),
    ("风雷西阁", "中州"),
    ("风雷南阁", "中州"),
    ("风雷北阁", "中州"),
    ("玄冥宗", "中州"),
    ("冥河盟", "中州"),
    ("中域", "中州"),
    ("中州南域", "中州"),
    ("中州西域", "中州"),
    ("中州东域", "中州"),
    ("中州北域", "中州"),
    ("妖火平原", "中州"),
    ("丹界", "中州"),
    ("灵界", "远古"),
    ("石界", "远古"),
    ("雷界", "远古"),
    ("炎界", "远古"),
    ("天罡殿", "黑渊殿"),
    ("人殿", "黑渊殿"),
    ("地殿", "黑渊殿"),
    ("天殿", "黑渊殿"),
    ("死寂门", "黑渊殿"),
    ("锁黑渊殿", "黑渊殿"),
    ("落雁帝国", "西北大陆"),
    ("慕兰帝国", "西北大陆"),
    ("蛇人族圣城", "赤沙荒漠"),
    ("蛇人族部落", "赤沙荒漠"),
    ("赤鳞神殿", "赤沙荒漠"),
    ("沧澜圣城", "沧澜帝国"),
    ("黑焰城", "沧澜帝国"),
    ("白城", "沧澜帝国"),
    ("焱城", "沧澜帝国"),
    ("天目山脉", "中州"),
    ("天山血潭", "中州"),
    ("岩浆地底世界", "迦南学院"),
    ("源火广场", "古帝洞府"),
    ("林家", "青石城"),
    ("星陨峰", "中州"),
    ("空间交易会", "中州"),
    ("四方阁大会", "中州"),
    ("云族天墓", "古界"),
    ("龙墓", "龙岛"),
    ("万蝎门", "出云帝国"),
    ("魔焰谷", "暗角域"),
    ("黑域大平原", "暗角域"),
    ("暗角域大平原", "暗角域"),
    ("黑域平原", "暗角域"),
    ("天妖凰族", "中州/兽域"),
    ("虚空龙族", "虚空"),
    ("九幽地冥蟒", "兽域"),
    ("天府", "中州"),
    ("天元联盟", "中州"),
    # Cities between 沧澜 and 暗角域
    ("大岭城", "沧澜帝国边境"),
    ("镇鬼关", "沧澜帝国边境"),
    # Specific notable locations
    ("青山镇", "魔兽山脉"),
    ("和平镇", "迦南学院"),
    ("黑印城", "暗角域"),
    ("枫城", "暗角域"),
    ("黑皇城", "暗角域"),
    ("天北城", "中州"),
    ("叶城", "丹域"),
    ("圣丹城", "丹域"),
    ("幽冥山脉", "中州"),
    ("葬尸山脉", "中州"),
    ("玄黄要塞", "西北大陆"),
    ("九幽黄泉", "兽域"),
]

for loc_name, region in scan_locations:
    count = content.count(loc_name)
    in_game = loc_name in existing_maps
    if count > 0 and not in_game:
        output.append(f"  [MISSING] {loc_name} (出现{count}次) - {region}")
    elif count == 0:
        output.append(f"  [NOT IN NOVEL] {loc_name} - {region}")

# ── 3. MISSING CHARACTERS ──
output.append("\n\n### 深度人物扫描:")
scan_chars = [
    "海波东", "加刑天", "法犸", "夭夜", "夭月",
    "若琳", "琥嘉", "吴昊", "白山", "林修崖", "林焱", "柳擎", "柳菲",
    "韩月", "韩雪", "韩池", "韩闲",
    "苏千", "苏媚",
    "紫妍", "欣蓝", "萧玉", "萧宁", "萧媚",
    "凌影", "青鳞", "小医仙",
    "青韵", "青山", "青棱",
    "古河", "柳翎", "月儿",
    "雅妃", "谷尼", "毕凡",
    "赤鳞", "月媚", "花蛇儿", "墨巴斯",
    "玄炉老人", "风尊者", "铁剑尊者",
    "唐震", "唐火儿", "唐鹰",
    "冰河", "冰河尊者",
    "黄泉尊者", "雷尊者", "剑尊者",
    "玄空子", "玄衣", "天雷子",
    "丹晨", "曹颖", "宋清",
    "叶重", "欣蓝",
    "慕骨老人", "青华老怪", "鹰山老人",
    "冷煜", "金银二老", "莫天行",
    "蝎毕岩", "万蝎门",
    "魂灭生", "魂元天", "魂生天", "魂尧", "魂虚子", "魂风", "魂玉", "魂魔老人",
    "玄冥帝", "虚无吞炎",
    "云元", "古烈", "古青阳", "古华", "古刑", "古妖", "古真", "古南海",
    "炎烬", "雷赢",
    "药丹", "药万归", "药星极",
    "苍坤", "北龙王", "南龙王", "西龙王", "黑擎",
    "林烬", "林战", "萧鼎", "萧厉", "萧潇", "林玄", "萧晨",
    "云曦", "苏婉清", "纳兰桀", "纳兰肃",
    "米特尔腾山", "木辰", "木战",
    "严狮", "风黎", "丘陵",
    "骛护法", "摘星老鬼",
    "地魔老鬼", "方言", "方言三老",
    "范痨", "范凌",
    "郝长老", "火长老", "柳长老",
    "程耀", "姚盛", "付敖", "费天",
    "墨承", "穆蛇", "铁乌",
    "绿蛮", "白牙", "阴世", "袁衣",
    "净莲妖圣", "黄泉妖圣",
    "源帝", "林玄",
    # Check for missing ones
    "熊战", "天火尊者", "玄黄", "妖暝",
    "十大地尊", "九天尊",
    "药天", "药灵", "药火",
    "魂屠", "魂煞", "魂镜",
    "古谦", "古虚", "古道",
    "炎耀", "炎火",
    "雷云", "雷电",
    "东龙甲", "西龙丁",
]

for char_name in scan_chars:
    count = content.count(char_name)
    in_game = char_name in existing_npcs
    if count > 0 and not in_game:
        output.append(f"  [MISSING NPC] {char_name} (出现{count}次)")
    elif count == 0:
        pass  # Not in novel

# ── 4. MISSING SKILLS/ITEMS ──
output.append("\n\n### 缺失灵技/功法扫描:")
scan_skills = [
    "八荒崩", "焰分噬浪尺", "佛怒火莲", "帝印决", "五轮离火法",
    "天火三玄变", "金刚琉璃体", "大天造化掌", "黄泉天怒", "黄泉掌", "黄泉指",
    "三千雷动", "三千雷幻身", "风之极", "风之极陨杀", "风推势",
    "吸掌", "吹火掌", "狮山裂", "狂狮怒罡", "狂狮吟",
    "六合游身尺", "覆地印", "湮天印", "开山印", "翻海印",
    "古帝印", "毁灭火体", "龙凰古甲", "虚空龙族之力",
    "金乌焚天火", "青莲源火", "陨心源火", "净世白莲火", "三千星空火",
    "玄冥冷火", "海心焰", "玄黄炎", "万兽灵火", "八荒破灭焱",
    "九幽金祖火", "红莲业火", "九幽风炎", "火云水炎", "龟灵地火", "火山石焰",
    "生灵之焱", "虚无吞炎",
    "紫云翼", "碧蛇三花瞳", "厄难毒体",
    "焚诀", "血宗秘法", "玄族秘法", "花宗秘法", "蛇人封印术",
    "魂手印", "魂锁", "魂帝秘法",
    "林族族纹", "联盟号令",
    "绝世好剑",  # joke
    "大寂灭指", "黄泉指",
    "六合游身", "龙凰古甲", "虚空龙族",
    "死寂之门", "锁魂之术",
]

for skill_name in scan_skills:
    count = content.count(skill_name)
    in_game = skill_name in existing_skills or any(skill_name in s for s in existing_skills)
    if count > 5 and not in_game:
        output.append(f"  [MISSING SKILL] {skill_name} (出现{count}次)")
    elif count > 0 and not in_game:
        output.append(f"  [RARE SKILL] {skill_name} (出现{count}次)")

# ── 5. MISSING ITEMS ──
output.append("\n\n### 缺失道具扫描:")
scan_items = [
    "纳戒", "玄重尺", "药鼎", "万兽鼎", "火莲瓶",
    "聚气散", "筑基灵液", "三纹青灵丹", "灵师丹", "皇极丹",
    "破宗丹", "噬生丹", "复灵紫丹", "青冥寿丹", "阴阳玄龙丹",
    "生骨融血丹", "紫心破障丹", "茯苓青丹",
    "地心淬体乳", "七幻青灵涎", "菩提化体涎",
    "化形丹",
    "净世白莲火残图", "源帝玉",
    "空间玉简", "妖傀", "天妖傀", "北王",
    "远古虫皇衣", "天墓之魂",
    "帝品雏丹", "菩提心", "菩提子",
    "黄泉血晶",
    "魂婴果",
    "黑色戒指", "七彩毒经",
]

for item_name in scan_items:
    count = content.count(item_name)
    in_game = item_name in existing_items
    if count > 5 and not in_game:
        output.append(f"  [MISSING ITEM] {item_name} (出现{count}次)")
    elif count > 0 and not in_game:
        output.append(f"  [RARE ITEM] {item_name} (出现{count}次)")

# Write report
with open('_chapter_scan_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print("Scan complete. Report written to _chapter_scan_report.txt")
PYEOF