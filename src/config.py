import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]

GMAIL_QUERY = (
    '('
    # Core application signals
    '"application received" OR "thank you for applying" OR "application confirmation" OR '
    '"Ihre Bewerbung" OR "Bewerbung erhalten" OR "Deine Bewerbung" OR'
    # Interview / process stages
    '"interview" OR "interview invitation" OR "technical interview" OR '
    '"assessment" OR "online test" OR "coding challenge" OR '
    '"Vorstellungsgespräch" OR "Interview Einladung" OR "Einstellungstest" OR '
    # Offers
    '"job offer" OR "offer letter" OR "we are pleased to offer" OR '
    '"Angebot" OR "Stellenangebot" OR '
    # Rejections
    '"rejection" OR "we regret to inform" OR'
    '"Absage" OR "nicht berücksichtigen" OR '
    ') '
    # EXCLUDE job boards which are sending job recommendations
    '-from:glassdoor -from:xing -from:stepstone -from:indeed -from:linkedin' 
    # Exclude common job-alert phrasing
    '-("job alert" OR "recommended jobs" OR "jobs you may like" OR "You have a great chance for an interview for this job" OR "recommendation") '
    # Noise reduction
    '-("unsubscribe" OR "newsletter" OR "marketing" OR "sale" OR "discount" OR "Bank of Maharashtra" OR "Vikas Pisal" OR "Recharge successful" OR "LeetCode" OR "Github" OR "Telekom" OR "Ausländerbehörde")'
    # Time filter (YYYY/MM/DD) (after-inclusive) (before-exclusive)
    'after:2026/03/01'  # Adjust the date based on use case (backfilling, sync)
    'before:2026/03/05'
)


SHEET_NAME = "job_applications"
SHEET_ID = os.getenv("SHEET_ID")
SHEET_COLUMN_NAME_INDEX_MAPPING = { # Mapping of column names to its indices (don't modify the keys, only values (sheet indices) can be modified)
    "application-date": "A",
    "company-name": "B",
    "role": "C",
    "current-status": "D",
    "current-confidence": "E",
    "source": "F",
    "history": "G",
    "last-row-modification-date": "H",
    "message-ids": "J",
}

# GEMINI SETTING
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY"),
    "model": "gemini-3-flash",
    "max_retries": 5,
    "temp": 0.2,
    "consecutive_query_delay": 5, # in seconds
}
# Successfully used free gemini models (with RPD):
# Version 2.5: gemini-2.5-flash-lite (20), gemini-2.5-flash (20),

'''
# Old Gmail query 
GMAIL_QUERY = (
    '('
    # Core application signals
    '"application received" OR "thank you for applying" OR "application confirmation" OR '
    '"Ihre Bewerbung" OR "Bewerbung erhalten" OR "Deine Bewerbung" OR'
    # Interview / process stages
    '"interview" OR "interview invitation" OR "technical interview" OR '
    '"assessment" OR "online test" OR "coding challenge" OR '
    '"Vorstellungsgespräch" OR "Interview Einladung" OR "Einstellungstest" OR '
    # Offers
    '"job offer" OR "offer letter" OR "we are pleased to offer" OR '
    '"Angebot" OR "Stellenangebot" OR '
    # Rejections
    '"rejection" OR "we regret to inform" OR'
    '"Absage" OR "nicht berücksichtigen" OR '
    # Platforms / ATS systems (useful signals)
    '"StepStone" OR "Indeed" OR "Glassdoor" OR "XING" OR "LinkedIn"'
    ') '
    # Time filter (YYYY/MM/DD)
    'after:2026/04/25 '  # Adjust the date based on use case (backfilling, sync)
    # Noise reduction
    '-("unsubscribe" OR "newsletter" OR "marketing" OR "sale" OR "discount" OR "Bank of Maharashtra" OR "Vikas Pisal" OR "Recharge successful" OR "LeetCode" OR "Github" OR "Telekom" OR "Ausländerbehörde")'
)
'''