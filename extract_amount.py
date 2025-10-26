import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime
try:
    from dateutil import parser as _dateutil_parser
except Exception:
    _dateutil_parser = None

load_dotenv()

_genai_model = None
def _get_genai_model():
    global _genai_model
    if _genai_model is not None:
        return _genai_model
    api_key = os.getenv("gemini_api_key")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    _genai_model = genai.GenerativeModel("models/gemini-2.5-flash")
    return _genai_model


def extract_amount_and_date(text: str):
    # preprocessing helpers to make ocr output cleaner for the llm
    def _clean_text(s: str) -> str:
        s = re.sub(r"[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]+", "", s)
        s = s.replace('\r\n', '\n').replace('\r', '\n')
        s = re.sub(r"\n{2,}", "\n", s)
        lines = [re.sub(r"\s+", " ", ln).strip() for ln in s.split('\n')]
        return "\n".join([ln for ln in lines if ln])