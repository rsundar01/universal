# Authentication Flow Guide

This document explains how users/clients authenticate and get access tokens to use the Universal Service API.

## Overview

The Universal Service API uses **Auth0** for authentication via **OAuth 2.0 Client Credentials Flow** (Machine-to-Machine). This is the recommended flow for server-to-server communication.

## Quick Start

### 1. Check Authentication Status

First, check if authentication is enabled and get instructions:

```bash
curl http://localhost:8000/api/auth/info
```

This endpoint returns:
- Whether auth is enabled
- Your Auth0 domain and API audience
- Step-by-step instructions on how to get a token
- Example curl commands

### 2. Get an Access Token

You need to request a token from Auth0 using your **Client ID** and **Client Secret**:

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

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### 3. Use the Token

Include the token in the `Authorization` header:

```bash
curl http://localhost:8000/api/items \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Authentication Flow Diagram

```
┌─────────────┐
│   Client    │
│ Application │
└──────┬──────┘
       │
       │ 1. Request Token
       │ POST /oauth/token
       │ {client_id, client_secret, audience, grant_type}
       ▼
┌─────────────┐
│   Auth0     │
│   Server    │
└──────┬──────┘
       │
       │ 2. Return Access Token
       │ {access_token, token_type, expires_in}
       ▼
┌─────────────┐
│   Client    │
│ Application │
└──────┬──────┘
       │
       │ 3. API Request
       │ GET /api/items
       │ Authorization: Bearer <token>
       ▼
┌─────────────┐
│  Universal  │
│   Service   │
│     API     │
└─────────────┘
       │
       │ 4. Verify Token
       │ - Fetch JWKS from Auth0
       │ - Validate signature
       │ - Check audience & issuer
       │ - Verify expiration
       ▼
┌─────────────┐
│   Response  │
│  (200 OK)   │
└─────────────┘
```

## Step-by-Step Process

### Step 1: Get Client Credentials from Auth0

1. Log in to [Auth0 Dashboard](https://manage.auth0.com)
2. Go to **Applications** → **Applications**
3. Find your **Machine to Machine Application**
4. Go to **Settings** tab
5. Copy:
   - **Client ID**
   - **Client Secret**
   - **Domain** (this is your `AUTH0_DOMAIN`)

### Step 2: Request Access Token

Use the Client Credentials flow to get a token:

**Using curl:**
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

**Using Python:**
```python
import requests

response = requests.post(
    "https://YOUR_AUTH0_DOMAIN/oauth/token",
    json={
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "audience": "https://universal-app/api",
        "grant_type": "client_credentials"
    }
)

token_data = response.json()
access_token = token_data["access_token"]
```

**Using JavaScript/Node.js:**
```javascript
const axios = require('axios');

const response = await axios.post(
  `https://YOUR_AUTH0_DOMAIN/oauth/token`,
  {
    client_id: 'YOUR_CLIENT_ID',
    client_secret: 'YOUR_CLIENT_SECRET',
    audience: 'https://universal-app/api',
    grant_type: 'client_credentials'
  },
  {
    headers: { 'Content-Type': 'application/json' }
  }
);

const accessToken = response.data.access_token;
```

### Step 3: Use the Token

Include the token in all API requests:

**Using curl:**
```bash
curl http://localhost:8000/api/items \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Using Python:**
```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    "http://localhost:8000/api/items",
    headers=headers
)

items = response.json()
```

**Using JavaScript:**
```javascript
const response = await axios.get(
  'http://localhost:8000/api/items',
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);
```

## Token Lifecycle

1. **Token Expiration**: Tokens typically expire after 24 hours (86400 seconds)
2. **Token Refresh**: When a token expires, request a new one using the same Client Credentials flow
3. **Token Storage**: Store tokens securely (environment variables, secrets manager, etc.)
4. **Token Caching**: Cache tokens until they expire to avoid unnecessary requests

## Example: Complete Workflow

```bash
# 1. Get token
TOKEN_RESPONSE=$(curl -s --request POST \
  --url https://YOUR_AUTH0_DOMAIN/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "audience": "https://universal-app/api",
    "grant_type": "client_credentials"
  }')

# 2. Extract token
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

# 3. Use token to access API
curl http://localhost:8000/api/items \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 4. Create an item
curl -X POST http://localhost:8000/api/items \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Item",
    "description": "Test item",
    "price": 99.99
  }'
```

## Error Handling

### 401 Unauthorized
- **Cause**: Missing or invalid token
- **Solution**: Request a new token or check token expiration

### 403 Forbidden
- **Cause**: Token doesn't have required permissions/scopes
- **Solution**: Ensure your Auth0 application has the required permissions granted

### Token Expired
- **Cause**: Token has passed its expiration time
- **Solution**: Request a new token

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** or secrets managers for Client ID/Secret
3. **Rotate credentials** regularly
4. **Use HTTPS** in production
5. **Store tokens securely** and don't log them
6. **Implement token caching** to reduce Auth0 API calls
7. **Monitor token usage** for suspicious activity

## Testing Without Authentication

If authentication is not configured (AUTH0_DOMAIN and API_AUDIENCE not set), the API will work without authentication. Check the status:

```bash
curl http://localhost:8000/api/auth/info
```

If `enabled: false`, authentication is disabled and all endpoints are accessible without tokens.

## Additional Resources

- [Auth0 Client Credentials Flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/client-credentials-flow)
- [Auth0 API Authentication](https://auth0.com/docs/secure/tokens/access-tokens)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)



