# Production image for the Fly.io demo deployment (WBS 1.5.5).
#
# Single-app topology: the compiled SPA is served by the API process, so the
# demo runs on one machine with no CORS boundary between frontend and backend.
# The development setup is unchanged — docker-compose.yml still builds
# backend/Dockerfile and frontend/Dockerfile separately with hot reload.
#
# Multi-stage, satisfying the WBS 1.2.6.3 constraint that the runtime image
# carry no build toolchain.

# ---- Stage 1: build the SPA -------------------------------------------------
FROM node:20-alpine AS frontend

WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Same-origin in this topology, so the client uses relative /api paths.
ENV VITE_API_URL=""
RUN npm run build

# ---- Stage 2: python dependencies ------------------------------------------
FROM python:3.12-slim AS deps

# build-essential and libpq-dev are needed to compile wheels but must not reach
# the runtime image.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r /tmp/requirements.txt

# ---- Stage 3: runtime -------------------------------------------------------
FROM python:3.12-slim AS runtime

# libpq5 is the runtime library only; the -dev package and compilers stay behind.
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 lighthouse

COPY --from=deps /install /usr/local

WORKDIR /app
COPY backend/ /app/
COPY --from=frontend /build/dist /app/static

# Uploads are deliberately ephemeral on the demo: no Fly volume is attached, so
# the directory resets on each deploy. Seeded evidence records are recreated by
# the seeder at boot.
RUN mkdir -p /app/uploads && chown -R lighthouse:lighthouse /app

USER lighthouse

ENV PYTHONUNBUFFERED=1 \
    STATIC_DIR=/app/static \
    UPLOAD_DIR=/app/uploads

EXPOSE 8000

# No --reload: that is a development-only flag and would fork a reloader process.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
