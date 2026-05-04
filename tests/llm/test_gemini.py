import pytest
from unittest.mock import MagicMock
from src.llm.gemini import extract_job_info, get_gemini_client

@pytest.fixture
def mock_client():
    return MagicMock()

def test_extract_job_info(mock_client):
    mock_response = MagicMock(parsed={"normalized_company_name": "Test Company", "normalized_job_title": "Engineer"})
    mock_client.models.generate_content.return_value = mock_response
    job_info = extract_job_info(mock_client, "test_prompt", "test_email")
    assert job_info["normalized_company_name"] == "Test Company"
    assert job_info["normalized_job_title"] == "Engineer"

def test_extract_job_info_with_invalid_response(mock_client):
    mock_response = MagicMock(parsed="Invalid response")
    mock_client.models.generate_content.return_value = mock_response
    with pytest.raises(ValueError):
        extract_job_info(mock_client, "test_prompt", "test_email")