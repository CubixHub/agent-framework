# API design rules

- REST or RPC: pick one per service, document the choice in an ADR.
- Version prefix: `/api/v1/...` (or RPC namespace). Never break v1 without v2.
- Idempotency keys on every mutating endpoint that the client may retry.
- Error shape: `{ "code": "MACHINE_READABLE", "message": "Human readable", "details": {} }`.
  Never expose internal errors or stack traces.
- Status codes are the contract: 200 ok, 201 created, 204 no content, 400 client error,
  401 unauth, 403 forbidden, 404 not found, 409 conflict, 422 validation, 5xx server.
- Auth at every protected route via middleware. Never trust client claims.
- Input validation with Zod (TS) or Pydantic (Py) at the boundary — typed structs only past it.
- Pagination: cursor-based (`?after=<cursor>&limit=N`); never raw page numbers.
- Timestamps: RFC 3339 UTC, never local time, never epoch seconds.
- Backward-compat: additive only. Deprecate before removing. Document in CHANGELOG.
