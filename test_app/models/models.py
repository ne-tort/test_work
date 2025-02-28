from sqlalchemy import Column, Numeric
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from test_app.db.database import SessionLocal

class Base(DeclarativeBase):
    __abstract__ = True

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    balance = Column(Numeric(precision=10, scale=2), nullable=False, default=0.0)

    def __repr__(self):
        return f"<Wallet(id={self.id}, balance={self.balance})>"

async def get_db():
    async with SessionLocal() as session:
        yield session