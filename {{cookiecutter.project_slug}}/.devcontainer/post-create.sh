#!/usr/bin/env bash
# Devcontainer post-create. Installs the tools the rendered project's
# `make sync` and `make validate` targets expect but that the
# devcontainer base image does not ship: uv (Astral), jq, ripgrep,
# claude, codex, gemini, gh-copilot.
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

ensure_ai_clis() {
  # Best-effort install of AI CLIs the operator typically uses outside
  # the devcontainer (Claude Code, Codex, Gemini, gh-copilot).
  # Each step is a no-op when the binary is already on PATH and
  # logs-and-continues on failure (network, registry, auth).
  if ! command -v npm >/dev/null 2>&1; then
    log "npm not on PATH — skipping npm-distributed AI CLI installs"
  else
    # The Node devcontainer feature (nvm) sets a user-writable global prefix
    # automatically. In plain container images the default prefix (/usr/local)
    # is owned by root. Detect that and reconfigure to a user-local path so
    # installs succeed without sudo.
    local npm_prefix
    npm_prefix=$(npm config get prefix 2>/dev/null) || npm_prefix=""
    if [ -n "$npm_prefix" ] && [ ! -w "$npm_prefix" ]; then
      log "npm global prefix '${npm_prefix}' not writable — reconfiguring to \$HOME/.npm-global"
      npm config set prefix "$HOME/.npm-global"
      mkdir -p "$HOME/.npm-global/bin"
      export PATH="$HOME/.npm-global/bin:$PATH"
    fi

    local -A npm_pkg_bin=(
      [@anthropic-ai/claude-code]=claude
      [@openai/codex]=codex
      [@google/gemini-cli]=gemini
    )
    for pkg in "${!npm_pkg_bin[@]}"; do
      local bin="${npm_pkg_bin[$pkg]}"
      if command -v "$bin" >/dev/null 2>&1; then
        log "$bin already installed: $(command -v "$bin")"
        continue
      fi
      log "installing $pkg (provides $bin)"
      if ! npm install -g --no-fund --no-audit "$pkg"; then
        log "npm install failed for $pkg (continuing — re-run manually)"
      fi
    done
  fi

  if command -v gh >/dev/null 2>&1; then
    # gh 2.92+ ships `gh copilot` as a built-in that auto-downloads on
    # first real use; installing the extension against that version fails.
    # Prefer the built-in and fall back to the extension on older gh.
    if gh copilot --help >/dev/null 2>&1; then
      log "gh copilot built-in available (binary fetched on first use)"
    elif gh extension list 2>/dev/null | grep -q 'gh-copilot'; then
      log "gh-copilot extension already installed"
    else
      log "installing gh extension github/gh-copilot"
      if ! gh extension install github/gh-copilot >/dev/null 2>&1; then
        log "gh extension install gh-copilot failed (continuing — may need 'gh auth login')"
      fi
    fi
  else
    log "gh CLI not found — skipping gh-copilot install"
  fi
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
  ensure_ai_clis
  run_sync_if_possible
  log "post-create complete"
}

main "$@"
