from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Booking, User
from app.schemas import BookingResponse, UserProfile
from app.database import get_db

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user