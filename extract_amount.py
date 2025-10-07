import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
api_key=os.getenv("gemini_api_key")
if not api_key:
    raise ValueError("Gemini API key not found")

genai.configure(api_key=os.getenv("gemini_api_key"))

model = genai.GenerativeModel("models/gemini-1.5-flash")
# print("avail models:" , genai.get_model());

def extract_amount_and_date(text: str):
    prompt = f"""
    You are a financial assistant. 
    I extracted this receipt ocr text:
    ---
    {text}
    ---
    Please return a valid JSON with:
    - total_amount (as a number, without currency symbol)
    - date (in YYYY-MM-DD format, if possible, else null)

    Example:
    {{
        "total_amount": 1250.50,
        "date": "2024-09-12"
    }}
    Return ONLY JSON , nothing else.
    """
    try:
        response = model.generate_content(prompt)
        raw_output = response.candidates[0].content.parts[0].text.strip()
        json_str = re.search(r"\{.*\}", raw_output, re.DOTALL).group(0)
        data = json.loads(json_str)
        total_amount = data.get("total_amount")
        date = data.get("date")
        if not date:
            date = datetime.today().strftime("%Y-%m-%d")

        return {
            "total_amount": total_amount,
            "date": date
        }
    except Exception as e:
        return {"total_amount": None, "date": datetime.today().strftime("%Y-%m-%d") , "error": str(e)}
