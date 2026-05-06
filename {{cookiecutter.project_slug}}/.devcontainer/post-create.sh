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
  # Map (apt package name) -> (binary that proves it is installed).
  # `ripgrep` ships the `rg` binary; the package and binary names differ.
  local -A pkg_bin=(
    [jq]=jq
    [ripgrep]=rg
    [make]=make
  )
  local missing=()
  for pkg in "${!pkg_bin[@]}"; do
    if ! command -v "${pkg_bin[$pkg]}" >/dev/null 2>&1; then
      missing+=("$pkg")
    fi
  done
  if [ "${#missing[@]}" -eq 0 ]; then
    log "apt packages already present (jq, ripgrep, make)"
    return 0
  fi
  log "installing apt packages: ${missing[*]}"
  # Tolerate transient apt failures — the script's contract is to
  # report and continue, not abort `postCreateCommand`.
  if ! sudo apt-get update -y; then
    log "apt-get update failed — skipping apt install (rerun this script manually)"
    return 0
  fi
  if ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"; then
    log "apt-get install failed for: ${missing[*]} (continuing)"
  fi
  sudo rm -rf /var/lib/apt/lists/* || true
}

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    log "uv already installed: $(uv --version)"
    return 0
  fi
  log "installing uv (Astral) to /usr/local/bin"
  # Drop the binary into a system-wide location so it survives across
  # shells without relying on the user's ~/.local/bin being on PATH.
  if ! curl -LsSf https://astral.sh/uv/install.sh \
        | sudo env UV_INSTALL_DIR=/usr/local/bin UV_NO_MODIFY_PATH=1 sh; then
    log "uv install failed (continuing — re-run this script manually)"
    return 0
  fi
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
