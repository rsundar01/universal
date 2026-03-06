#!/bin/sh
# Initialize SQLite user DB (run from host or inside container).
# Usage: ./init-db.sh [path-to-db]
# Default DB path: ./data/userdb.sqlite (relative to dev/)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEV_DIR="$(dirname "$SCRIPT_DIR")"
DB_PATH="${1:-$DEV_DIR/data/userdb.sqlite}"

mkdir -p "$(dirname "$DB_PATH")"
sqlite3 "$DB_PATH" < "$DEV_DIR/schema.sql"
echo "Initialized database at $DB_PATH"
