from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Folders
DATA_DIR_PATH = PROJECT_ROOT / "data"
PROMPTS_DIR_PATH = DATA_DIR_PATH / "prompts"
MANUAL_CHECK_DIR = DATA_DIR_PATH / "manual_check"
FETCHED_EMAILS = DATA_DIR_PATH / "fetched_emails"
LOGS_DIR_PATH = DATA_DIR_PATH / "logs"

# Files
CREDENTIALS_FILE_PATH = DATA_DIR_PATH / "credentials.json"
TOKEN_FILE_PATH = DATA_DIR_PATH / "token.json"
DUP_BY_MSG_ID_FILE_PATH = MANUAL_CHECK_DIR / "duplicate_by_msg_id.jsonl"
LLM_LOW_CONF_OUTPUT_FILE = MANUAL_CHECK_DIR / "llm_low_confidence_output.jsonl"
DUP_BY_FUZZY_MATCH = MANUAL_CHECK_DIR / "duplicate_by_fuzzy_matching.jsonl"


# List of all paths to create the folders and files dynamically at once before starting application
ALL_PATHS = [
    DATA_DIR_PATH, PROMPTS_DIR_PATH, MANUAL_CHECK_DIR, FETCHED_EMAILS, LOGS_DIR_PATH,
    CREDENTIALS_FILE_PATH, TOKEN_FILE_PATH, DUP_BY_MSG_ID_FILE_PATH, LLM_LOW_CONF_OUTPUT_FILE, DUP_BY_FUZZY_MATCH
]