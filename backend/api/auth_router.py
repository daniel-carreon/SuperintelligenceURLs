"""
Authentication Router - Simple password-based auth
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel


router = APIRouter(prefix="/auth", tags=["auth"])

# Simple in-memory token storage (para MVP)
# En producción usarías Redis o una DB
valid_tokens = set()

# Token expiration time (24 hours)
TOKEN_EXPIRY = timedelta(hours=24)


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str
    message: str


def generate_token() -> str:
    """Generate a random secure token"""
    return secrets.token_urlsafe(32)


def is_valid_token(token: str) -> bool:
    """Check if token exists in valid tokens"""
    return token in valid_tokens


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint - validates password and returns token

    Password is stored in AUTH_PASSWORD environment variable
    """
    auth_password = os.getenv("AUTH_PASSWORD")

    if not auth_password:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error"
        )

    # Validate password
    if credentials.password != auth_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    # Generate token
    token = generate_token()
    valid_tokens.add(token)

    print(f"✅ User logged in successfully - Token: {token[:10]}...")

    return LoginResponse(
        token=token,
        message="Login successful"
    )


@router.post("/verify")
async def verify_token(authorization: str = Header(None)):
    """
    Verify if a token is valid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )

    token = authorization.replace("Bearer ", "")

    if not is_valid_token(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return {"valid": True, "message": "Token is valid"}


@router.post("/logout")
async def logout(authorization: str = Header(None)):
    """
    Logout - invalidate token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )

    token = authorization.replace("Bearer ", "")

    if token in valid_tokens:
        valid_tokens.remove(token)
        print(f"✅ User logged out - Token invalidated")

    return {"message": "Logged out successfully"}
