"""
Auth schemas — request/response models for authentication endpoints.
Pydantic handles validation automatically.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role: str = Field(default="patient", pattern="^(patient|doctor|admin)$")


class LoginRequest(BaseModel):
    """Request body for login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response with JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Request body for token refresh."""

    refresh_token: str


class UserResponse(BaseModel):
    """Response with current user info."""

    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}
