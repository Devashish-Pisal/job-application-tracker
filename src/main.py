import time
from loguru import logger
# from src.utils.helpers import *
from path_config import  PROMPTS_DIR_PATH, DUP_BY_MSG_ID_FILE_PATH, DUP_BY_DEDUP_KEY_FILE_PATH, LLM_LOW_CONF_OUTPUT_FILE
from src.services.gmail_service import fetch_all_emails
from src.config import SHEET_ID, GEMINI_CONFIG, GMAIL_QUERY
from src.llm.gemini import get_gemini_client, extract_job_info
from src.utils.helpers import load_raw_prompt, convert_email_dict_to_text, generate_dedup_key, append_jsonl, get_gmail_and_sheet_services
from src.services.parser_service import parse_email
from src.services.sheets_service import append_row, message_exists_by_id, message_exists_by_dedup_key


def process_high_conf_output(sheet_service, combined_email_data):
    pass



def pipeline():
    logger.info("Starting Job Tracker Pipeline...")
    gmail_service, sheet_service = get_gmail_and_sheet_services()
    client = get_gemini_client()
    system_prompt = load_raw_prompt(PROMPTS_DIR_PATH / "SYSTEM_PROMPT.txt")
    messages = fetch_all_emails(gmail_service, GMAIL_QUERY)
    messages = messages
    for msg in messages:
        email_data = parse_email(msg)
        msg_id = email_data['id']
        if not message_exists_by_id(sheet_service, SHEET_ID, msg_id):
            formated_email_data = convert_email_dict_to_text(email_data)
            time.sleep(GEMINI_CONFIG["consecutive_query_delay"])
            llm_output = extract_job_info(
                client=client,
                system_prompt=system_prompt,
                email_data=formated_email_data,
                model=GEMINI_CONFIG["model"],
                max_retries=GEMINI_CONFIG["max_retries"],
                temp=GEMINI_CONFIG["temp"]
            )
            if float(llm_output["confidence"]) >= 0.70:
                dedup_key = generate_dedup_key(llm_output["normalized_company_name"], llm_output["normalized_job_title"])
                if not message_exists_by_dedup_key(sheet_service, SHEET_ID, dedup_key):
                    output = {
                        "date": email_data["date"],
                        "company": llm_output["normalized_company_name"].strip().upper(),
                        "role": llm_output["normalized_job_title"].strip().lower(),
                        "status": llm_output["email_type"],
                        "source": email_data["source"].strip().lower(),
                        "confidence": float(llm_output["confidence"]),
                        "email_body": email_data["body"],
                        "status_flow": "APPLIED", # because most probably it is new entry
                        "message_id": email_data["id"],
                        "dedup_key": dedup_key
                    }
                    append_row(sheet_service, SHEET_ID, output)
                else:
                    # TODO:check for status
                    logger.warning(f"DEDUP_CHECK_BY_DEDUP_KEY_(FUZZY): Message already exists in sheet. | Parsed Message {email_data} | LLM Output {llm_output}.")
                    append_jsonl(DUP_BY_DEDUP_KEY_FILE_PATH, llm_output)
            else:
                logger.warning(f"LLM_LOW_CONFIDENCE: Model is not confident about classification. | Parsed Message {email_data} | LLM Output {llm_output}.")
                append_jsonl(LLM_LOW_CONF_OUTPUT_FILE, llm_output)
        else:
            logger.warning(f"DEDUP_CHECK_BY_MSG_ID: Message already exists in sheet. | Parsed Message {email_data}.")
            append_jsonl(DUP_BY_MSG_ID_FILE_PATH, email_data)




if __name__ == "__main__":
    pipeline()