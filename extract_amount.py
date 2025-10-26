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

