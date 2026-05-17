#!/usr/bin/env python3
"""Captures #-prefixed messages as memories.

- "#text" → project memory (.agent-os/memories.md in current project)
- "##text" → personal memory (~/.agent-os/memories.md)

Wire as UserPromptSubmit hook in your CLI's settings.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def find_project_memory() -> Path:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or \
                  os.environ.get("DROID_PROJECT_DIR") or \
                  os.environ.get("PROJECT_DIR") or os.getcwd()
    return Path(project_dir) / ".agent-os" / "memories.md"


def find_personal_memory() -> Path:
    return Path.home() / ".agent-os" / "memories.md"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    prompt = (data.get("prompt") or "").strip()
    if not prompt.startswith("#"):
        return
    if prompt.startswith("##"):
        target = find_personal_memory()
        content = prompt[2:].strip()
    else:
        target = find_project_memory()
        content = prompt[1:].strip()
    if not content:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text("# Memories\n\n", encoding="utf-8")
    stamp = datetime.now().strftime("%Y-%m-%d")
    with target.open("a", encoding="utf-8") as fh:
        fh.write(f"- [{stamp}] {content}\n")
    print(json.dumps({"systemMessage": f"OK saved to {target}"}))


if __name__ == "__main__":
    main()
