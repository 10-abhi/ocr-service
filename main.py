from fastapi import FastAPI , File , UploadFile
import easyocr
import io
from PIL import Image , ImageEnhance , ImageFilter
import numpy as np
import joblib
from extract_amount import extract_amount_and_date

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
    
    #some image preprocessing
    image = image.convert("L")                   
    image = image.resize((image.width*3, image.height*3))
    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3)


    # Convert image to numpy array
    img_array = np.array(image)

    #run ocr
    result = reader.readtext(img_array)
    print("text before cleaning :")
    for bbox, text, conf in result:
        print(text, conf)
    print("text after cleaning :")
    raw_text = clean_text(" ".join([res[1] for res in result if res[2]>0.3]))

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