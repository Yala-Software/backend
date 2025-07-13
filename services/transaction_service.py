from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from datetime import datetime, timezone

from database.models import User, Account, Transaction, Currency
from services.exchange_service import ExchangeService
from services.account_service import AccountService
from services.user_service import UserService
from services.email_service import send_transaction_notification

class TransactionService:
    @staticmethod
    def create_transaction(
        db: Session, 
        user_id: int, 
        source_account_id: int, 
        destination_account_id: int, 
        amount: float, 
        description: str = None
    ):
        """Crear una nueva transacción entre cuentas"""
        source_account = db.query(Account).filter(
            Account.id == source_account_id,
            Account.user_id == user_id
        ).first()
        
        if not source_account:
            raise HTTPException(status_code=404, detail="La cuenta de origen no existe o no pertenece al usuario")
        
        destination_account = db.query(Account).filter(
            Account.id == destination_account_id
        ).first()
        
        if not destination_account:
            raise HTTPException(status_code=404, detail="La cuenta de destino no existe")
        
        if source_account.balance < amount:
            raise HTTPException(status_code=400, detail="Balance insuficiente en la cuenta de origen")
        
        source_currency = db.query(Currency).filter(Currency.id == source_account.currency_id).first()
        destination_currency = db.query(Currency).filter(Currency.id == destination_account.currency_id).first()
        
        exchange_service = ExchangeService()
        if source_currency.code != destination_currency.code:
            exchange_rate = exchange_service.get_exchange_rate(source_currency.code, destination_currency.code)
            destination_amount = amount * exchange_rate
        else:
            exchange_rate = 1.0
            destination_amount = amount
        
        now = datetime.now(timezone.utc)

        new_transaction = Transaction(
            sender_id=user_id,
            receiver_id=destination_account.user_id,
            source_account_id=source_account.id,
            destination_account_id=destination_account.id,
            source_amount=amount,
            source_currency_id=source_currency.id,
            destination_amount=destination_amount,
            destination_currency_id=destination_currency.id,
            exchange_rate=exchange_rate,
            description=description,
            timestamp=now
        )
        
        source_account.balance -= amount
        destination_account.balance += destination_amount
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        receiver = UserService.get_user_by_id(db, destination_account.user_id)
        sender = UserService.get_user_by_id(db, user_id)
        
        try:
            send_transaction_notification(
                sender.email,
                sender.full_name, 
                new_transaction, 
                source_currency.code,
                destination_currency.code,
                is_sender=True
            )
            
            send_transaction_notification(
                receiver.email,
                receiver.full_name,
                new_transaction,
                source_currency.code,
                destination_currency.code,
                is_sender=False
            )
        except Exception as e:
            print(f"Error al enviar la notificación: {e}")

        return new_transaction
    
    @staticmethod
    def get_user_transactions(db: Session, user_id: int) -> List[Transaction]:
        """Obtener todas las transacciones de un usuario"""
        return db.query(Transaction).filter(
            (Transaction.sender_id == user_id) | 
            (Transaction.receiver_id == user_id)
        ).order_by(Transaction.timestamp.desc()).all() 