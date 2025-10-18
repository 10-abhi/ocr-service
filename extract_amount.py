import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Lazily configure the genai model to avoid heavy import-time activity and
# to allow deployments without the GEMINI API key (we'll skip LLM path then).
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

# models = genai.list_models()

# print("\nAvailable Gemini models for your API key:\n")
# for m in models:
#     print(f"- {m.name}")
    

def extract_amount_and_date(text: str):
    total_patterns = [
        r"(?:grand\s*total)[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:total\s*amount)[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:bill\s*total)[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:amount\s*payable)[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:total)[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)"
    ]

    total_amount = None
    for pat in total_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                total_amount = float(match.group(1).replace(",", ""))
                break
            except:
                continue
    
    date_regex = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
    extracted_date = None
    if date_regex:
        try:
            date_str = date_regex.group(1)
            for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    extracted_date = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                    break
                except:
                    continue
        except:
            extracted_date = None

    if total_amount is None:
        prompt = f"""
        You are a financial assistant.
        I extracted this receipt OCR text:
        ---
        {text}
        ---
        Please return a valid JSON with:
        - total_amount (as a number, without currency symbol, if not found return -1)
        - date (in YYYY-MM-DD format, if possible, else null)
        Return ONLY JSON, nothing else.
        """
    
    model = _get_genai_model()
    if total_amount is None and model is not None:
        try:
            response = model.generate_content(prompt)
            raw_output = response.candidates[0].content.parts[0].text.strip()
            json_str = re.search(r"\{.*\}", raw_output, re.DOTALL).group(0)
            data = json.loads(json_str)
            total_amount = data.get("total_amount", -1)
            if not extracted_date:
                extracted_date = data.get("date")
        except Exception as e:
            print("LLM error:", e)
    else:
        if total_amount is None and model is None:
            # No API key configured; skip LLM extraction.
            print("Gemini API key not configured; skipping LLM extraction")
    
    if total_amount in [None, -1]:
        total_amount = 0.0
    if not extracted_date:
        extracted_date = datetime.today().strftime("%Y-%m-%d")

    return {
        "total_amount": total_amount,
        "date": extracted_date
    }

