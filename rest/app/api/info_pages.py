from fastapi import APIRouter, HTTPException, Form
from app.core.schemas import InfoPage

router = APIRouter()

@router.get("/about", response_model=InfoPage)
async def about():
    """О нас: описание проекта, миссия, ценности."""
    return {
        "title": "О нас",
        "content": "Наш проект создан для упрощения бронирования ресторанов. "
                   "Наша миссия – сделать ваш опыт удобным и приятным! "
                   "Мы ценим ваш комфорт и работаем над тем, чтобы каждая деталь вашего посещения была продумана."
    }


@router.get("/faq", response_model=list[InfoPage])
async def faq():
    """FAQ: ответы на часто задаваемые вопросы."""
    return [
        {
            "title": "Как зарегистрироваться?",
            "content": "Нажмите на кнопку 'Регистрация' и введите ваш email и пароль."
        },
        {
            "title": "Как отменить бронирование?",
            "content": "Перейдите в личный кабинет и выберите активное бронирование для отмены."
        },
        {
            "title": "Что делать, если не пришло подтверждение?",
            "content": "Проверьте папку 'Спам'. Если письмо отсутствует, напишите в поддержку."
        },
    ]


@router.get("/contacts", response_model=InfoPage)
async def contacts():
    """Контакты: способы связи с поддержкой."""
    return {
        "title": "Контакты",
        "content": "Вы можете связаться с нами по email support@restaurant.com или телефону +1(234)5678900. "
                   "Также вы можете воспользоваться формой обратной связи ниже."
    }


@router.post("/contacts/feedback")
async def feedback(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
):
    """Форма обратной связи."""
    # Реализация: отправка сообщения в лог/на email/в базу данных (пример логирования)
    if not name or not email or not message:
        raise HTTPException(status_code=400, detail="Все поля формы обязательны для заполнения")

    # Пример: отправка сообщения в лог (замените на вашу реализацию)
    print(f"Сообщение от {name} ({email}): {message}")

    return {"message": "Ваше сообщение отправлено. Спасибо за обратную связь!"}
