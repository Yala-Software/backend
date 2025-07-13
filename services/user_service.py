from sqlalchemy.orm import Session
from database.models import User

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        """Obtener un usuario por su ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        """Obtener un usuario por su email"""
        return db.query(User).filter(User.email == email).first() 