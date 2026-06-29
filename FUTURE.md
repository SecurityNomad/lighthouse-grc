# Future Features

Features deferred beyond v1.0. Add ideas here rather than implementing them directly.

## Phase 3 — Plugins & Integrations
- **AWS Config / Security Hub**: Automated control evidence pull via AWS SDK
- **MISP (threat intel)**: Ingest threat indicators to pre-populate risk register
- **Slack notifications**: Alert on new open findings, evidence expiry, high-risk items

## Phase 4 — Advanced TPRM
- **Vendor assessment workflow UI**: Step-by-step guided questionnaire for vendors (backend APIs exist in v1.0, frontend UI deferred)
- **Vendor portal**: Self-service vendor questionnaire submission link

## Phase 5 — Reporting & Export
- **PDF export**: Audit report, risk register snapshot, gap analysis summary
- **CSV export**: Risk register, vendor register, evidence log
- **Executive dashboard**: One-page summary suitable for board presentations

## Phase 6 — Auth & Multi-tenancy
- **User authentication**: JWT-based login, role-based access (Admin / Analyst / Viewer)
- **Organisation scoping**: Multi-tenant support for MSP use cases

## Phase 7 — Automation
- **Scheduled evidence freshness checks**: Automated alerts when evidence approaches expiry
- **Recurring risk review reminders**: Email/Slack nudge when `review_date` passes
- **CI/CD integration**: GitHub Actions or GitLab CI hooks for automated evidence capture
