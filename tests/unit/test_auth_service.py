import pytest
from fastapi import HTTPException
from services.auth_service import AuthService
from core.security import verify_password
from jose import jwt
from config import JWT_SECRET_KEY, JWT_ALGORITHM

def test_authenticate_user_success(db_session, test_user):
    # Probar autenticación exitosa
    result = AuthService.authenticate_user(db_session, "test@example.com", "password123")
    
    assert result is not None
    assert "access_token" in result
    assert "token_type" in result
    assert result["token_type"] == "bearer"
    
    # Verificar token
    token = result["access_token"]
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert "sub" in payload
    assert payload["sub"] == "test@example.com"

def test_authenticate_user_invalid_email(db_session):
    # Probar autenticación con email inválido
    with pytest.raises(HTTPException) as excinfo:
        AuthService.authenticate_user(db_session, "wrong@example.com", "password123")
    
    assert excinfo.value.status_code == 401
    assert "Correo electrónico o contraseña incorrectos" in excinfo.value.detail

def test_authenticate_user_invalid_password(db_session, test_user):
    # Probar autenticación con contraseña inválida
    with pytest.raises(HTTPException) as excinfo:
        AuthService.authenticate_user(db_session, "test@example.com", "wrongpassword")
    
    assert excinfo.value.status_code == 401
    assert "Correo electrónico o contraseña incorrectos" in excinfo.value.detail

def test_register_user(db_session, monkeypatch):
    # Mockear función de envío de email
    def mock_send_welcome_email(email, name):
        return True
    
    monkeypatch.setattr("services.auth_service.send_welcome_email", mock_send_welcome_email)
    
    # Probar registro de usuario
    result = AuthService.register_user(
        db_session,
        username="newuser",
        email="new@example.com",
        password="newpassword",
        full_name="New User"
    )
    
    assert result is not None
    assert "access_token" in result
    assert "token_type" in result
    
    # Verificar usuario creado
    from services.user_service import UserService
    user = UserService.get_user_by_email(db_session, "new@example.com")
    assert user is not None
    assert user.username == "newuser"
    assert user.full_name == "New User"
    assert verify_password("newpassword", user.hashed_password)

def test_register_user_existing_email(db_session, test_user, monkeypatch):
    # Mockear función de envío de email
    def mock_send_welcome_email(email, name):
        return True
    
    monkeypatch.setattr("services.auth_service.send_welcome_email", mock_send_welcome_email)
    
    # Probar registro con email existente
    with pytest.raises(HTTPException) as excinfo:
        AuthService.register_user(
            db_session,
            username="duplicateuser",
            email="test@example.com",  # Email ya existente
            password="password123",
            full_name="Duplicate User"
        )
    
    assert excinfo.value.status_code == 400
    assert "El correo electrónico ya está registrado" in excinfo.value.detail 