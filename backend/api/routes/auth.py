"""
Authentication Router.

Provides endpoints for user authentication:
- POST /login: Authenticate user and return JWT tokens
- POST /register: Register new user (admin only in production)
- POST /refresh: Refresh access token
- GET /me: Get current user info
- POST /logout: Logout (client-side token invalidation)
"""

from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models_db import User, UserRole
from backend.core.config import settings
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
)
from backend.api.deps import CurrentUser, DbSession


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)


# ========================================
# Request/Response Schemas
# ========================================

class TokenResponse(BaseModel):
    """JWT token response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""
    refresh_token: str = Field(..., description="Refresh token")


class UserCreate(BaseModel):
    """User creation schema."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# ========================================
# Authentication Endpoints
# ========================================

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    
    Uses OAuth2 password flow for authentication.
    Returns access token (short-lived) and refresh token (long-lived).
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: DbSession,
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Returns a new access token if the refresh token is valid.
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Verify user still exists and is active
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DbSession,
) -> User:
    """
    Register a new user.
    
    In production, this endpoint should be protected or disabled.
    Consider adding email verification for production use.
    """
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        is_admin=user_data.role == UserRole.ADMIN,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> User:
    """
    Get current authenticated user's information.
    
    Requires valid JWT access token.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> User:
    """
    Update current user's information.
    
    Allows users to update their own email, full name, and password.
    """
    # Update fields if provided
    if update_data.email is not None:
        # Check if email is taken by another user
        result = await db.execute(
            select(User).where(
                User.email == update_data.email,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        current_user.email = update_data.email
    
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    
    if update_data.password is not None:
        current_user.hashed_password = get_password_hash(update_data.password)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/logout")
async def logout(current_user: CurrentUser) -> dict:
    """
    Logout endpoint.
    
    Note: JWT tokens are stateless, so this endpoint mainly serves
    as a signal for the client to discard the token.
    For production, consider implementing a token blacklist with Redis.
    """
    return {
        "message": "Successfully logged out",
        "detail": "Token should be discarded by the client"
    }
