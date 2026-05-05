import os
from loguru import logger
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from path_config import CREDENTIALS_FILE_PATH, TOKEN_FILE_PATH
from src.config import SCOPES


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing token...")
            creds.refresh(Request())
        else:
            logger.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE_PATH,
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE_PATH, "w") as token:
            token.write(creds.to_json())
        logger.success("OAuth authentication complete")
    return creds