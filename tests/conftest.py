import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, User, Currency, Account, Transaction
import datetime
from core.security import hash_password

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))) 

@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_currencies(db_session):
    currencies = {
        "PEN": "Sol Peruano",
        "USD": "Dolar Estadounidense",
    }
    
    result = {}
    for code, name in currencies.items():
        currency = Currency(code=code, name=name)
        db_session.add(currency)
        db_session.commit()
        db_session.refresh(currency)
        result[code] = currency
    
    return result

@pytest.fixture
def test_accounts(db_session, test_user, test_currencies):
    pen_account = Account(
        user_id=test_user.id,
        currency_id=test_currencies["PEN"].id,
        balance=1000.0
    )
    
    usd_account = Account(
        user_id=test_user.id,
        currency_id=test_currencies["USD"].id,
        balance=500.0
    )
    
    db_session.add(pen_account)
    db_session.add(usd_account)
    db_session.commit()
    db_session.refresh(pen_account)
    db_session.refresh(usd_account)
    
    return {"PEN": pen_account, "USD": usd_account} 