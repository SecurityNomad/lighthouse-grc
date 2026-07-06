# Product

## Register

product

## Users

Two audiences, one product:

- **In-house GRC/security practitioners** at small-to-mid SaaS companies — the person running the ISMS who today lives in spreadsheets (a risk register tab, a controls tab, a folder of evidence PDFs). Their context: preparing for or maintaining SOC 2 / ISO 27001, usually part-time on GRC alongside other security work, no budget for enterprise GRC suites.
- **Security consultants / vCISOs / MSPs** managing several client organisations from one console (e.g. an ISO 27001 programme for one client, SOC 2 readiness for another). This is why the platform is multi-client scoped (`client_id`).

The job to be done: run a coherent, audit-ready ISMS — risks, controls, evidence, third-party risk, and audits that all connect back to each other — without the spreadsheet fragility or the enterprise-suite configuration ceremony. The primary task on any given screen is *understand the current state and act on it* (which risks are uncovered, what evidence is expiring, what findings are open), not admire a dashboard.

## Product Purpose

Lighthouse is a minimalist, opinionated GRC platform for the underserved market below enterprise budgets. It replaces the spreadsheet approach to an ISMS with one connected system: a Risk Register as the source of truth, a YAML-defined control framework library (SOC 2, ISO 27001, CIS), risk↔control mapping, evidence collection, TPRM, audit management, a live dashboard, and optional integration plugins (AWS Config/Security Hub, MISP, Slack).

Success is: a practitioner can walk into an audit with the state of their programme legible in one place; a consultant can switch between clients without losing the thread; and nothing on screen makes a security-literate person distrust the tool. (It is also a portfolio artefact demonstrating GRC domain depth plus product-engineering craft — the interface has to hold up to inspection by hiring managers.)

## Brand Personality

**Trustworthy · calm · precise.** The name is the brief: a lighthouse gives reliable guidance and signals danger before ships run aground. The interface should convey quiet authority — the confidence of a tool built by someone who understands the domain. Voice is plain and exact, never hype. Dense compliance data is made legible and unstressful rather than dramatized. Clarity beats flash every time; restraint reads as competence to this audience.

## Anti-references

- **Enterprise GRC bloat** — Archer, ServiceNow GRC, OneTrust: cluttered, dated, configuration-heavy dashboards that need months of setup. Lighthouse is explicitly positioned against these (ADR-001).
- **Generic AI SaaS** — cream/sand backgrounds, gradient-text heroes, endless identical icon-card grids, tiny uppercase tracked eyebrows on every section. The 2026 AI-slop template; an instant credibility loss here.
- **Crypto/fintech dark-neon** — navy-and-gold or black-and-neon "trading terminal" aesthetics that read as hype rather than trust. Wrong signal for a compliance audience.

Also avoid: gamified/consumer-playful patterns (badges, confetti) that undercut credibility with auditors and CISOs.

## Design Principles

1. **The risk register is the source of truth.** Every module — controls, evidence, TPRM, audits, plugins — visibly connects back to risk. Nothing is a standalone spreadsheet replacement. (Mirrors ADR-001 #1.)
2. **Legible under load.** The value is dense, cross-referenced GRC data made calm and scannable. When a screen gets busy, the answer is clearer hierarchy and rhythm, not more chrome.
3. **Practitioner power without enterprise ceremony.** Capable but immediately usable — no configuration maze before the first risk is recorded. Opinionated defaults over endless settings.
4. **Trust is earned by restraint.** Quiet confidence; no hype, no gamification, no decoration that a security-literate user would read as unserious. Every element should survive the "would an auditor trust this?" test.
5. **Accessible and honest by default.** Meets its stated accessibility bar as a baseline, and never dresses up demo-grade functionality as more than it is (per ADR-001 / ADR-002 honesty about demo auth).

## Accessibility & Inclusion

Target: **WCAG 2.1 AA, plus honoring `prefers-reduced-motion`.**

- Contrast: body text ≥ 4.5:1, large/bold text ≥ 3:1, including placeholder text — no light-gray-for-elegance body copy.
- Full keyboard operability: focus-visible states, focus traps and Escape on modals (dialogs use `role="dialog"` / `aria-modal`), logical tab order.
- Labels/roles: icon-only controls carry `aria-label`s; live status uses appropriate roles (already applied in the toast system and modal pass).
- Motion: every non-trivial animation has a `prefers-reduced-motion: reduce` alternative (crossfade or instant).
- Color is never the sole carrier of meaning (impact/status badges pair color with text).
