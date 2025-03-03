from uuid import UUID, uuid4
from fastapi import HTTPException
from pydantic import condecimal
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from test_app.models.models import Wallet
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
async def create_wallet(balance: condecimal(gt=0, decimal_places=2), db: AsyncSession):
    wallet = Wallet(id=uuid4(), balance=balance)
    try:
        db.add(wallet)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return wallet

@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
async def get_wallet(wallet_uuid: UUID, db: AsyncSession):
    try:
        wallet = await db.execute(select(Wallet).filter(Wallet.id == wallet_uuid))
        wallet = wallet.scalars().first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return wallet

@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
async def wallet_operation(wallet_uuid: UUID, operation : str, amount: condecimal, db: AsyncSession):
    wallet = await get_wallet(wallet_uuid, db)
    if operation == "DEPOSIT":
        atomic = update(Wallet).where(Wallet.id == wallet_uuid).values(balance=Wallet.balance + amount)
    elif operation == "WITHDRAW":
        if wallet.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        atomic = update(Wallet).where(Wallet.id == wallet_uuid).values(balance=Wallet.balance + amount)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown error")
    try:
        await db.execute(atomic)
        await db.commit()
        await db.refresh(wallet)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Unknown error: {str(e)}")

    return wallet