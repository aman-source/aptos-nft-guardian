# app/utils/file_utils.py

import os
import base64
import httpx
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

async def upload_to_imgbb(file: UploadFile) -> str:
    # Read and encode file to base64
    contents = await file.read()
    b64_image = base64.b64encode(contents).decode("utf-8")

    params = {
        "key": IMGBB_API_KEY,
        "image": b64_image,
        "expiration": '3600'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(IMGBB_UPLOAD_URL, data=params)
        result = response.json()

        if response.status_code == 200 and result["success"]:
            return result["data"]["url"]
        else:
            raise Exception("Failed to upload to imgbb")
