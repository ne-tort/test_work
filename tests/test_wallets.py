import pytest
import pytest_asyncio
from test_app.models import Base, engine
from test_app.main import app
from httpx import AsyncClient, ASGITransport


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_wallet_operations(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

        response = await client.post(f"/api/v1/wallets/new_wallet/100")
        assert response.status_code == 200
        wallet_uuid = response.json()["wallet_uuid"]

        response = await client.get(f"/api/v1/wallets/{wallet_uuid}")
        assert response.status_code == 200
        assert float(response.json()["balance"]) == 100

        response = await client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "DEPOSIT", "amount": 50.00})
        assert response.status_code == 200
        assert float(response.json()["amount"]) == 50

        response = await client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "WITHDRAW", "amount": 30.50})
        assert response.status_code == 200
        assert float(response.json()["amount"]) == 30.50

        response = await client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "WITHDRAW", "amount": 500})
        assert response.status_code == 400

        response = await client.post(f"/api/v1/wallets/{wallet_uuid}/operation", json={"operation": "WITHDRAW", "amount": "test"})
        assert response.status_code == 422

        response = await client.get(f"/api/v1/wallets/{wallet_uuid}")
        assert response.status_code == 200
        assert float(response.json()["balance"]) == 119.5
