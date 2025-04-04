# app/services/image_validator.py

from fastapi import UploadFile
from PIL import Image
import io
from app.services.ml_validator import validate_with_clip
from app.utils.file_utils import upload_to_imgbb
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Stats
from scipy.spatial.distance import cosine
from sqlalchemy import select
from app.db.models import MintHistory


async def is_duplicate(embedding, db, threshold=0.8):
    query = select(MintHistory.embedding).where(MintHistory.embedding != None)
    result = await db.execute(query)
    existing_embeddings = result.scalars().all()

    # Compare with each embedding
    for existing in existing_embeddings:
        if existing is None:
            continue
        similarity = 1 - cosine(existing, embedding)
        if similarity > threshold:
            return True

    return False

async def validate_image(file: UploadFile, db: AsyncSession):
    stats = None
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        stats = await db.get(Stats, 1)
        stats.total_uploads += 1
        await db.commit()
        result = validate_with_clip(image)

        image_url = None
        
        if await is_duplicate(result["embedding"], db):
            return {
                "status": "invalid",
                "reason": "Duplicate or near-duplicate image detected.",
                "image_url": None
            }
        if result["is_valid"]:
            file.file.seek(0)
            image_url = await upload_to_imgbb(file)
        else:
            stats.total_rejected += 1
            await db.commit()
        return {
            "status": "valid" if result["is_valid"] else "invalid",
            "image_url": image_url,
            "label": result["label"],
            "score": result["score"],
            "embedding": result["embedding"],
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
