# OPA Policy Engine (Open Policy Agent)

This folder contains the **authorization policy** for the Universal Service API. OPA evaluates **allow/deny** decisions using Rego policies, so authorization logic lives in one place and can be tested and versioned independently.

## How it fits with Auth0

- **Auth0** = **Authentication** (who you are): validates JWT, provides `sub`, `email`, `permissions`, `scope`.
- **OPA** = **Authorization** (what you can do): decides if that user is allowed to perform this **method** on this **path** using the permissions from the token.

Flow:

1. Request hits the API with `Authorization: Bearer <JWT>`.
2. API validates the JWT with Auth0 (existing `auth.py`).
3. API builds an **input** object: `{ request: { method, path }, user: { sub, permissions, scope, ... } }`.
4. API asks OPA: “Is this input allowed?” (e.g. `POST /v1/data/authz/allow` with body `input`).
5. If OPA returns `allow: true`, the API proceeds; otherwise it returns 403.

So: **Auth0 identifies the user and supplies permissions; OPA enforces which actions those permissions allow.**

## Folder structure

```
opa/
├── README.md                 # This file
├── config.yaml               # OPA server config (logging, bundles, etc.)
├── Dockerfile                # Run OPA as a server (e.g. sidecar in k8s)
├── policies/
│   ├── authz.rego            # Main authorization policy (allow by path + method + permissions)
│   └── .manifest             # Optional bundle manifest
├── data/                     # Optional JSON data (e.g. roles, config)
│   └── roles.json
└── input-examples/           # Example inputs for testing
    ├── allow.json            # Should be allowed
    └── deny.json             # Should be denied
```

## Input contract (API → OPA)

The API must send a JSON **input** when querying OPA. Suggested shape:

```json
{
  "request": {
    "method": "GET",
    "path": "/api/items",
    "headers": {}
  },
  "user": {
    "sub": "auth0|user-id",
    "email": "user@example.com",
    "permissions": ["read:items", "create:items"],
    "scope": "read:items create:items"
  }
}
```

- **Unauthenticated requests**: omit `user` or set `user: null`. Only health/docs and `/api/auth/info` are allowed without a user.
- **Authenticated requests**: `user` must include at least `permissions` (array) and/or `scope` (string), matching what Auth0 puts in the JWT.

## Policy → Auth0 permissions

The Rego policy maps HTTP method + path to the Auth0 permission from `AUTH0_SETUP.md`:

| Method | Path              | Required permission |
|--------|-------------------|----------------------|
| GET    | `/api/items`      | `read:items`         |
| GET    | `/api/items/{id}` | `read:items`         |
| POST   | `/api/items`      | `create:items`       |
| PUT    | `/api/items/{id}` | `update:items`       |
| DELETE | `/api/items/{id}` | `delete:items`       |
| GET    | `/api/me`         | `read:items`         |

Health/docs and `/api/auth/info` are allowed without a user.

## Running OPA locally

### 1. Run as a server (policies from disk)

```bash
cd opa
docker run -it --rm -p 8181:8181 -v $(pwd)/policies:/policies openpolicyagent/opa:0.69.0-rootless run --server /policies
```

Or with [OPA binary](https://www.openpolicyagent.org/docs/latest/#running-opa):

```bash
opa run --server ./policies
```

OPA API: `http://localhost:8181`.

### 2. Query allow decision

```bash
curl -X POST http://localhost:8181/v1/data/authz/allow \
  -H "Content-Type: application/json" \
  -d @input-examples/allow.json
# Expect: {"result": true}
```

```bash
curl -X POST http://localhost:8181/v1/data/authz/allow \
  -H "Content-Type: application/json" \
  -d @input-examples/deny.json
# Expect: {"result": false}
```

### 3. Get reason (optional)

```bash
curl -X POST http://localhost:8181/v1/data/authz/reason \
  -H "Content-Type: application/json" \
  -d @input-examples/deny.json
# e.g. {"result": "insufficient permissions"}
```

## Integrating the API with OPA

1. **Add OPA base URL** to config (e.g. `OPA_URL=http://localhost:8181` or in k8s `http://localhost:8181` for sidecar).
2. **After** Auth0 JWT validation in `auth.py`, build the input:
   - `request.method`, `request.path` from the current request.
   - `user` from the decoded JWT: `sub`, `permissions`, `scope`, and optionally `email`, `name`.
3. **POST** to `{OPA_URL}/v1/data/authz/allow` with body `{"input": <input>}`.
4. If response `result !== true`, return HTTP 403 and optionally include `reason` from `authz/reason`.

Example (pseudo-code in the API):

```python
# After verify_token returns payload
input_doc = {
    "request": {"method": request.method, "path": request.url.path},
    "user": {
        "sub": payload.get("sub"),
        "permissions": payload.get("permissions", []),
        "scope": payload.get("scope", ""),
    }
}
allowed = requests.post(f"{OPA_URL}/v1/data/authz/allow", json={"input": input_doc}).json().get("result")
if not allowed:
    raise HTTPException(403, "Forbidden")
```

## Kubernetes (optional)

- Run OPA as a **sidecar** in the same pod as the API, or as a separate Deployment + Service.
- Point the API at OPA via `http://localhost:8181` (sidecar) or `http://opa-service:8181` (separate service).
- Load policies via volume mount or [bundles](https://www.openpolicyagent.org/docs/latest/management/#bundles).

## Next steps (to discuss)

- **API integration**: Add the OPA HTTP call in FastAPI (dependency or middleware) and wire `OPA_URL` in config.
- **More policies**: Resource-level rules (e.g. “user can only delete their own items”) using `sub` or custom claims.
- **RBAC**: Use `data/roles.json` and Rego to map roles → permissions, with Auth0 supplying a role claim.
- **Testing**: Rego unit tests (e.g. `opa test ./policies`) and integration tests that send example inputs to the API.

## References

- [OPA docs](https://www.openpolicyagent.org/docs/latest/)
- [Rego language](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [REST API authorization](https://www.openpolicyagent.org/docs/latest/rest-api/)
