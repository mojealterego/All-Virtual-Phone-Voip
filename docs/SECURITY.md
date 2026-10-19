# Security and abuse-prevention policy

## Threat model

| Risk | Control currently implemented | Before production |
| --- | --- | --- |
| Spoofed outbound CLI | Tenant ownership, active DID, carrier proof, voice capability and fresh DNO clearance | Integration with authoritative carrier and regulator feeds |
| Tenant impersonation | API keys establish role + tenant ID independently of JSON request | Identity provider, mTLS/workload identity, automated key rotation |
| Unauthorized incoming routing | Carrier-only API role; provider-provisioned DID checks | Allowlisted, mutually authenticated SIP ingress and reconciliation |
| SIP header injection | Validated E.164 and restricted SIP target URI | SBC header parser tests and canonicalization / fuzz testing |
| Stale compliance state | DNO checks fail closed after 24 h | Scheduled verified DNO feed, integrity and staleness monitoring |
| Cross-tenant disclosure | Repository queries bound to authenticated tenant | Row-level security (RLS), DB role separation, integration tests |
| Resource exhaustion | Request sizes constrained by schema | Edge quotas, request timeout, API throttling, admission controls |
| Secret disclosure | No source-embedded production secrets | Secret manager, audit logs, leakage scanning, key revoke drills |
| Telecom fraud/smishing | No arbitrary spoofing or SMS sender API | Provider anti-fraud, abuse reporting, throttling, user verification |
| Replay/credential theft | TLS/mTLS required at gateway | Short-lived signed workload credentials + nonce/audience semantics |

## Operational non-negotiables

- Do not publish API keys, carrier tokens, SIP trunk passwords, database credentials or user data.
- Use legally assigned / verified E.164 numbers only for public PSTN caller identity.
- Do not send a call on a number marked DNO or with unverified/cross-tenant CLI.
- Do not claim universal STIR/SHAKEN support: attestation depends on originating service provider and its authorization.
- Treat on-net free-form aliases separately from actual routed PSTN/DID identifiers.
- Preserve opt-in/consent, anti-spam policy, complaint workflow and data retention controls.
- For recording, media and call metadata, obtain required notice/consent and implement regional retention policies.
- Keep SIP control plane off public internet behind a trusted authenticated gateway.

## Current limitations

The initial stage stores compliance flags supplied by trusted back-office processing; automatic regulator and carrier synchronization is **not yet implemented**. The local SQLite test suite does not prove isolation across independent DB hosts. An API success returns an authorization decision only, not a successful call or guaranteed callback.
