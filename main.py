from fastapi import FastAPI , File , UploadFile
import pytesseract
from PIL import Image , ImageOps , ImageFilter
import io

app = FastAPI()

@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        return {"error": "Invalid image file"}

    #convert bytes to pil image
    image = Image.open(io.BytesIO(contents))
    #converting to grayscale
    image = image.convert("L")
    image = image.point(lambda x: 0 if x<140 else 255 ,'1')

    #small font to hard 
    new_size = (image.width * 2 , image.height * 2)
    image = image.resize(new_size)
    
    #sharpen
    image = image.filter(ImageFilter.SHARPEN)

    #run ocr 
    text = pytesseract.image_to_string(image, config="--oem 3 --psm 3").strip()
    print("text", text);

    return {"extracted_text" : text}

