from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    base_url: Mapped[Optional[str]] = mapped_column(String(255))

    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="source")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    location_city: Mapped[Optional[str]] = mapped_column(String(100))

    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="company")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(String(200))
    location_city: Mapped[Optional[str]] = mapped_column(String(100))
    salary_min: Mapped[Optional[float]] = mapped_column(Float)
    salary_max: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="CNY")
    description: Mapped[Optional[str]] = mapped_column(Text)
    posted_at: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 外键关系
    source: Mapped["Source"] = relationship("Source", back_populates="jobs")
    company: Mapped["Company"] = relationship("Company", back_populates="jobs")
