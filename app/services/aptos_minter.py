# app/services/aptos_minter.py

import os
import json
from dotenv import load_dotenv
from aptos_sdk.account import Account
from aptos_sdk.aptos_tokenv1_client import AptosTokenV1Client
from aptos_sdk.async_client import RestClient

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
        txn_hash = await token_client.create_collection(
            creator_account,
            COLLECTION_NAME,
            COLLECTION_DESCRIPTION,
            COLLECTION_URI
        )
        await rest_client.wait_for_transaction(txn_hash)
        print(f"Collection created! Txn: {txn_hash}")
        return txn_hash

async def mint_nft(receiver_address: str, name: str, description: str, image_url: str):
    print(f"Minting NFT to: {receiver_address}")

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
    print(f"NFT minted! Txn: {txn_hash}")
    return txn_hash
