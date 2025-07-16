from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    bookings = relationship("Booking", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cuisine = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(String)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    open_time = Column(String, nullable=True)
    close_time = Column(String, nullable=True)

    tables = relationship("Table", back_populates="restaurant")


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    number = Column(Integer)
    seats = Column(Integer)
    status = Column(String, default="available")  # available, reserved, occupied

    restaurant = relationship("Restaurant", back_populates="tables")
    bookings = relationship("Booking", back_populates="table")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    date_time = Column(DateTime)
    status = Column(String, default="confirmed")  # confirmed, cancelled, completed

    user = relationship("User", back_populates="bookings")
    table = relationship("Table", back_populates="bookings")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    subject = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    user = relationship("User", back_populates="feedback")
