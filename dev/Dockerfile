# Dev SQLite user DB - minimal image with sqlite3 for running schema and scripts
FROM alpine:3.19

RUN apk add --no-cache sqlite

WORKDIR /data

COPY schema.sql /schema/schema.sql

# Default: keep container alive so volume-mounted DB is available
# Init DB: docker run --rm -v $(pwd)/data:/data dev-userdb sh -c "sqlite3 /data/userdb.sqlite < /schema/schema.sql"
CMD ["tail", "-f", "/dev/null"]
