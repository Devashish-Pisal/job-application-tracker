import json
import time
import random
from loguru import logger
from google import genai
from src.config import GEMINI_CONFIG
from google.api_core.exceptions import (
    ResourceExhausted,
    PermissionDenied,
    InvalidArgument,
)

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

def extract_job_info(client, system_prompt, email_data, models, max_retries=3, temp=0.1):
    last_error = None
    for model in models:
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
            except ResourceExhausted as e:
                logger.warning(f"'{model}' models rate limit is reached. Use another model.")
                break
            except Exception as e:
                last_error = e
                wait = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"['{model}' retry {attempt}] Error: {e} | waiting {wait:.2f}s")
                time.sleep(wait)
        logger.warning(f"'{model}' failed after {max_retries} retries. Last error: {last_error}")
    raise RuntimeError(f"All models in list {models} failed")


"""
# Gemini Error Structure 
['gemini-3-flash-preview' retry 1] Error: 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5, model: gemini-3-flash\nPlease retry in 36.975663988s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier', 'quotaDimensions': {'model': 'gemini-3-flash', 'location': 'global'}, 'quotaValue': '5'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '36s'}]}} | waiting 2.50s
"""