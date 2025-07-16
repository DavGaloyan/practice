from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from app.models import Base



class UserCreate(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class RestaurantBase(BaseModel):
    name: str
    cuisine: str
    location: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantOut(RestaurantBase):
    id: int


# Бронирования
class BookingBase(BaseModel):
    restaurant_id: int
    date: datetime
    time: str


class BookingCreate(BookingBase):
    pass


class BookingOut(BookingBase):
    id: int
    user_id: int
    restaurant: RestaurantOut

    class Config:
        from_attributes = True


class FAQ(BaseModel):
    question: str
    answer: str


class Contact(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    message: Optional[str] = None


class UserBookingsOut(BaseModel):
    user: UserOut
    bookings: List[BookingOut]


class BookingResponse(BaseModel):
    id: int
    user_id: int
    table_id: int
    date_time: datetime

    class Config:
        from_attributes = True


class InfoPage(BaseModel):
    title: str
    content: str


class BookingHistory(BaseModel):
    id: int
    restaurant: RestaurantOut
    date: datetime
    time: str

    class Config:
        from_attributes = True


class BookingUpdate(BaseModel):
    date: Optional[datetime] = None
    time: Optional[str] = None
    restaurant_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    bookings: List[BookingOut]

    class Config:
        from_attributes = True
