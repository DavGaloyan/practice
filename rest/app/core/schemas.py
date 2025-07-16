from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


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

    class Config:
        from_attributes = True


class TableOut(BaseModel):
    id: int
    number: int
    seats: int

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    restaurant_id: int
    date: datetime
    time: str


class BookingCreate(BaseModel):
    restaurant_id: int
    table_id: int
    date_time: datetime
class BookingOut(BaseModel):
    id: int
    user_id: int
    date_time: datetime
    restaurant: RestaurantOut
    table: TableOut

    class Config:
        from_attributes = True


class BookingPublicResponse(BaseModel):
    id: int
    restaurant_name: str
    date_time: datetime

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

    class Config:
        from_attributes = True


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
    date_time: Optional[datetime] = None
    restaurant_id: Optional[int] = None
    table_id: Optional[int] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    bookings: List[BookingOut]

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

    class Config:
        from_attributes = True


class FeedbackOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    subject: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
