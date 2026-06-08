from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STORY_DIR = PROJECT_ROOT / "story"
SAVE_DIR = PROJECT_ROOT / "saves"
WORKBOOK_PATH = STORY_DIR / "text_game_event_schema_v4.xlsx"
SAVE_PATH = SAVE_DIR / "save.json"
