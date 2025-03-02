from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import condecimal
from sqlalchemy.ext.asyncio import AsyncSession
from test_app.db.database import get_db
from test_app.schemas.schemas import WalletPostRequest, WalletPostResponse, WalletGetResponse
from test_app.services.wallet_operations import create_wallet, get_wallet, wallet_operation

router_wallet = APIRouter()

@router_wallet.post("/wallets/new_wallet/{balance}", response_model=WalletGetResponse)
async def api_create_wallet(balance: condecimal(gt=0, decimal_places=2), db: AsyncSession = Depends(get_db)):
    wallet = await create_wallet(balance, db)

    return WalletGetResponse(wallet_uuid=wallet.id, balance=wallet.balance)

@router_wallet.get("/wallets/{wallet_uuid}", response_model=WalletGetResponse)
async def api_get_balance(wallet_uuid: UUID, db: AsyncSession = Depends(get_db)):
    wallet = await get_wallet(wallet_uuid, db)

    return {
        "wallet_uuid": wallet.id,
        "balance": wallet.balance
    }

@router_wallet.post("/wallets/{wallet_uuid}/operation", response_model=WalletPostResponse)
async def api_wallet_operation(wallet_uuid: UUID,data: WalletPostRequest, db: AsyncSession = Depends(get_db)):
    wallet = await wallet_operation(wallet_uuid, data.operation, data.amount, db)

    return {
        "wallet_uuid": wallet.id,
        "operation": data.operation,
        "amount": data.amount,
    }

