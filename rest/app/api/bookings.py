from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_current_user_from_cookie, get_db
from app.core.models import Booking, Restaurant, Table, User
from app.core.schemas import BookingCreate, BookingUpdate

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")



@router.get("/bookings/new", response_class=HTMLResponse)
async def show_create_booking_page(
    request: Request,
    restaurant_id: int = None,
    table_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Отображение страницы для создания бронирования."""
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Получаем список ресторанов
    restaurant_results = await db.execute(select(Restaurant))
    restaurants = restaurant_results.scalars().all()

    selected_restaurant = None
    available_tables = []

    if restaurant_id:
        # Если выбран ресторан, получаем его и доступные столики
        restaurant_result = await db.execute(
            select(Restaurant).filter(Restaurant.id == restaurant_id)
        )
        selected_restaurant = restaurant_result.scalar_one_or_none()

        if selected_restaurant:
            # Получаем столики для выбранного ресторана
            table_results = await db.execute(
                select(Table).filter(Table.restaurant_id == restaurant_id)
            )
            available_tables = table_results.scalars().all()

    selected_table = None
    if table_id:
        # Если выбран столик, получаем его данные
        table_result = await db.execute(
            select(Table).filter(Table.id == table_id)
        )
        selected_table = table_result.scalar_one_or_none()

    # Добавляем текущую дату для минимального значения в поле выбора даты
    now = datetime.now()

    return templates.TemplateResponse(
        "create_booking.html",
        {
            "request": request,
            "user": current_user,
            "restaurants": restaurants,
            "selected_restaurant": selected_restaurant,
            "available_tables": available_tables,
            "selected_table": selected_table,
            "now": now
        },
    )

@router.post("/bookings/create", response_class=HTMLResponse)
async def create_booking(
    request: Request,
    table_id: int = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Создание нового бронирования."""
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Получаем информацию о столике
    table_result = await db.execute(select(Table).filter(Table.id == table_id))
    table = table_result.scalar_one_or_none()

    if not table:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Столик не найден",
                "user": current_user
            },
        )

    # Преобразуем дату и время в datetime
    try:
        date_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Неверный формат даты или времени",
                "user": current_user
            },
        )

    # Проверяем, не занят ли столик на указанное время
    query = select(Booking).where(
        Booking.table_id == table_id,
        Booking.date_time == date_time
    )
    existing_booking = await db.execute(query)
    if existing_booking.scalars().first():
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "Этот столик уже забронирован на указанное время",
                "user": current_user
            },
        )

    # Создаем бронирование
    new_booking = Booking(
        user_id=current_user.id,
        table_id=table_id,
        date_time=date_time,
        status="confirmed"  # Устанавливаем статус бронирования
    )

    # Обновляем статус столика
    table.status = "booked"

    # Сохраняем изменения в базе данных
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    # Получаем информацию о ресторане для отображения в сообщении об успехе
    restaurant_result = await db.execute(
        select(Restaurant).filter(Restaurant.id == table.restaurant_id)
    )
    restaurant = restaurant_result.scalar_one_or_none()

    return templates.TemplateResponse(
        "booking_success.html",
        {
            "request": request,
            "booking": new_booking,
            "table": table,
            "restaurant": restaurant,
            "user": current_user
        }
    )



@router.get("/profile/bookings/", response_class=HTMLResponse)
async def get_user_bookings(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Получаем бронирования пользователя с загрузкой столиков и ресторанов
    query = select(Booking).where(Booking.user_id == current_user.id).options(
        selectinload(Booking.table).selectinload(Table.restaurant)
    )
    result = await db.execute(query)
    bookings = result.scalars().all()

    return templates.TemplateResponse(
        "user_bookings.html", {"request": request, "bookings": bookings, "user": current_user}
    )


@router.get("/bookings/{booking_id}/edit", response_class=HTMLResponse)
async def show_update_booking_page(
    request: Request,
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)

    booking = await db.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.id:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Бронирование не найдено", "user": current_user}
        )

    restaurants = await db.execute(select(Restaurant))
    tables = await db.execute(select(Table))
    return templates.TemplateResponse(
        "edit_booking.html",
        {
            "request": request,
            "booking": booking,
            "restaurants": restaurants.scalars().all(),
            "tables": tables.scalars().all(),
            "user": current_user
        },
    )


@router.put("/bookings/{booking_id}", response_class=HTMLResponse)
async def update_booking(
    request: Request,
    booking_id: int,
    booking_data: BookingUpdate,
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)

    booking = await db.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.id:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Бронирование не найдено", "user": current_user}
        )

    for field, value in booking_data.dict(exclude_unset=True).items():
        setattr(booking, field, value)

    await db.commit()
    await db.refresh(booking)
    return RedirectResponse(url="/profile/bookings/", status_code=302)


@router.post("/bookings/{booking_id}", response_class=HTMLResponse)
async def delete_booking(
    request: Request,
    booking_id: int,
    method_type: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Проверяем, является ли это запросом на удаление
    if method_type and method_type.lower() == "delete":
        booking = await db.get(Booking, booking_id)
        if not booking or booking.user_id != current_user.id:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error_message": "Бронирование не найдено или у вас нет прав на его удаление",
                    "user": current_user
                }
            )
        await db.delete(booking)
        await db.commit()
        return RedirectResponse(url="/profile/bookings/", status_code=302)

    # Если это не запрос на удаление, перенаправляем на страницу редактирования
    return RedirectResponse(url=f"/bookings/{booking_id}/edit", status_code=302)
