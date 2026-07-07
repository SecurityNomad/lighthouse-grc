# Future Features

Features deferred beyond v1.0. Add ideas here rather than implementing them directly.

## v2.0 — Consultant Engagement Workflow (deferred 2026-07-07, see CHG-010)

Successor scope defined by the pre-Phase-4 consultant-workflow review. Turns the platform
into an end-to-end consulting tool: engagement intake → scoped questionnaires → generated
risks/gaps → report export → reassessment → closure with history. Est. ~85–110 h total.
**Not in the current project baseline** — proposed as a v2.0 successor project at M5 closure.

### T1 — Engagement backbone (~20–25 h)
- **Engagement model**: client FK, engagement_type (Gap Assessment / Risk Assessment / Compliance Audit / Reassessment), frameworks_in_scope, status lifecycle (Scoping → Fieldwork → Analysis → Reporting → Remediation → Closed), lead consultant, dates, `parent_engagement_id` self-FK for reassessments
- Nullable `engagement_id` FK on Risk / Evidence / AuditPlan / AuditFinding for traceability
- Engagement CRUD + close + reassess endpoints; intake form; active + completed-history lists
- Block deletion of clients with engagement history (current `SET NULL` FKs silently orphan records — archive instead)

### T2 — Assessment questionnaire engine (~35–45 h)
- YAML-seeded `AssessmentTemplate` + `AssessmentQuestion` banks (start: ISO 27001:2022 Annex A gap assessment, then SOC 2); questions carry control refs, risk templates, and recommendations
- `AssessmentRun` + `AssessmentAnswer` (mirrors the vendor-assessment data model); questions filtered by the engagement's frameworks_in_scope
- Generation service: answers → raise risks (source=`assessment`, idempotent via `external_id`), mark control implementation status, attach recommendations — with a consultant review/accept screen before commit
- Guided questionnaire UI (sectioned, progress, save-and-resume) — build once, reuse for the vendor assessment UI (Phase 4 below)

### T3 — Reporting, snapshots & reassessment (~20–25 h)
- Absorbs "Phase 5 — Reporting & Export" below: engagement report service → PDF (WeasyPrint) + slide deck (python-pptx, or a print-view first cut); CSV exports
- Point-in-time JSON snapshot of engagement state on closure; read-only snapshot viewer; "then vs. now" delta in reassessments
- `next_reassessment_date` on engagements, surfaced on the dashboard

### T4 — Threat-intel relevance (~10–15 h)
- Client profile/sector tags; MISP imports filtered by client profile and routed to the active engagement
- "Relevant threat intel" dashboard panel per client

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

## Phase 5 — Reporting & Export — absorbed into v2.0 T3 above
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
