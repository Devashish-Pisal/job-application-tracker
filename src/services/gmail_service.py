from googleapiclient.discovery import build
from src.config import GMAIL_QUERY
from loguru import logger


def get_gmail_service(creds):
    return build("gmail", "v1", credentials=creds)


def fetch_emails(service, max_results=3):
    results = service.users().messages().list(
        userId="me",
        q=GMAIL_QUERY,
        maxResults=max_results
    ).execute()
    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()
        emails.append(msg_data)
    return emails


# Pagination
def fetch_all_emails(service, query, max_per_page=100):
    emails = []
    request = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_per_page
    )
    while request is not None:
        response = request.execute()
        messages = response.get("messages", [])
        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full"
            ).execute()
            emails.append(msg_data)
        request = service.users().messages().list_next(request, response)
    # Sort email based on "internalDate" field, oldest email first
    emails.sort(
        key=lambda m: int(m.get("internalDate", 0)),
        reverse=False
    )
    logger.info(f"Total number of fetched email/s is/are {len(emails)}")
    return emails