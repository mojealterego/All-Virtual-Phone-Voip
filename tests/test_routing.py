from __future__ import annotations

from datetime import datetime, timedelta, timezone

from avp.db import VirtualDid
from avp.security import Principal
from avp.routing import RoutingDenied, authorize_outbound
from .conftest import CARRIER, TENANT_A, TENANT_B, token


CALL = {"callee_e164": "+48221234567", "cli_e164": "+48500123456"}


def test_health_and_readiness(ctx):
    client, _ = ctx
    assert client.get("/healthz").json() == {"status": "alive"}
    assert client.get("/readyz").status_code == 200


def test_requires_real_authentication(ctx):
    client, _ = ctx
    assert client.post("/v1/route/outbound", json=CALL).status_code == 401
    assert client.post("/v1/route/outbound", json=CALL, headers=token("invalid")).status_code == 401


def test_valid_outbound_requires_verified_owned_did(ctx, did_factory):
    client, _ = ctx
    did_factory()
    res = client.post("/v1/route/outbound", json=CALL, headers=token(TENANT_A))
    assert res.status_code == 200
    assert res.json()["effective_cli"] == "+48500123456"
    assert "target_uri" not in res.json()


def test_tenant_isolation_blocks_cli_theft(ctx, did_factory):
    client, _ = ctx
    did_factory()
    res = client.post("/v1/route/outbound", json=CALL, headers=token(TENANT_B))
    assert res.status_code == 403


def test_outbound_rejects_unregistered_cli(ctx):
    client, _ = ctx
    res = client.post("/v1/route/outbound", json=CALL, headers=token(TENANT_A))
    assert res.status_code == 403


def test_dno_flag_rejects_outbound(ctx, did_factory):
    client, _ = ctx
    did_factory(dno_blocked=True)
    assert client.post("/v1/route/outbound", json=CALL, headers=token(TENANT_A)).status_code == 403


def test_stale_dno_rejects_outbound(ctx, did_factory):
    client, _ = ctx
    did_factory(dno_checked_at=datetime.now(timezone.utc) - timedelta(days=2))
    assert client.post("/v1/route/outbound", json=CALL, headers=token(TENANT_A)).status_code == 403


def test_provisioning_and_cli_proof_reject(ctx, did_factory):
    client, factory = ctx
    did = did_factory(cli_verified=False)
    assert client.post("/v1/route/outbound", json=CALL, headers=token(TENANT_A)).status_code == 403
    with factory() as session:
        item = session.get(VirtualDid, did.id)
        item.cli_verified = True
        item.provisioning_verified_at = None
        session.commit()
    assert client.post("/v1/route/outbound", json=CALL, headers=token(TENANT_A)).status_code == 403


def test_carrier_cannot_originate(ctx, did_factory):
    client, _ = ctx
    did_factory()
    assert client.post("/v1/route/outbound", json=CALL, headers=token(CARRIER)).status_code == 403


def test_inbound_requires_carrier_and_active_provisioned_did(ctx, did_factory):
    client, _ = ctx
    did_factory()
    req = {"did_e164": "+48500123456"}
    assert client.post("/v1/route/inbound", json=req, headers=token(TENANT_A)).status_code == 404
    res = client.post("/v1/route/inbound", json=req, headers=token(CARRIER))
    assert res.status_code == 200
    assert res.json()["target_uri"] == "sips:account-1@voice.example.test"


def test_inbound_must_not_route_unsafe_uri(ctx, did_factory):
    client, _ = ctx
    did_factory(target_uri="sips:account-1@voice.example.test%0d%0aInjected")
    assert client.post(
        "/v1/route/inbound",
        json={"did_e164": "+48500123456"},
        headers=token(CARRIER),
    ).status_code == 404


def test_inbound_rejects_unprovisioned(ctx, did_factory):
    client, factory = ctx
    did = did_factory()
    with factory() as session:
        item = session.get(VirtualDid, did.id)
        item.provisioning_verified_at = None
        session.commit()
    assert client.post(
        "/v1/route/inbound",
        json={"did_e164": "+48500123456"},
        headers=token(CARRIER),
    ).status_code == 404


def test_invalid_e164_and_extra_field_fail_validation(ctx, did_factory):
    client, _ = ctx
    did_factory()
    invalid = {**CALL, "cli_e164": "+00000"}
    assert client.post("/v1/route/outbound", json=invalid, headers=token(TENANT_A)).status_code == 422
    injected = {**CALL, "tenant_id": "tenant-b"}
    assert client.post("/v1/route/outbound", json=injected, headers=token(TENANT_A)).status_code == 422
