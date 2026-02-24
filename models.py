import os
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pydantic
from pydantic import Field

PG_DSN = os.getenv('PG_DSN', 'postgresql+asyncpg://user:password@localhost:5432/advertisements_flask_db')
engine = create_async_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class AdModel(Base):
    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(String(100), nullable=False, index=True)


class CreateAdModel(pydantic.BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    owner: str = Field(..., min_length=1, max_length=100)


class UpdateAdModel(pydantic.BaseModel):
    title: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, min_length=1, max_length=500)
    owner: str | None = Field(None, min_length=1, max_length=100)


class HTTPError(Exception):
    def __init__(self, status_code: int, message: str | list | dict):
        self.status_code = status_code
        self.message = message


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)