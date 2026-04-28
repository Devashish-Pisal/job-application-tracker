import json
import time
import random
from loguru import logger
from google import genai
from src.config import GEMINI_CONFIG

def get_gemini_client():
    client = genai.Client(api_key=GEMINI_CONFIG["api_key"])
    return client


JOB_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "normalized_company_name": {"type": "STRING"},
        "normalized_job_title": {"type": "STRING"},
        "email_type": {
            "type": "STRING",
            "enum": ["APPLIED", "TEST_INVITATION", "INTERVIEW", "OFFER", "REJECTION", "OTHER"]
        },
        "confidence": {"type": "NUMBER"}
    },
    "required": [
        "normalized_company_name",
        "normalized_job_title",
        "email_type",
        "confidence"
    ]
}

def extract_job_info(client, system_prompt, email_data, model="gemini-2.5-flash", max_retries=3, temp=0.2):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[
                    system_prompt,
                    f"Input Email data:\n{email_data}"
                ],
                config={
                    "temperature": temp,
                    "response_mime_type": "application/json",
                    "response_schema": JOB_SCHEMA
                }
            )
            if isinstance(response.parsed, dict):
                return response.parsed
            else:
                return json.loads(response.text)
        except Exception as e:
            last_error = e
            wait = (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"[Retry {attempt}] Error: {e} | waiting {wait:.2f}s")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {max_retries} retries. Last error: {last_error}")