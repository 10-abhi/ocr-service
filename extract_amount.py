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

    def _normalize_common_ocr_errors(s: str) -> str:
        #fixing common ocr confusions in numeric contexts
        #replace letter O with zero when surrounded by digits
        s = re.sub(r"(?<=\d)O(?=\d)", "0", s)
        s = re.sub(r"(?<=\d)l(?=\d)", "1", s)
        s = re.sub(r"(?<=\d)S(?=\d)", "5", s)
        return s


    def _candidate_lines(s: str):
        #returns lines that likely contain amounts or dates or keywords
        lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
        keywords = ["total", "amount", "balance", "subtotal", "grand", "bill", "net", "due"]
        cand = []
        for i, ln in enumerate(lines):
            lower = ln.lower()
            # include lines with money like patterns or keywords
            if any(k in lower for k in keywords) or re.search(r"\d[\d,]*[\.]?\d{0,2}", ln):
                cand.append((i, ln))
        # include few surrounding lines for context
        indexes = set()
        for i, _ in cand:
            for j in range(max(0, i - 2), i + 3):
                indexes.add(j)
        result = [lines[i] for i in sorted(indexes) if 0 <= i < len(lines)]
        return result


    # detect likely phone numbers or addresses to avoid picking them as totals
    def _looks_like_phone_or_address(s: str) -> bool:
        low = s.lower()
        # phone patterns
        if re.search(r"\b(?:\+\d{1,3}[ -]?)?(?:\d{2,4}[ -]?){2,}\d{2,4}\b", s):
            return True
        # common address keywords
        if any(w in low for w in ["street", "st", "road", "rd", "drive", "dr", "lane", "ln", "avenue", "ave", "suite", "ste", "floor", "unit", "block", "p.o.", "postal", "pin", "zip", "tin", "gstin"]):
            return True
        return False


    