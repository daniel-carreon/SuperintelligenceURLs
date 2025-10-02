"""
Authentication Middleware
Protects endpoints except public ones (login, redirects)
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from api.auth_router import is_valid_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that checks for valid authentication token
    Excepts:
    - /auth/* endpoints (login, etc)
    - /{short_code} redirects (public URLs)
    - / health check
    - /docs, /redoc (API documentation)
    """

    async def dispatch(self, request: Request, call_next):
        # Allow all OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # List of public paths that don't require authentication
        public_paths = [
            "/",  # Health check
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

        # Check if path is public
        if request.url.path in public_paths:
            return await call_next(request)

        # Allow /auth/* endpoints (login, verify, logout)
        if request.url.path.startswith("/auth"):
            return await call_next(request)

        # Allow redirect endpoints /{short_code} (GET only)
        # Pattern: single path segment, no slashes
        path_segments = [p for p in request.url.path.split("/") if p]
        if len(path_segments) == 1 and request.method == "GET":
            # This is a redirect path like /abc123
            return await call_next(request)

        # All other endpoints require authentication
        authorization = request.headers.get("authorization")

        if not authorization or not authorization.startswith("Bearer "):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )

        token = authorization.replace("Bearer ", "")

        if not is_valid_token(token):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )

        # Token is valid, proceed
        return await call_next(request)
