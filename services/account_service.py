from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from typing import List

from database.models import Account, Transaction, User, Currency
from services.email_service import send_account_statement

class AccountService:
    @staticmethod
    def get_user_accounts(db: Session, user_id: int) -> List[Account]:
        """Obtener todas las cuentas de un usuario"""
        return db.query(Account).filter(
            Account.user_id == user_id
        ).join(Currency).options(
            joinedload(Account.currency)
        ).all()
    
    @staticmethod
    def get_account_details(db: Session, account_id: int, user_id: int):
        """Obtener detalles de una cuenta y sus transacciones"""
        account = db.query(Account).filter(
            Account.id == account_id, 
            Account.user_id == user_id
        ).join(Currency).options(
            joinedload(Account.currency)
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        
        transactions = db.query(Transaction).filter(
            (Transaction.source_account_id == account_id) | 
            (Transaction.destination_account_id == account_id)
        ).order_by(Transaction.timestamp.desc()).all()
        
        return {"account": account, "transactions": transactions}
    
    @staticmethod
    def export_account_statement(db: Session, account_id: int, user_id: int, user_email: str, user_full_name: str, format: str):
        """Exportar estado de cuenta en formato específico y enviarlo por email"""
        account = db.query(Account).filter(
            Account.id == account_id, 
            Account.user_id == user_id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
            
        transactions = db.query(Transaction).filter(
            (Transaction.source_account_id == account_id) | 
            (Transaction.destination_account_id == account_id)
        ).order_by(Transaction.timestamp.desc()).all()
        
        try:
            send_account_statement(user_email, user_full_name, account, transactions, format)
            return {"message": f"El estado de cuenta en formato {format.upper()} ha sido enviado a tu correo electrónico"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al enviar el estado de cuenta: {str(e)}")
    
    @staticmethod
    def get_account_by_id(db: Session, account_id: int):
        """Obtener una cuenta por su ID"""
        return db.query(Account).filter(Account.id == account_id).first() 