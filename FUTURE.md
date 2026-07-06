# Future Features

Features deferred beyond v1.0. Add ideas here rather than implementing them directly.

## Phase 3 — Plugins & Integrations — ✅ SHIPPED in v1.3
- ~~**AWS Config / Security Hub**~~ — imports non-compliant findings into the Risk Register (`aws_config` plugin)
- ~~**MISP (threat intel)**~~ — ingests MISP events into the Risk Register (`misp` plugin)
- ~~**Slack notifications**~~ — posts new High/Critical risks to a webhook (`slack` plugin)

  Typed plugin SDK with live/demo modes — see `docs/adr/ADR-005-plugin-architecture.md` and `docs/plugin-sdk.md`. Remaining plugin work below (scheduled polling; more channels/sources).

## Phase 3.x — Plugin follow-ups
- **Scheduled collection**: background polling per plugin (currently on-demand via UI/API)
- **More notification triggers**: evidence expiry, new audit findings, overdue TPRM assessments
- **More sources/channels**: Azure/GCP source plugins; email/PagerDuty notifications

## Phase 4 — Advanced TPRM
- **Vendor assessment workflow UI**: Step-by-step guided questionnaire for vendors (backend APIs exist in v1.0, frontend UI deferred)
- **Vendor portal**: Self-service vendor questionnaire submission link

## Phase 5 — Reporting & Export
- **PDF export**: Audit report, risk register snapshot, gap analysis summary
- **CSV export**: Risk register, vendor register, evidence log
- **Executive dashboard**: One-page summary suitable for board presentations

## Phase 6 — Auth & Multi-tenancy — ✅ SHIPPED in v1.1 / v1.2
- ~~**User authentication**: JWT-based login~~ — shipped v1.1
- ~~**Role-based access (Admin / Analyst / Viewer)**~~ — admin/analyst/viewer roles shipped v1.1; write endpoints enforce the viewer read-only role as of v1.2
- ~~**Organisation scoping**: Multi-client scoping for consulting/MSP use cases~~ — shipped v1.1 (`client_id` FK model; see `docs/adr/ADR-002-multi-client-scoping.md`)
- **Admin console**: user management UI — shipped v1.1

  Remaining future work in this area: SSO/OIDC, token refresh/revocation, and true row-level tenant isolation (see ADR-002 known limits).

## Phase 7 — Automation
- **Scheduled evidence freshness checks**: Automated alerts when evidence approaches expiry
- **Recurring risk review reminders**: Email/Slack nudge when `review_date` passes
- **CI/CD integration**: GitHub Actions or GitLab CI hooks for automated evidence capture
