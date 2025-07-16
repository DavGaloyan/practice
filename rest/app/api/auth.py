from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pathlib import Path
from app.core.security import authenticate_user, get_password_hash, create_access_token
from app.core.models import User
from app.core.schemas import UserCreate
from app.core.database import get_db, get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user_from_cookie(request, db)
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register_new.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: AsyncSession = Depends(get_db)
):
    existing_user = await db.execute(select(User).where(User.email == email))
    if existing_user.scalars().first():
        return templates.TemplateResponse("register_new.html", {"request": request, "error": "Email уже используется."})
    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    # Создаем токен для пользователя
    token = create_access_token({"sub": new_user.email, "user_id": new_user.id})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user_from_cookie(request, db)
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: AsyncSession = Depends(get_db)
):
    db_user = await authenticate_user(email, password, db)
    if not db_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные учетные данные."})
    token = create_access_token({"sub": db_user.email, "user_id": db_user.id})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/forgot-password", response_class=HTMLResponse)
async def show_forgot_password_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.post("/forgot-password", response_class=HTMLResponse)
async def process_forgot_password(request: Request, email: str = Form(...), db: AsyncSession = Depends(get_db)):
    # Проверка существования пользователя
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    
    if not user:
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "error": "Пользователь с таким email не найден."
        })
    
    # В реальном приложении здесь будет генерация токена и отправка email
    # Для примера просто показываем сообщение об успехе
    
    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
        "success": "Инструкции по восстановлению пароля отправлены на ваш email."
    })


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    # Выход пользователя - удаляем токен из куки
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response
