# Authorization policy for Universal Service API
# Integrates with Auth0: input.user contains JWT claims (sub, permissions, etc.)
# OPA decides allow/deny based on method, path, and user permissions.

package authz

import future.keywords.if
import future.keywords.in

default allow := false

# Allow health endpoints without auth (no user in input)
allow if {
	path_is_health(input.request.path)
}

# Allow authenticated requests when user has required permission for the action
allow if {
	input.user != null
	required_permission := method_to_permission[input.request.method][input.request.path]
	required_permission != null
	user_has_permission(input.user, required_permission)
}

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

path_is_health(path) if {
	path == "/"
}
path_is_health(path) if {
	path == "/health"
}
path_is_health(path) if {
	path == "/docs"
}
path_is_health(path) if {
	path == "/redoc"
}
path_is_health(path) if {
	path == "/openapi.json"
}
path_is_health(path) if {
	path == "/api/auth/info"
}

# ---------------------------------------------------------------------------
# Method + path -> required Auth0 permission (matches AUTH0_SETUP.md scopes)
# ---------------------------------------------------------------------------

method_to_permission[method][path] := permission if {
	path == "/api/items"
	method == "GET"
	permission := "read:items"
}
method_to_permission[method][path] := permission if {
	path == "/api/items"
	method == "POST"
	permission := "create:items"
}
method_to_permission[method][path] := permission if {
	path_matches("/api/items/*", path)
	method == "GET"
	permission := "read:items"
}
method_to_permission[method][path] := permission if {
	path_matches("/api/items/*", path)
	method == "PUT"
	permission := "update:items"
}
method_to_permission[method][path] := permission if {
	path_matches("/api/items/*", path)
	method == "DELETE"
	permission := "delete:items"
}
method_to_permission[method][path] := permission if {
	path == "/api/me"
	method == "GET"
	permission := "read:items"
}

# Match path patterns like /api/items/123 (by-ID resource)
path_matches(_pattern, path) if {
	# /api/items/1, /api/items/42 etc. (not /api/items which is list)
	startswith(path, "/api/items/")
	count(split(path, "/")) >= 4
}

# ---------------------------------------------------------------------------
# User has permission: check Auth0 "permissions" array or "scope" string
# ---------------------------------------------------------------------------

user_has_permission(user, permission) if {
	permission in user.permissions
}
user_has_permission(user, permission) if {
	scopes := split(user.scope, " ")
	permission in scopes
}

# ---------------------------------------------------------------------------
# Optional: reason for denial (for debugging / audit)
# ---------------------------------------------------------------------------

reason := "allowed" if {
	allow
}
reason := "unauthenticated" if {
	not allow
	input.user == null
	not path_is_health(input.request.path)
}
reason := "insufficient permissions" if {
	not allow
	input.user != null
}
