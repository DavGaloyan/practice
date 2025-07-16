from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.models import Booking
from app.schemas import BookingCreate, BookingResponse
from app.database import get_db

router = APIRouter()
@router.post("/", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db)):
    db_booking = Booking(**booking.dict())
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    return db_booking

@router.get("/bookings", response_model=list[BookingResponse])
async def get_booking_history(user_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Booking).filter(Booking.user_id == user_id))
        return result.scalars().all()

@router.delete("/bookings/{booking_id}", response_model=dict)
async def cancel_booking(booking_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(
            select(Booking).filter(Booking.id == booking_id, Booking.user_id == user_id)
        )
        booking = result.scalars().first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found or unauthorized")

        await db.delete(booking)
        await db.commit()
        return {"message": "Booking successfully cancelled"}

@router.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: int, booking: BookingCreate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Booking).filter(Booking.id == booking_id))
        existing_booking = result.scalars().first()

        if not existing_booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        for key, value in booking.dict().items():
            setattr(existing_booking, key, value)

        db.add(existing_booking)
        await db.commit()
        await db.refresh(existing_booking)
        return existing_booking