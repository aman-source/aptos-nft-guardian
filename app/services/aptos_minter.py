# app/services/aptos_minter.py

import os
import json
from dotenv import load_dotenv
from aptos_sdk.account import Account
from aptos_sdk.aptos_tokenv1_client import AptosTokenV1Client
from aptos_sdk.async_client import RestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import Stats, MintHistory


load_dotenv()

# Load env variables
NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Setup clients
rest_client = RestClient(NODE_URL)
token_client = AptosTokenV1Client(rest_client)

# Load backend minter account
creator_account = Account.load_key(PRIVATE_KEY)

# Collection metadata
COLLECTION_NAME = "Aptos Guardian Collection"
COLLECTION_DESCRIPTION = "AI-verified NFT collection"
COLLECTION_URI = "https://aptos.dev"

async def ensure_collection_exists():
    try:
        collection_data = await token_client.get_collection(
            creator_account.address(),
            COLLECTION_NAME
        )
        print(f"Collection already exists: {collection_data['collection_name']}")
        return collection_data

    except Exception as e:
        print("Collection does not exist. Creating new collection...")
        try:
            txn_hash = await token_client.create_collection(
                creator_account,
                COLLECTION_NAME,
                COLLECTION_DESCRIPTION,
                COLLECTION_URI
            )
            await rest_client.wait_for_transaction(txn_hash)
            print(f"Collection created! Txn: {txn_hash}")
            return txn_hash
        except Exception as create_error:
            if "ECOLLECTION_ALREADY_EXISTS" in str(create_error):
                print("Collection already exists, skipping creation.")
                return {"status": "already_exists"}
            else:
                raise create_error


async def mint_nft(
    receiver_address: str,
    name: str,
    description: str,
    image_url: str,
    label: str,
    score: float,
    embedding: list,
    db: AsyncSession
) -> str:
    print(f"Minting NFT to: {receiver_address}")

    try:
        txn_hash = await token_client.create_token(
            creator_account,
            COLLECTION_NAME,
            name,
            description,
            1,  # supply
            image_url,
            0   # royalty
        )
        await rest_client.wait_for_transaction(txn_hash)
        print(f"NFT minted successfully. Transaction hash: {txn_hash}")

        stats = await db.get(Stats, 1)
        if stats:
            stats.total_valid_mints += 1
            stats.total_score += score
        else:
            print("Stats record not found in database.")

        mint_entry = MintHistory(
            name=name,
            description=description,
            creator_address=receiver_address,
            txn_hash=txn_hash,
            image_url=image_url,
            label=label,
            score=score,
            embedding = embedding
        )
        db.add(mint_entry)

        await db.commit()

        return txn_hash

    except Exception as e:
        print(f"Error during NFT minting: {str(e)}")
        await db.rollback()
        raise e
