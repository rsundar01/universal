#!/bin/sh
# Generate random users and insert into dev SQLite user DB.
# Password format: hash = base64(sha256(salt || plain_password)); salt stored in base64.
# Usage: ./generate-random-users.sh [count] [db_path]
# Example: ./generate-random-users.sh 5
# Requires: sqlite3, openssl, sh (POSIX)

set -e

COUNT="${1:-3}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEV_DIR="$(dirname "$SCRIPT_DIR")"
DB_PATH="${2:-$DEV_DIR/data/userdb.sqlite}"
USERID_START=1000000001

if [ ! -f "$DB_PATH" ]; then
  echo "Database not found at $DB_PATH. Run init-db.sh first."
  exit 1
fi

# Generate base64 salt (16 bytes)
gen_salt() {
  openssl rand -base64 16 | tr -d '\n'
}

# Hash: SHA256(salt_plain || password), then base64. Salt stored in base64; decode then concat.
# Portable: use openssl for base64 decode (-A = no newlines).
hash_password() {
  local salt_b64="$1"
  local password="$2"
  local salt_raw
  salt_raw=$(echo "$salt_b64" | openssl base64 -d -A 2>/dev/null)
  printf '%s%s' "$salt_raw" "$password" | openssl dgst -sha256 -binary | openssl base64 -A
}

# Random email (local part + @example.com)
random_email() {
  local n
  n=$(openssl rand -hex 4)
  echo "user${n}@example.com"
}

# Random tenant (e.g. tenant_1, tenant_2)
random_tenant() {
  local hex n
  hex=$(openssl rand -hex 2)
  n=$((0x${hex} % 10 + 1))
  echo "tenant_${n}"
}

i=0
while [ "$i" -lt "$COUNT" ]; do
  user_email=$(random_email)
  tenant_id=$(random_tenant)
  password="TestPass${i}_$(openssl rand -hex 2)"
  salt=$(gen_salt)
  password_hash=$(hash_password "$salt" "$password")

  # Next userid: max(userid) + 1, or USERID_START if empty
  next_id=$(sqlite3 "$DB_PATH" "SELECT COALESCE(MAX(userid), $((USERID_START - 1))) + 1 FROM users;")
  last_login_ts=""   # NULL for new users; set via app when they log in

  # Escape single quotes for SQLite (double them)
  eq() { echo "$1" | sed "s/'/''/g"; }
  e_email=$(eq "$user_email")
  e_tenant=$(eq "$tenant_id")
  e_hash=$(eq "$password_hash")
  e_salt=$(eq "$salt")

  sqlite3 "$DB_PATH" "INSERT INTO users (userid, user_email, tenant_id, password_hash, salt) VALUES ($next_id, '$e_email', '$e_tenant', '$e_hash', '$e_salt');"

  echo "Created userid=$next_id email=$user_email tenant=$tenant_id password=$password"
  i=$((i + 1))
done

echo "Inserted $COUNT user(s) into $DB_PATH"
