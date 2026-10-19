from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from avp.api import create_app
from avp.db import Base, VirtualDid
from avp.security import ApiCredentials


TENANT_A = "a" * 48
TENANT_B = "b" * 48
CARRIER = "c" * 48


@pytest.fixture
def ctx():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    app = create_app(
        factory,
        ApiCredentials({"tenant-a": TENANT_A, "tenant-b": TENANT_B}, {"carrier-1": CARRIER}),
    )
    with TestClient(app) as client:
        yield client, factory
    engine.dispose()


@pytest.fixture
def did_factory(ctx):
    _, factory = ctx

    def add(
        *,
        tenant_id: str = "tenant-a",
        e164: str = "+48500123456",
        status: str = "active",
        voice_enabled: bool = True,
        cli_verified: bool = True,
        dno_blocked: bool = False,
        dno_checked_at: datetime | None = None,
        provisioning_verified_at: datetime | None = None,
        target_uri: str = "sips:account-1@voice.example.test",
    ) -> VirtualDid:
        now = datetime.now(timezone.utc)
        did = VirtualDid(
            tenant_id=tenant_id,
            e164=e164,
            alias="primary",
            provider_id="carrier-1",
            provider_reference="assigned-123",
            target_uri=target_uri,
            status=status,
            voice_enabled=voice_enabled,
            sms_enabled=False,
            cli_verified=cli_verified,
            dno_blocked=dno_blocked,
            dno_checked_at=dno_checked_at if dno_checked_at is not None else now,
            provisioning_verified_at=(
                provisioning_verified_at
                if provisioning_verified_at is not None else now
            ),
        )
        with factory() as session:
            session.add(did)
            session.commit()
            session.refresh(did)
        return did

    return add


def token(value: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {value}"}
