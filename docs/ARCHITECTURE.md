# GOWM-X architecture — decision record and service boundaries

## Source baseline

The three supplied PDFs specify (1) SIP/ENUM routing and PostgreSQL/Redis, (2) Rust/Tokio vanity and Kamailio/FreeSWITCH/SMPP, and (3) an expanded platform containing Android Jetpack Compose/CallsManager, voice, SMS/MMS, SMTP/JMAP reverse aliases and an Obsidian/Gold visual system. See [REQUIREMENTS.md](REQUIREMENTS.md) for traceability.

## Logical planes

```text
Android (Kotlin / Jetpack Compose / CallsManager)
    | TLS: authenticated control API         | SRTP/DTLS: media
    v                                        v
API Gateway / IAM / Rate limits         WebRTC / TURN
    |                                        |
    v                                        v
Routing Control Plane                    Kamailio / FreeSWITCH
    |         |                                |
    |         +--- Provider-number Inventory   +---> Licensed carrier SIP trunk
    |         +--- DNO/CLI approval source     |
    |         +--- Outbound/Inbound decisions <+
    |
    +---> PostgreSQL (source of truth)
    +---> Redis (future short-lived call state only)

Messaging plane: authenticated API -> compliant SMS provider / SMPP -> DLR and MO callbacks
Mail plane: authenticated API -> reverse-alias service -> Stalwart SMTP/JMAP
Observability: structured logs, traces, CDR/event journal, privacy-aware metrics
```

**Implemented now:** a Python/FastAPI control-plane slice with database-backed, tenant-isolated, authorized outbound decisions; carrier-only inbound DID lookup; and deterministic vanity tier scoring. The API does **not** control Kamailio, FreeSWITCH, a carrier, Android, SMPP, or Stalwart. There is no real-time DID reservation.

**Future Rust/Tokio component:** Global Alias Engine, an independently deployed high-throughput lookup service behind the same explicit policy boundary. The Python API remains a control-plane adapter. Rust, Zenoh, Python and Android component choices must be benchmarked, not assumed to meet sub-millisecond targets.

## Contracts available in v0.1

- `GET /healthz` — process liveness
- `GET /readyz` — database readiness
- `POST /v1/vanity/classify` — numeric candidate classification, not purchase/reservation
- `POST /v1/route/outbound` — authorized CLI/destination decision; no outbound call is dialed
- `POST /v1/route/inbound` — trusted-carrier DID resolution; no inbound call is answered

Authentication: `Authorization: Bearer <secret>`. The process config is:

- `AVP_DATABASE_URL`: PostgreSQL connection string with `postgresql+psycopg://`
- `AVP_API_KEYS_JSON`: JSON with `tenants` and `carriers` maps of identity-to-unique-secret, each secret at least 32 UTF-8 bytes

Credentials are injected by a secret manager; not stored in Git. TLS or mTLS and gateway request filtering are mandatory for deployment. The current credentials adapter is bootstrap-level: per-tenant key rotation, key IDs, asymmetric workload identity and revocation/audit require implementation before public release.

## Domain status transitions

```text
reserved --(provider assignment + proof + DNO check)--> active
   |                                                      |
   +-----------------------> released                     v
                                                      suspended
                                                          |
                                        (compliance release) active
                                                          |
                                                    released
```

The database is authoritative for entitlement and active routing. A candidate vanity number does not create an inventory record. A provider allocation must be confirmed out-of-band by a dedicated, authenticated provisioning integration (not implemented).

## Failure invariants

- DNO match, missing DNO proof or check older than 24h: outbound denial; timeout means denial.
- Missing verified carrier assignment, disabled/foreign DID, invalid E.164: denial.
- No silent fallback to unverified From/P-Asserted-Identity or alternative "grey-route" gateways.
- Stale Redis cannot override PostgreSQL ownership or entitlement.
- SIP injection is blocked at domain-contract boundaries; SIP identity construction is delegated only to trusted SBC adapters.
- No guaranteed global SMS/MMS support from a voice-only number; capabilities are provider-specific.

## Operational readiness gates

The control plane needs a migration runner, database permissions split, log redaction, durable provider reconciliation, backups, failover verification, observability and multi-host recovery tests. No SLA, delivery guarantee, STIR/SHAKEN attestation or legal compliance is claimed without carrier verification and field evidence.
