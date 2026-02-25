import os
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship
import pydantic
from pydantic import Field

PG_DSN = os.getenv('PG_DSN', 'postgresql+asyncpg://user:password@localhost:5432/advertisements_flask_db')
engine = create_async_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    ads = relationship('AdModel', back_populates='user')


class AdModel(Base):
    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('UserModel', back_populates='ads')


# Pydantic схемы
class CreateUserModel(pydantic.BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class LoginUserModel(pydantic.BaseModel):
    username: str
    password: str


class CreateAdModel(pydantic.BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)


class UpdateAdModel(pydantic.BaseModel):
    title: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, min_length=1, max_length=500)


class HTTPError(Exception):
    def __init__(self, status_code: int, message: str | list | dict):
        self.status_code = status_code
        self.message = message


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
