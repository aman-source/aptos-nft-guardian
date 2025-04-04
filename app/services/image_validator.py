# app/services/image_validator.py

from fastapi import UploadFile
from PIL import Image
import io
from app.services.ml_validator import validate_with_clip
from app.utils.file_utils import upload_to_imgbb
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.database import get_db
from app.db.models import Stats


async def validate_image(file: UploadFile, db: AsyncSession):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        stats = await db.get(Stats, 1)
        stats.total_uploads += 1
        await db.commit()
        result = validate_with_clip(image)

        image_url = None
        if result["is_valid"]:
            file.file.seek(0)
            image_url = await upload_to_imgbb(file)
            stats.total_uploads += 1
            await db.commit()
        else:
            stats.total_rejected += 1
            await db.commit()
        return {
            "status": "valid" if result["is_valid"] else "invalid",
            "image_url": image_url,
            "label": result["label"],
            "score": result["score"],
            "reason": f"Classified as '{result['label']}' with score {result['score']}"
        }

    except Exception as e:
        if stats:
            stats.total_rejected += 1
            await db.commit()
        return {
            "status": "invalid",
            "image_url": None,
            "reason": f"Validation failed: {str(e)}"
        }
