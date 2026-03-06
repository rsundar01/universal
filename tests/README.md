# API Tests

Test scripts for the Universal Service API.

## Prerequisites

1. **Port-forward must be running:**
   ```bash
   kubectl port-forward service/universal-service 8000:80
   ```

2. **For Python tests**, install requests:
   ```bash
   pip install requests
   ```

## Running Tests

### Bash Script (test_api.sh)

Simple bash script with curl commands:

```bash
# Make sure port-forward is running first
kubectl port-forward service/universal-service 8000:80

# In another terminal, run tests
./tests/test_api.sh
```

### Python Script (test_api.py)

Python script using requests library:

```bash
# Install requests if needed
pip install requests

# Run tests
python tests/test_api.py
```

## What Tests Cover

1. ✅ Health check endpoint
2. ✅ Root endpoint
3. ✅ Create item (POST)
4. ✅ List all items (GET)
5. ✅ Get item by ID (GET)
6. ✅ Update item (PUT)
7. ✅ Delete item (DELETE)
8. ✅ Multiple items management

## Manual Testing

You can also test manually using:

- **Interactive API docs**: http://localhost:8000/docs
- **cURL commands**: See examples in `test_api.sh`
- **Python requests**: See examples in `test_api.py`

## Troubleshooting

**Connection Error:**
- Make sure `kubectl port-forward` is running
- Check that pods are running: `kubectl get pods -l app=universal`

**404 Errors:**
- Verify service is accessible: `curl http://localhost:8000/health`

**Import Error (Python):**
- Install requests: `pip install requests`

