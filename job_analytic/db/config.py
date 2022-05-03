from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.settings import settings


SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    host=settings["DATABASE"]["Host"],
    username=settings["DATABASE"]["Username"],
    password=settings["DATABASE"]["Password"],
    database=settings["DATABASE"]["Name"],
)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()


async def get_session():
    async with async_session() as session:
        yield session
