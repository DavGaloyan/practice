from fastapi import APIRouter
from app.schemas import InfoPage

router = APIRouter()

@router.get("/about", response_model=InfoPage)
async def about():
    return {
        "title": "О нас",
        "content": "Наш проект создан для упрощения бронирования ресторанов. Наша миссия – сделать ваш опыт удобным и приятным!"
    }

