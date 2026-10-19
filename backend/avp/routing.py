"""Fail-closed call authorization, independent of SIP header construction."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import VirtualDid
from .security import Principal
from .vanity import require_e164


SIP_URI_RE = re.compile(
    r"^sips?:[A-Za-z0-9_.+~-]+@[A-Za-z0-9.-]+(?::[0-9]{1,5})?$"
)
MAX_DNO_CHECK_AGE = timedelta(hours=24)


class RoutingDenied(Exception):
    """Explicit denial, with no fallback to an arbitrary CLI or destination."""


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def authorize_outbound(
    session: Session,
    principal: Principal,
    callee_e164: str,
    cli_e164: str,
    *,
    now: datetime | None = None,
) -> dict[str, str]:
    if principal.role != "tenant":
        raise RoutingDenied("Tenant credentials required")
    require_e164(callee_e164)
    require_e164(cli_e164)
    did = session.scalar(
        select(VirtualDid).where(
            VirtualDid.tenant_id == principal.identity,
            VirtualDid.e164 == cli_e164,
        )
    )
    if did is None or did.status != "active":
        raise RoutingDenied("CLI is not owned and active")
    if not did.voice_enabled or not did.cli_verified or did.provisioning_verified_at is None:
        raise RoutingDenied("Carrier verification incomplete")
    if did.dno_blocked or did.dno_checked_at is None:
        raise RoutingDenied("DNO clearance missing")
    clock = now or datetime.now(timezone.utc)
    age = _utc(clock) - _utc(did.dno_checked_at)
    if age < timedelta(0) or age > MAX_DNO_CHECK_AGE:
        raise RoutingDenied("DNO clearance stale")
    # SBC, not the API caller, assembles verified SIP identity headers.
    return {
        "status": "AUTHORIZED",
        "callee_e164": callee_e164,
        "effective_cli": did.e164,
        "did_id": did.id,
        "provider_id": did.provider_id,
    }


def resolve_inbound(
    session: Session,
    principal: Principal,
    did_e164: str,
) -> dict[str, str]:
    if principal.role != "carrier":
        raise RoutingDenied("Carrier ingress credentials required")
    require_e164(did_e164)
    did = session.scalar(select(VirtualDid).where(VirtualDid.e164 == did_e164))
    if (
        did is None
        or did.status != "active"
        or not did.voice_enabled
        or did.provisioning_verified_at is None
        or not SIP_URI_RE.fullmatch(did.target_uri)
    ):
        raise RoutingDenied("DID is not routable")
    return {"status": "ROUTED", "did_id": did.id, "target_uri": did.target_uri}
