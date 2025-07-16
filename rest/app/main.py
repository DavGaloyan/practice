from app.api import auth, restaurants, bookings, user_profile, info_pages, pages, feedback
from app.core.database import create_tables
from app.core.config import settings
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Инициализация приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Система бронирования ресторанов."
)

# Настройка шаблонов
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Подключение статики
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# Подключение маршрутов
app.include_router(pages.router, tags=["Страницы"])  # Маршруты для веб-страниц
app.include_router(auth.router, prefix="/auth", tags=["Авторизация"])
app.include_router(bookings.router, tags=["Бронирования"])  # Обновлено для работы с веб-формами
app.include_router(restaurants.router, tags=["Рестораны"])  # Маршруты для веб-страниц ресторанов
app.include_router(user_profile.router, tags=["Профили"])  # Маршруты для веб-страниц профилей
app.include_router(info_pages.router, prefix="/api/info", tags=["API Информация"])
app.include_router(feedback.router, tags=["Обратная связь"])

# Стартовые действия
@app.on_event("startup")
async def on_startup():
    await create_tables()

@app.exception_handler(404)
async def custom_404_handler(request, __):
    return templates.TemplateResponse("404.html", {"request": request})

# Корневой маршрут обрабатывается в pages.py)
