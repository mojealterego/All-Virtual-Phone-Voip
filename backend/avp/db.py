"""Persistent inventory of operator-provisioned and verified DID resources."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Index, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VirtualDid(Base):
    __tablename__ = "virtual_dids"
    __table_args__ = (
        UniqueConstraint("tenant_id", "alias", name="uq_tenant_alias"),
        Index("ix_virtual_dids_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    e164: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    alias: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_reference: Mapped[str] = mapped_column(String(256), nullable=False)
    target_uri: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="reserved")
    voice_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cli_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dno_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    dno_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provisioning_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
