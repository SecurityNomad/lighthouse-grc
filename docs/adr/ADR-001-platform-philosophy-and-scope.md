# ADR-001: Platform Philosophy and Scope Boundaries

## Status
Accepted

## Date
2026-05-19

## Context

Small-to-mid SaaS companies managing an ISMS typically do so in spreadsheets — a risk register in Google Sheets, a control mapping tab, and a folder of PDF evidence. This works until a SOC 2 audit or ISO 27001 gap assessment arrives, at which point the spreadsheet approach collapses under the weight of cross-referencing, version control, and stakeholder reporting. Dedicated enterprise GRC platforms (ServiceNow GRC, OneTrust, Archer) exist but are priced for Fortune 500 procurement budgets and require months of configuration before a single risk can be recorded. The market below $50k/year is underserved.

This project sits at the intersection of two goals. First, it is a genuine attempt to build a tool that solves a real problem Raha has observed repeatedly in SaaS security programmes. Second, it is a portfolio project designed to demonstrate the full stack of skills required for a Senior Information Security Manager or CISO-track role: threat modelling and risk methodology, control framework literacy (ISO 27001, NIST CSF, SOC 2), and the product-engineering instinct to design and ship a coherent system rather than just audit one. The combination of GRC domain knowledge and hands-on engineering is rare and valuable, and this project is intended to make that combination visible and credible to hiring stakeholders.

The central tension in scope is depth vs. shippability. A complete GRC platform would include workflow engines, multi-tenant SaaS infrastructure, SSO, a policy authoring environment, fine-grained RBAC, and integrations with every cloud provider's security tooling. Building all of that in a 4-month MVP window is not realistic, and attempting it would produce a half-finished platform that demonstrates neither good engineering nor good programme design. The decision is to build a tight core that is genuinely complete and functional, and to defer everything else explicitly.

Two alternative approaches were considered before building from scratch. The first was forking SimpleRisk, an open-source PHP GRC platform. SimpleRisk has a large feature set but the codebase is difficult to extend, the UI is dated, and forking someone else's project does not demonstrate product design instinct. The second was forking Eramba, which is more modern but community-edition restricted and similarly hard to extend cleanly. Both alternatives would result in a portfolio project that showcases integration and configuration skills rather than design and engineering skills. The decision is to build from scratch with a modern, well-documented stack that a hiring manager or technical interviewer can read and evaluate directly.

## Decision

The following principles govern every scope and architecture decision in the Lighthouse platform:

1. **The risk register is the source of truth.** Every other module — controls, TPRM, evidence, audits — connects back to risks. Nothing in the platform is standalone. This mirrors how a well-run ISMS actually works and prevents the platform from becoming a disconnected collection of spreadsheet replacements.

2. **Frameworks are YAML-defined.** ISO 27001, NIST CSF, SOC 2 TSC, and any custom framework are expressed as YAML files loaded at startup. Adding a new framework requires no changes to application code. This is the correct abstraction: the control framework is configuration, not application logic.

3. **Plugins follow a typed interface.** All integrations (AWS Security Hub, MISP, Slack) implement a common Python protocol. They are optional: the platform runs fully without any plugin installed. This keeps the core dependency surface small and makes the integration pattern legible to anyone reading the codebase.

4. **Single-tenant only for MVP.** Multi-tenancy introduces row-level security, schema isolation, billing logic, and onboarding flows — all of which are engineering work unrelated to demonstrating GRC domain knowledge. The demo runs as a single tenant. Multi-tenancy is explicitly deferred and documented.

5. **No workflow engine.** Approvals, reviews, and sign-offs are tracked as status fields on records, not as routed workflow tasks. This keeps the data model flat and auditable: the state of any risk or control can be determined by reading one row in one table. It also reflects the reality that most small SaaS companies manage approvals through Slack and email anyway.

6. **Policy authoring stays in Git.** The platform links to markdown files in a Git repository; it does not try to replace version control for policy documents. Git provides a better audit trail, diff history, and review workflow than anything that could be built in a 4-month MVP. The platform's role is to surface links to the canonical policy, not to store it.

7. **Platform name: Lighthouse.** A lighthouse provides reliable guidance and signals danger before ships run aground. A well-run ISMS does the same thing for an organisation's information security posture. The name is short, memorable, and does not depend on an acronym or jargon that would require explanation to a non-technical executive.

## Consequences

### Positive
- Tight scope makes the MVP shippable within a 4-month window with a single contributor.
- YAML frameworks allow anyone to add ISO 27001, NIST CSF, or PCI-DSS without writing a pull request against core application code.
- Manual state transitions are easy to audit and explain to non-technical stakeholders, auditors, and board members.
- The plugin SDK is the multiplier — one clean integration pattern means any cloud security service can be wired in as a plugin without touching core logic.
- The Git-first policy approach means the platform's policy library is immediately compatible with existing policy repositories that most security teams already have.

### Negative
- Without a workflow engine, approvals and risk reviews are out-of-band (email, Slack, Jira). The platform records that a review happened; it does not enforce that it happens on schedule. This is a meaningful functional gap for larger organisations.
- Single-tenant architecture means the demo resets between deployments. A seeding script is required to populate meaningful demo data on startup.
- No SSO means the authentication story is demo-grade only. This must be called out explicitly in all demo contexts and the README, and is explicitly labelled Phase 2 in the roadmap.
- Building from scratch rather than forking means reinventing a small amount of wheel in areas like evidence file storage and finding deduplication.

## Explicitly Deferred (FUTURE.md)
- Multi-tenant SaaS architecture (row-level security, schema isolation, tenant onboarding)
- Fine-grained RBAC beyond admin / contributor / viewer roles
- Workflow engine and approval chains with email and Slack notifications
- SSO / SAML integration (Okta, Azure AD, Google Workspace)
- User-facing audit portal for external auditor read-only access
- Azure Security Center and GCP Security Command Center plugin integrations
- Policy authoring and versioning inside the platform (beyond Git link storage)
- Risk appetite and quantitative risk scoring (FAIR methodology)
- Automated control testing via API integrations
