# ADR-002: Multi-Client Scoping via `client_id` Foreign Key

## Status
Accepted

## Date
2026-07-06

## Supersedes
Partially supersedes ADR-001 decision #4 ("Single-tenant only for MVP") and the "No SSO / demo-grade auth" consequence. ADR-001's core scope philosophy otherwise stands.

## Context

ADR-001 committed the MVP to a single tenant, deferring multi-tenancy on the grounds that row-level security, schema isolation, billing, and onboarding are engineering work unrelated to demonstrating GRC domain knowledge. That reasoning holds for *true SaaS multi-tenancy*.

However, the anchor-tenant and portfolio narrative for Lighthouse is a **security consultant / vCISO / MSP** managing several client organisations from one console — e.g. running an ISO 27001 programme for Hospital A while tracking a SOC 2 readiness effort for Insurer B. That story needs the data of one client to be separable from another's *within a single deployment operated by a trusted internal team*. It does **not** need hostile-tenant isolation, per-tenant databases, or billing.

This is a materially weaker requirement than SaaS multi-tenancy, and it can be met with a much simpler mechanism. v1.1 therefore introduced JWT authentication, a `clients` table, and a `client_id` foreign key on the client-owned resources (Risk, Evidence, Vendor, Audit Plan), with a client selector in the UI that scopes list and dashboard queries.

The 2026-07-06 review found two leaks in that first cut — the dashboard ignored `client_id`, and the frontend served the previous client's cached data after switching — both fixed in v1.2. This ADR documents the decision the implementation rests on.

## Decision

1. **Scope with a nullable `client_id` FK, not row-level security (RLS).** Each client-owned row carries an optional `client_id` referencing `clients.id`. List endpoints and the dashboard accept a `client_id` query parameter and filter on it; the frontend axios client injects the selected client from `localStorage` into every request. RLS (Postgres policies) and schema-per-tenant were both rejected as disproportionate to a trusted-operator model and as coupling the app tightly to Postgres, which would undermine the SQLite-in-CI test strategy (see CHG-001).

2. **`client_id` is nullable.** Global/unassigned records (and all pre-v1.1 seed data) have `client_id = NULL`. A request with no client selected is unscoped and sees everything — the consultant's "all clients" view. This keeps the single-tenant demo path working unchanged.

3. **Scoping is applied at the list/aggregate layer.** `GET /` collection endpoints and `/dashboard` filter by `client_id`. Findings are scoped transitively through their parent audit plan.

4. **Trust model: cooperative, not adversarial.** All authenticated users are members of the operating team (admin / analyst / viewer). Scoping exists to prevent *accidental* cross-client mistakes ("I thought I was looking at Insurer B"), not to defend against a malicious authenticated user attempting to read another client's data. Authentication is JWT with an 8-hour expiry; roles gate writes (viewer is read-only as of v1.2).

## Consequences

### Positive
- Small, legible change: one nullable column per owned table plus a query filter — readable by an interviewer in minutes.
- Backward compatible: existing single-tenant seed data (`client_id = NULL`) and the no-client "all clients" view keep working.
- Database-agnostic: no Postgres-specific RLS, so the SQLite-based test suite is unaffected.
- Delivers the consulting/vCISO demo narrative that differentiates the portfolio, without the cost of real SaaS multi-tenancy.

### Negative / Known Limits
- **Detail endpoints are not yet client-scoped.** `GET/PUT/DELETE /{id}` fetch by primary key without a `client_id` check. Under the trusted-operator model this is acceptable, but it is a data-isolation hole the moment a client-facing or externally-shared user exists. Tracked as a follow-up ("Client-scope detail endpoints").
- **Enforcement is filter-based, not mandatory.** Scoping depends on the caller passing `client_id`; a hand-crafted request omitting it sees all clients. This is by design for the cooperative trust model but must **not** be mistaken for tenant isolation.
- **Not true multi-tenancy.** No per-tenant encryption, no isolation guarantees against a hostile authenticated user, no billing/onboarding. A real SaaS offering would require ADR-001 decision #4 to be revisited in full (RLS or schema-per-tenant).
- Auth remains demo-grade (default seeded admin, `SECRET_KEY` default, no token refresh/revocation, no SSO). This must continue to be called out in demo contexts and the README, per ADR-001.

## Future Work
- Client-scope detail (`/{id}`) endpoints before any client-facing or viewer-only external user exists.
- SSO / OIDC and token refresh/revocation (FUTURE.md Phase 6 remainder).
- Revisit RLS or schema-per-tenant only if Lighthouse is offered as hosted SaaS to mutually-untrusted tenants.
