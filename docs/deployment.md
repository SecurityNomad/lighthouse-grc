# Deployment — Fly.io public demo

Covers WBS 1.5.5. The public demo runs as a **single Fly app** that serves both
the API and the compiled SPA, backed by a separate Fly Postgres cluster.

Local development is unaffected: `docker compose up` still builds
`backend/Dockerfile` and `frontend/Dockerfile` separately with hot reload. The
root `Dockerfile` is used only for the deployed image.

## Why one app

Two apps (an API and an nginx frontend) would mirror the compose topology more
closely, but cost two machines instead of one and introduce a CORS boundary and
a second hostname for no demo benefit. Serving the built SPA from the API
process keeps everything same-origin, so the client uses relative `/api` paths
and `CORS_ORIGINS` stays empty.

The API routes are registered before the static mount, so `/api/v1/*`, `/docs`,
`/redoc`, and `/health` always win. Anything else falls back to `index.html` so
client-side routes such as `/soa` survive a hard refresh. A request under
`/api/` that matches no route returns a JSON 404 rather than the HTML shell —
otherwise an API typo would surface on the client as a confusing parse error.

## Prerequisites

```bash
brew install flyctl     # not currently installed on this machine
fly auth login
```

## First deploy

```bash
cd lighthouse

# 1. Create the app without deploying yet (fly.toml already exists).
fly apps create lighthouse-grc

# 2. Create Postgres and attach it. `attach` injects DATABASE_URL as a secret.
fly postgres create --name lighthouse-db --region lhr \
    --vm-size shared-cpu-1x --volume-size 1 --initial-cluster-size 1
fly postgres attach lighthouse-db --app lighthouse-grc

# 3. Set the signing key. Do NOT reuse the development value.
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" --app lighthouse-grc

# 4. Deploy. The release_command runs `alembic upgrade head` in a one-off
#    machine first; if migrations fail the deploy aborts and the previous
#    release keeps serving.
fly deploy

# 5. Confirm.
fly status --app lighthouse-grc
curl -fsS https://lighthouse-grc.fly.dev/health
open https://lighthouse-grc.fly.dev
```

### DATABASE_URL scheme

`fly postgres attach` sets `DATABASE_URL` to a `postgres://…` URL. SQLAlchemy's
async engine cannot use that scheme — it resolves the default psycopg2 driver
and fails at startup with an unhelpful `greenlet_spawn has not been called`.
`app/config.py` rewrites `postgres://` and `postgresql://` to
`postgresql+asyncpg://` on load, so the value Fly injects works unedited. Do not
"fix" the secret by hand.

## Demo credentials

The admin user is seeded at boot from `app/seed.py`. Change the password
immediately after the first deploy, since the default is public in this repo:

```bash
# after logging in once at https://lighthouse-grc.fly.dev
# use the admin console to rotate the password, or:
fly ssh console --app lighthouse-grc
```

Publish the working demo credentials in the root `README.md` so a reviewer can
sign in without setup — WBS 1.5.5 requires the anchor tenant to be visible
either without login or with documented credentials.

## Anchor tenant data

`SEED_DEMO_DATA=true` is set in `fly.toml`, so the Savanna Commercial Bank
anchor tenant is seeded on first boot: 25 risks, 15 vendors, the ISO 27001 SoA
across all 93 Annex A controls, SOC 2 Common Criteria readiness, and one
completed audit cycle. The seeder is idempotent — it is gated on a sentinel
risk title — so restarts and redeploys do not duplicate it.

To reset the demo to a clean state:

```bash
fly postgres connect --app lighthouse-db
# \c lighthouse_grc
# TRUNCATE risks, vendors, control_applicability, audit_plans CASCADE;
fly apps restart lighthouse-grc     # reseeds on boot
```

## Cost control

`fly.toml` sets `auto_stop_machines = "stop"` with `min_machines_running = 0`,
so the machine sleeps when idle and wakes on the next request. The first hit
after a sleep pays a cold start — an acceptable trade for a portfolio demo that
is idle most of the time. The Postgres cluster is the standing cost.

## Uploads are ephemeral

No Fly volume is attached. Evidence files uploaded through the demo live in the
container filesystem and are lost on restart or redeploy; the seeded evidence
*records* are recreated each boot. This is deliberate: a public demo accepting
uploads would otherwise accumulate unreviewed files with no cleanup path. If
persistence is ever wanted, create a volume and mount it at `/app/uploads`.

## Image

The root `Dockerfile` is multi-stage:

1. `node:20-alpine` builds the SPA (`npm ci && npm run build`).
2. `python:3.12-slim` compiles Python wheels with `build-essential` and `libpq-dev`.
3. `python:3.12-slim` runtime copies only the installed packages, the app, and
   the compiled `dist/` — no compilers, no `-dev` packages. Runs as a
   non-root `lighthouse` user.

This also satisfies the WBS 1.2.6.3 constraint that the runtime image carry no
build toolchain, which the development `backend/Dockerfile` never met.

## Verification status

At the time of writing, the deployment path has been verified only in part:

- **Verified** — static serving, SPA fallback for client routes, JSON 404 for
  unknown `/api/` paths, path-traversal containment, and `DATABASE_URL` scheme
  rewriting, all exercised against the ASGI app directly (8/8 checks).
- **Not verified** — the Docker image has never been built. The local Docker
  daemon was not running, and `npm run build` cannot run on this machine
  because `frontend/node_modules` contains only linux rollup binaries (it was
  installed inside a container). Neither affects the image build, which runs
  `npm ci` fresh on linux, but the multi-stage build is unproven until someone
  runs `docker build .` or `fly deploy`.
