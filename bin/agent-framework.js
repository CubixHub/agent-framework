#!/usr/bin/env node
/**
 * @cubixhub/agent-framework — npx entry point.
 *
 * Usage:
 *   npx github:cubixhub/agent-framework [target-dir]
 *   npx github:cubixhub/agent-framework my-app
 *   npx @cubixhub/agent-framework@latest my-app    (if published to npm)
 *
 * This is a thin wrapper that:
 *   1. Locates the Framework root (resolved via __dirname).
 *   2. Verifies bash + git are installed.
 *   3. Spawns scripts/init-project.sh with the target directory.
 *   4. Forwards stdio so the user sees prompts and answers them live.
 *
 * Windows: bash is required. WSL or Git Bash should both work; the script
 * itself is POSIX bash.
 */

'use strict';

const { spawn, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const FRAMEWORK_DIR = path.resolve(__dirname, '..');
const INIT_SCRIPT = path.join(FRAMEWORK_DIR, 'scripts', 'init-project.sh');

const RED = '\x1b[0;31m';
const GREEN = '\x1b[0;32m';
const YELLOW = '\x1b[1;33m';
const BLUE = '\x1b[0;34m';
const BOLD = '\x1b[1m';
const RESET = '\x1b[0m';

function die(msg, code = 1) {
  process.stderr.write(`${RED}error${RESET}  ${msg}\n`);
  process.exit(code);
}

function info(msg) {
  process.stderr.write(`${BLUE}==>${RESET} ${BOLD}${msg}${RESET}\n`);
}

function which(bin) {
  const r = spawnSync(process.platform === 'win32' ? 'where' : 'which', [bin], {
    stdio: ['ignore', 'pipe', 'ignore']
  });
  return r.status === 0 && r.stdout.toString().trim();
}

function preflight() {
  if (!which('bash')) {
    die(
      'bash not found on PATH.\n' +
        '  - macOS/Linux: bash is built in.\n' +
        '  - Windows: install WSL (https://aka.ms/wsl) or Git Bash.\n' +
        '  - Then re-run this command.'
    );
  }
  if (!which('git')) {
    die('git not found on PATH. Install git, then re-run.');
  }
  if (!fs.existsSync(INIT_SCRIPT)) {
    die(`init-project.sh not found at ${INIT_SCRIPT}. The package looks corrupt.`);
  }
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const flags = { help: false, version: false, dryRun: false };
  const positional = [];
  for (const a of args) {
    if (a === '-h' || a === '--help') flags.help = true;
    else if (a === '-V' || a === '--version') flags.version = true;
    else if (a === '--dry-run') flags.dryRun = true;
    else positional.push(a);
  }
  return { flags, positional };
}

function printHelp() {
  const pkg = require(path.join(FRAMEWORK_DIR, 'package.json'));
  process.stdout.write(
    `\n${BOLD}@cubixhub/agent-framework${RESET}  v${pkg.version}\n` +
      `${pkg.description}\n\n` +
      `${BOLD}Usage:${RESET}\n` +
      `  npx github:cubixhub/agent-framework [target-dir]\n` +
      `  agent-framework [target-dir]\n\n` +
      `${BOLD}Flags:${RESET}\n` +
      `  -h, --help       Show this message.\n` +
      `  -V, --version    Print version.\n` +
      `  --dry-run        Print what would be scaffolded; do not write.\n\n` +
      `${BOLD}What it does:${RESET}\n` +
      `  Interactive prompts for project name, default branch, owner,\n` +
      `  PM tool (linear|plane|none), CLIs to enable, languages. Copies\n` +
      `  template/, substitutes placeholders, installs skills + agents +\n` +
      `  orchestration, runs git init, makes an initial commit.\n\n` +
      `${BOLD}After scaffolding:${RESET}\n` +
      `  cd <target>\n` +
      `  cp .env.example .env  && $EDITOR .env    # if you chose linear/plane\n` +
      `  claude    # or codex, or pi\n\n` +
      `Docs: ${pkg.homepage}\n\n`
  );
}

function printVersion() {
  const pkg = require(path.join(FRAMEWORK_DIR, 'package.json'));
  process.stdout.write(`${pkg.version}\n`);
}

function run() {
  const { flags, positional } = parseArgs(process.argv);

  if (flags.help) {
    printHelp();
    return;
  }
  if (flags.version) {
    printVersion();
    return;
  }

  preflight();

  const target = positional[0]; // optional
  info('Tri-CLI Project Scaffolder — invoking init-project.sh');

  const env = { ...process.env };
  if (flags.dryRun) env.DRY_RUN = '1';

  // Spawn the bash script with stdio inherited so the user sees prompts.
  const args = [INIT_SCRIPT];
  if (target) args.push(target);

  const child = spawn('bash', args, {
    stdio: 'inherit',
    env,
    cwd: process.cwd()
  });

  child.on('exit', (code, signal) => {
    if (signal) process.exit(1);
    process.exit(code ?? 1);
  });

  child.on('error', (err) => {
    die(`failed to spawn bash: ${err.message}`);
  });
}

run();
