from googleapiclient.discovery import build
from loguru import logger
from rapidfuzz import fuzz

def get_sheets_service(creds):
    return build("sheets", "v4", credentials=creds)


def append_row(service, sheet_id, data):
    values = [[
        data["date"], # column A
        data["company"], # column B
        data["role"], # column C
        data["status"], # column D
        data["source"], # column E
        data["confidence"], # column F
        data["email_body"], # column G
        data["status_flow"], # column H
        data["message_id"], #  column I
        data["dedup_key"] # (company_role )  column J
    ]]
    body = {"values": values}
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A:J",
        valueInputOption="RAW",
        body=body
    ).execute()
    logger.info(f"Row appended to spreadsheet: {values}")


def modify_row(service, sheet_id, row_index, new_data):
    # TODO
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="Sheet1!A5:D5",  # row 5
        valueInputOption="USER_ENTERED",
        body={
            "values": [[
                "new_company",
                "new_title",
                "new_status",
                "new_dedup_key"
            ]]
        }
    ).execute()
    pass

def message_exists_by_id(service, sheet_id, message_id):
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="Sheet1!I:I"
    ).execute()
    values = result.get("values", [])
    for row in values:
        if row and row[0] == message_id:
            return True
    return False


def message_exists_by_dedup_key(service, sheet_id, dedup_key):
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="Sheet1!J:J"
    ).execute()
    values = result.get("values", [])
    for idx, row in enumerate(values):
        if not row or not row[0] or idx == 0:
            continue
        if is_similar_dedup_key(dedup_key, row[0]):
            return True
    return False


def is_similar_dedup_key(key1: str, key2: str, threshold=85):
    company1, title1 = key1.split("|")
    company2, title2 = key2.split("|")
    company_score = fuzz.partial_ratio(company1, company2)
    title_score = fuzz.token_sort_ratio(title1, title2)
    # weight company higher (more important)
    final_score = (0.6 * company_score) + (0.4 * title_score)
    return final_score >= threshold