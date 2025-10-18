from fastapi import FastAPI , File , UploadFile
import easyocr
import io
from PIL import Image , ImageEnhance , ImageFilter
import numpy as np
import joblib
from extract_amount import extract_amount_and_date

app = FastAPI()

# Lazy singletons to avoid heavy import-time initialization which can
# cause high memory usage on small deployment instances.
_reader = None
_pipeline = None

def get_reader():
    """Lazily create and return the easyocr.Reader instance."""
    global _reader
    if _reader is None:
        # keep gpu=False on platforms without CUDA
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader

def get_pipeline():
    """Lazily load and return the sklearn pipeline from disk."""
    global _pipeline
    if _pipeline is None:
        import os
        path = "category_pipeline.pkl"
        if not os.path.exists(path):
            # Fail early with a clear error if the model file is missing
            raise FileNotFoundError(f"{path} not found")
        _pipeline = joblib.load(path)
    return _pipeline

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
    
    # some image preprocessing
    # convert to grayscale
    image = image.convert("L")

    # Cap dimensions to avoid huge memory usage on small instances.
    # Do NOT upscale images (that multiplies pixel count massively).
    # Lowered max dimension to reduce memory footprint on 512MB instances.
    max_dim = 640
    w, h = image.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        image = image.resize((new_w, new_h), resample=Image.LANCZOS)

    # apply a mild sharpen and moderate contrast only
    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)


    # Convert image to numpy array for OCR and run OCR
    img_array = np.array(image)
    result = get_reader().readtext(img_array)

    # Free the numpy array ASAP to lower peak memory usage
    try:
        del img_array
    except Exception:
        pass
    import gc
    gc.collect()
    print("text before cleaning :")
    for bbox, text, conf in result:
        print(text, conf)
    print("text after cleaning :")
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
    # Optionally skip loading the classifier on low-memory instances. Set
    # environment variable USE_CLASSIFIER=0 to disable.
    import os
    use_classifier = os.getenv("USE_CLASSIFIER", "1") not in ("0", "false", "False")
    predicted_category = None
    if use_classifier:
        predicted_category = get_pipeline().predict([raw_text])[0]
    else:
        predicted_category = "unknown"
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