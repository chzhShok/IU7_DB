from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, Numeric,
    DateTime, Date, Boolean, CheckConstraint
)
from sqlalchemy.sql import func

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name='email_check'),
        CheckConstraint("registration_date BETWEEN '2020-01-01' AND CURRENT_DATE", name='registration_date_check'),
        CheckConstraint("subscription_type IN ('basic', 'standard', 'premium')", name='subscription_type_check'),
        CheckConstraint("created_at <= CURRENT_TIMESTAMP", name='created_at_check'),
        {'schema': 'cinema'},
    )

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(Text, nullable=False)
    registration_date = Column(Date, nullable=False, default=func.current_date())
    subscription_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())

    devices = relationship("Devices", back_populates="user")
    payment_methods = relationship("PaymentMethods", back_populates="user")
    viewing_history = relationship("ViewingHistory", back_populates="user")


class Movies(Base):
    __tablename__ = 'movies'
    __table_args__ = (
        CheckConstraint("release_year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE) + 5", name='release_year_check'),
        CheckConstraint("duration_minutes > 0", name='duration_minutes_check'),
        CheckConstraint("imdb_rating BETWEEN 0 AND 10", name='imdb_rating_check'),
        CheckConstraint("created_at <= CURRENT_TIMESTAMP", name='created_at_check'),
        {'schema': 'cinema'},
    )

    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    director = Column(Text, nullable=False)
    release_year = Column(Integer)
    genres = Column(Text)
    duration_minutes = Column(Integer)
    imdb_rating = Column(Numeric(2, 1))
    created_at = Column(DateTime, default=func.current_timestamp())

    viewing_history = relationship("ViewingHistory", back_populates="movie")


class Devices(Base):
    __tablename__ = 'devices'
    __table_args__ = (
        CheckConstraint("device_type IN ('smarttv', 'phone', 'tablet', 'pc', 'console')", name='device_type_check'),
        CheckConstraint("last_login_date <= CURRENT_DATE", name='last_login_date_check'),
        CheckConstraint("created_at <= CURRENT_TIMESTAMP", name='created_at_check'),
        {'schema': 'cinema'},
    )

    device_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('cinema.users.user_id', ondelete='CASCADE'), nullable=False)
    device_type = Column(String(20), nullable=False)
    device_name = Column(String(255), nullable=False)
    last_login_date = Column(Date)
    app_version = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    user = relationship("Users", back_populates="devices")
    viewing_history = relationship("ViewingHistory", back_populates="device")


class PaymentMethods(Base):
    __tablename__ = 'payment_methods'
    __table_args__ = (
        CheckConstraint("method_type IN ('credit card', 'debit card', 'paypal', 'google pay', 'apple pay')", name='method_type_check'),
        CheckConstraint("card_last_digits::varchar(4) ~ '^[0-9]{4}$'", name='card_last_digits_check'),
        CheckConstraint("added_date <= CURRENT_TIMESTAMP", name='added_date_check'),
        CheckConstraint("expiry_date > added_date", name='expiry_date_check'),
        CheckConstraint("created_at <= CURRENT_TIMESTAMP", name='created_at_check'),
        {'schema': 'cinema'},
    )

    payment_method_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('cinema.users.user_id', ondelete='CASCADE'), nullable=False)
    method_type = Column(String(20), nullable=False)
    card_last_digits = Column(Numeric(4, 0))
    is_default = Column(Boolean, default=False)
    added_date = Column(Date, nullable=False, default=func.current_date())
    expiry_date = Column(Date)
    created_at = Column(DateTime, default=func.current_timestamp())

    user = relationship("Users", back_populates="payment_methods")


class ViewingHistory(Base):
    __tablename__ = 'viewing_history'
    __table_args__ = (
        CheckConstraint("start_time <= CURRENT_TIMESTAMP", name='start_time_check'),
        CheckConstraint("end_time >= start_time", name='end_time_check'),
        CheckConstraint("viewed_percentage BETWEEN 0 AND 100", name='viewed_percentage_check'),
        CheckConstraint("created_at <= CURRENT_TIMESTAMP", name='created_at_check'),
        {'schema': 'cinema'},
    )

    view_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('cinema.users.user_id', ondelete='CASCADE'), nullable=False)
    movie_id = Column(Integer, ForeignKey('cinema.movies.movie_id', ondelete='CASCADE'), nullable=False)
    device_id = Column(Integer, ForeignKey('cinema.devices.device_id', ondelete='CASCADE'), nullable=False)
    start_time = Column(DateTime, nullable=False, default=func.current_timestamp())
    end_time = Column(DateTime)
    viewed_percentage = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())

    user = relationship("Users", back_populates="viewing_history")
    movie = relationship("Movies", back_populates="viewing_history")
    device = relationship("Devices", back_populates="viewing_history")
