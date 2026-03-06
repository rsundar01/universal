"""
Universal Service for Kubernetes Interview Assessment
Built with FastAPI
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os
import uvicorn

# Import configuration
from config import settings

# Import Auth0 authentication (only if configured)
if settings.auth_enabled:
    from auth import verify_token, require_scope, get_current_user
else:
    verify_token = None
    require_scope = None
    get_current_user = None

# Initialize FastAPI app
app = FastAPI(
    title="Universal Service",
    description="A REST API service deployed on Kubernetes",
    version="1.0.0"
)

# CORS Configuration
# Environment-aware: permissive for development, restrictive for production
if settings.environment.lower() == "production":
    # Production: Only allow specific origins
    allowed_origins = [
        "http://localhost:8000",  # Same origin
        # Add your production frontend URL(s) here
        # "https://yourdomain.com",
    ]
    allowed_methods = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers = ["Content-Type", "Accept", "Authorization"]
else:
    # Development: More permissive for local testing
    allowed_origins = [
        "http://localhost:8000",
        "http://localhost:3000",  # Common React/Vue dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
    ]
    allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers = ["Content-Type", "Accept", "Authorization"]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

# Data models
class Item(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Item name", min_length=1)
    description: Optional[str] = None
    price: float = Field(..., ge=0, description="Item price (must be >= 0)")
    created_at: Optional[datetime] = None

class ItemCreate(BaseModel):
    name: str = Field(..., description="Item name", min_length=1)
    description: Optional[str] = None
    price: float = Field(..., ge=0, description="Item price (must be >= 0)")

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)

# In-memory storage (for demonstration - use database in production)
# Using dict for O(1) lookups by ID
items_db: Dict[int, Item] = {}
next_id = 1

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Universal Service is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "universal-service"
    }

@app.get("/api/items", response_model=List[Item], tags=["Items"])
async def get_items(user: dict = Depends(verify_token) if settings.auth_enabled else None):
    """Get all items - Requires authentication if enabled"""
    if settings.auth_enabled and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return list(items_db.values())

@app.get("/api/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int, user: dict = Depends(verify_token) if settings.auth_enabled else None):
    """Get item by ID - Requires authentication if enabled"""
    if settings.auth_enabled and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    item = items_db.get(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return item

@app.post("/api/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(
    item: ItemCreate,
    user: dict = Depends(verify_token) if settings.auth_enabled else None,
    # Uncomment to require specific permission:
    # _: dict = Depends(require_scope("create:items")) if settings.auth_enabled else None
):
    """Create a new item - Requires authentication if enabled"""
    if settings.auth_enabled and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    global next_id
    new_item = Item(
        id=next_id,
        name=item.name,
        description=item.description,
        price=item.price,
        created_at=datetime.now()
    )
    items_db[next_id] = new_item
    next_id += 1
    return new_item

@app.put("/api/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    user: dict = Depends(verify_token) if settings.auth_enabled else None,
    # Uncomment to require specific permission:
    # _: dict = Depends(require_scope("update:items")) if settings.auth_enabled else None
):
    """Update an existing item - Requires authentication if enabled"""
    if settings.auth_enabled and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    item = items_db.get(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Update fields if provided
    if item_update.name is not None:
        item.name = item_update.name
    if item_update.description is not None:
        item.description = item_update.description
    if item_update.price is not None:
        item.price = item_update.price
    
    return item

@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(
    item_id: int,
    user: dict = Depends(verify_token) if settings.auth_enabled else None,
    # Uncomment to require specific permission:
    # _: dict = Depends(require_scope("delete:items")) if settings.auth_enabled else None
):
    """Delete an item - Requires authentication if enabled"""
    if settings.auth_enabled and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    item = items_db.pop(item_id, None)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return None

# Authentication info endpoint
@app.get("/api/auth/info", tags=["Auth"])
async def get_auth_info():
    """Get authentication configuration and instructions"""
    if not settings.auth_enabled:
        return {
            "enabled": False,
            "message": "Authentication is not configured. Set AUTH0_DOMAIN and API_AUDIENCE to enable.",
            "instructions": "See AUTH0_SETUP.md for configuration instructions."
        }
    
    return {
        "enabled": True,
        "auth0_domain": settings.auth0_domain,
        "api_audience": settings.api_audience,
        "token_endpoint": f"https://{settings.auth0_domain}/oauth/token",
        "instructions": {
            "how_to_get_token": "Use Auth0's OAuth 2.0 Client Credentials flow to get an access token",
            "machine_to_machine": {
                "description": "For server-to-server communication (recommended for API access)",
                "endpoint": f"https://{settings.auth0_domain}/oauth/token",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "client_id": "YOUR_CLIENT_ID",
                    "client_secret": "YOUR_CLIENT_SECRET",
                    "audience": settings.api_audience,
                    "grant_type": "client_credentials"
                },
                "example_curl": f"""curl --request POST \\
  --url https://{settings.auth0_domain}/oauth/token \\
  --header 'content-type: application/json' \\
  --data '{{"client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_CLIENT_SECRET","audience":"{settings.api_audience}","grant_type":"client_credentials"}}'"""
            },
            "using_token": {
                "description": "Include the access token in the Authorization header",
                "header": "Authorization: Bearer <your_access_token>",
                "example_curl": "curl -H 'Authorization: Bearer <token>' http://localhost:8000/api/items"
            },
            "more_info": "See AUTH0_SETUP.md for detailed setup instructions"
        }
    }

# User info endpoint (requires authentication)
@app.get("/api/me", tags=["Auth"])
async def get_current_user_info(user: dict = Depends(get_current_user) if settings.auth_enabled else None):
    """Get current authenticated user information"""
    if settings.auth_enabled:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        return user
    return {"message": "Authentication not configured"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

