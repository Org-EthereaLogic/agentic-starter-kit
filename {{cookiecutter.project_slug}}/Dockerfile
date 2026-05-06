# syntax=docker/dockerfile:1.7
#
# Production Dockerfile for {{ cookiecutter.project_name }}.
#
# Multi-stage build. The base image is pinned by digest so the image
# only changes when Dependabot opens a PR with a fresh digest. Update
# the digest by running:
#
#   docker pull <image>:<tag>
#   docker inspect --format='{{ '{{' }}index .RepoDigests 0{{ '}}' }}' <image>:<tag>
#
# Then paste the resulting `<image>@sha256:...` reference back into the
# `FROM` lines below. Dependabot's `docker` ecosystem (configured in
# .github/dependabot.yml) automates this.

{% if cookiecutter.primary_language in ('python', 'polyglot') -%}
ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:58525e1a8dada8e72d6f8a11a0ddff8d981fd888549108db52455d577f927f77
{% endif -%}
{% if cookiecutter.primary_language in ('typescript', 'polyglot') -%}
ARG NODE_IMAGE=node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0
{% endif %}
{% if cookiecutter.primary_language == 'python' -%}
# ----- builder ------------------------------------------------------
FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# uv is the build/runtime package manager — pinned by major version.
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/

WORKDIR /app
COPY pyproject.toml uv.lock* ./
# `--frozen` requires a committed `uv.lock`. Fall back to a regular
# resolve when the lockfile is absent so a freshly-rendered project
# still builds; the warning makes the slower path visible.
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then \
        uv sync --frozen --no-install-project --no-dev; \
    else \
        echo "warning: no uv.lock — resolving dependencies on the fly"; \
        uv sync --no-install-project --no-dev; \
    fi

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then \
        uv sync --frozen --no-dev; \
    else \
        uv sync --no-dev; \
    fi

# ----- runtime ------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --create-home --home-dir /home/app app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

USER app

# Replace with the actual entrypoint your project ships. The default
# `python -m {{ cookiecutter.python_package_name }}` works once the
# package exposes a `__main__.py`.
CMD ["python", "-m", "{{ cookiecutter.python_package_name }}"]
{%- elif cookiecutter.primary_language == 'typescript' -%}
# ----- builder ------------------------------------------------------
FROM ${NODE_IMAGE} AS builder

ENV NODE_ENV=production \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

WORKDIR /app
COPY package.json package-lock.json* ./
# `npm ci` requires a committed lockfile; fall back to `npm install`
# when one is absent so a freshly-rendered project still builds.
RUN if [ -f package-lock.json ]; then \
        npm ci --include=dev; \
    else \
        echo "warning: no package-lock.json — running npm install"; \
        npm install --include=dev; \
    fi

COPY . .
# Run `build` when (and only when) the project defines one; a missing
# script is fine, but a real failure must abort the build.
RUN if node -e "process.exit(require('./package.json').scripts && require('./package.json').scripts.build ? 0 : 1)"; then \
        npm run build; \
    else \
        echo "no build script — skipping"; \
    fi
# `dist/` is the conventional output directory; ensure it exists even
# when no build step ran so the runtime stage's COPY is unconditional.
RUN mkdir -p dist
RUN npm prune --omit=dev

# ----- runtime ------------------------------------------------------
FROM ${NODE_IMAGE} AS runtime

ENV NODE_ENV=production

RUN groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --create-home --home-dir /home/app app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

USER app

# Replace with the actual entrypoint the rendered project exposes.
CMD ["node", "dist/index.js"]
{%- elif cookiecutter.primary_language == 'polyglot' -%}
# ----- python builder -----------------------------------------------
FROM ${PYTHON_IMAGE} AS python-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then \
        uv sync --frozen --no-install-project --no-dev; \
    else \
        echo "warning: no uv.lock — resolving dependencies on the fly"; \
        uv sync --no-install-project --no-dev; \
    fi
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then \
        uv sync --frozen --no-dev; \
    else \
        uv sync --no-dev; \
    fi

# ----- node builder -------------------------------------------------
FROM ${NODE_IMAGE} AS node-builder

ENV NODE_ENV=production \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
        npm ci --include=dev; \
    else \
        echo "warning: no package-lock.json — running npm install"; \
        npm install --include=dev; \
    fi
COPY . .
RUN if node -e "process.exit(require('./package.json').scripts && require('./package.json').scripts.build ? 0 : 1)"; then \
        npm run build; \
    else \
        echo "no build script — skipping"; \
    fi
# Ensure `dist/` always exists so the runtime COPY below is unconditional.
RUN mkdir -p dist
RUN npm prune --omit=dev

# ----- runtime (python-based, with node bundled) --------------------
FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=production \
    PATH="/app/.venv/bin:/usr/local/lib/node/bin:$PATH"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=node-builder /usr/local/bin/node /usr/local/bin/node
COPY --from=node-builder /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

RUN groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --create-home --home-dir /home/app app

WORKDIR /app
COPY --from=python-builder --chown=app:app /app /app
COPY --from=node-builder --chown=app:app /app/node_modules /app/node_modules
COPY --from=node-builder --chown=app:app /app/dist /app/dist

USER app

CMD ["python", "-m", "{{ cookiecutter.python_package_name }}"]
{%- endif %}
