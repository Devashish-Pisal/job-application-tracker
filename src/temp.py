from src.services.sheets_service import get_all_rows, is_next_status
from src.utils.helpers import get_gmail_and_sheet_services
from src.config import SHEET_ID, GEMINI_CONFIG, SHEET_COLUMN_NAME_INDEX_MAPPING
import pandas as pd
from rapidfuzz import fuzz
from pprint import pprint
import time

def fuzzy_match_company_and_role(service, sheet_id, all_columns_indices, company_col_index, role_col_index, status_col_index, company_name, role, curr_status, company_thresh, role_thresh):
    time.sleep(1)
    data = get_all_rows(service, sheet_id)
    rows = data[1:]
    df = pd.DataFrame(rows, columns=all_columns_indices)
    df["sheet_row"] = range(2, len(rows) + 2) # create new colum for exact sheet row numbers

    sub_df = df[[company_col_index, "sheet_row"]]
    company_matches = pd.DataFrame(columns=df.columns)
    for _, row in sub_df.iterrows():
        existing_company = str(row[company_col_index]).strip().upper()
        company_score = fuzz.token_set_ratio(company_name, existing_company) / 100
        if company_score >= company_thresh:
            matched_row = df[df["sheet_row"] == row["sheet_row"]]
            company_matches = pd.concat(
                [company_matches, matched_row],
                ignore_index=True
            )
    sub_df = company_matches[[role_col_index, "sheet_row"]]
    final_matches = pd.DataFrame(columns=df.columns)
    for _,row in sub_df.iterrows():
        existing_role = str(row[role_col_index]).strip().lower()
        role_score = fuzz.token_set_ratio(role, existing_role) / 100
        if role_score >= role_thresh:
            matched_row = df[df["sheet_row"] == row["sheet_row"]]
            final_matches = pd.concat(
                [final_matches, matched_row],
                ignore_index=True
            )
    matches = []
    for _, row in final_matches.iterrows():
        if is_next_status(row[status_col_index], curr_status):
            matches.append({
                "row_index": row["sheet_row"],  # index == actual row number
                "company_name": row[company_col_index],
                "role_name": row[role_col_index],
                "score": "N/A",
            })
    return len(matches), matches


if __name__ == "__main__":
    '''
    gmail_service, sheet_service = get_gmail_and_sheet_services()
    company_name = "SOFTWARE"
    role = "werkstudent software-entwicklung"
    current_status = "APPLIED"
    count, matches = fuzzy_match_company_and_role(
        sheet_service,
        SHEET_ID,
        SHEET_COLUMN_NAME_INDEX_MAPPING.values(),
        "B",
        "C",
        "D",
        company_name,
        role,
        current_status,
        0.90,
        0.85
    )
    print(count)
    pprint(matches)
    '''

