from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database.database import get_db
from database.models import User, Account, Transaction
from core.security import get_current_user
from services.transaction_service import TransactionService

router = APIRouter()

class TransactionCreate(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: float
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    source_amount: float
    source_currency_id: int
    destination_amount: float
    destination_currency_id: int
    exchange_rate: float
    description: Optional[str]
    timestamp: Optional[str]
    
    class Config:
        orm_mode = True

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = TransactionService.create_transaction(
        db,
        current_user.id,
        transaction_data.source_account_id,
        transaction_data.destination_account_id,
        transaction_data.amount,
        transaction_data.description
    )
    
    transaction_response = TransactionResponse(
        id=transaction.id,
        source_amount=transaction.source_amount,
        source_currency_id=transaction.source_currency_id,
        destination_amount=transaction.destination_amount,
        destination_currency_id=transaction.destination_currency_id,
        exchange_rate=transaction.exchange_rate,
        description=transaction.description,
        timestamp=transaction.timestamp.isoformat() if transaction.timestamp else None
    )

    return transaction_response


@router.get("/", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return TransactionService.get_user_transactions(db, current_user.id)
