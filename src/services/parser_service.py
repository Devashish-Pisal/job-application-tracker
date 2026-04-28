from src.utils.helpers import decode_base64, clean_html
from email.utils import parsedate_to_datetime


def parse_email(msg):
    header_data = extract_headers(msg)
    body = get_body(msg["payload"])
    source = detect_source(header_data["from_name"], header_data["subject"], body)
    return {
        "date": header_data["date"],
        "sender_name": header_data["from_name"],
        "sender_email": header_data["from_email"],
        "subject": header_data["subject"],
        "source": source,
        "body": body,
        "id": header_data["id"],
    }


def extract_headers(email):
    headers = email.get("payload", {}).get("headers", [])
    data = {
        "id": email['id'],
        "date": None,
        "from_name": None,
        "from_email": None,
        "subject": None,
    }
    for h in headers:
        name = h['name']
        value = h['value']
        if name == 'From':
            if "<" in value:
                data["from_name"] = value.split("<")[0].strip().strip('"')
                data["from_email"] = value.split("<")[1].replace(">", "").strip()
            else:
                data["from_email"] = value

        elif name == 'Subject':
            data["subject"] = value
        elif name == 'Date':
            dt = parsedate_to_datetime(value)
            data["date"] = dt.strftime("%Y-%m-%d")
    return data


def get_body(payload):
    """
    Recursively extract email body.
    Prefer text/plain, fallback to cleaned HTML.
    """
    if payload.get("mimeType") == "text/plain":
        data = payload['body'].get('data')
        if data:
            return decode_base64(data)
    if payload.get("mimeType") == "text/html":
        data = payload['body'].get('data')
        if data:
            html = decode_base64(data)
            return clean_html(html)
    # If multipart → recurse
    if 'parts' in payload:
        for part in payload['parts']:
            result = get_body(part)
            if result:
                return result
    return ""


def detect_source(sender, subject, body):
    text = (sender + subject + body).lower()
    if "stepstone" in text:
        return "StepStone"
    if "indeed" in text:
        return "Indeed"
    if "glassdoor" in text:
        return "Glassdoor"
    if "xing" in text:
        return "XING"
    return "Company Website / Other"

