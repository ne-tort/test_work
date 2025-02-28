from sqlalchemy import Column, Numeric
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from test_app.config import Settings
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class Base(DeclarativeBase):
    __abstract__ = True

settings = Settings()
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=50,
        max_overflow=100
    )

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
)


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    balance = Column(Numeric(precision=10, scale=2), nullable=False, default=0.0)

    def __repr__(self):
        return f"<Wallet(id={self.id}, balance={self.balance})>"


async def get_db():
    async with SessionLocal() as session:
        yield session