import json
from loguru import logger
from googleapiclient.discovery import build
from path_config import FETCHED_EMAILS



def get_gmail_service(creds):
    return build("gmail", "v1", credentials=creds)


# With Pagination
def fetch_all_emails_and_save(service, query, max_per_page=100):
    logger.info("Fetching and Saving Emails...")
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
            email_id = msg_data['id']
            with open(str(FETCHED_EMAILS) + f"/{email_id}.json", "w", encoding="utf-8") as file:
                file.write(json.dumps(msg_data, indent=2, ensure_ascii=False))
                logger.info(f"{email_id}.json file saved!")
        request = service.users().messages().list_next(request, response)
    # Sort email based on "internalDate" field, oldest email first
    emails.sort(
        key=lambda m: int(m.get("internalDate", 0)),
        reverse=False
    )
    logger.info(f"Total number of fetched email/s is/are {len(emails)} and are stored in folder '{str(FETCHED_EMAILS)}'")



'''
# Without pagination
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
'''