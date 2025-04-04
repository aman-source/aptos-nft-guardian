# app/services/image_validator.py

from fastapi import UploadFile
from PIL import Image
import io
from app.services.ml_validator import validate_with_clip
from app.utils.file_utils import upload_to_imgbb

async def validate_image(file: UploadFile):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        result = validate_with_clip(image)

        image_url = None
        if result["is_valid"]:
            file.file.seek(0)
            image_url = await upload_to_imgbb(file)

        return {
            "status": "valid" if result["is_valid"] else "invalid",
            "image_url": image_url,
            "label": result["label"],
            "score": result["score"],
            "reason": f"Classified as '{result['label']}' with score {result['score']}"
        }

    except Exception as e:
        return {
            "status": "invalid",
            "image_url": None,
            "reason": f"Validation failed: {str(e)}"
        }
