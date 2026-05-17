#!/usr/bin/env bash
# install-prereqs.sh — best-effort install of the three CLIs + helpers
# Detects macOS/Debian/Ubuntu; documents manual fallbacks for everything else.
set -euo pipefail

C_BLUE='\033[0;34m'; C_OFF='\033[0m'
say() { printf "${C_BLUE}==>${C_OFF} %s\n" "$*"; }

OS="unknown"
[[ "$(uname)" == "Darwin" ]] && OS="macos"
[[ -f /etc/debian_version ]] && OS="debian"

install_jq() {
  command -v jq >/dev/null && return 0
  case "$OS" in
    macos)  brew install jq ;;
    debian) sudo apt-get install -y jq ;;
    *) echo "manual: install jq from https://jqlang.github.io/jq/" ;;
  esac
}

install_tmux() {
  command -v tmux >/dev/null && return 0
  case "$OS" in
    macos)  brew install tmux ;;
    debian) sudo apt-get install -y tmux ;;
    *) echo "manual: install tmux" ;;
  esac
}

install_node() {
  command -v node >/dev/null && return 0
  case "$OS" in
    macos)  brew install node ;;
    debian) curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y nodejs ;;
    *) echo "manual: install Node 22+ from https://nodejs.org/" ;;
  esac
}

install_claude() {
  command -v claude >/dev/null && { say "claude already installed"; return 0; }
  say "Installing Claude Code..."
  npm install -g @anthropic-ai/claude-code || echo "manual: https://docs.claude.com/claude-code"
}

install_codex() {
  command -v codex >/dev/null && { say "codex already installed"; return 0; }
  say "Installing Codex..."
  npm install -g @openai/codex || echo "manual: https://github.com/openai/codex"
}

install_pi() {
  command -v pi >/dev/null && { say "pi already installed"; return 0; }
  say "Installing Pi..."
  if curl -fsSL https://pi.dev/install.sh | sh; then return 0; fi
  npm install -g @earendil-works/pi-coding-agent || echo "manual: see https://pi.dev/"
}

say "Detected OS: $OS"
install_jq
install_tmux
install_node
install_claude
install_codex
install_pi

say "Done. Run scripts/verify-install.sh to confirm."
