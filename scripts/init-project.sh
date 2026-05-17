#!/usr/bin/env bash
# init-project.sh — scaffold a new tri-CLI agent-native project
# Usage: bash scripts/init-project.sh [target-dir]
set -euo pipefail

FRAMEWORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$FRAMEWORK_DIR/template"

C_BLUE='\033[0;34m'; C_GREEN='\033[0;32m'; C_YELLOW='\033[1;33m'
C_RED='\033[0;31m'; C_BOLD='\033[1m'; C_OFF='\033[0m'

say()  { printf "${C_BLUE}==>${C_OFF} ${C_BOLD}%s${C_OFF}\n" "$*"; }
ok()   { printf "${C_GREEN}  ok${C_OFF} %s\n" "$*"; }
warn() { printf "${C_YELLOW}  ![${C_OFF} %s\n" "$*"; }
err()  { printf "${C_RED}  X${C_OFF} %s\n" "$*" >&2; }
ask()  {
  local prompt="$1" default="${2:-}" var
  # Prompt text goes to STDERR so $(...) captures only the answer.
  printf "${C_BOLD}?${C_OFF} %s${default:+ [${default}]} " "$prompt" >&2
  if [ -t 0 ] && [ -t 1 ]; then
    read -r var </dev/tty || true
  else
    read -r var || true
  fi
  printf "%s" "${var:-$default}"
}
ask_choice() {
  local prompt="$1"; shift; local -a opts=("$@"); local i=1
  printf "${C_BOLD}?${C_OFF} %s\n" "$prompt" >&2
  for o in "${opts[@]}"; do printf "    %d) %s\n" "$i" "$o" >&2; i=$((i+1)); done
  local n; n=$(ask "Choice" "1"); printf "%s" "${opts[$((n-1))]}"
}

say "Tri-CLI Project Scaffolder"
echo

PROJECT_NAME=$(ask "Project name (kebab-case)")
[ -z "$PROJECT_NAME" ] && err "Project name required" && exit 1

TARGET_DIR="${1:-$PWD/$PROJECT_NAME}"
if [ -e "$TARGET_DIR" ]; then
  err "$TARGET_DIR already exists"; exit 1
fi

DEFAULT_BRANCH=$(ask "Default git branch" "main")
OWNER=$(ask "Owner (github user or org)" "$USER")
REPO_URL=$(ask "Remote URL (blank to skip)" "")

PM_TOOL=$(ask_choice "Project management tool" "linear" "plane" "none")
CLI_CHOICE=$(ask_choice "Which CLI(s) to enable" "all" "claude" "codex" "pi")
LANGUAGES=$(ask "Primary languages (space-sep, e.g. 'typescript python')" "typescript")

echo
say "Scaffolding to: $TARGET_DIR"
mkdir -p "$TARGET_DIR"
cp -r "$TEMPLATE_DIR"/. "$TARGET_DIR"/
ok "Template files copied"

# Substitute placeholders in *.tmpl files, rename to drop .tmpl
TODAY=$(date +%Y-%m-%d)
find "$TARGET_DIR" -type f -name "*.tmpl" | while read -r f; do
  out="${f%.tmpl}"
  sed -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" \
      -e "s|{{REPO_URL}}|${REPO_URL:-TBD}|g" \
      -e "s|{{OWNER}}|$OWNER|g" \
      -e "s|{{DEFAULT_BRANCH}}|$DEFAULT_BRANCH|g" \
      -e "s|{{PM_TOOL}}|$PM_TOOL|g" \
      -e "s|{{CLI_CHOICE}}|$CLI_CHOICE|g" \
      -e "s|{{LANGUAGES}}|$LANGUAGES|g" \
      -e "s|{{DATE}}|$TODAY|g" \
      "$f" > "$out"
  rm "$f"
done
ok "Placeholders substituted"

# Copy skills, agents, orchestration into the new project
mkdir -p "$TARGET_DIR/.agent-os/skills" "$TARGET_DIR/.agent-os/agents"
cp -r "$FRAMEWORK_DIR/skills"/. "$TARGET_DIR/.agent-os/skills/" 2>/dev/null || true
cp -r "$FRAMEWORK_DIR/agents"/. "$TARGET_DIR/.agent-os/agents/" 2>/dev/null || true
cp -r "$FRAMEWORK_DIR/orchestration" "$TARGET_DIR/orchestration"
ok "Skills, agents, orchestration installed"

# Wire PM tool
if [ "$PM_TOOL" != "none" ]; then
  cp "$FRAMEWORK_DIR/integrations/$PM_TOOL/env.example" "$TARGET_DIR/.env.example"
  ok "PM env template: $TARGET_DIR/.env.example (edit with your API key)"
fi

# Wire CLI overlays based on choice
if [ "$CLI_CHOICE" != "claude" ] && [ "$CLI_CHOICE" != "all" ]; then rm -rf "$TARGET_DIR/.claude"; fi
if [ "$CLI_CHOICE" != "codex"  ] && [ "$CLI_CHOICE" != "all" ]; then rm -rf "$TARGET_DIR/.codex";  fi
if [ "$CLI_CHOICE" != "pi"     ] && [ "$CLI_CHOICE" != "all" ]; then rm -rf "$TARGET_DIR/.pi";     fi
ok "CLI overlays configured ($CLI_CHOICE)"

# Persist settings
cat > "$TARGET_DIR/.agent-os/settings.json" <<JSON
{
  "project_name": "$PROJECT_NAME",
  "owner": "$OWNER",
  "default_branch": "$DEFAULT_BRANCH",
  "pm_provider": "$PM_TOOL",
  "cli_active": "$CLI_CHOICE",
  "languages": "$LANGUAGES",
  "autonomy_mode": "M1",
  "hooks_enabled": true,
  "skills_enabled": true
}
JSON
ok "Project settings written: .agent-os/settings.json"

# Mark hooks executable
chmod +x "$TARGET_DIR/.agent-os/hooks/"*.sh 2>/dev/null || true

# git init + first commit
cd "$TARGET_DIR"
git init -b "$DEFAULT_BRANCH" >/dev/null
[ -n "$REPO_URL" ] && git remote add origin "$REPO_URL"
git add . >/dev/null
git -c user.email="scaffold@local" -c user.name="init-project.sh" \
    commit -m "scaffold: $PROJECT_NAME via Framework init" >/dev/null
ok "git initialized, first commit made"

echo
say "Next steps"
echo "  cd $TARGET_DIR"
[ "$PM_TOOL" != "none" ] && echo "  cp .env.example .env  && \$EDITOR .env   # add your $PM_TOOL API key"
[ "$PM_TOOL" != "none" ] && echo "  bash ../Framework/integrations/$PM_TOOL/bootstrap.sh"
echo "  bash ../Framework/scripts/verify-install.sh   # check CLI binaries"
echo "  # then start a CLI of your choice:"
[ "$CLI_CHOICE" = "claude" ] || [ "$CLI_CHOICE" = "all" ] && echo "  claude"
[ "$CLI_CHOICE" = "codex"  ] || [ "$CLI_CHOICE" = "all" ] && echo "  codex"
[ "$CLI_CHOICE" = "pi"     ] || [ "$CLI_CHOICE" = "all" ] && echo "  pi"
echo
ok "Done — project ready at $TARGET_DIR"
