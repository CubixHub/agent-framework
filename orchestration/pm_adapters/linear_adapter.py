"""Linear PM adapter — GraphQL.

Env vars:
  LINEAR_API_KEY     (required)
  LINEAR_TEAM_KEY    (required, e.g. "AEV")
  LINEAR_PROJECT_ID  (optional; scopes fetch_queue)

State + label IDs are cached at /tmp/linear_state.json so we don't
re-query schema metadata on every poll. Delete that file to force a
refresh on next tick (e.g. after adding a new workflow state).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

from .base import Issue, PMAdapter

LINEAR_API = "https://api.linear.app/graphql"
CACHE_PATH = Path("/tmp/linear_state.json")


def _gql(query: str, variables: dict[str, Any] | None = None) -> dict:
    key = os.environ["LINEAR_API_KEY"]
    r = requests.post(
        LINEAR_API,
        headers={"Authorization": key, "Content-Type": "application/json"},
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"linear GraphQL: {data['errors']}")
    return data["data"]


class LinearAdapter(PMAdapter):
    name = "linear"

    def __init__(self,
                 eligible_states: list[str],
                 processing_state: str = "Processing") -> None:
        self.eligible = set(eligible_states)
        self.processing_state = processing_state
        self.cache = self._load_cache()

    # ---------- schema cache ----------

    def _load_cache(self) -> dict:
        if CACHE_PATH.exists():
            try:
                return json.loads(CACHE_PATH.read_text())
            except Exception:
                pass
        cache = self._refresh_cache()
        CACHE_PATH.write_text(json.dumps(cache, indent=2))
        return cache

    def _refresh_cache(self) -> dict:
        team_key = os.environ["LINEAR_TEAM_KEY"]
        q = """
        query($key: String!) {
          teams(filter: {key: {eq: $key}}) {
            nodes {
              id
              states { nodes { id name } }
              labels { nodes { id name } }
            }
          }
        }
        """
        d = _gql(q, {"key": team_key})
        nodes = d["teams"]["nodes"]
        if not nodes:
            raise RuntimeError(f"linear team {team_key} not found")
        t = nodes[0]
        return {
            "fetched_at": time.time(),
            "team_id": t["id"],
            "team_key": team_key,
            "states": {s["name"]: s["id"] for s in t["states"]["nodes"]},
            "labels": {l["name"]: l["id"] for l in t["labels"]["nodes"]},
        }

    # ---------- queue ----------

    def fetch_queue(self) -> list[Issue]:
        state_ids = [self.cache["states"][s] for s in self.eligible
                     if s in self.cache["states"]]
        if not state_ids:
            return []
        proj = os.environ.get("LINEAR_PROJECT_ID")
        q = """
        query($team: String!, $states: [ID!], $proj: ID) {
          issues(
            filter: {
              team:    {id: {eq: $team}},
              state:   {id: {in: $states}},
              project: {id: {eq: $proj}}
            }
          ) {
            nodes {
              id identifier title description
              state { name }
              labels { nodes { name } }
            }
          }
        }
        """
        d = _gql(q, {"team": self.cache["team_id"], "states": state_ids, "proj": proj})
        out: list[Issue] = []
        for n in d["issues"]["nodes"]:
            out.append(Issue(
                id=n["identifier"],
                title=n["title"] or "",
                body=n["description"] or "",
                state=n["state"]["name"],
                labels=[l["name"] for l in n["labels"]["nodes"]],
                pm_native={"node_id": n["id"]},
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
            raise RuntimeError(f"linear state {state_name!r} not found")
        m = """
        mutation($id: String!, $sid: String!) {
          issueUpdate(id: $id, input: {stateId: $sid}) { success }
        }
        """
        d = _gql(m, {"id": issue.pm_native["node_id"], "sid": sid})
        return bool(d["issueUpdate"]["success"])

    def post_comment(self, issue: Issue, body: str) -> bool:
        if not body:
            return True
        m = """
        mutation($id: String!, $body: String!) {
          commentCreate(input: {issueId: $id, body: $body}) { success }
        }
        """
        d = _gql(m, {"id": issue.pm_native["node_id"], "body": body})
        return bool(d["commentCreate"]["success"])

    def claim(self, issue: Issue, comment: str = "") -> bool:
        if comment:
            self.post_comment(issue, comment)
        return self._set_state(issue, self.processing_state)

    def transition_state(self, issue: Issue, state: str, comment: str = "") -> bool:
        if comment:
            self.post_comment(issue, comment)
        return self._set_state(issue, state)
