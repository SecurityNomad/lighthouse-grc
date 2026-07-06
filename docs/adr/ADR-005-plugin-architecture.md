# ADR-005: Plugin Architecture

## Status
Accepted

## Date
2026-07-06

## Context

ADR-001 (#3) committed Lighthouse to a typed, optional plugin interface as the platform's key differentiator: "All integrations implement a common Python protocol. They are optional: the platform runs fully without any plugin installed." Phase 3 delivers the first three plugins — AWS Config/Security Hub, MISP threat intelligence, and Slack notifications (WBS 1.4.1–1.4.3).

Two forces shaped the design:

1. **The plugins do different kinds of work.** AWS and MISP *pull* external findings into the Risk Register; Slack *pushes* domain events outward. A single "do something" interface would be too loose to be useful or type-safe.
2. **The demo can't reach live AWS/MISP/Slack.** A portfolio reviewer runs the app locally with no cloud credentials. Per the WBS ("live or mocked AWS endpoint"), each plugin must be demonstrable end-to-end without external services, while still containing real client code for the live path.

## Decision

1. **Two capability interfaces over one base `Plugin`.**
   - `RiskSourcePlugin.collect(db, client_id) -> PluginRunResult` — imports findings as risks.
   - `NotificationPlugin.send(event) -> bool` — delivers a `NotificationEvent`.
   Both extend `Plugin`, which requires a `status() -> PluginStatus` method so the operator can see configured/healthy/mode without triggering a run.

2. **A module-level `registry`.** Each plugin module calls `registry.register(...)` at import time; `import app.plugins` wires up all built-ins. The registry is queryable by type, which the notification dispatcher and the API use. This keeps registration declarative and makes adding a plugin a single self-contained module.

3. **Live / demo / disabled modes, chosen from config.** Every plugin reports one of three modes. `demo` uses bundled sample findings (AWS/MISP) or logs instead of posting (Slack), so the flow works with zero external setup — this is the default. `live` uses real clients (lazily-imported `boto3` for AWS; `httpx` for MISP and Slack). `disabled` is an explicit off switch. This is the mechanism that satisfies "demonstrable without live services" without faking the live code path.

4. **Idempotent imports via risk provenance.** Risks carry `source` (plugin name or "Manual") and `external_id` (the source system's id). `upsert_risks` skips candidates whose `(source, external_id)` already exists, so re-running a plugin never duplicates. Provenance is also surfaced in the API/UI.

5. **Failsafe notification dispatch.** `dispatch_notification` iterates notification plugins and swallows/logs any error — a down Slack webhook must never fail the domain action (e.g. creating a risk) that triggered it. New High/Critical risks fire the first trigger; other triggers (evidence expiry, findings) reuse the same dispatcher.

6. **`boto3` is not a hard dependency.** It is imported lazily inside the AWS live path only. The platform (and CI, which installs `requirements.txt`) runs and tests fully without it; live AWS mode requires `pip install boto3`. MISP and Slack reuse `httpx`, already a dependency.

## Consequences

### Positive
- One clean, typed pattern; a new integration is a single module that registers itself — exactly the extensibility story ADR-001 promised.
- The whole feature is demonstrable locally in demo mode; imported findings appear in the existing Risk Register with no new UI required (a Plugins page adds run/status controls on top).
- Idempotency means the demo can be re-run safely; provenance makes imported vs. manual risks auditable.
- Notifications can't take down core flows.

### Negative / Known limits
- Demo-mode sample data is static; it demonstrates the pipeline, not real-time intel.
- Runs are on-demand (triggered via API/UI). Scheduled/polling collection (WBS "configurable polling interval") is deferred — the collect interface is compatible with a future scheduler.
- Filter-based dedup keys on `external_id` stability; a source that changes ids per run would re-import. Acceptable for the three built-ins.
- No per-plugin secrets vault — config comes from environment settings, consistent with the platform's demo-grade posture (ADR-002).

## Future Work
- Scheduled collection (background task / cron) with a per-plugin interval.
- Additional triggers wired to the dispatcher (evidence expiry, new findings, overdue TPRM assessments).
- Azure/GCP source plugins and additional notification channels (email, PagerDuty) using the same interfaces.
