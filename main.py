from fastapi import FastAPI , File , UploadFile
import pytesseract
from PIL import Image , ImageEnhance , ImageFilter
import numpy as np
import joblib
import os
import logging
from extract_amount import extract_amount_and_date
# from google.cloud import vision
import io
# import os
# import requests

app = FastAPI()
# client = vision.ImageAnnotatorClient()

# import google.generativeai as genai
# reader = easyocr.Reader(['en'] , gpu=False);

pipeline = joblib.load("category_pipeline.pkl")

# env-driven logging (default to prod warning)
_DEV_MODE = os.getenv("EXTRACT_DEBUG", "0").lower() in ("1", "true", "yes")
logging.basicConfig(
    level=logging.DEBUG if _DEV_MODE else logging.WARNING,
    format=("%(levelname)s %(name)s: %(message)s" if _DEV_MODE else "%(asctime)s %(levelname)s %(name)s: %(message)s"),
)
logger = logging.getLogger(__name__)

# api_key = os.getenv("gemini_api_key")
# api_key = os.getenv("ocrspaceapikey")

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

def extract_text(image_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        logger.exception("Failed to open image")
        return ""
    
    image = image.convert("L") 
    image = image.resize((image.width * 3, image.height * 3))
    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3)

    image = image.point(lambda x: 0 if x < 128 else 255, '1')
    text = pytesseract.image_to_string(image, lang="eng")
    return text.strip()


def clean_text(text):
    text = text.replace("\n", " ").strip()
    text = " ".join(text.split()) 
    return text

#gemini pro
# genai.configure(api_key=api_key)
# model = genai.GenerativeModel("models/gemini-1.5-flash")

# print(" Available models: ", genai.list_models())

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # image = Image.open(io.BytesIO(contents))
        raw_text = extract_text(contents)
    except Exception:
        return {"error":"Invalid image file"}
    
    # buf = io.BytesIO()
    # image.save(buf , format="PNG")
    # img_bytes = buf.getvalue()


    # Convert image to numpy array
    # img_array = np.array(image)
    # raw_text = extract_text(img_array)
    raw_text = clean_text(raw_text)
    logger.debug("the raw text is %s", raw_text)

    #run ocr
    # result = reader.readtext(img_array)
    # print("text before cleaning :")
    # for bbox, text, conf in result:
    #     print(text, conf)
    # print("text after cleaning :")
    # raw_text = clean_text(" ".join([res[1] for res in result if res[2]>0.5]))

    #prompting gemini to structure data
    # print("Available models:", genai.list_models())

    # prompt = f"""
    # You are a financial assistant. I extracted this receipt text:
    # ---
    # {raw_text}
    # ---
    # Return structured JSON with these fields:
    # - merchant
    # - date
    # - items (list of {{"name":..., "price":...}})
    # - currency
    # Only return valid JSON, no explanations.
    # """
    # try:
    #     response = model.generate_content(prompt)
    #     structured = getattr(response, "text", str(response))
    # except Exception as e:
    #     return {"error": f"Gemini API failed: {str(e)}"}
    
    # return {
    #     "raw_text": raw_text,
    #     "structured": structured
    # }
    predicted_category = pipeline.predict([raw_text])[0]
    extracted = extract_amount_and_date(raw_text)

    logger.debug("predicted_category=%s", predicted_category)
    logger.debug("extracted total=%s date=%s", extracted.get("total_amount"), extracted.get("date"))
    
    return {
        "total_amount": extracted.get("total_amount"),
        "predicted_category": predicted_category,
        "date": extracted.get("date"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=_DEV_MODE,
        log_level="debug" if _DEV_MODE else "info",
    )