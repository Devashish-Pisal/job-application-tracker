import base64
import json
import re
from pathlib import Path
from loguru import logger
from datetime import datetime
from bs4 import BeautifulSoup
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


def generate_dedup_key(company_name:str, job_title:str):
    if not company_name:
        company_name = "null"
    if not job_title:
        job_title = "null"
    company_name = company_name.strip().lower()
    job_title = job_title.strip().lower()
    company_name = re.sub(r"[^\w\s]", "", company_name)
    job_title = re.sub(r"[^\w\s]", "", job_title)
    company_name = re.sub(r"\s+", " ", company_name).strip().replace(" ", "-")
    job_title = re.sub(r"\s+", " ", job_title).strip().replace(" ", "-")
    return f"{company_name}|{job_title}"


def append_jsonl(file_path:Path, new_data):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(new_data, ensure_ascii=False) + "\n")


def get_gmail_and_sheet_services():
    creds = get_credentials()
    gmail_service = get_gmail_service(creds=creds)
    sheet_service = get_sheets_service(creds=creds)
    return gmail_service, sheet_service


def prepare_new_row_data(llm_output, email_data):
    return{
        "application_date": email_data.get("date"),
        "company_name": llm_output.get("normalized_company_name").strip().upper(),
        "role": llm_output.get("normalized_job_title").strip().lower(),
        "current_status": llm_output.get("email_type"),
        "current_confidence": llm_output.get("confidence"),
        "source": email_data.get("source"),
        "history": prepare_history_to_append(llm_output, email_data),
        "last_row_modification_date": datetime.now().strftime("%Y-%m-%d"),
        "message_id": email_data.get("id")
    }




def prepare_row_modification_data(llm_output, email_data, existing_row):
    pass



def prepare_history_to_append(llm_output, email_data):
    formatted_llm = json.dumps(llm_output, indent=2, ensure_ascii=False)
    history_entry = f"""--- NEW EMAIL ENTRY ---
date appended: {datetime.now().strftime("%Y-%m-%d")}

llm_output:
{formatted_llm}

email metadata:
  message id: {email_data.get("id")}
  date received: {email_data.get("date")}
  sender name: {email_data.get("sender_name")}
  sender email: {email_data.get("sender_email")}

subject:
{email_data.get("subject")}

body:
{email_data.get("body")}

============================================================
"""
    return history_entry