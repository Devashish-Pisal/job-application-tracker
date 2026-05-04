import pytest
from src.services.parser_service import parse_email

def test_parse_email():
    email_data = {
        "payload": {
            "headers": [
                {"name": "From", "value": "test@example.com"},
                {"name": "Subject", "value": "Test Subject"},
                {"name": "Date", "value": "2023-05-04T00:00:00Z"}
            ],
            "body": {"data": "test data"}
        },
        "id": "1"
    }
    parsed = parse_email(email_data)
    assert parsed["sender_email"] == "test@example.com"
    assert parsed["subject"] == "Test Subject"
    assert parsed["body"] == "test data"

def test_parse_email_with_missing_subject():
    email_data = {
        "payload": {
            "headers": [
                {"name": "From", "value": "test@example.com"},
                {"name": "Date", "value": "2023-05-04T00:00:00Z"}
            ],
            "body": {"data": "test data"}
        },
        "id": "1"
    }
    parsed = parse_email(email_data)
    assert parsed["subject"] is None