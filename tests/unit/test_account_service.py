import pytest
from fastapi import HTTPException
from services.account_service import AccountService
from database.models import Account, Transaction
from datetime import datetime

def test_get_user_accounts(db_session, test_user, test_accounts):
    # Test getting user accounts
    accounts = AccountService.get_user_accounts(db_session, test_user.id)
    
    assert accounts is not None
    assert len(accounts) == 2
    
    # Verify account details
    currencies = ["PEN", "USD"]
    for account in accounts:
        assert account.user_id == test_user.id
        assert account.currency.code in currencies
        assert account.balance > 0

def test_get_account_details(db_session, test_user, test_accounts):
    # Test getting account details
    pen_account = test_accounts["PEN"]
    result = AccountService.get_account_details(db_session, pen_account.id, test_user.id)
    
    assert result is not None
    assert "account" in result
    assert "transactions" in result
    assert result["account"].id == pen_account.id
    assert result["account"].user_id == test_user.id
    assert result["account"].balance == 1000.0
    
    # Initially there are no transactions
    assert len(result["transactions"]) == 0

def test_get_account_details_not_found(db_session, test_user):
    # Test getting details of a non-existent account
    with pytest.raises(HTTPException) as excinfo:
        AccountService.get_account_details(db_session, 999, test_user.id)
    
    assert excinfo.value.status_code == 404
    assert "Cuenta no encontrada" in excinfo.value.detail

def test_get_account_details_wrong_user(db_session, test_accounts):
    # Test getting account details with wrong user ID
    pen_account = test_accounts["PEN"]
    with pytest.raises(HTTPException) as excinfo:
        AccountService.get_account_details(db_session, pen_account.id, 999)
    
    assert excinfo.value.status_code == 404
    assert "Cuenta no encontrada" in excinfo.value.detail

def test_export_account_statement(db_session, test_user, test_accounts, monkeypatch):
    # Mock the email sending function
    def mock_send_account_statement(email, name, account, transactions, format):
        return True
    
    monkeypatch.setattr("services.account_service.send_account_statement", mock_send_account_statement)
    
    # Test exporting account statement
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
    # Mock the email sending function
    def mock_send_account_statement(email, name, account, transactions, format):
        return True
    
    monkeypatch.setattr("services.account_service.send_account_statement", mock_send_account_statement)
    
    # Test exporting statement for non-existent account
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
    # Mock the email sending function to raise an exception
    def mock_send_account_statement(email, name, account, transactions, format):
        raise Exception("Test error")
    
    monkeypatch.setattr("services.account_service.send_account_statement", mock_send_account_statement)
    
    # Test export with email sending error
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
    # Test getting account by ID
    pen_account = test_accounts["PEN"]
    result = AccountService.get_account_by_id(db_session, pen_account.id)
    
    assert result is not None
    assert result.id == pen_account.id
    assert result.balance == 1000.0
    
    # Test with non-existent ID
    result = AccountService.get_account_by_id(db_session, 999)
    assert result is None 