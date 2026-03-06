#!/usr/bin/env bash
# Quick test of OPA authz policy with example inputs.
# Run OPA first: opa run --server ./policies   (from opa/ dir)

set -e
OPA_URL="${OPA_URL:-http://localhost:8181}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPA_DIR="$(dirname "$SCRIPT_DIR")"
INPUT_DIR="$OPA_DIR/input-examples"

echo "Using OPA at $OPA_URL"
echo ""

for name in allow deny; do
  f="$INPUT_DIR/${name}.json"
  if [[ ! -f "$f" ]]; then continue; fi
  result=$(curl -s -X POST "$OPA_URL/v1/data/authz/allow" -H "Content-Type: application/json" -d @"$f")
  echo "$name: $result"
done

echo ""
echo "Done. Expected: allow -> {\"result\":true}, deny -> {\"result\":false}"
