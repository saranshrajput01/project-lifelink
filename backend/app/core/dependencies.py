"""
FastAPI dependencies — reusable injections for authentication, database, etc.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token

# Bearer token scheme — expects "Authorization: Bearer <token>" header
security_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """
    Extract and validate the current user from the JWT token.
    Returns the user ID (subject) from the token.

    Raises 401 if token is missing, expired, or invalid.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
        )

    return user_id


def require_role(*allowed_roles: str):
    """
    Dependency factory — restricts endpoint to specific roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint(): ...

        @router.get("/staff", dependencies=[Depends(require_role("admin", "doctor"))])
        async def staff_endpoint(): ...
    """

    async def role_checker(
        user_id: str = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
    ):
        from app.models.user import User

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )

        return user

    return role_checker
