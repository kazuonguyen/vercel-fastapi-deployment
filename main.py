from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from pathlib import Path
import uvicorn
import base64

app = FastAPI()

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

class ImageInfo(BaseModel):
    filename: str
    base64: str

class ImageListResponse(BaseModel):
    images: List[ImageInfo]

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

@app.get("/images", response_model=ImageListResponse)
def list_images():
    image_files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                image_files.append(ImageInfo(filename=filename, base64=encoded_string))
    return ImageListResponse(images=image_files)

@app.get("/download/{filename}")
def download_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return {"filename": filename, "base64": encoded_string}

if __name__ == "__main__":
    

    uvicorn.run(app, host="localhost", port=8000)
