"""HTTP transport for validated, authenticated routing decisions.

Production startup: uvicorn avp.api:create_app_from_env --factory
"""
from __future__ import annotations

import os
from collections.abc import Iterator

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .routing import RoutingDenied, authorize_outbound, resolve_inbound
from .security import ApiCredentials, Principal
from .vanity import evaluate_number


E164_PATTERN = r"^\+[1-9][0-9]{1,14}$"


class OutboundRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    callee_e164: str = Field(pattern=E164_PATTERN, max_length=16)
    cli_e164: str = Field(pattern=E164_PATTERN, max_length=16)


class InboundRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    did_e164: str = Field(pattern=E164_PATTERN, max_length=16)


class VanityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    e164: str = Field(pattern=E164_PATTERN, max_length=16)


def create_app(
    sessions: sessionmaker[Session],
    credentials: ApiCredentials,
) -> FastAPI:
    app = FastAPI(
        title="All Virtual Phone GOWM-X Control Plane",
        version="0.1.0",
        description="Authorized DID routing decisions; no telephony/media provisioning.",
    )

    def get_session() -> Iterator[Session]:
        with sessions() as session:
            yield session

    def principal(
        authorization: str | None = Header(default=None),
    ) -> Principal:
        scheme, separator, token = (authorization or "").partition(" ")
        if not separator or scheme.lower() != "bearer" or not token:
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        result = credentials.resolve(token)
        if result is None:
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return result

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/readyz")
    def ready(session: Session = Depends(get_session)) -> dict[str, str]:
        try:
            session.execute(text("SELECT 1"))
            return {"status": "ready"}
        except Exception:
            raise HTTPException(status_code=503, detail="database unavailable") from None

    @app.post("/v1/route/outbound")
    def outbound(
        request: OutboundRequest,
        current: Principal = Depends(principal),
        session: Session = Depends(get_session),
    ) -> dict[str, str]:
        try:
            return authorize_outbound(
                session, current, request.callee_e164, request.cli_e164
            )
        except RoutingDenied:
            raise HTTPException(status_code=403, detail="Routing denied") from None

    @app.post("/v1/route/inbound")
    def inbound(
        request: InboundRequest,
        current: Principal = Depends(principal),
        session: Session = Depends(get_session),
    ) -> dict[str, str]:
        try:
            return resolve_inbound(session, current, request.did_e164)
        except RoutingDenied:
            raise HTTPException(status_code=404, detail="Route not found") from None

    @app.post("/v1/vanity/classify")
    def vanity(
        request: VanityRequest,
        current: Principal = Depends(principal),
    ) -> dict:
        if current.role != "tenant":
            raise HTTPException(status_code=403, detail="Tenant credentials required")
        return evaluate_number(request.e164).as_dict()

    return app


def create_app_from_env() -> FastAPI:
    database_url = os.environ.get("AVP_DATABASE_URL", "")
    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError("AVP_DATABASE_URL must specify PostgreSQL with psycopg")
    credentials = ApiCredentials.from_environment()
    engine = create_engine(database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
    return create_app(sessionmaker(bind=engine, expire_on_commit=False), credentials)
