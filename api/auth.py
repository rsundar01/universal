"""
Auth0 OIDC Authentication and OAuth 2.0 Authorization
"""
import httpx
from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.utils import base64url_decode
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from functools import lru_cache

from config import settings

ALGORITHMS = ["RS256"]

# Security scheme for Authorization: Bearer <token>
security = HTTPBearer()


def validate_auth0_config():
    """Validate that Auth0 configuration is present"""
    if not settings.auth0_domain:
        raise ValueError("AUTH0_DOMAIN environment variable is required")
    if not settings.api_audience:
        raise ValueError("API_AUDIENCE environment variable is required")


# JWKS returned from Auth0
@lru_cache()
def get_jwks():
    """Fetch and cache JWKS from Auth0"""
    validate_auth0_config()
    jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
    resp = httpx.get(jwks_url, timeout=10.0)
    resp.raise_for_status()
    return resp.json()


def rsa_public_key_from_jwk(jwk: dict):
    """Convert JWK to RSA public key object"""
    n = base64url_decode(jwk["n"].encode("utf-8"))
    e = base64url_decode(jwk["e"].encode("utf-8"))
    
    pub_key = rsa.RSAPublicNumbers(
        int.from_bytes(e, byteorder="big"),
        int.from_bytes(n, byteorder="big")
    ).public_key(default_backend())
    
    return pub_key


def get_signing_key(token: str):
    """Get the signing key for a token based on its kid"""
    try:
        # Extract kid from token header
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(status_code=401, detail="Token missing kid in header")
        
        jwks = get_jwks()
        
        # Find the key with matching kid
        for key in jwks["keys"]:
            if key["kid"] == kid:
                # Convert JWK to RSA public key
                return rsa_public_key_from_jwk(key)
        
        raise HTTPException(status_code=401, detail="Invalid token: unknown kid")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error processing token: {str(e)}")


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify JWT token from Auth0
    Returns the decoded payload if valid
    """
    validate_auth0_config()
    token = credentials.credentials
    public_key = get_signing_key(token)
    
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=ALGORITHMS,  # ["RS256"]
            audience=settings.api_audience,
            issuer=f"https://{settings.auth0_domain}/"
        )
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token claims: {str(e)}")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification error: {str(e)}")


def require_scope(required_scope: str):
    """
    Decorator factory for requiring specific OAuth scopes
    Usage: @app.get("/protected", dependencies=[Depends(require_scope("read:items"))])
    """
    def scope_checker(payload: dict = Depends(verify_token)):
        scopes = payload.get("scope", "").split()
        permissions = payload.get("permissions", [])
        
        # Check both scopes and permissions (Auth0 uses permissions)
        if required_scope in scopes or required_scope in permissions:
            return payload
        
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required scope: {required_scope}"
        )
    
    return scope_checker


def get_current_user(payload: dict = Depends(verify_token)):
    """
    Get current authenticated user info from token payload
    Returns user info dictionary
    """
    return {
        "sub": payload.get("sub"),  # Auth0 user ID
        "email": payload.get("email"),
        "name": payload.get("name"),
        "nickname": payload.get("nickname"),
        "permissions": payload.get("permissions", []),
        "scope": payload.get("scope", "")
    }
