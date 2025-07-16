from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from starlette.templating import Jinja2Templates
import os

from app.core.database import get_db
from app.core.models import Feedback, User
from app.core.schemas import FeedbackCreate, FeedbackOut
from app.core.security import get_current_user

router = APIRouter(tags=["feedback"])

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/feedback", response_class=HTMLResponse)
async def feedback_form(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """Страница с формой обратной связи"""
    current_user = None
    if access_token:
        current_user = await get_current_user(access_token, db)

    return templates.TemplateResponse(
        "feedback.html",
        {"request": request, "current_user": current_user}
    )

@router.post("/feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    """Обработка отправки формы обратной связи"""
    current_user = None
    if access_token:
        current_user = await get_current_user(access_token, db)

    feedback_data = FeedbackCreate(
        name=name,
        email=email,
        subject=subject,
        message=message
    )

    feedback = Feedback(
        name=feedback_data.name,
        email=feedback_data.email,
        subject=feedback_data.subject,
        message=feedback_data.message,
        user_id=current_user.id if current_user else None
    )

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # Перенаправляем на страницу с сообщением об успехе
    return templates.TemplateResponse(
        "feedback_success.html",
        {"request": request, "current_user": current_user}
    )

@router.get("/api/feedback", response_model=list[FeedbackOut])
async def list_feedback(
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None)
):
    """API для получения списка отзывов (только для администраторов)"""
    current_user = None
    if access_token:
        current_user = await get_current_user(access_token, db)

    if not current_user or current_user.email != "admin@example.com":
        raise HTTPException(status_code=403, detail="Нет доступа")

    result = await db.execute(select(Feedback))
    feedbacks = result.scalars().all()
    return feedbacks
