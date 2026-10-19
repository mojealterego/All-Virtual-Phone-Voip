# Requirements traceability: supplied PDFs

Sources supplied by the project owner (2026-10-19):

- **S1**: `All_Virtual_Phone_VoIP_Architecture_261018_221439.pdf` (2 pages)
- **S2**: `All_Virtual_Phone_VoIP_Advanced_Architecture_261018_221422.pdf` (2 pages)
- **S3**: `Projekt Aplikacji All Virtual Phone.pdf` (48 pages)

| ID | Requirement from source | Source | Repository delivery | State |
| --- | --- | --- | --- | --- |
| R-001 | VirtualNumber and RoutingPolicy domain entities | S1 p.1; S3 pp.7–8 | `backend/avp/db.py`: verified DID inventory only | Partial |
| R-002 | SIP alias lookup and routing policy | S1 pp.1–2; S3 pp.9–12 | `backend/avp/routing.py`, `api.py`: permissioned DID routing | Partial |
| R-003 | Rust/Tokio Global Alias Engine | S2 p.1; S3 p.6 | Architecture target | Not started |
| R-004 | Vanity / gold / platinum classification | S2 pp.1–2; S3 pp.13–19 | `backend/avp/vanity.py` | Partial (classification) |
| R-005 | Carrier DID purchase / lease / callback mapping | S3 pp.1–3, 44–45 | Carrier contract + adapter required | Not started |
| R-006 | DNO/UKE and authenticated CLI | S3 pp.5–6 | Auth/DNO checks, no live feed | Partial |
| R-007 | Kamailio SBC and FreeSWITCH bridge | S1 p.1; S2 p.1; S3 pp.7–9 | Architecture only | Not started |
| R-008 | Native Android UI, CallsManager and WebRTC | S3 pp.24–38 | Architecture only | Not started |
| R-009 | SMPP SMS/MMS, DLR and media storage | S2 p.1; S3 pp.20–24 | Architecture only | Not started |
| R-010 | Stalwart/JMAP reverse e-mail aliases | S3 pp.21–24, 42–44 | Architecture only | Not started |
| R-011 | Imperial Obsidian & Gold design tokens | S3 pp.24–26 | Planned Android design system | Not started |
| R-012 | CDR, observability and billing | S1 p.1; S3 pp.8–9 | Roadmap | Not started |

## Engineering corrections and evidence levels

- The PDFs sometimes label illustrative fragments "production code". S3 pp.36–41 shows UI state changes for calls and SMS without an actual SIP call or SMPP submission. Treat these as **UI prototypes**, not telecom integrations.
- S2 p.1 describes "dynamic spoofing"; the compliant implementation instead verifies actual ownership/authorization of caller identity before presenting a DID.
- The documents assert universal callback delivery and highly optimistic performance. Real-world routing depends on carrier interconnect, number capabilities, jurisdiction, availability, system failure and empirical service-level testing. Neither global 100% delivery nor sub-millisecond performance is accepted as a verified result.
- Generated numeric patterns are not legal numbering rights; the vanity classifier returns **candidates only**.
- A dedicated current-law review is required prior to each jurisdiction's production launch. This file records requirements, not legal advice.

Statuses mean: **Not started**, **Partial**, **Implemented**, **Locally tested**, **Integration verified**, **Production verified**. Source inclusion is not proof of implementation.
