import pytest
from fastapi import HTTPException
from services.account_service import AccountService
from database.models import Account, Transaction
from datetime import datetime

def test_get_user_accounts(db_session, test_user, test_accounts):
    # Probar obtención de cuentas de usuario
    accounts = AccountService.get_user_accounts(db_session, test_user.id)
    
    assert accounts is not None
    assert len(accounts) == 2
    
    # Verificar detalles
    currencies = ["PEN", "USD"]
    for account in accounts:
        assert account.user_id == test_user.id
        assert account.currency.code in currencies
        assert account.balance > 0

def test_get_account_details(db_session, test_user, test_accounts):
    # Probar obtención de detalles de cuenta
    pen_account = test_accounts["PEN"]
    result = AccountService.get_account_details(db_session, pen_account.id, test_user.id)
    
    assert result is not None
    assert "account" in result
    assert "transactions" in result
    assert result["account"].id == pen_account.id
    assert result["account"].user_id == test_user.id
    assert result["account"].balance == 1000.0
    
    # Inicialmente no hay transacciones
    assert len(result["transactions"]) == 0

def test_get_account_details_not_found(db_session, test_user):
    # Probar con cuenta inexistente
    with pytest.raises(HTTPException) as excinfo:
        AccountService.get_account_details(db_session, 999, test_user.id)
    
    assert excinfo.value.status_code == 404
    assert "Cuenta no encontrada" in excinfo.value.detail

def test_get_account_details_wrong_user(db_session, test_accounts):
    # Probar con ID de usuario incorrecto
    pen_account = test_accounts["PEN"]
    with pytest.raises(HTTPException) as excinfo:
        AccountService.get_account_details(db_session, pen_account.id, 999)
    
    assert excinfo.value.status_code == 404
    assert "Cuenta no encontrada" in excinfo.value.detail

def test_export_account_statement(db_session, test_user, test_accounts, monkeypatch):
    # Mockear función de envío de estado de cuenta
    def mock_send_account_statement(email, name, account, transactions, format):
        return True
    
    monkeypatch.setattr("services.account_service.send_account_statement", mock_send_account_statement)
    
    # Probar exportación de estado de cuenta
    pen_account = test_accounts["PEN"]
    result = AccountService.export_account_statement(
        db_session, 
        pen_account.id, 
        test_user.id, 
        test_user.email, 
        test_user.full_name, 
        "csv"
    )
    
    assert result is not None
    assert "message" in result
    assert "CSV" in result["message"]

def test_export_account_statement_not_found(db_session, test_user, monkeypatch):
    # Mockear función de envío
    def mock_send_account_statement(email, name, account, transactions, format):
        return True
    
    monkeypatch.setattr("services.account_service.send_account_statement", mock_send_account_statement)
    
    # Probar con cuenta inexistente
    with pytest.raises(HTTPException) as excinfo:
        AccountService.export_account_statement(
            db_session, 
            999, 
            test_user.id, 
            test_user.email, 
            test_user.full_name, 
            "csv"
        )
    
    assert excinfo.value.status_code == 404
    assert "Cuenta no encontrada" in excinfo.value.detail

def test_export_account_statement_error(db_session, test_user, test_accounts, monkeypatch):
    # Mockear función de envío que genera error
    def mock_send_account_statement(email, name, account, transactions, format):
        raise Exception("Error de prueba")
    
    monkeypatch.setattr("services.account_service.send_account_statement", mock_send_account_statement)
    
    # Probar exportación con error de envío
    pen_account = test_accounts["PEN"]
    with pytest.raises(HTTPException) as excinfo:
        AccountService.export_account_statement(
            db_session, 
            pen_account.id, 
            test_user.id, 
            test_user.email, 
            test_user.full_name, 
            "csv"
        )
    
    assert excinfo.value.status_code == 500
    assert "Error al enviar el estado de cuenta" in excinfo.value.detail

def test_get_account_by_id(db_session, test_accounts):
    # Probar obtención de cuenta por ID
    pen_account = test_accounts["PEN"]
    result = AccountService.get_account_by_id(db_session, pen_account.id)
    
    assert result is not None
    assert result.id == pen_account.id
    assert result.balance == 1000.0
    
    # Probar con ID inexistente
    result = AccountService.get_account_by_id(db_session, 999)
    assert result is None 