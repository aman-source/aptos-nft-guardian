
from fastapi import APIRouter, UploadFile, File, Form
from app.services.image_validator import validate_image
from app.services.aptos_minter import mint_nft
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select, text
from app.db.database import get_db
from app.db.models import MintHistory, Stats


router = APIRouter()

@router.post("/validate-image")
async def validate(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    result = await validate_image(file,db)
    return result


@router.post("/mint-nft")
async def mint(
    receiver_address: str = Form(...),
    image_url: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    label: str = Form(...),
    score: float = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        txn_hash = await mint_nft(receiver_address, name, description, image_url, label, score, db)
        return {
            "status": "success",
            "transaction_hash": txn_hash,
            "explorer_url": f"https://explorer.aptoslabs.com/txn/{txn_hash}?network=devnet"
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}
    
    
@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    stats = await db.get(Stats, 1)

    if not stats:
        return {
            "total_uploads": 0,
            "total_valid_mints": 0,
            "total_rejected": 0,
            "average_score": 0.0
        }

    # Avoid division by zero
    average_score = (
        stats.total_score / stats.total_valid_mints if stats.total_valid_mints > 0 else 0.0
    )

    return {
        "total_uploads": stats.total_uploads,
        "total_valid_mints": stats.total_valid_mints,
        "total_rejected": stats.total_rejected,
        "average_score": average_score
    }

        
@router.get("/mint-history")
async def get_mint_history(db: AsyncSession = Depends(get_db)):
    query = select(MintHistory).order_by(desc(MintHistory.created_at))
    result = await db.execute(query)
    mints = result.scalars().all()

    history = [
        {
            "name": mint.name,
            "description": mint.description,
            "creator_address": mint.creator_address,
            "txn_hash": mint.txn_hash,
            "image_url": mint.image_url,
            "label": mint.label,
            "score": mint.score,
            "created_at": mint.created_at.isoformat()
        }
        for mint in mints
    ]

    return {"mint_history": history}


@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    query = (
        select(
            MintHistory.creator_address,
            func.count(MintHistory.id).label("mint_count")
        )
        .group_by(MintHistory.creator_address)
        .order_by(desc("mint_count"))
    )

    result = await db.execute(query)
    leaderboard = [
        {
            "creator_address": row.creator_address,
            "mint_count": row.mint_count
        }
        for row in result
    ]

    return {"leaderboard": leaderboard}

