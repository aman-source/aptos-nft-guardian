
from fastapi import APIRouter, UploadFile, File, Form
from app.services.image_validator import validate_image
from app.services.aptos_minter import mint_nft


router = APIRouter()

@router.post("/validate-image")
async def validate(file: UploadFile = File(...)):
    result = await validate_image(file)
    return result


@router.post("/mint-nft")
async def mint(
    receiver_address: str = Form(...),
    image_url: str = Form(...),
    name: str = Form(...),
    description: str = Form(...)
):
    try:
        txn_hash = await mint_nft(receiver_address, name, description, image_url)
        return {
            "status": "success",
            "transaction_hash": txn_hash,
            "explorer_url": f"https://explorer.aptoslabs.com/txn/{txn_hash}?network=devnet"
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }