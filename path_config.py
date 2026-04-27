from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Folders
DATA_DIR_PATH = PROJECT_ROOT / "data"
PROMPTS_DIR_PATH = DATA_DIR_PATH / "prompts"
MANUAL_CHECK_DIR = DATA_DIR_PATH / "manual_check"


# Files
CREDENTIALS_FILE_PATH = DATA_DIR_PATH / "credentials.json"
TOKEN_FILE_PATH = DATA_DIR_PATH / "token.json"
DUP_BY_MSG_ID_FILE_PATH = MANUAL_CHECK_DIR / "duplicate_by_msg_id.jsonl"
DUP_BY_DEDUP_KEY_FILE_PATH = MANUAL_CHECK_DIR / "duplicate_by_dedup_key.jsonl"
LLM_LOW_CONF_OUTPUT_FILE = MANUAL_CHECK_DIR / "llm_low_confidence_output.jsonl"

