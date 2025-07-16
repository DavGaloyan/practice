"""
Скрипт для заполнения базы данных тестовыми данными
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.core.models import Base, Restaurant, Table, User, Booking
from app.core.security import get_password_hash

load_dotenv()

DATABASE_URL = os.getenv('DB_ADMIN')
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    from app.core.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Создаем рестораны
        restaurants = [
            {
                "name": "Итальянский ресторан",
                "cuisine": "Итальянская",
                "location": "ул. Пушкина, 10",
                "description": "Аутентичная итальянская кухня в сердце города. Пицца, паста и вино.",
                "address": "ул. Пушкина, 10",
                "phone": "+7 (495) 123-45-67",
                "email": "italian@example.com",
                "open_time": "10:00",
                "close_time": "22:00"
            },
            {
                "name": "Японский ресторан Сакура",
                "cuisine": "Японская",
                "location": "ул. Ленина, 15",
                "description": "Суши, роллы и другие блюда японской кухни. Уютная атмосфера и быстрое обслуживание.",
                "address": "ул. Ленина, 15",
                "phone": "+7 (495) 234-56-78",
                "email": "sakura@example.com",
                "open_time": "11:00",
                "close_time": "23:00"
            },
            {
                "name": "Грузинский ресторан Сакартвело",
                "cuisine": "Грузинская",
                "location": "ул. Гоголя, 7",
                "description": "Настоящие хачапури и хинкали. Гостеприимная атмосфера и живая музыка по выходным.",
                "address": "ул. Гоголя, 7",
                "phone": "+7 (495) 345-67-89",
                "email": "sakartvelo@example.com",
                "open_time": "12:00",
                "close_time": "00:00"
            },
            {
                "name": "Французское бистро",
                "cuisine": "Французская",
                "location": "ул. Чехова, 22",
                "description": "Изысканная французская кухня, круассаны и вино. Романтическая атмосфера для особых случаев.",
                "address": "ул. Чехова, 22",
                "phone": "+7 (495) 456-78-90",
                "email": "bistro@example.com",
                "open_time": "09:00",
                "close_time": "21:00"
            },
            {
                "name": "Американский бургер-бар",
                "cuisine": "Американская",
                "location": "пр. Ленина, 45",
                "description": "Сочные бургеры, картофель фри и молочные коктейли. Атмосфера в стиле американских диннеров 50-х.",
                "address": "пр. Ленина, 45",
                "phone": "+7 (495) 567-89-01",
                "email": "burger@example.com",
                "open_time": "10:00",
                "close_time": "23:00"
            },
            {
                "name": "Индийский ресторан Тадж Махал",
                "cuisine": "Индийская",
                "location": "ул. Достоевского, 12",
                "description": "Ароматные специи и традиционные блюда индийской кухни. Вегетарианские опции доступны.",
                "address": "ул. Достоевского, 12",
                "phone": "+7 (495) 678-90-12",
                "email": "tajmahal@example.com",
                "open_time": "11:00",
                "close_time": "22:00"
            }
        ]
        
        restaurant_objects = []
        for restaurant_data in restaurants:
            restaurant = Restaurant(**restaurant_data)
            session.add(restaurant)
            restaurant_objects.append(restaurant)
        
        await session.commit()
        
        # Создаем столики для каждого ресторана
        for restaurant in restaurant_objects:
            # Для каждого ресторана создаем разное количество столиков
            num_tables = 10 if restaurant.id % 2 == 0 else 8
            
            for i in range(1, num_tables + 1):
                # Разное количество мест для разных столиков
                seats = 2 if i % 3 == 0 else (4 if i % 3 == 1 else 6)
                
                table = Table(
                    restaurant_id=restaurant.id,
                    number=i,
                    seats=seats
                )
                session.add(table)
        
        await session.commit()
        
        # Создаем тестового пользователя, если его нет
        from sqlalchemy import select
        test_user_email = "test@example.com"
        user_query = select(User).where(User.email == test_user_email)
        result = await session.execute(user_query)
        user = result.scalars().first()
        
        if not user:
            test_user = User(
                email=test_user_email,
                hashed_password=get_password_hash("password123")
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            user_id = test_user.id
        else:
            user_id = user.id
            
        # Добавляем несколько бронирований для тестового пользователя
        # Добавляем несколько бронирований для тестового пользователя
        # Получаем столики из разных ресторанов
        from sqlalchemy import select
        
        # Столики из первого ресторана
        tables_query1 = select(Table).where(Table.restaurant_id == 1).limit(2)
        result1 = await session.execute(tables_query1)
        tables1 = result1.scalars().all()
        
        # Столики из второго ресторана
        tables_query2 = select(Table).where(Table.restaurant_id == 2).limit(1)
        result2 = await session.execute(tables_query2)
        tables2 = result2.scalars().all()
        
        # Столики из третьего ресторана
        tables_query3 = select(Table).where(Table.restaurant_id == 3).limit(1)
        result3 = await session.execute(tables_query3)
        tables3 = result3.scalars().all()
        
        # Создаем бронирования на разные даты в разных ресторанах
        if tables1:
            # Предстоящее бронирование
            booking1 = Booking(
                user_id=user_id,
                table_id=tables1[0].id,
                date_time=datetime.now() + timedelta(days=2),
                status="confirmed"
            )
            
            # Прошедшее бронирование
            booking2 = Booking(
                user_id=user_id,
                table_id=tables1[1].id if len(tables1) > 1 else tables1[0].id,
                date_time=datetime.now() - timedelta(days=5),
                status="completed"
            )
            
            session.add(booking1)
            session.add(booking2)
        
        if tables2:
            # Бронирование на сегодня
            booking3 = Booking(
                user_id=user_id,
                table_id=tables2[0].id,
                date_time=datetime.now() + timedelta(hours=3),
                status="confirmed"
            )
            session.add(booking3)
        
        if tables3:
            # Отмененное бронирование
            booking4 = Booking(
                user_id=user_id,
                table_id=tables3[0].id,
                date_time=datetime.now() + timedelta(days=1),
                status="cancelled"
            )
            session.add(booking4)
            
        await session.commit()

async def main():
    # Пересоздаем таблицы
    from app.core.database import drop_tables, create_tables
    print("Dropping all tables...")
    await drop_tables()
    print("Creating new tables...")
    await create_tables()
    print("Database reset completed!")
    
    # Заполняем данными
    await seed_data()
    print("База данных успешно заполнена тестовыми данными!")

if __name__ == "__main__":
    asyncio.run(main())