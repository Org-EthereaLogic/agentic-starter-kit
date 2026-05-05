#!/usr/bin/env bash
# Devcontainer post-create. Installs the tools the rendered project's
# `make sync` and `make validate` targets expect but that the
# devcontainer base image does not ship: uv (Astral), jq, ripgrep.
#
# Idempotent: every install step is a no-op when the tool is already
# present. The script never fails the container build on a single
# tool missing — surface the diagnostic and continue.

set -eu

log() { printf '[devcontainer] %s\n' "$*"; }

ensure_apt_packages() {
  local missing=()
  for pkg in jq ripgrep make; do
    if ! command -v "$pkg" >/dev/null 2>&1; then
      missing+=("$pkg")
    fi
  done
  if [ "${#missing[@]}" -eq 0 ]; then
    log "apt packages already present (jq, ripgrep, make)"
    return 0
  fi
  log "installing apt packages: ${missing[*]}"
  sudo apt-get update -y
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"
  sudo rm -rf /var/lib/apt/lists/*
}

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    log "uv already installed: $(uv --version)"
    return 0
  fi
  log "installing uv (Astral)"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # The installer drops uv in ~/.local/bin; make it visible for this shell.
  export PATH="$HOME/.local/bin:$PATH"
  log "uv installed: $(uv --version)"
}

run_sync_if_possible() {
  if [ ! -f Makefile ]; then
    return 0
  fi
  if ! grep -q '^sync:' Makefile && ! grep -q '^sync:' Makefile.fragments/*.mk 2>/dev/null; then
    return 0
  fi
  log "running make sync"
  make sync || log "make sync failed (continuing — re-run manually)"
}

main() {
  ensure_apt_packages
  ensure_uv
  run_sync_if_possible
  log "post-create complete"
}

main "$@"
