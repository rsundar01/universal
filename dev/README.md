# Dev User Database (SQLite)

Test user database for local/dev use. SQLite with schema and scripts to create and seed users.

## Data model

| Column            | Type    | Description |
|-------------------|---------|-------------|
| `userid`          | INTEGER | Unique numeric ID, system-generated, ≥ 1000000001 |
| `user_email`      | TEXT    | Login identifier; unique |
| `tenant_id`       | TEXT    | Tenant for multi-tenancy |
| `password_hash`   | TEXT    | Base64-encoded hash: `base64(sha256(salt \|\| password))` |
| `salt`            | TEXT    | Random salt, base64-encoded |
| `last_login_ts`   | TEXT    | ISO8601 or Unix timestamp; NULL if never logged in |
| `created_at`      | TEXT    | Row creation time (ISO8601) |
| `updated_at`      | TEXT    | Last update time (ISO8601) |

**Password format:** Store a hash, not the raw password. Use `password_hash = base64(sha256(salt_plain || password))` with a random salt; store the salt in base64 in `salt`. Verify by recomputing the same hash from stored salt and supplied password.

## Setup

### 1. Create schema (local)

```bash
mkdir -p data
./scripts/init-db.sh
# Or with explicit path:
./scripts/init-db.sh ./data/userdb.sqlite
```

### 2. Run in Docker

```bash
# Build and start container (persistent volume at ./data)
docker compose up -d

# Initialize DB inside container (schema is in image)
docker compose exec userdb sh -c "sqlite3 /data/userdb.sqlite < /schema/schema.sql"

# Or bind-mount schema and run from host:
docker compose run --rm -v "$(pwd)/schema.sql:/schema.sql" -v "$(pwd)/data:/data" userdb sh -c "sqlite3 /data/userdb.sqlite < /schema.sql"
```

### 3. Generate random users

From repo root or `dev/`:

```bash
chmod +x dev/scripts/generate-random-users.sh dev/scripts/init-db.sh
./dev/scripts/init-db.sh          # if not done yet
./dev/scripts/generate-random-users.sh 5
```

Options:

- `./scripts/generate-random-users.sh [count] [db_path]`
- Default count: 3. Default DB: `./data/userdb.sqlite`.

The script prints each generated password once (for test logins); it is not stored in the DB.

### 4. Query (local or in Docker)

```bash
# Local
sqlite3 data/userdb.sqlite "SELECT userid, user_email, tenant_id, last_login_ts FROM users;"

# Docker
docker compose exec userdb sqlite3 /data/userdb.sqlite "SELECT userid, user_email, tenant_id FROM users;"
```

## Files

- `schema.sql` – Table and indexes.
- `scripts/init-db.sh` – Create DB and apply schema.
- `scripts/generate-random-users.sh` – Insert random users (userid, email, tenant, password hash + salt).
- `Dockerfile` – Alpine + sqlite3 for running schema/scripts.
- `docker-compose.yml` – Service with `./data` mounted at `/data`.

## Requirements

- **Local:** `sqlite3`, `openssl` (for script).
- **Docker:** Docker and Docker Compose.
