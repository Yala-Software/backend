from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database.database import get_db
from database.models import Account, Transaction, Currency, User
from core.security import get_current_user
from services.exchange_service import ExchangeService

exchange_service = ExchangeService()

router = APIRouter()

class TransactionCreate(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: float
    description: str = None

class TransactionResponse(BaseModel):
    id: int
    source_amount: float
    source_currency_id: int
    destination_amount: float
    destination_currency_id: int
    exchange_rate: float
    description: str = None
    timestamp: str

    class Config:
        orm_mode = True

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    tx: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    source_account = db.query(Account).filter_by(id=tx.source_account_id, user_id=current_user.id).first()
    destination_account = db.query(Account).filter_by(id=tx.destination_account_id).first()

    if not source_account or not destination_account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    if source_account.balance < tx.amount:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    if source_account.currency_id == destination_account.currency_id:
        exchange_rate = 1.0
        destination_amount = tx.amount
    else:
        exchange_rate = exchange_service.get_exchange_rate(source_account.currency.code, destination_account.currency.code)
        destination_amount = tx.amount * exchange_rate

    # Actualizar balances
    source_account.balance -= tx.amount
    destination_account.balance += destination_amount

    transaction = Transaction(
        source_account_id=tx.source_account_id,
        destination_account_id=tx.destination_account_id,
        source_amount=tx.amount,
        destination_amount=destination_amount,
        source_currency_id=source_account.currency_id,
        destination_currency_id=destination_account.currency_id,
        exchange_rate=exchange_rate,
        description=tx.description
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@router.get("/", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    accounts = db.query(Account.id).filter_by(user_id=current_user.id).all()
    account_ids = [acc.id for acc in accounts]

    transactions = db.query(Transaction).filter(
        Transaction.source_account_id.in_(account_ids) |
        Transaction.destination_account_id.in_(account_ids)
    ).order_by(Transaction.timestamp.desc()).all()

    return transactions
