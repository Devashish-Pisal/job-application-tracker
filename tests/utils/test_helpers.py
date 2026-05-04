import pytest
from src.utils.helpers import decode_base64, clean_html

def test_decode_base64():
    encoded = "dGVzdA=="
    decoded = decode_base64(encoded)
    assert decoded == "test"

def test_clean_html():
    html = "<html><body><p>Test</p></body></html>"
    clean = clean_html(html)
    assert clean == "Test"

def test_clean_html_with_empty_string():
    html = ""
    clean = clean_html(html)
    assert clean == ""