import time
import json
from rapidfuzz import fuzz
from loguru import logger
from datetime import datetime
from googleapiclient.discovery import build
from src.config import SHEET_COLUMN_NAME_INDEX_MAPPING




def get_sheets_service(creds):
    return build("sheets", "v4", credentials=creds)


def append_row(service, sheet_id, data):
    values = [[
        data["application_date"], # column A
        data["company_name"], # column B
        data["role"], # column C
        data["current_status"], # column D
        data["current_confidence"], # column E
        data["status_flow"], # column F
        data["history"], # column G
        data["last_row_modification_date"], # column H
        data["message_id"], #  column I
    ]]
    body = {"values": values}
    time.sleep(1) # Sleep for 1 sec to avoid "Too many requests" error
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A:I",
        valueInputOption="RAW",
        body=body
    ).execute()
    logger.success(f"Row appended to spreadsheet: {values}")


def modify_row(service, sheet_id, row_index, llm_output, email_data):
    time.sleep(1)
    row_data = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"Sheet1!{row_index}:{row_index}"
    ).execute()
    values = row_data.get("values", [])[0]
    updated_row = prepare_row_modification_data(llm_output, email_data, values)
    time.sleep(1)
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"Sheet1!A{row_index}:I{row_index}",
        valueInputOption="RAW",
        body={
            "values": updated_row
        }
    ).execute()
    logger.success(f"Row at index {row_index} successfully modified with values {updated_row}")


def message_exists_by_id(service, sheet_id, message_id):
    time.sleep(1)
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"Sheet1!{SHEET_COLUMN_NAME_INDEX_MAPPING["message-ids"]}:{SHEET_COLUMN_NAME_INDEX_MAPPING["message-ids"]}"
    ).execute()
    values = result.get("values", [])
    ids = {
        single_id.strip()
        for row in values if row
        for single_id in row[0].split(",")
    }
    return message_id in ids


def fuzzy_match_column_values(service, sheet_id, column_index:str, status_col_index, input_to_match:str, curr_status, threshold:float):
    time.sleep(1)
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"Sheet1!{column_index}:{column_index}"
    ).execute()
    status_res = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"Sheet1!{status_col_index}:{status_col_index}"
    ).execute()
    values = result.get("values", [])
    status_list = status_res.get("values", [])
    matches = []
    input_to_match = (input_to_match or "").strip()
    for idx,(row, status) in enumerate(zip(values[1:], status_list[1:]), start=2):
        if not row:
            continue
        if input_to_match.isupper(): # If it is upper, then it is company name
            value = row[0].strip().upper()
        else: # otherwise role
            value = row[0].strip().lower()
        if value in ("", "null", "n/a", "N/A"):
            continue
        score = fuzz.token_set_ratio(input_to_match, value) / 100
        if score >= threshold and is_next_status(status[0].strip().upper(), curr_status):
            matches.append({
                "row_index": idx, # index == actual row number
                "value": value,
                "score": score,
            })
    return len(matches), matches


def fuzzy_match_company_and_role(service, sheet_id, company_col_index, role_col_index, status_col_index, company_name, role, curr_status, threshold):
    time.sleep(1)
    company_res = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"Sheet1!{company_col_index}:{company_col_index}"
    ).execute()
    time.sleep(1)
    role_res = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"Sheet1!{role_col_index}:{role_col_index}"
    ).execute()
    status_res = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"Sheet1!{status_col_index}:{status_col_index}"
    ).execute()
    company_col = company_res.get("values", [])
    role_col = role_res.get("values", [])
    status_col = status_res.get("values", [])
    matches = []
    for idx, (c_name, r_name, status) in enumerate(zip(company_col[1:], role_col[1:], status_col[1:]), start=2):
        c_name = c_name[0].strip().upper() if c_name else ""
        r_name = r_name[0].strip().lower() if r_name else ""
        c_score = fuzz.token_set_ratio(company_name, c_name) / 100
        r_score = fuzz.token_set_ratio(role, r_name) / 100
        final_score = c_score * 0.6 + r_score * 0.4
        if final_score >= threshold and is_next_status(status[0].strip().upper(), curr_status):
            matches.append({
                "row_index": idx, # index == actual row number
                "company_name": c_name,
                "role_name": r_name,
                "score": final_score,
            })
    return len(matches), matches


def get_all_rows(service, sheet_id):
    time.sleep(1)
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="Sheet1!A:J"
    ).execute()
    return result.get("values", [])



def prepare_new_row_data(llm_output, email_data):
    history = prepare_history_to_append(llm_output, email_data)
    company_name = llm_output["normalized_company_name"] if llm_output.get("normalized_company_name") and llm_output.get("normalized_company_name") != "null" else "N/A"
    role = llm_output["normalized_job_title"]  if llm_output.get("normalized_job_title") and llm_output.get("normalized_job_title") != "null" else "n/a"
    return{
        "application_date": email_data.get("date", "N/A"),
        "company_name": company_name.strip().upper(),
        "role": role.strip().lower(),
        "current_status": llm_output.get("email_type", "N/A"),
        "current_confidence": llm_output.get("confidence", "N/A"),
        "status_flow": llm_output.get("email_type", "N/A"),
        "history":  history if history else "N/A",
        "last_row_modification_date": datetime.now().strftime("%Y-%m-%d"),
        "message_id": email_data.get("id", "N/A")
    }



def prepare_row_modification_data(llm_output, email_data, existing_row):
    modified_row = [existing_row[0]]
    # Fix company name (if not available)
    if existing_row[1] == "N/A" and llm_output["normalized_company_name"] and llm_output["normalized_company_name"] != "null":
        modified_row.append(llm_output.get("normalized_company_name", "N/A").strip().upper())
    else:
        modified_row.append(existing_row[1])
    # Fix role (if not available)
    if existing_row[2] == "n/a" and llm_output["normalized_job_title"] and llm_output["normalized_job_title"] != "null":
        modified_row.append(llm_output.get("normalized_job_title", "n/a").strip().lower())
    else:
        modified_row.append(existing_row[2])
    # take current status as it is
    modified_row.append(llm_output.get("email_type", "N/A"))
    # take current confidence as it is
    modified_row.append(llm_output.get("confidence", "N/A"))
    # update status flow
    new_status_flow = existing_row[5] + " ⟶ " + llm_output["email_type"]
    modified_row.append(new_status_flow)
    # update history
    new_history = existing_row[6] + prepare_history_to_append(llm_output, email_data)
    if len(new_history) >= 50000:
        new_history = new_history[0:49980] + f"\n TRUNCATED....."
    modified_row.append(new_history)
    # add last row modification date
    modified_row.append(datetime.now().strftime("%Y-%m-%d"))
    # append new email id
    new_ids = existing_row[8] + ", " + email_data.get('id')
    modified_row.append(new_ids)
    return [modified_row]


def is_next_status(old_status, new_status):
    status_scores = {
        "APPLIED": 0,
        "TEST_INVITATION": 1,
        "INTERVIEW": 1,
        "OFFER": 2,
        "REJECTION": 2,
        "OTHER": 3
    }
    return status_scores[new_status] >= status_scores[old_status]


def prepare_history_to_append(llm_output, email_data):
    formatted_llm = json.dumps(llm_output, indent=2, ensure_ascii=False)
    email_metadata = {
        "message id": email_data.get("id"),
        "received date": email_data.get("date"),
        "sender name": email_data.get("sender_name"),
        "sender email": email_data.get("sender_email")
    }
    email_metadata = json.dumps(email_metadata, indent=2, ensure_ascii=False)
    history_entry = f"""--- NEW EMAIL ENTRY ---
date appended: {datetime.now().strftime("%Y-%m-%d")}

llm_output:
{formatted_llm}

email metadata:
{email_metadata}

subject:
{email_data.get("subject")}

body:
{email_data.get("body")}

=================================================================================================================================
"""
    if len(history_entry) >= 50000:
        history_entry = history_entry[0:49980] + f"\n TRUNCATED....."
    return history_entry