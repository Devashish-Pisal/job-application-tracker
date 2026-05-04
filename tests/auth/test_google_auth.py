import pytest
from unittest.mock import patch, MagicMock
from src.auth.google_auth import get_credentials

@patch("src.auth.google_auth.Credentials.from_authorized_user_file")
@patch("src.auth.google_auth.InstalledAppFlow.from_client_secrets_file")
@patch("src.auth.google_auth.logger.info")
def test_get_credentials(mock_logger, mock_installed_app_flow, mock_creds):
    mock_creds.return_value = MagicMock(valid=True)
    mock_installed_app_flow.return_value.run_local_server.return_value = mock_creds
    creds = get_credentials()
    assert creds is not None
    mock_logger.assert_any_call("OAuth authentication complete")

@patch("src.auth.google_auth.Credentials.from_authorized_user_file")
@patch("src.auth.google_auth.InstalledAppFlow.from_client_secrets_file")
@patch("src.auth.google_auth.logger.info")
def test_get_credentials_with_invalid_creds(mock_logger, mock_installed_app_flow, mock_creds):
    mock_creds.return_value = MagicMock(valid=False, expired=True, refresh_token="dummy")
    mock_installed_app_flow.return_value.run_local_server.return_value = mock_creds
    creds = get_credentials()
    assert creds is not None
    mock_logger.assert_any_call("Refreshing token...")