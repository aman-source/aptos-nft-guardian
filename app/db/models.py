# app/db/models.py

from sqlalchemy import ARRAY, Column, Integer, String, Float, DateTime, func
from app.db.database import Base

# Mint history table
class MintHistory(Base):
    __tablename__ = "mint_history"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    creator_address = Column(String, index=True)
    txn_hash = Column(String, index=True)
    image_url = Column(String)
    label = Column(String)
    score = Column(Float)
    embedding = Column(ARRAY(Float))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Stats table
class Stats(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, index=True)
    total_uploads = Column(Integer, default=0)
    total_valid_mints = Column(Integer, default=0)
    total_rejected = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
