from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pathlib import Path

from app.core.models import Restaurant, Table, Booking
from app.core.schemas import (
    BookingCreate,
)
from app.core.database import get_db, get_current_user_from_cookie

router = APIRouter()

# Указываем путь к шаблонам
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

# --------------------- Маршруты ---------------------

@router.get("/", response_class=HTMLResponse)
async def get_restaurants(request: Request, db: AsyncSession = Depends(get_db)):
    """Получение списка ресторанов с отображением на странице."""
    current_user = await get_current_user_from_cookie(request, db)
    
    async with db.begin():
        result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    return templates.TemplateResponse("restaurants.html", {
        "request": request, 
        "restaurants": restaurants,
        "user": current_user
    })


@router.get("/{restaurant_id}/", response_class=HTMLResponse)
async def restaurant_details(
    request: Request,
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Детали ресторана и доступные столики."""
    current_user = await get_current_user_from_cookie(request, db)
    
    restaurant = await db.get(Restaurant, restaurant_id)
    if not restaurant:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Ресторан не найден",
            "user": current_user
        })

    async with db.begin():
        tables_query = (
            select(Table)
            .where(Table.restaurant_id == restaurant_id)
        )
        tables = (await db.execute(tables_query)).scalars().all()

    return templates.TemplateResponse("restaurant_detail.html", {
        "request": request,
        "restaurant": restaurant,
        "tables": tables,
        "user": current_user
    })


@router.post("/bookings/", response_class=HTMLResponse)
async def create_booking(
    request: Request,
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создание нового бронирования через форму."""
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Для бронирования необходимо войти в систему"
        })
    
    # Проверка существования ресторана
    restaurant = await db.get(Restaurant, booking.restaurant_id)
    if not restaurant:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Ресторан не найден",
            "user": current_user
        })

    # Проверка доступности столика
    query = select(Booking).where(
        Booking.table_id == booking.table_id,
        Booking.date_time == booking.date_time
    )
    async with db.begin():
        existing_booking = await db.execute(query)
        if existing_booking.scalars().first():
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "Столик уже забронирован на это время",
                "user": current_user
            })

    # Создание бронирования
    db_booking = Booking(
        user_id=current_user.id,
        table_id=booking.table_id,
        date_time=booking.date_time
    )
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)

    # Получаем столик для отображения информации
    table = await db.get(Table, db_booking.table_id)

    return templates.TemplateResponse("booking_success.html", {
        "request": request,
        "restaurant": restaurant,
        "table": table,
        "booking": db_booking,
        "user": current_user
    })
