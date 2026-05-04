import pytest
from unittest.mock import MagicMock
from src.services.gmail_service import fetch_all_emails_and_save, get_gmail_service


@pytest.fixture
def mock_service():
    return MagicMock()


def test_fetch_all_emails_and_save(mock_service):
    mock_service.users().messages().list.return_value.execute.return_value = {"messages": [{"id": "123"}]}
    mock_service.users().messages().get.return_value.execute.return_value = {"id": "123",
                                                                             "payload": {"body": {"data": "test"}}}
    fetch_all_emails_and_save(mock_service, "test query")
    mock_service.users().messages().list.assert_called_once()
    mock_service.users().messages().get.assert_called_once()


def test_fetch_all_emails_and_save_empty(mock_service):
    mock_service.users().messages().list.return_value.execute.return_value = {"messages": []}
    fetch_all_emails_and_save(mock_service, "test query")
    mock_service.users().messages().list.assert_called_once()
    mock_service.users().messages().get.assert_not_called()