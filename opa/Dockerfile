# OPA policy engine - used as sidecar or standalone for authorization
FROM openpolicyagent/opa:0.69.0-rootless

# Copy policies and optional data
COPY policies/ /policies/
COPY data/ /data/
COPY config.yaml /config.yaml

# Run as API server; policies loaded from directory
# API will expose POST /v1/data/authz/allow and /v1/data/authz/reason
ENTRYPOINT ["opa"]
CMD ["run", "--server", "--config-file", "/config.yaml", "/policies"]
