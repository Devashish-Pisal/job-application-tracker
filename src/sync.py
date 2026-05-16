from loguru import logger
from src.pipeline import pipeline
from path_config import FETCHED_EMAILS
from src.config import GMAIL_SYNC_QUERY
from src.utils.helpers import get_gmail_and_sheet_services
from src.services.gmail_service import fetch_all_emails_and_save
from src.utils.helpers import setup_logger, create_necessary_paths


if __name__ == '__main__':
    create_necessary_paths()
    setup_logger()
    logger.info("=" * 120)
    logger.info("TASK: SYNC")
    logger.info("=" * 120)
    if not any(FETCHED_EMAILS.iterdir()):
        gmail_service, _  = get_gmail_and_sheet_services()
        fetch_all_emails_and_save(gmail_service, GMAIL_SYNC_QUERY)
    pipeline()