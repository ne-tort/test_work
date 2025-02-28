from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, condecimal
from typing import Literal
from test_app.models import Wallet, get_db
from sqlalchemy.future import select
from uuid import UUID, uuid4

router_wallet = APIRouter()

class WalletPostRequest(BaseModel):
    operation: Literal["DEPOSIT", "WITHDRAW"]
    amount: condecimal(gt=0, decimal_places=2)

class WalletPostResponse(BaseModel):
    wallet_uuid: UUID
    operation: Literal["DEPOSIT", "WITHDRAW"]
    amount: condecimal(gt=0, decimal_places=2)

class WalletGetResponse(BaseModel):
    wallet_uuid: UUID
    balance: condecimal(gt=0, decimal_places=2)

@router_wallet.post("/wallets/{wallet_uuid}/operation", response_model=WalletPostResponse)
async def wallet_operations(wallet_uuid: UUID,
                            data: WalletPostRequest,
                            db: AsyncSession = Depends(get_db)):
    try:
        response = await db.execute(select(Wallet).filter(Wallet.id == wallet_uuid))
        wallet = response.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if data.operation == "DEPOSIT":
        wallet.balance += data.amount
    elif data.operation == "WITHDRAW":
        if wallet.balance >= data.amount:
            wallet.balance -= data.amount
        else:
            raise HTTPException(status_code=400, detail="Insufficient funds")
    try:
        await db.commit()
        await db.refresh(wallet)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "wallet_uuid": wallet.id,
        "operation": data.operation,
        "amount": data.amount,
    }

@router_wallet.get("/wallets/{wallet_uuid}", response_model=WalletGetResponse)
async def get_balance(wallet_uuid: UUID, db: AsyncSession = Depends(get_db)):
    try:
        response = await db.execute(select(Wallet).filter(Wallet.id == wallet_uuid))
        wallet = response.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {
        "wallet_uuid": wallet.id,
        "balance": wallet.balance
    }


@router_wallet.post("/wallets/new_wallet/{balance}", response_model=WalletGetResponse)
async def create_wallet(balance: condecimal(gt=0, decimal_places=2), db: AsyncSession = Depends(get_db)):
    wallet = Wallet(id=uuid4(), balance=balance)
    try:
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return WalletGetResponse(wallet_uuid=wallet.id, balance=wallet.balance)