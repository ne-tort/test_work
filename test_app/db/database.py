from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from test_app.db.config import Settings

settings = Settings()

if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
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