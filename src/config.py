import os
from dotenv import load_dotenv
load_dotenv()


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]


# https://support.google.com/mail/answer/7190?hl=en (gmail query documentation)
GMAIL_BACKFILL_QUERY = (
    # Get messages only from the inbox
    'in:inbox'
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
    # Remove matching users reply's 
    '-in:sent -from:me'
    # Exclude common job-alert phrasing
    '-("job alert" OR "recommended jobs" OR "jobs you may like" OR "You have a great chance for an interview for this job" OR "recommendation") '
    # Noise reduction
    '-("unsubscribe" OR "newsletter" OR "marketing" OR "sale" OR "discount" OR "Bank of Maharashtra" OR "Vikas Pisal" OR "Recharge successful" OR "LeetCode" OR "Github" OR "Telekom" OR "Ausländerbehörde")'
    # Time filter (YYYY/MM/DD) (after-inclusive) (before-exclusive)
    'after:2026/02/01 '  # Adjust the date based on the backfilling time period
    'before:2026/05/05 '
)

# Total 196 emails in gmail app
# Fetched 203 emails via API

# To execute in gmail app:
'''
(in:inbox "application received" OR "thank you for applying" OR "application confirmation" OR "Ihre Bewerbung" OR "Bewerbung erhalten" OR "Deine Bewerbung" OR "interview" OR "interview invitation" OR "technical interview" OR "assessment" OR "online test" OR "coding challenge" OR "Vorstellungsgespräch" OR "Interview Einladung" OR "Einstellungstest" OR "job offer" OR "offer letter" OR "we are pleased to offer" OR "Angebot" OR "Stellenangebot" OR "rejection" OR "we regret to inform" OR "Absage" OR "nicht berücksichtigen") -from:glassdoor -from:xing -from:stepstone -from:indeed -from:linkedin -in:sent -from:me -("job alert" OR "recommended jobs" OR "jobs you may like" OR "You have a great chance for an interview for this job" OR "recommendation") -("unsubscribe" OR "newsletter" OR "marketing" OR "sale" OR "discount" OR "Bank of Maharashtra" OR "Vikas Pisal" OR "Recharge successful" OR "LeetCode" OR "Github" OR "Telekom" OR "Ausländerbehörde") after:2026/02/01 before:2026/05/05
'''

GMAIL_SYNC_QUERY = (
    'label:job-application '
    # Adjust the following time periods based on sync frequency
    # 'after:2026/05/01 ' # inclusive (YYYY/MM/DD)
    # 'before:2026/05/04 ' # exclusive (YYYY/MM/DD)
    # 'newer_than:1d ' # for daily sync setup
)



SHEET_NAME = "job_applications"
SHEET_ID = os.getenv("SHEET_ID")
# Do not edit this dict, because currently it is hardcoded in codebase
SHEET_COLUMN_NAME_INDEX_MAPPING = {
    "application-date": "A", # idx = 0
    "company-name": "B", # idx = 1
    "role": "C",  # idx = 2
    "current-status": "D",  # idx = 3
    "current-confidence": "E",  # idx = 4
    "status-flow": "F",  # idx = 5
    "history": "G",  # idx = 6
    "last-row-modification-date": "H",  # idx = 7
    "message-ids": "I",  # idx = 8
}



# GEMINI SETTING
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY"),
    "model": "gemini-3.1-flash-lite-preview",
    "max_retries": 5,
    "temp": 0.2,
    "consecutive_query_delay": 5, # in seconds
}
# Successfully tested free gemini models (with RPM, TPM, RPD):
# Version 2.5: gemini-2.5-flash (5, 250k, 20), gemini-2.5-flash-lite (10, 250k, 20),
# Version 3: gemini-3-flash-preview (5, 250k, 20), gemini-3.1-flash-lite-preview (15, 250k, 500),
