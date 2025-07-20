from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from database.models import User
from core.security import verify_password, create_access_token, hash_password
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from services.email_service import send_welcome_email
from services.user_service import UserService

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        """Autenticar usuario y devolver token si es válido"""
        user = UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo electrónico o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    @staticmethod
    def register_user(db: Session, username: str, email: str, password: str, full_name: str):
        """Registrar un nuevo usuario"""
        if UserService.get_user_by_email(db, email):
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
        
        hashed_password = hash_password(password)
        
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        try:
            send_welcome_email(new_user.email, new_user.full_name)
        except Exception as e:
            print(f"Error al enviar el correo de bienvenida: {e}")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.email},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"} 