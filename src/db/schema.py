from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TransactionRaw(Base):
    __tablename__ = "transactions_raw"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_file: Mapped[str | None] = mapped_column(String(255))
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    posted_at: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    payload: Mapped[dict | list | None] = mapped_column(JSON)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class TransactionClean(Base):
    __tablename__ = "transactions_clean"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions_raw.id"), index=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(255), index=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class CategoryRule(Base, TimestampMixin):
    __tablename__ = "category_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pattern: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class MerchantAlias(Base, TimestampMixin):
    __tablename__ = "merchant_aliases"
    __table_args__ = (UniqueConstraint("raw_name", "normalized_name", name="uq_merchant_aliases_names"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open", index=True)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions_clean.id"), index=True)
    details: Mapped[dict | list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
