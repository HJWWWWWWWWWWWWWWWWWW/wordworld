import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BUNDLE_ROOT = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
RUNTIME_ROOT = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else PROJECT_ROOT
)
STORY_DIR = BUNDLE_ROOT / "story"
SAVE_DIR = RUNTIME_ROOT / "saves"
WORKBOOK_PATH = STORY_DIR / "text_game_event_schema_v4.xlsx"
SAVE_PATH = SAVE_DIR / "save.json"
