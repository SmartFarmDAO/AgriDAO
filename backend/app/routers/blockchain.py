"""Blockchain transparency API endpoints."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import json

router = APIRouter()


class Transaction(BaseModel):
    id: str | None = None
    type: str
    amount: float
    from_address: str
    to_address: str
    timestamp: str | None = None
    hash: str | None = None
    status: str = "pending"


class BlockchainStats(BaseModel):
    total_transactions: int
    total_value: float
    active_users: int
    last_block_time: str


# In-memory storage (replace with database in production)
transactions_db: List[Transaction] = []


def generate_hash(data: dict) -> str:
    """Generate a simple hash for transaction."""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


@router.get("/transactions", response_model=List[Transaction])
def get_transactions(limit: int = 20) -> List[Transaction]:
    """Get recent blockchain transactions."""
    return transactions_db[-limit:]


@router.post("/transactions", response_model=Transaction, status_code=201)
def create_transaction(tx: Transaction) -> Transaction:
    """Create a new blockchain transaction."""
    tx.id = str(len(transactions_db) + 1)
    tx.timestamp = datetime.utcnow().isoformat()
    tx.hash = "0x" + generate_hash({
        "type": tx.type,
        "amount": tx.amount,
        "from": tx.from_address,
        "to": tx.to_address,
        "timestamp": tx.timestamp,
    })
    tx.status = "confirmed"
    
    transactions_db.append(tx)
    return tx


@router.get("/stats", response_model=BlockchainStats)
def get_blockchain_stats() -> BlockchainStats:
    """Get blockchain statistics."""
    total_value = sum(tx.amount for tx in transactions_db)
    unique_addresses = set()
    for tx in transactions_db:
        unique_addresses.add(tx.from_address)
        unique_addresses.add(tx.to_address)
    
    return BlockchainStats(
        total_transactions=len(transactions_db),
        total_value=total_value,
        active_users=len(unique_addresses),
        last_block_time=transactions_db[-1].timestamp if transactions_db else datetime.utcnow().isoformat(),
    )


@router.get("/transactions/{tx_hash}")
def get_transaction(tx_hash: str) -> Transaction:
    """Get transaction by hash."""
    for tx in transactions_db:
        if tx.hash == tx_hash:
            return tx
    raise HTTPException(status_code=404, detail="Transaction not found")
