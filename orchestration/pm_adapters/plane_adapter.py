"""Plane.so PM adapter — REST.

Env vars:
  PLANE_API_KEY            (required)
  PLANE_WORKSPACE_SLUG     (required)
  PLANE_PROJECT_ID         (required)
  PLANE_API_BASE_URL       (optional, defaults to https://api.plane.so/api/v1)

Plane concepts: workspace → project → issue. States and labels are
per-project resources. We cache state/label name→id maps in
/tmp/plane_state.json. Delete to refresh.

Docs: https://developers.plane.so/api-reference/introduction
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

from .base import Issue, PMAdapter

CACHE_PATH = Path("/tmp/plane_state.json")


def _base() -> str:
    return os.environ.get("PLANE_API_BASE_URL", "https://api.plane.so/api/v1").rstrip("/")


def _headers() -> dict:
    return {
        "X-API-Key": os.environ["PLANE_API_KEY"],
        "Content-Type": "application/json",
    }


def _ws() -> str:
    return os.environ["PLANE_WORKSPACE_SLUG"]


def _proj() -> str:
    return os.environ["PLANE_PROJECT_ID"]


def _get(path: str, params: dict | None = None) -> Any:
    r = requests.get(f"{_base()}{path}", headers=_headers(), params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json()


def _post(path: str, payload: dict) -> Any:
    r = requests.post(f"{_base()}{path}", headers=_headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def _patch(path: str, payload: dict) -> Any:
    r = requests.patch(f"{_base()}{path}", headers=_headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


class PlaneAdapter(PMAdapter):
    name = "plane"

    def __init__(self,
                 eligible_states: list[str],
                 processing_state: str = "Processing") -> None:
        self.eligible = set(eligible_states)
        self.processing_state = processing_state
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if CACHE_PATH.exists():
            try:
                return json.loads(CACHE_PATH.read_text())
            except Exception:
                pass
        c = self._refresh_cache()
        CACHE_PATH.write_text(json.dumps(c, indent=2))
        return c

    def _refresh_cache(self) -> dict:
        prefix = f"/workspaces/{_ws()}/projects/{_proj()}"
        states = _get(f"{prefix}/states/")
        labels = _get(f"{prefix}/labels/")
        return {
            "fetched_at": time.time(),
            "workspace": _ws(),
            "project_id": _proj(),
            "states": {s["name"]: s["id"] for s in (states.get("results") or states)},
            "labels": {l["name"]: l["id"] for l in (labels.get("results") or labels)},
        }

    # ---------- queue ----------

    def fetch_queue(self) -> list[Issue]:
        prefix = f"/workspaces/{_ws()}/projects/{_proj()}"
        state_ids = [self.cache["states"][s] for s in self.eligible
                     if s in self.cache["states"]]
        if not state_ids:
            return []
        # Plane allows state filter via query string (comma-sep).
        params = {"state": ",".join(state_ids), "per_page": "100"}
        data = _get(f"{prefix}/issues/", params=params)
        results = data.get("results") if isinstance(data, dict) else data
        out: list[Issue] = []
        # Build id->name reverse maps for human-friendly fields.
        rev_state = {v: k for k, v in self.cache["states"].items()}
        rev_label = {v: k for k, v in self.cache["labels"].items()}
        for n in results or []:
            labels = [rev_label.get(lid, lid) for lid in (n.get("label_ids") or [])]
            out.append(Issue(
                id=n.get("sequence_id") and f"{n.get('project_identifier','ISSUE')}-{n['sequence_id']}"
                   or n["id"],
                title=n.get("name") or "",
                body=n.get("description_stripped") or n.get("description") or "",
                state=rev_state.get(n.get("state"), str(n.get("state"))),
                labels=labels,
                pm_native={"plane_id": n["id"]},
            ))
        return out

    # ---------- mutations ----------

    def _set_state(self, issue: Issue, state_name: str) -> bool:
        sid = self.cache["states"].get(state_name)
        if not sid:
            self.cache = self._refresh_cache()
            CACHE_PATH.write_text(json.dumps(self.cache, indent=2))
            sid = self.cache["states"].get(state_name)
        if not sid:
            raise RuntimeError(f"plane state {state_name!r} not found")
        prefix = f"/workspaces/{_ws()}/projects/{_proj()}"
        _patch(f"{prefix}/issues/{issue.pm_native['plane_id']}/", {"state": sid})
        return True

    def post_comment(self, issue: Issue, body: str) -> bool:
        if not body:
            return True
        prefix = f"/workspaces/{_ws()}/projects/{_proj()}"
        _post(f"{prefix}/issues/{issue.pm_native['plane_id']}/comments/",
              {"comment_html": body, "comment_stripped": body})
        return True

    def claim(self, issue: Issue, comment: str = "") -> bool:
        if comment:
            self.post_comment(issue, comment)
        return self._set_state(issue, self.processing_state)

    def transition_state(self, issue: Issue, state: str, comment: str = "") -> bool:
        if comment:
            self.post_comment(issue, comment)
        return self._set_state(issue, state)
