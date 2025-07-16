
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from .models import *



load_dotenv()


DATABASE_URL = os.getenv('DB_ADMIN')


engine = create_async_engine(DATABASE_URL, echo=True)


AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def create_tables():
    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user_from_cookie(request, db):
    from fastapi import Depends
    from app.security import get_current_user
    
    token = request.cookies.get("access_token")
    if not token:
        return None
    return await get_current_user(token, db)
