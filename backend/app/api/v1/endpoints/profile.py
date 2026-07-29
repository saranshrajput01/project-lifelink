"""
User Profile endpoints — manage patient health profile.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.profile import UserProfile
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's health profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == UUID(user_id))
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first.",
        )

    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    request: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create or update the current user's health profile (upsert)."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == UUID(user_id))
    )
    profile = result.scalar_one_or_none()

    if profile:
        # Update existing profile
        for field, value in request.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
    else:
        # Create new profile
        profile = UserProfile(
            user_id=UUID(user_id),
            **request.model_dump(exclude_unset=True),
        )
        db.add(profile)

    await db.flush()
    await db.refresh(profile)
    return profile
