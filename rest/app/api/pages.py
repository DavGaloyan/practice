from http.client import HTTPException
from pathlib import Path

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_current_user_from_cookie, get_db
from app.core.models import Booking, Restaurant, Table, User

router = APIRouter()

# Настройка шаблонов
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/", response_class=HTMLResponse)
@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Главная страница"""
    current_user = await get_current_user_from_cookie(request, db)

    # Получаем список ресторанов для отображения на главной странице
    results = await db.execute(select(Restaurant).limit(3))
    restaurants = results.scalars().all()

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": current_user, "restaurants": restaurants},
    )


@router.get("/info/about", response_class=HTMLResponse)
async def about_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница о нас"""
    current_user = await get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(
        "about.html", {"request": request, "user": current_user}
    )


@router.get("/info/faq", response_class=HTMLResponse)
async def faq_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница с часто задаваемыми вопросами"""
    current_user = await get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(
        "faq.html", {"request": request, "user": current_user}
    )


@router.get("/info/contacts", response_class=HTMLResponse)
async def contacts_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница с контактами"""
    current_user = await get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(
        "contacts.html", {"request": request, "user": current_user}
    )


@router.get("/info/terms", response_class=HTMLResponse)
async def terms_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница с условиями использования"""
    current_user = await get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(
        "terms.html", {"request": request, "user": current_user}
    )


@router.get("/info/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница с политикой конфиденциальности"""
    current_user = await get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(
        "privacy.html", {"request": request, "user": current_user}
    )


@router.get("/restaurants", response_class=HTMLResponse)
async def restaurants_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница со списком ресторанов"""
    current_user = await get_current_user_from_cookie(request, db)

    # Получаем список ресторанов из БД
    results = await db.execute(select(Restaurant))
    restaurants = results.scalars().all()

    return templates.TemplateResponse(
        "restaurants.html",
        {"request": request, "restaurants": restaurants, "user": current_user},
    )


@router.get("/restaurants/{restaurant_id}", response_class=HTMLResponse)
async def restaurant_detail_page(
    request: Request, restaurant_id: int, db: AsyncSession = Depends(get_db)
):
    """Страница с деталями ресторана"""
    current_user = await get_current_user_from_cookie(request, db)

    # Получаем ресторан по ID
    result = await db.execute(
        select(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .options(selectinload(Restaurant.tables))
    )
    restaurant = result.scalar_one_or_none()

    if not restaurant:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error_message": "Ресторан не найден"}
        )

    # Получаем доступные столики
    tables = restaurant.tables

    # Получаем существующие бронирования для этого ресторана
    # В реальном приложении нужно фильтровать по дате
    bookings_result = await db.execute(
        select(Booking).join(Table).filter(Table.restaurant_id == restaurant_id)
    )
    bookings = bookings_result.scalars().all()

    # Определяем занятые столики
    booked_table_ids = [booking.table_id for booking in bookings]

    # Помечаем столики как доступные или занятые
    tables_with_status = []
    for table in tables:
        tables_with_status.append(
            {
                "id": table.id,
                "number": table.number,
                "seats": table.seats,
                "is_available": table.id not in booked_table_ids,
            }
        )

    return templates.TemplateResponse(
        "restaurant_detail.html",
        {
            "request": request,
            "restaurant": restaurant,
            "tables": tables_with_status,
            "user": current_user,
        },
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница профиля пользователя"""
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return HTMLResponse(status_code=302, headers={"Location": "/auth/login"})

    # Получаем информацию о пользователе и его бронированиях
    result = await db.execute(
        select(User)
        .filter(User.id == current_user.id)
        .options(selectinload(User.bookings))
    )
    user = result.scalar_one_or_none()

    # Получаем детали бронирований
    bookings_with_details = []
    for booking in user.bookings:
        # Получаем информацию о столике
        table_result = await db.execute(
            select(Table)
            .filter(Table.id == booking.table_id)
            .options(selectinload(Table.restaurant))
        )
        table = table_result.scalar_one_or_none()

        # Получаем информацию о ресторане
        restaurant_result = await db.execute(
            select(Restaurant).filter(Restaurant.id == table.restaurant_id)
        )
        restaurant = restaurant_result.scalar_one_or_none()

        bookings_with_details.append(
            {
                "id": booking.id,
                "date_time": booking.date_time,
                "table_number": table.number,
                "seats": table.seats,
                "restaurant_name": restaurant.name,
                "restaurant_id": restaurant.id,
            }
        )

    return templates.TemplateResponse(
        "user_profile.html",
        {"request": request, "user": user, "bookings": bookings_with_details},
    )


@router.get("/bookings/{booking_id}/edit", response_class=HTMLResponse)
async def edit_booking_page(request: Request, booking_id: int):
    """Страница редактирования бронирования"""
    # В реальном приложении здесь будет проверка авторизации
    booking = {
        "id": booking_id,
        "restaurant_id": 1,
        "date": "2025-03-15",
        "time": "19:00",
        "guests": 2,
    }
    restaurants = [
        {"id": 1, "name": "Итальянский ресторан"},
        {"id": 2, "name": "Японский ресторан"},
        {"id": 3, "name": "Грузинский ресторан"},
    ]
    return templates.TemplateResponse(
        "edit_booking.html",
        {"request": request, "booking": booking, "restaurants": restaurants},
    )
