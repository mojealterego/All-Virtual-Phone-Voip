# GOWM-X delivery ROADMAP

**Repository:** `mojealterego/All-Virtual-Phone-Voip`  
**Default branch:** `main`  
**Plan date:** 2026-10-19

This roadmap is the single canonical, top-level project tracker. Update it in the **same commit** as work affecting a milestone. Do not mark production readiness from screenshots, mock responses, or documentation alone.

## Stage gates

- **DESIGNED** — documented and scoped, not code.
- **IMPLEMENTED** — code exists, but validation status is tracked separately.
- **TESTED** — a concrete test run and reference is recorded.
- **INTEGRATED** — exercised against a real external service/test environment.
- **PRODUCTION** — deployed and independently verified.
- **PENDING** — no implementation.

## Milestones

| ID | Milestone | State | Acceptance evidence |
| --- | --- | --- | --- |
| 00 | Source inventory, scope, safety constraints | IMPLEMENTED | README and requirements traceability |
| 01 | Repository structure, package, CI workflow | IMPLEMENTED | Files committed; CI job proof required |
| 02 | Deterministic vanity classification / validation | IMPLEMENTED | Unit test suite; CI success required to mark TESTED |
| 03 | Tenant and carrier authentication | IMPLEMENTED | No unauthenticated routing; tests present |
| 04 | Tenant-isolated authorized CLI routing | IMPLEMENTED | Ownership + provider approval + DNO freshness tests present |
| 05 | Inbound DID resolution control plane | IMPLEMENTED | Carrier role and verified DID required |
| 06 | PostgreSQL schema and versioned migrations | IMPLEMENTED | SQL migration; real Postgres integration required |
| 07 | Rust/Tokio Global Alias Engine, API contracts | PENDING | Rust unit/integration tests and benchmarks |
| 08 | Number inventory lifecycle and provider reconciliation | PENDING | Idempotent lease/assign/release and recovery |
| 09 | DID provider adapters (primary/failover) | PENDING | Real provisioning/availability evidence and callbacks |
| 10 | CLI proof, DNO/UKE feeds, policy decision logging | PENDING | Time-bounded feed integrity and blocked-CLI evidence |
| 11 | Kamailio SIP edge/SBC and trunk routing | PENDING | SIPp interop, failover, unauthorized INVITE blocking |
| 12 | FreeSWITCH, SRTP/DTLS, codec/DTMF handling | PENDING | Live call/media quality evidence |
| 13 | Android Kotlin multi-module client | PENDING | Tested build, device tests |
| 14 | Android system calling, Push/FCM, WebRTC | PENDING | Real inbound/outbound and lockscreen scenarios |
| 15 | SMS/MMS gateway, sender rights, DLR | PENDING | Provider MO/MT and message receipt proof |
| 16 | Secure attachment storage and media lifecycle | PENDING | Encryption, URL TTL, anti-malware tests |
| 17 | Stalwart mail/JMAP reverse-alias relay | PENDING | DKIM/SPF/DMARC and reply-flow tests |
| 18 | Vanity number marketplace and reservations | PENDING | Inventory-only results; provider hold and fulfillment |
| 19 | CDR, rating, billing, abuse controls | PENDING | Reconciled usage and refund tests |
| 20 | Privacy, security, compliance and audit | PENDING | External penetration test and jurisdictional review |
| 21 | Reliability, observability, backups and restore | PENDING | SLOs, load tests, independent-host disaster drill |
| 22 | Cross-provider and cross-country E2E validation | PENDING | Documented test calls, SMS/MMS/email and failure matrix |
| 23 | Production launch and ongoing carrier operations | PENDING | Deployment artifacts + verified production call paths |

## Immediate next gates

1. Run CI on Python 3.11 and 3.13; fix any broken tests before designating the core TESTED.
2. Run versioned schema migration and integration tests on a real PostgreSQL instance (test suite currently uses SQLite).
3. Build a provider capability/provisioning contract, including proof of numbering rights, inbound capabilities and release semantics.
4. Implement authoritative DNO ingestion and freshness audit. Do not launch PSTN origination without it.
5. Implement signed policy responses and workload identity between routing control plane and SBC.
6. Only then add Kamailio/FreeSWITCH and validate end-to-end call paths with legitimately provisioned test DID numbers.

## Tracking rule

Never conflate a generated number pattern, an authorized route decision and an actual connected call. Each is an independent observable milestone.
