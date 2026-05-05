import json
import time
from loguru import logger
from src.services.parser_service import parse_email
from src.llm.gemini import get_gemini_client, extract_job_info
from src.config import SHEET_ID, GEMINI_CONFIG, SHEET_COLUMN_NAME_INDEX_MAPPING
from path_config import  PROMPTS_DIR_PATH, DUP_BY_MSG_ID_FILE_PATH, DUP_BY_FUZZY_MATCH, LLM_LOW_CONF_OUTPUT_FILE, FETCHED_EMAILS
from src.services.sheets_service import append_row, message_exists_by_id, fuzzy_match_column_values, modify_row, fuzzy_match_company_and_role, prepare_new_row_data
from src.utils.helpers import load_raw_prompt, convert_email_dict_to_text, append_jsonl, get_gmail_and_sheet_services, construct_logging_object, delete_files, normalize_umlauts




def process_high_conf_output(sheet_service,llm_output, email_data, logging_obj):
    company_fuzzy_threshold = 0.90
    role_fuzzy_threshold = 0.85
    company_name_col_index = SHEET_COLUMN_NAME_INDEX_MAPPING["company-name"]
    role_col_index = SHEET_COLUMN_NAME_INDEX_MAPPING["role"]
    status_col_index = SHEET_COLUMN_NAME_INDEX_MAPPING["current-status"]
    company_name = llm_output["normalized_company_name"].strip().upper()
    role = llm_output["normalized_job_title"].strip().lower()
    current_status = llm_output["email_type"].strip().upper()
    new_entry = prepare_new_row_data(llm_output=llm_output, email_data=email_data)

    if company_name and role and company_name != "NULL" and role != "null": # Company name - Present; Role - Present
        count, matches = fuzzy_match_company_and_role(sheet_service, SHEET_ID, company_name_col_index, role_col_index, status_col_index, company_name, role, current_status, threshold=0.87)
        if count == 0:
            append_row(service=sheet_service, sheet_id=SHEET_ID, data=new_entry)
        elif count == 1:
            modify_row(sheet_service, SHEET_ID, matches[0]["row_index"], llm_output, email_data)
        elif count > 1 :
            logging_obj["Reason"] = f"Company Name and Role both present, but {count} many matches found | Matches: {matches}"
            append_jsonl(DUP_BY_FUZZY_MATCH, logging_obj)

    elif company_name and company_name != "NULL" and (not role or role == "null"): # Company name - Present; Role - Absent
        count, matches = fuzzy_match_column_values(sheet_service, SHEET_ID, company_name_col_index, status_col_index, company_name, current_status, company_fuzzy_threshold)
        if count == 0:
            append_row(sheet_service, SHEET_ID, new_entry)
        elif count == 1:
            modify_row(sheet_service, SHEET_ID,  matches[0]["row_index"], llm_output, email_data)
        elif count > 1:
            logging_obj["Reason"] = f"Only Company Name present, but {count} many matches found | Matches: {matches}"
            append_jsonl(DUP_BY_FUZZY_MATCH, logging_obj)

    elif (not company_name or company_name == "NULL") and role and role != "null": # Company name - Absent; Role - Present
        count, matches = fuzzy_match_column_values(sheet_service, SHEET_ID, role_col_index, status_col_index, role, current_status, role_fuzzy_threshold)
        if count == 0:
            append_row(sheet_service, SHEET_ID, new_entry)
        elif count == 1:
            modify_row(sheet_service, SHEET_ID, matches[0]["row_index"], llm_output, email_data)
        elif count > 0:
            logging_obj["Reason"] = f"Only Role present, but {count} many matches found | Matches: {matches}"
            append_jsonl(DUP_BY_FUZZY_MATCH, logging_obj)

    else: # Company name - Absent; Role - Absent
        logging_obj["Reason"] = f"Both Company Name and Role absent, but still classified as high confidence llm output."
        append_jsonl(DUP_BY_FUZZY_MATCH, logging_obj)




def pipeline():
    logger.info("Starting Tracking Pipeline...")
    gmail_service, sheet_service = get_gmail_and_sheet_services()
    client = get_gemini_client()
    system_prompt = load_raw_prompt(PROMPTS_DIR_PATH / "SYSTEM_PROMPT.txt")
    processed_files = []
    try:
        for file in FETCHED_EMAILS.iterdir():
            if file.name.endswith(".json"):
                msg = None
                with open(file, "r", encoding="utf-8") as f:
                    msg = json.load(f)
                if msg:
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
                        llm_output = normalize_umlauts(llm_output)
                        logging_obj = construct_logging_object(llm_output, email_data)
                        if float(llm_output["confidence"]) >= 0.70:
                            process_high_conf_output(sheet_service, llm_output, email_data, logging_obj)
                            processed_files.append(file)
                        else:
                            logging_obj["Reason"] = "LLM low confidence inference."
                            append_jsonl(LLM_LOW_CONF_OUTPUT_FILE, logging_obj)
                    else:
                        logging_obj = construct_logging_object("N/A", email_data)
                        logging_obj["Reason"] = "Message id already exists."
                        append_jsonl(DUP_BY_MSG_ID_FILE_PATH, logging_obj)
                else:
                    logger.error(f"Unable to read file {file}.")
    except Exception as e:
        logger.exception(f"Exception {e} occurred while backfilling.")
    finally:
        logger.info(f"Deleting {len(processed_files)} processed email file/s from directory {FETCHED_EMAILS}")
        delete_files(processed_files)


