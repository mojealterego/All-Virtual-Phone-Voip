# All Virtual Phone VoIP — GOWM-X

Multi-channel telecommunications platform: licensed/verified DID numbers, authorized CLI, SIP/WebRTC voice routing, SMS/MMS, and e-mail reverse aliases.

> **Status: INITIAL DEVELOPMENT.** This repository is not a deployed telephony service. No public PSTN calls, DID provisioning, SMS, MMS, WebRTC media, or e-mail delivery are available yet.

## Project navigation

- [ROADMAP.md](ROADMAP.md) — milestones, acceptance criteria, and verified completion states
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — service boundaries and data flow
- [docs/SECURITY.md](docs/SECURITY.md) — abuse prevention and trust boundaries
- [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) — traceability to the three supplied PDF specifications
- [backend/avp/](backend/avp/) — Python routing control plane and vanity-number scoring
- [tests/](tests/) — backend tests

## Architectural invariants

1. A generated telephone number is **only a candidate**. It cannot become an active PSTN identity unless a legitimate provider provisions it and confirms inbound routing.
2. Outbound caller ID is restricted to the **authenticated tenant's active, provider-verified** DID numbers; prohibited DNO entries and stale DNO checks fail closed.
3. API credentials establish tenant/carrier roles independently of untrusted request data.
4. Inbound public PSTN traffic resolves only provisioned active DID records.
5. An alphanumeric alias is *on-net only* until an appropriate carrier capability is explicitly confirmed. It cannot be assumed to support PSTN callback or bidirectional SMS.
6. Routing authorization is not the same as a completed call: SIP signaling and media integration are separate deliverables.

## First development milestone

The routing control plane is implemented in Python/FastAPI and SQLAlchemy. Production configuration requires an explicit database URL, role-specific API credentials and HTTPS/mTLS termination upstream. The service returns **routing decisions**, not simulated completed calls.

CI verification: [25 tests passed on Python 3.11 and 3.13](https://github.com/mojealterego/All-Virtual-Phone-Voip/actions/runs/39212431543). See [ROADMAP.md](ROADMAP.md) for the exact validated commit and remaining gates.

### Local development

Install Python 3.11+ and run:

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Runtime startup (requires separately configured PostgreSQL schema and secrets):

```bash
uvicorn avp.api:create_app_from_env --factory --host 127.0.0.1 --port 8080
```

Required runtime environment variables: `AVP_DATABASE_URL`, `AVP_API_KEYS_JSON`. See security and architecture docs for format. Never expose the API directly to the public internet.

## Licensing and external dependencies

The future media plane requires provider contracts, numbering-rights validation, jurisdiction-specific regulatory review, consent/abuse safeguards, and operational telephony infrastructure. The PDF source documents are design inputs, not evidence of completed carrier integrations.
