from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

async_engine = create_async_engine(url=settings.db.db_url)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session


db_session: type[AsyncSession] = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass