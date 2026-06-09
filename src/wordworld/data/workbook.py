import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List
from zipfile import ZipFile


from wordworld.config.paths import WORKBOOK_PATH

SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOCUMENT_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

ROW_TAG = f"{{{SPREADSHEET_NS}}}row"
CELL_TAG = f"{{{SPREADSHEET_NS}}}c"
VALUE_TAG = f"{{{SPREADSHEET_NS}}}v"
TEXT_TAG = f"{{{SPREADSHEET_NS}}}t"
COLUMN_PATTERN = re.compile(r"^[A-Z]+")


def _to_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))


def _to_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "yes", "true", "y"}


def _cell_value(cell: ET.Element) -> str:
    if cell.get("t") == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(TEXT_TAG))
    value = cell.find(VALUE_TAG)
    return value.text if value is not None and value.text is not None else ""


class WorkbookReader:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _sheet_paths(self, archive: ZipFile) -> Dict[str, str]:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            relation.get("Id"): relation.get("Target", "")
            for relation in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
        }

        result: Dict[str, str] = {}
        sheets = workbook.find(f"{{{SPREADSHEET_NS}}}sheets")
        if sheets is None:
            return result

        for sheet in sheets:
            relation_id = sheet.get(f"{{{DOCUMENT_REL_NS}}}id", "")
            target = targets.get(relation_id, "").replace("\\", "/")
            if target.startswith("/"):
                target = target.lstrip("/")
            elif not target.startswith("xl/"):
                target = f"xl/{target}"
            result[sheet.get("name", "")] = target
        return result

    def read_sheets(self, sheet_names: Iterable[str]) -> Dict[str, List[Dict[str, str]]]:
        requested = set(sheet_names)
        result: Dict[str, List[Dict[str, str]]] = {}
        with ZipFile(self.path) as archive:
            paths = self._sheet_paths(archive)
            missing = requested.difference(paths)
            if missing:
                raise ValueError(f"工作簿缺少配置表：{', '.join(sorted(missing))}")
            for sheet_name in requested:
                result[sheet_name] = self._read_sheet(archive, paths[sheet_name])
        return result

    @staticmethod
    def _read_sheet(archive: ZipFile, path: str) -> List[Dict[str, str]]:
        headers: Dict[str, str] = {}
        rows: List[Dict[str, str]] = []
        with archive.open(path) as stream:
            for _, element in ET.iterparse(stream, events=("end",)):
                if element.tag != ROW_TAG:
                    continue

                values: Dict[str, str] = {}
                for cell in element.findall(CELL_TAG):
                    match = COLUMN_PATTERN.match(cell.get("r", ""))
                    if match:
                        values[match.group(0)] = _cell_value(cell)

                if not headers:
                    headers = values
                else:
                    rows.append(
                        {
                            header: values.get(column, "")
                            for column, header in headers.items()
                            if header
                        }
                    )
                element.clear()
        return rows


def _parse_events(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for row in rows:
        event_id = row.get("ID", "")
        if not event_id:
            continue
        options: List[Dict[str, Any]] = []
        for index in range(1, 5):
            text = row.get(f"Opt{index}_Text", "")
            if not text:
                continue
            options.append(
                {
                    "text": text,
                    "conditions": row.get(f"Opt{index}_Condition", ""),
                    "next": row.get(f"Opt{index}_Next", ""),
                    "effects": row.get(f"Opt{index}_Effect", ""),
                }
            )
        events.append(
            {
                "id": event_id,
                "title": row.get("Notes", "") or event_id,
                "kind": row.get("Type", "story") or "story",
                "pool": row.get("Pool", ""),
                "text": row.get("Text", ""),
                "conditions": row.get("Pre_Condition", ""),
                "weight": _to_int(row.get("Weight"), 1),
                "options": options,
                "speaker_id": row.get("Speaker_ID", ""),
                "scene_npcs": [
                    item for item in row.get("Scene_NPCs", "").split(",") if item
                ],
                "faction_context": [
                    item for item in row.get("Faction_Context", "").split(",") if item
                ],
            }
        )
    return events


def _parse_attributes(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    return {
        row["Attr_ID"]: {
            "id": row["Attr_ID"],
            "name": row.get("Name", row["Attr_ID"]),
            "initial": _to_int(row.get("Initial")),
            "min": _to_int(row.get("Min"), -999999999),
            "max": _to_int(row.get("Max"), 999999999),
        }
        for row in rows
        if row.get("Attr_ID")
    }


def _parse_relationships(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    relationships: List[Dict[str, Any]] = []
    for row in rows:
        relation_id = row.get("Relation_ID", "")
        if not relation_id:
            continue
        relationships.append(
            {
                "id": relation_id,
                "source": row.get("Source_ID", ""),
                "target": row.get("Target_ID", ""),
                "type": row.get("Relation_Type", ""),
                "initial_value": _to_int(row.get("Initial_Value")),
                "min_value": _to_int(row.get("Min_Value"), -100),
                "max_value": _to_int(row.get("Max_Value"), 100),
                "stage_rule": row.get("Stage_Rule", ""),
                "bidirectional": _to_bool(row.get("Is_Bidirectional")),
                "visible": _to_bool(row.get("Visible_To_Player")),
                "pre_condition": row.get("Pre_Condition", ""),
                "on_reach_effect": row.get("On_Reach_Effect", ""),
            }
        )
    return relationships


def _parse_level_progression(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    progression: List[Dict[str, Any]] = []
    for row in rows:
        raw_range = row.get("Level_Range", "")
        if not raw_range:
            continue
        if "-" in raw_range:
            start, end = raw_range.split("-", 1)
        else:
            start = end = raw_range
        progression.append(
            {
                "min_level": _to_int(start),
                "max_level": _to_int(end),
                "exp_formula": row.get("Exp_Formula", ""),
                "progress_exp": _to_int(row.get("Progress_Exp")),
                "gains": {
                    "douqi": _to_int(row.get("Douqi_Gain")),
                    "hp": _to_int(row.get("HP_Gain")),
                    "atk": _to_int(row.get("ATK_Gain")),
                    "def": _to_int(row.get("DEF_Gain")),
                    "spd": _to_int(row.get("SPD_Gain")),
                },
            }
        )
    return progression


def _parse_options(row: Dict[str, str], count: int = 3) -> List[Dict[str, str]]:
    return [
        {
            "text": row.get(f"Opt{index}_Text", ""),
            "conditions": row.get(f"Opt{index}_Condition", ""),
            "next": row.get(f"Opt{index}_Next", ""),
            "effects": row.get(f"Opt{index}_Effect", ""),
        }
        for index in range(1, count + 1)
        if row.get(f"Opt{index}_Text")
    ]


def _parse_maps(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    return {
        row["Map_ID"]: {
            "id": row["Map_ID"],
            "name": row.get("Name", row["Map_ID"]),
            "region": row.get("Region", ""),
            "unlock_condition": row.get("Unlock_Condition", ""),
            "recommend_level": _to_int(row.get("Recommend_Level"), 1),
            "stamina_cost": _to_int(row.get("Explore_Stamina_Cost"), 5),
            "safe_zone": _to_bool(row.get("Safe_Zone")),
            "exit_event": row.get("Exit_Event", ""),
            "description": row.get("Description", ""),
        }
        for row in rows
        if row.get("Map_ID")
    }


def _parse_encounters(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": row["Event_ID"],
            "map_id": row.get("Map_ID", ""),
            "weight": _to_int(row.get("Weight"), 1),
            "text": row.get("Text", ""),
            "conditions": row.get("Pre_Condition", ""),
            "options": _parse_options(row),
        }
        for row in rows
        if row.get("Event_ID")
    ]


def _parse_enemies(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    return {
        row["Enemy_ID"]: {
            "id": row["Enemy_ID"],
            "name": row.get("Name", row["Enemy_ID"]),
            "type": row.get("Type", ""),
            "level": _to_int(row.get("Level"), 1),
            "hp": _to_int(row.get("HP"), 30),
            "atk": _to_int(row.get("ATK"), 5),
            "def": _to_int(row.get("DEF"), 2),
            "spd": _to_int(row.get("SPD"), 5),
            "drop_table": row.get("Drop_Table", ""),
            "exp_reward": _to_int(row.get("Exp_Reward"), 10),
            "win_next": row.get("Win_Next", ""),
            "lose_next": row.get("Lose_Next", ""),
            "notes": row.get("Notes", ""),
            "can_kill": "non_lethal" not in str(row.get("Notes", "")),
            "skills": [
                skill.strip() for skill in row.get("Skills", "").split(",") if skill.strip()
            ],
        }
        for row in rows
        if row.get("Enemy_ID")
    }


def _parse_items(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    return {
        row["Item_ID"]: {
            "id": row["Item_ID"],
            "name": row.get("Name", row["Item_ID"]),
            "type": row.get("Type", ""),
            "use_condition": row.get("Use_Condition", ""),
            "use_effect": row.get("Use_Effect", ""),
            "description": row.get("Description", ""),
        }
        for row in rows
        if row.get("Item_ID")
    }


def _parse_skills(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    return {
        row["Skill_ID"]: {
            "id": row["Skill_ID"],
            "name": row.get("Name", row["Skill_ID"]),
            "type": row.get("Type", ""),
            "rank": row.get("Rank", ""),
            "effect": row.get("Effect", ""),
            "description": row.get("Description", ""),
        }
        for row in rows
        if row.get("Skill_ID")
    }


def _parse_realms(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": row["Realm_ID"],
            "name": row.get("Name", row["Realm_ID"]),
            "min_level": _to_int(row.get("Min_Level"), 1),
            "max_level": _to_int(row.get("Max_Level"), 99),
        }
        for row in rows
        if row.get("Realm_ID")
    ]


@lru_cache(maxsize=4)
def _load_game_data_cached(path_text: str) -> Dict[str, Any]:
    path = Path(path_text)
    if not path.exists():
        raise FileNotFoundError(f"找不到最新剧情数据：{path}")

    sheets = WorkbookReader(path).read_sheets(
        {
            "Events_剧情配置",
            "Attributes_属性库",
            "Flags_开关库",
            "NPCs_人物表",
            "Relationships_关系表",
            "Level_Progression_等级成长",
            "Maps_地图库",
            "Map_Encounters_奇遇池",
            "Enemies_敌人配置",
            "Items_道具库",
            "Skills_斗技功法",
            "Realms_境界成长",
        }
    )
    events = _parse_events(sheets["Events_剧情配置"])
    if not events:
        raise ValueError("最新剧情数据中没有可用事件。")

    return {
        "events": events,
        "attributes": _parse_attributes(sheets["Attributes_属性库"]),
        "flag_defaults": {
            row["Flag_ID"]: _to_int(row.get("Default_Value"))
            for row in sheets["Flags_开关库"]
            if row.get("Flag_ID")
        },
        "npc_names": {
            row["Character_ID"]: row.get("Name", row["Character_ID"])
            for row in sheets["NPCs_人物表"]
            if row.get("Character_ID")
        },
        "relationships": _parse_relationships(sheets["Relationships_关系表"]),
        "level_progression": _parse_level_progression(
            sheets["Level_Progression_等级成长"]
        ),
        "maps": _parse_maps(sheets["Maps_地图库"]),
        "encounters": _parse_encounters(sheets["Map_Encounters_奇遇池"]),
        "enemies": _parse_enemies(sheets["Enemies_敌人配置"]),
        "items": _parse_items(sheets["Items_道具库"]),
        "skills": _parse_skills(sheets["Skills_斗技功法"]),
        "realms": _parse_realms(sheets["Realms_境界成长"]),
        "start_event": events[0]["id"],
        "source_path": str(path),
    }


def load_game_data(path: Path = WORKBOOK_PATH) -> Dict[str, Any]:
    return _load_game_data_cached(str(path.resolve()))
