"""
API Dependencies Module.

Provides reusable dependencies for FastAPI endpoints including:
- Authentication (get_current_user)
- Database sessions
- Pagination
- Rate limiting
"""

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from backend.database import get_db
from backend.core.config import settings
from backend.core.security import verify_token
from backend.models_db import User


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False  # Don't auto-error, we'll handle it
)


async def get_current_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
    
    # Verify and decode the token
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise credentials_exception
    
    # Extract user identifier from token
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Fetch user from database
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current user and verify they are active.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current user and verify they have admin privileges.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Admin User object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_optional_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Optional[User]:
    """
    Optionally get the current user if authenticated.
    
    Does not raise an exception if no valid token is provided.
    Useful for endpoints that have different behavior for 
    authenticated vs unauthenticated users.
    
    Args:
        token: Optional JWT access token
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if token is None:
        return None
    
    payload = verify_token(token, token_type="access")
    if payload is None:
        return None
    
    username: Optional[str] = payload.get("sub")
    if username is None:
        return None
    
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        return None
    
    return user


async def get_current_user_or_dev_bypass(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Optional[User]:
    """
    Get current user OR bypass auth in development mode.
    
    In development mode (settings.is_development = True):
    - If no token provided, returns None (allows unauthenticated access)
    - If token provided, validates and returns user
    
    In production mode:
    - Always requires valid token, raises 401 if missing/invalid
    
    This allows frontend development without requiring login,
    while enforcing auth in production.
    """
    # Development mode bypass
    if settings.is_development and token is None:
        return None  # Allow unauthenticated access in dev
    
    # Production mode: require auth
    if not settings.is_development and token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If token provided, validate it
    if token is not None:
        payload = verify_token(token, token_type="access")
        if payload is None:
            if settings.is_development:
                return None  # Invalid token in dev = treat as no auth
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username: Optional[str] = payload.get("sub")
        if username:
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            if user and user.is_active:
                return user
    
    # In development, return None for unauthenticated access
    if settings.is_development:
        return None
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
OptionalUser = Annotated[Optional[User], Depends(get_optional_user)]
DevUser = Annotated[Optional[User], Depends(get_current_user_or_dev_bypass)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
