import os
import json
import base64
from pathlib import Path
from loguru import logger
from datetime import datetime
from bs4 import BeautifulSoup
from path_config import LOGS_DIR_PATH, ALL_PATHS
from src.auth.google_auth import get_credentials
from src.services.gmail_service import get_gmail_service
from src.services.sheets_service import get_sheets_service


def decode_base64(data):
    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def load_raw_prompt(path:Path):
    if path.exists() and path.is_file() and str(path).endswith(".txt"):
        data = None
        with open(path, "r", encoding="utf-8") as file:
            data = file.read()
        if data:
            return data
        else:
            raise ValueError(f"File {path} is empty.")
    else:
        raise FileNotFoundError(f"File not found at {path} OR folder path provided OR file is not a text file.")


def convert_email_dict_to_text(email_dict:dict):
    text = f"""
Sender Name: {email_dict["sender_name"]}
Sender Email: {email_dict["sender_email"]}
Subject: {email_dict["subject"]}
Body:
{email_dict["body"]}       
    """
    return text


def append_jsonl(file_path:Path, new_data):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(new_data, ensure_ascii=False) + "\n")
    logger.info(f"New data is appended to file {file_path}. | Data = {new_data}")


def get_gmail_and_sheet_services():
    creds = get_credentials()
    gmail_service = get_gmail_service(creds=creds)
    sheet_service = get_sheets_service(creds=creds)
    return gmail_service, sheet_service


def construct_logging_object(llm_output, email_data):
    result = {
        "Reason": "", # will be injected on the fly
        "llm_output": llm_output,
        "email_data": email_data,
    }
    return result



def delete_files(files:list):
    for file in files:
        os.remove(file)
        logger.info(f"File '{file}' deleted!")


def setup_logger():
    log_file_name = LOGS_DIR_PATH / (datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")
    logger.add(log_file_name, retention="30 days")
    logger.info(f"Logs of this run will be saved in file '{log_file_name}'")


def create_necessary_paths():
    for path in ALL_PATHS:
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)


def normalize_umlauts(llm_output):
    company_name = llm_output.get("normalized_company_name", "NULL")
    role = llm_output.get("normalized_job_title", "null")
    translation = str.maketrans({
        "Ä": "AE",
        "Ö": "OE",
        "Ü": "UE",
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
    })
    llm_output["normalized_company_name"] = company_name.translate(translation).strip().upper() # compony names are stored in sheet in upper case
    llm_output["normalized_job_title"] = role.translate(translation).strip().lower() # roles are stored in sheet in lower case
    return llm_output