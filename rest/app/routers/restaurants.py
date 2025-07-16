from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Restaurant
from app.schemas import RestaurantCreate, RestaurantOut
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[RestaurantOut])
async def get_restaurants(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Restaurant))
    return result.scalars().all()

@router.post("/", response_model=RestaurantOut)
async def create_restaurant(restaurant: RestaurantCreate, db: AsyncSession = Depends(get_db)):
    db_restaurant = Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant

@router.get("/search/", response_model=list[RestaurantOut])
async def search_restaurants(
    name: str = None, cuisine: str = None, location: str = None, db: AsyncSession = Depends(get_db)
):
    query = select(Restaurant)
    if name:
        query = query.where(Restaurant.name.ilike(f"%{name}%"))
    if cuisine:
        query = query.where(Restaurant.cuisine.ilike(f"%{cuisine}%"))
    if location:
        query = query.where(Restaurant.location.ilike(f"%{location}%"))
    async with db.begin():
        result = await db.execute(query)
    return result.scalars().all()