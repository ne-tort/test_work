from fastapi.testclient import TestClient
from test_app.models.models import Base
from test_app.db.database import engine
from decimal import Decimal
import pytest_asyncio
from test_app.main import app

client = TestClient(app)
balance = Decimal("100")

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def create_wallet():
    response = client.post(f"/api/v1/wallets/new_wallet/{balance}")
    return response.json()["wallet_uuid"]


def test_get_balance():
    wallet_uuid = create_wallet()
    response = client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == balance

def test_invalid_wallet():
    wallet_uuid = "afac809f-f5d7-4745-b1cf-ef230a461f09"
    response = client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert response.status_code == 404

def test_deposit():
    wallet_uuid = create_wallet()
    response = client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "DEPOSIT", "amount": '50.00'})
    assert response.status_code == 200
    assert Decimal(response.json()["amount"]) == Decimal('50.00')


def test_withdraw():
    wallet_uuid = create_wallet()
    response = client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "WITHDRAW", "amount": '30.50'})
    assert response.status_code == 200
    assert Decimal(response.json()["amount"]) == Decimal('30.50')


def test_insufficient_funds():
    wallet_uuid = create_wallet()
    response = client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "WITHDRAW", "amount": '500'})
    assert response.status_code == 400


def test_invalid_amount():
    wallet_uuid = create_wallet()
    response = client.post(f"/api/v1/wallets/{wallet_uuid}/operation",
                           json={"operation": "WITHDRAW", "amount": "3465f"})
    assert response.status_code == 422


def test_negative_amount():
    wallet_uuid = create_wallet()
    response = client.post(f"/api/v1/wallets/{wallet_uuid}/operation",
                           json={"operation": "WITHDRAW", "amount": -100})
    assert response.status_code == 422


def test_null_amount():
    wallet_uuid = create_wallet()
    response = client.post(f"/api/v1/wallets/{wallet_uuid}/operation",
                           json={"operation": "WITHDRAW", "amount": 0})
    assert response.status_code == 422


def test_invalid_float_amount():
    wallet_uuid = create_wallet()
    response = client.post(f"/api/v1/wallets/{wallet_uuid}/operation",
                           json={"operation": "WITHDRAW", "amount": 5.456546})
    assert response.status_code == 422


def test_final_balance():
    wallet_uuid = create_wallet()
    client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "DEPOSIT", "amount": '50.00'})
    client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "WITHDRAW", "amount": '30.50'})

    response = client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == balance + Decimal('50.00') - Decimal('30.50')
