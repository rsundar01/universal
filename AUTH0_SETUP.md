# Auth0 Setup Guide

This guide explains how to configure Auth0 OIDC authentication and OAuth 2.0 authorization for the Universal Service API.

## Prerequisites

- Auth0 account (Free tier works)
- Auth0 domain (e.g., `dev-xxx.us.auth0.com`)
- API Audience/Identifier configured

## Step 1: Create an API in Auth0

1. **Log in to Auth0 Dashboard**: https://manage.auth0.com

2. **Create a new API**:
   - Go to **Applications** → **APIs**
   - Click **+ Create API**

3. **Configure the API**:
   - **Name**: Universal Service API (or any name)
   - **Identifier**: `https://universal-app/api` (or your preferred identifier)
     - ⚠️ This will be your `API_AUDIENCE` value
     - Note: This should match exactly what you'll use in environment variables
   - **Signing Algorithm**: RS256 (default)

4. **Save the API**

5. **Configure Permissions (Scopes)**:
   - In your API settings, go to **Settings** tab
   - Scroll to **Scopes** section
   - Add custom scopes:
     - `read:items` - Read items permission
     - `create:items` - Create items permission
     - `update:items` - Update items permission
     - `delete:items` - Delete items permission
   - Click **Save**

## Step 2: Create an Application in Auth0

1. **Create a Machine to Machine Application**:
   - Go to **Applications** → **Applications**
   - Click **+ Create Application**
   - Name: `Universal Service API Client`
   - Type: **Machine to Machine Applications**
   - Click **Create**

2. **Authorize the Application**:
   - Select your API (created in Step 1)
   - Toggle **Authorize**
   - Select the permissions you want to grant:
     - `read:items`
     - `create:items`
     - `update:items`
     - `delete:items`
   - Click **Authorize**

3. **Get Client Credentials**:
   - Go to **Settings** tab
   - Copy:
     - **Domain**: This is your `AUTH0_DOMAIN` (e.g., `dev-xxx.us.auth0.com`)
     - **Client ID**: Not needed for API validation, but useful for testing
     - **Client Secret**: Not needed for API validation, but useful for testing

## Step 3: Configure Environment Variables

### Local Development

Create a `.env` file in the `api/` directory (or export in your shell):

```bash
export AUTH0_DOMAIN="dev-xxx.us.auth0.com"
export API_AUDIENCE="https://universal-app/api"
```

Or in a `.env` file:
```
AUTH0_DOMAIN=dev-xxx.us.auth0.com
API_AUDIENCE=https://universal-app/api
```

### Kubernetes Deployment

Edit `k8s/deployment.yaml` and set the values:

```yaml
env:
  - name: AUTH0_DOMAIN
    value: "dev-xxx.us.auth0.com"  # Your Auth0 domain
  - name: API_AUDIENCE
    value: "https://universal-app/api"  # Your API identifier
```

**⚠️ Security Note**: For production, use Kubernetes Secrets instead of plain environment variables:

```bash
# Create a secret
kubectl create secret generic auth0-secrets \
  --from-literal=AUTH0_DOMAIN="dev-xxx.us.auth0.com" \
  --from-literal=API_AUDIENCE="https://universal-app/api"

# Update deployment.yaml to use:
env:
  - name: AUTH0_DOMAIN
    valueFrom:
      secretKeyRef:
        name: auth0-secrets
        key: AUTH0_DOMAIN
  - name: API_AUDIENCE
    valueFrom:
      secretKeyRef:
        name: auth0-secrets
        key: API_AUDIENCE
```

## Step 4: Test Authentication

### Get an Access Token

Using Auth0 Management API or curl:

```bash
curl --request POST \
  --url https://YOUR_AUTH0_DOMAIN/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "audience": "https://universal-app/api",
    "grant_type": "client_credentials"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### Test Protected Endpoint

```bash
# Without token (should fail)
curl http://localhost:8000/api/items

# With token (should succeed)
curl http://localhost:8000/api/items \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test User Info Endpoint

```bash
curl http://localhost:8000/api/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Step 5: Using Permissions (Scopes)

To require specific permissions, uncomment the scope checks in `app.py`:

```python
@app.post("/api/items", dependencies=[Depends(require_scope("create:items"))])
async def create_item(...):
    ...
```

## Troubleshooting

### Error: "AUTH0_DOMAIN environment variable is required"
- Make sure environment variables are set
- Check deployment: `kubectl describe pod <pod-name>`

### Error: "Token verification failed"
- Verify `API_AUDIENCE` matches the API identifier in Auth0
- Check token is not expired
- Verify token was issued by correct Auth0 domain

### Error: "Invalid token: unknown kid"
- Auth0 JWKS might have changed - restart the app to refresh cache
- Check network connectivity to Auth0

### Error: "Insufficient permissions"
- Make sure your token has the required scopes/permissions
- Check API permissions are granted to your application

## Security Best Practices

1. **Use Kubernetes Secrets** for production
2. **Never commit** Auth0 credentials to git
3. **Use HTTPS** in production
4. **Set token expiration** appropriately
5. **Use least privilege** - only grant necessary permissions
6. **Monitor Auth0 logs** for suspicious activity

## Additional Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io) - Debug JWT tokens

