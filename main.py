from fastapi import FastAPI , File , UploadFile
import easyocr
import io
from PIL import Image , ImageEnhance , ImageFilter
import numpy as np
import joblib
from extract_amount import extract_amount_and_date
from google.cloud import vision
import io

app = FastAPI()
client = vision.ImageAnnotatorClient()

def extract_text(image_bytes : bytes):
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description.strip()
    return ""


# import google.generativeai as genai
reader = easyocr.Reader(['en'] , gpu=False);
pipeline = joblib.load("category_pipeline.pkl");

# api_key = os.getenv("gemini_api_key")
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
        image = Image.open(io.BytesIO(contents))
    except Exception:
        return {"error":"Invalid image file"}
    
    #some image preprocessing
    image = image.convert("L")                   
    image = image.resize((image.width*3, image.height*3))
    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3)

    buf = io.BytesIO()
    image.save(buf , format="PNG")
    img_bytes = buf.getvalue()


    # Convert image to numpy array
    # img_array = np.array(image)
    # raw_text = extract_text(img_array)
    raw_text = extract_text(img_bytes)
    raw_text = clean_text(raw_text)

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
    predicted_category = pipeline.predict([raw_text])[0];
    extracted = extract_amount_and_date(raw_text)

    print("raw_text" , raw_text);
    print( "predicted_category", predicted_category)
    print("total_amount",extracted["total_amount"])
    print("ext date" , extracted["date"])
    return {
        # "raw_text": raw_text,
        "total_amount":extracted["total_amount"],
        "predicted_category": predicted_category,
        "date":extracted["date"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)