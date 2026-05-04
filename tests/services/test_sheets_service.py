import pytest
from unittest.mock import MagicMock
from src.services.sheets_service import append_row, modify_row

@pytest.fixture
def mock_service():
    return MagicMock()

def test_append_row(mock_service):
    data = {
        "application_date": "2023-05-04",
        "company_name": "Test Company",
        "role": "Engineer",
        "current_status": "Applied",
        "current_confidence": "High",
        "status_flow": "Applied",
        "history": "Test history",
        "last_row_modification_date": "2023-05-04",
        "message_id": "1"
    }
    append_row(mock_service, "sheet_id", data)
    mock_service.spreadsheets().values().append.assert_called_once()

def test_modify_row(mock_service):
    existing_row = ["Existing Data"] * 9
    llm_output = {"normalized_company_name": "New Company", "normalized_job_title": "Developer"}
    email_data = {"id": "1", "date": "2023-05-04"}
    modify_row(mock_service, "sheet_id", 1, llm_output, email_data)
    mock_service.spreadsheets().values().update.assert_called_once()