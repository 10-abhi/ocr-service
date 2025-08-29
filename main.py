from fastapi import FastAPI , File , UploadFile
import easyocr
import io
from PIL import Image
import numpy as np

app = FastAPI()

#load model once (important for speed!)
reader = easyocr.Reader(['en','hi'])

@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        return {"error":"Invalid image file"}
    
    # Convert PIL image to numpy array
    img_array = np.array(image)
    result = reader.readtext(img_array)
    
    extracted_data = []
    for bbox, text, conf in result:
        status = "low_confidence" if conf < 0.5 else "high_confidence"
        extracted_data.append({
            "text": text,
            "status": status
        })
    print(extracted_data)
    return {"results": extracted_data}
