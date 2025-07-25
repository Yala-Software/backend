import pytest
from services.user_service import UserService
from database.models import User

def test_get_user_by_id(db_session, test_user):
    # Probar obtención de usuario por ID
    result = UserService.get_user_by_id(db_session, test_user.id)
    assert result is not None
    assert result.id == test_user.id
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.full_name == "Test User"
    
    # Probar con ID inexistente
    result = UserService.get_user_by_id(db_session, 999)
    assert result is None

def test_get_user_by_email(db_session, test_user):
    # Probar obtención de usuario por email
    result = UserService.get_user_by_email(db_session, "test@example.com")
    assert result is not None
    assert result.id == test_user.id
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    
    # Probar con email inexistente
    result = UserService.get_user_by_email(db_session, "nonexistent@example.com")
    assert result is None 