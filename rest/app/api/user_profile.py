from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.core.models import User, Booking, Restaurant, Table
from app.core.database import get_db, get_current_user_from_cookie
from app.core.security import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/profile", response_class=HTMLResponse)
async def user_profile_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Рендер страницы профиля пользователя."""
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Получаем бронирования пользователя с информацией о столиках и ресторанах
    query = select(Booking).where(Booking.user_id == current_user.id).options(
        selectinload(Booking.table).selectinload(Table.restaurant)
    )
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    return templates.TemplateResponse(
        "user_profile.html", 
        {
            "request": request, 
            "user": current_user,
            "bookings": bookings
        }
    )