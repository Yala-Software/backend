import pytest
from fastapi import HTTPException
from services.transaction_service import TransactionService
from services.account_service import AccountService
from database.models import Transaction, Account

def test_create_transaction(db_session, test_user, test_accounts, monkeypatch):
    # Mock the exchange service and email notification
    def mock_get_exchange_rate(from_currency, to_currency):
        return 3.5  # Example rate PEN to USD
    
    def mock_send_transaction_notification(email, name, transaction, source_code, dest_code, is_sender):
        return True
    
    monkeypatch.setattr("services.transaction_service.ExchangeService.get_exchange_rate", mock_get_exchange_rate)
    monkeypatch.setattr("services.transaction_service.send_transaction_notification", mock_send_transaction_notification)
    
    # Get initial balances
    pen_account = test_accounts["PEN"]
    usd_account = test_accounts["USD"]
    initial_pen_balance = pen_account.balance
    initial_usd_balance = usd_account.balance
    
    # Test creating a transaction (PEN to USD)
    transaction = TransactionService.create_transaction(
        db_session,
        test_user.id,
        pen_account.id,
        usd_account.id,
        100.0,  # Transfer 100 PEN
        "Test transaction PEN to USD"
    )
    
    # Verify transaction details
    assert transaction is not None
    assert transaction.sender_id == test_user.id
    assert transaction.receiver_id == test_user.id  # Same user in this test
    assert transaction.source_account_id == pen_account.id
    assert transaction.destination_account_id == usd_account.id
    assert transaction.source_amount == 100.0
    assert transaction.destination_amount == 100.0 / 3.5  # PEN to USD with rate 3.5
    assert transaction.exchange_rate == 3.5
    assert transaction.description == "Test transaction PEN to USD"
    
    # Verify account balances have been updated
    updated_pen_account = AccountService.get_account_by_id(db_session, pen_account.id)
    updated_usd_account = AccountService.get_account_by_id(db_session, usd_account.id)
    
    assert updated_pen_account.balance == initial_pen_balance - 100.0
    assert updated_usd_account.balance == initial_usd_balance + (100.0 / 3.5)

def test_create_transaction_same_currency(db_session, test_user, test_accounts, monkeypatch):
    # Create a second PEN account
    second_pen_account = Account(
        user_id=test_user.id,
        currency_id=test_accounts["PEN"].currency_id,
        balance=500.0
    )
    db_session.add(second_pen_account)
    db_session.commit()
    db_session.refresh(second_pen_account)
    
    # Mock email notification
    def mock_send_transaction_notification(email, name, transaction, source_code, dest_code, is_sender):
        return True
    
    monkeypatch.setattr("services.transaction_service.send_transaction_notification", mock_send_transaction_notification)
    
    # Test creating a transaction between same currency (PEN to PEN)
    transaction = TransactionService.create_transaction(
        db_session,
        test_user.id,
        test_accounts["PEN"].id,
        second_pen_account.id,
        50.0,
        "Test transaction PEN to PEN"
    )
    
    # Verify transaction details
    assert transaction.exchange_rate == 1.0
    assert transaction.source_amount == 50.0
    assert transaction.destination_amount == 50.0
    
    # Verify account balances
    source_account = AccountService.get_account_by_id(db_session, test_accounts["PEN"].id)
    dest_account = AccountService.get_account_by_id(db_session, second_pen_account.id)
    
    assert source_account.balance == 1000.0 - 50.0
    assert dest_account.balance == 500.0 + 50.0

def test_create_transaction_insufficient_balance(db_session, test_user, test_accounts):
    # Test creating a transaction with insufficient balance
    with pytest.raises(HTTPException) as excinfo:
        TransactionService.create_transaction(
            db_session,
            test_user.id,
            test_accounts["PEN"].id,
            test_accounts["USD"].id,
            2000.0,  # More than available balance
            "Test transaction with insufficient balance"
        )
    
    assert excinfo.value.status_code == 400
    assert "Balance insuficiente" in excinfo.value.detail

def test_create_transaction_nonexistent_source_account(db_session, test_user, test_accounts):
    # Test creating a transaction with non-existent source account
    with pytest.raises(HTTPException) as excinfo:
        TransactionService.create_transaction(
            db_session,
            test_user.id,
            999,  # Non-existent account ID
            test_accounts["USD"].id,
            100.0,
            "Test transaction with non-existent source"
        )
    
    assert excinfo.value.status_code == 404
    assert "La cuenta de origen no existe" in excinfo.value.detail

def test_create_transaction_nonexistent_destination_account(db_session, test_user, test_accounts):
    # Test creating a transaction with non-existent destination account
    with pytest.raises(HTTPException) as excinfo:
        TransactionService.create_transaction(
            db_session,
            test_user.id,
            test_accounts["PEN"].id,
            999,  # Non-existent account ID
            100.0,
            "Test transaction with non-existent destination"
        )
    
    assert excinfo.value.status_code == 404
    assert "La cuenta de destino no existe" in excinfo.value.detail

def test_get_user_transactions(db_session, test_user, test_accounts, monkeypatch):
    # Mock the necessary functions
    def mock_get_exchange_rate(from_currency, to_currency):
        return 3.5
    
    def mock_send_transaction_notification(email, name, transaction, source_code, dest_code, is_sender):
        return True
    
    monkeypatch.setattr("services.transaction_service.ExchangeService.get_exchange_rate", mock_get_exchange_rate)
    monkeypatch.setattr("services.transaction_service.send_transaction_notification", mock_send_transaction_notification)
    
    # Create some test transactions
    for i in range(3):
        TransactionService.create_transaction(
            db_session,
            test_user.id,
            test_accounts["PEN"].id,
            test_accounts["USD"].id,
            10.0,
            f"Test transaction {i}"
        )
    
    # Test getting user transactions
    transactions = TransactionService.get_user_transactions(db_session, test_user.id)
    
    assert transactions is not None
    assert len(transactions) == 3
    
    # Verify transaction details
    for i, transaction in enumerate(transactions):
        assert transaction.sender_id == test_user.id
        assert transaction.source_account_id == test_accounts["PEN"].id
        assert transaction.destination_account_id == test_accounts["USD"].id
        assert transaction.source_amount == 10.0 