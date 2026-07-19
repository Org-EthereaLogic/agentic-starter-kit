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
warn() { printf '[devcontainer] WARN: %s\n' "$*" >&2; }

check_outbound_network() {
  # Probe a small canonical endpoint that every downstream step needs
  # (uv, pip, npm, gh all hit at least one of these registries). If
  # this fails the rest of post-create is going to fail with cryptic
  # tool-specific errors; surface a single clear diagnostic up front.
  #
  # Reasons this typically fails (in 2026):
  #   - VS Code Insiders 'Restricted Network Access' (approve via the
  #     IDE dialog, or pre-allow in user settings).
  #   - GitHub Codespaces restricted-internet policy
  #     (configure via the Codespaces UI; the declarative schema in
  #     `customizations.codespaces.*` is not yet documented).
  #   - GitHub Copilot Coding Agent firewall (allowlist domains in
  #     `.github/copilot/firewall.yml`).
  #   - Corporate proxy blocking the container bridge network (set
  #     `HTTP_PROXY` / `HTTPS_PROXY` in `containerEnv`).
  # See KNOWN-ISSUES.md > "Dev container internet access blocked".
  if ! command -v curl >/dev/null 2>&1; then
    # Some minimal base images omit curl. Without it the probe would
    # falsely report "no network" — skip and let the apt step install
    # curl alongside jq/ripgrep/make.
    log "curl not on PATH; skipping outbound-network probe"
    return 0
  fi
  if curl --max-time 5 --silent --fail --output /dev/null https://pypi.org/simple/ 2>/dev/null; then
    log "outbound network OK (pypi.org reachable)"
    return 0
  fi
  warn "no outbound HTTPS access to pypi.org from this container"
  warn "downstream apt/uv/npm/gh installs will likely fail with cryptic errors"
  warn "common causes:"
  warn "  - VS Code 'Restricted Network Access' (approve dialog or preset in user settings)"
  warn "  - Codespaces restricted internet (configure via the Codespaces UI)"
  warn "  - Copilot Coding Agent firewall (.github/copilot/firewall.yml)"
  warn "  - Corporate proxy (set HTTP_PROXY/HTTPS_PROXY in containerEnv)"
  warn "see KNOWN-ISSUES.md > 'Dev container internet access blocked' for remediation"
}

ensure_apt_packages() {
  # Map (apt package name) -> (binary that proves it is installed).
  # `ripgrep` ships the `rg` binary; the package and binary names differ.
  local -A pkg_bin=(
    [jq]=jq
    [ripgrep]=rg
    [make]=make
    [curl]=curl
  )
  local missing=()
  for pkg in "${!pkg_bin[@]}"; do
    if ! command -v "${pkg_bin[$pkg]}" >/dev/null 2>&1; then
      missing+=("$pkg")
    fi
  done
  if [ "${#missing[@]}" -eq 0 ]; then
    log "apt packages already present (jq, ripgrep, make, curl)"
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
  # Download to a temp file and check curl's own exit status before
  # running it — piping curl directly into `sh` masks a curl failure
  # (network blocked, 404, truncated download) behind sh's exit code,
  # which can be 0 on an empty/partial script and falsely report success.
  local uv_installer
  uv_installer="$(mktemp)"
  if ! curl -LsSf https://astral.sh/uv/install.sh -o "$uv_installer"; then
    log "uv install failed (continuing — re-run this script manually)"
    rm -f "$uv_installer"
    return 0
  fi
  if ! sudo env UV_INSTALL_DIR=/usr/local/bin UV_NO_MODIFY_PATH=1 sh "$uv_installer"; then
    log "uv install failed (continuing — re-run this script manually)"
    rm -f "$uv_installer"
    return 0
  fi
  rm -f "$uv_installer"
  if command -v uv >/dev/null 2>&1; then
    log "uv installed: $(uv --version)"
  else
    log "uv install script reported success but 'uv' is not on PATH (continuing — re-run this script manually)"
  fi
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
      npm config set prefix "$HOME/.npm-global" || log "npm config set prefix failed (continuing — npm-distributed AI CLI installs may fail)"
      mkdir -p "$HOME/.npm-global/bin" || log "mkdir -p \$HOME/.npm-global/bin failed (continuing — npm-distributed AI CLI installs may fail)"
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

install_git_hooks() {
  # Wire the git-layer protected-branch boundary (CRIT-008): point
  # core.hooksPath at the checked-in .githooks dir so .githooks/pre-commit
  # and pre-push run on every commit/push. Idempotent (git config
  # overwrites the same key). Log-and-continue on failure like every
  # other step. Literal `.githooks` — this file is copied without Jinja
  # rendering, so no branch-name interpolation is available or needed.
  if ! git rev-parse --git-dir >/dev/null 2>&1; then
    log "not a git work tree yet; skipping git-hook wiring (run 'make hooks-install' after 'git init')"
    return 0
  fi
  if [ ! -d .githooks ]; then
    log ".githooks not present; skipping git-hook wiring"
    return 0
  fi
  if git config core.hooksPath .githooks; then
    log "git-layer hooks wired: core.hooksPath -> .githooks (CRIT-008)"
  else
    log "git config core.hooksPath failed (continuing — run 'make hooks-install' manually)"
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
  check_outbound_network
  ensure_apt_packages
  ensure_uv
  ensure_ai_clis
  install_git_hooks
  run_sync_if_possible
  log "post-create complete"
}

main "$@"
