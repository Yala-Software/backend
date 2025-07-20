from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database.database import get_db
from database.models import User, Account, Currency, Transaction
from core.security import get_current_user
from services.account_service import AccountService

router = APIRouter()

class CurrencyInfo(BaseModel):
    id: int
    code: str
    name: str
    
    class Config:
        orm_mode = True

class AccountInfo(BaseModel):
    id: int
    currency: CurrencyInfo
    balance: float
    
    class Config:
        orm_mode = True

class TransactionInfo(BaseModel):
    id: int
    source_amount: float
    source_currency_id: int
    destination_amount: float
    destination_currency_id: int
    exchange_rate: float
    description: str = None
    timestamp: datetime
    
    class Config:
        orm_mode = True

class AccountWithTransactionsResponse(BaseModel):
    account: AccountInfo
    transactions: List[TransactionInfo]

@router.get("/", response_model=List[AccountInfo])
async def get_user_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AccountService.get_user_accounts(db, current_user.id)

@router.get("/{account_id}", response_model=AccountWithTransactionsResponse)
async def get_account_details(
    account_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return AccountService.get_account_details(db, account_id, current_user.id)

@router.post("/{account_id}/export")
async def export_account_statement(
    account_id: int,
    format: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return AccountService.export_account_statement(
        db, 
        account_id, 
        current_user.id, 
        current_user.email, 
        current_user.full_name, 
        format
    )
