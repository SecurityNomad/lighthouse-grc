# Lighthouse Plugin SDK

Plugins are optional integrations. The platform runs fully with none configured.
There are two kinds:

| Type | Interface | Does |
|---|---|---|
| **Risk source** | `RiskSourcePlugin.collect(db, client_id)` | Pulls external findings into the Risk Register |
| **Notification** | `NotificationPlugin.send(event)` | Pushes domain events to an external channel |

Built-ins: `aws_config`, `misp` (risk sources) and `slack` (notification). Code
lives in `backend/app/plugins/`.

## Modes

Every plugin reports a `PluginStatus` with a `mode`:

- **demo** — bundled sample data / logged output. No external service needed. Default.
- **live** — real clients (`boto3` for AWS, `httpx` for MISP/Slack). Needs config.
- **disabled** — turned off via `*_plugin_enabled=false`.

Configure via environment / `.env` (see `.env.example`).

## HTTP API

All routes require auth; running a plugin is a write (blocked for the `viewer` role).

- `GET /api/v1/plugins` — list plugins with status.
- `POST /api/v1/plugins/{name}/run[?client_id=...]` — run it.
  - Risk-source → imports findings; returns `{created, skipped, ...}` (idempotent:
    re-runs skip already-imported findings, matched by `source` + `external_id`).
  - Notification → sends a test message.

The **Plugins** page in the UI lists each plugin, its mode, and a Run button.

## Writing a plugin

Create a module in `app/plugins/`, subclass the right interface, and register it.

### A risk source

```python
from app.plugins.base import RiskSourcePlugin, RiskCandidate, upsert_risks, registry
from app.schemas.plugin import PluginStatus
from app.config import settings

class MySourcePlugin(RiskSourcePlugin):
    name = "my_source"
    display_name = "My Source"
    description = "Imports X findings as risks."

    def status(self) -> PluginStatus:
        if not settings.my_source_enabled:
            return PluginStatus(configured=False, healthy=False, mode="disabled", message="Disabled.")
        return PluginStatus(configured=True, healthy=True, mode="demo", message="Demo mode.")

    async def collect(self, db, client_id=None):
        candidates = [
            RiskCandidate(
                external_id="my-source:123",     # stable id → dedup
                title="Finding title",
                impact="High",                    # Critical/High/Medium/Low/Negligible
                likelihood="Likely",
                tags=["my-source"],
            ),
        ]
        return await upsert_risks(db, self.name, candidates, client_id)

registry.register(MySourcePlugin())
```

`upsert_risks` computes the integer risk scores and skips duplicates for you.

### A notification channel

```python
from app.plugins.base import NotificationPlugin, registry
from app.schemas.plugin import PluginStatus

class MyChannelPlugin(NotificationPlugin):
    name = "my_channel"
    display_name = "My Channel"
    description = "Posts events to X."

    def status(self) -> PluginStatus: ...

    async def send(self, event) -> bool:
        # event has: event_type, title, message, severity, link
        ...
        return True

registry.register(MyChannelPlugin())
```

### Register it

Add a side-effecting import in `app/plugins/__init__.py`:

```python
from app.plugins import my_source  # noqa: F401
```

That's it — it now appears in `GET /plugins`, the Plugins page, and (for
notifications) receives dispatched events.

## Triggering notifications

Emit an event from anywhere:

```python
from app.plugins.base import dispatch_notification, NotificationEvent

await dispatch_notification(NotificationEvent(
    event_type="risk.created",
    title="New Critical risk",
    message="…",
    severity="critical",
))
```

`dispatch_notification` fans out to every notification plugin and is **failsafe** —
a broken channel is logged, never raised, so it can't break the action that
triggered it. New High/Critical risks already fire this on create.

See `docs/adr/ADR-005-plugin-architecture.md` for the design rationale.
