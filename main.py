from fastapi import FastAPI , File , UploadFile
import easyocr
import io
from PIL import Image
import numpy as np
import joblib
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# import google.generativeai as genai
reader = easyocr.Reader(['en']);
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
async def extract_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        return {"error":"Invalid image file"}
    
    # Convert PIL image to numpy array
    img_array = np.array(image)

    #run ocr
    result = reader.readtext(img_array)
    raw_text = clean_text(" ".join([res[1] for res in result if res[2]>0.5]))

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
    print("raw_text" , raw_text);
    print( "predicted_category", predicted_category)
    return {
        "raw_text": raw_text,
        "predicted_category": predicted_category
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)