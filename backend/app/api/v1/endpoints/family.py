"""
Family member endpoints — manage health profiles for a patient's family.
No external provider needed; profiles are stored in the DB and surfaced in-app.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.family_member import FamilyMember
from app.schemas.family_member import (
    FamilyMemberCreate,
    FamilyMemberListResponse,
    FamilyMemberResponse,
    FamilyMemberUpdate,
)

router = APIRouter(prefix="/family", tags=["Family"])


@router.post("/", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    payload: FamilyMemberCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Add a family member health profile."""
    member = FamilyMember(owner_id=UUID(user_id), **payload.model_dump())
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


@router.get("/", response_model=FamilyMemberListResponse)
async def list_members(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's family member profiles."""
    result = await db.execute(
        select(FamilyMember)
        .where(FamilyMember.owner_id == UUID(user_id))
        .order_by(FamilyMember.created_at.asc())
    )
    members = result.scalars().all()
    return FamilyMemberListResponse(
        members=[FamilyMemberResponse.model_validate(m) for m in members],
        total=len(members),
    )


async def _get_owned(member_id: UUID, user_id: str, db: AsyncSession) -> FamilyMember:
    result = await db.execute(
        select(FamilyMember).where(
            FamilyMember.id == member_id,
            FamilyMember.owner_id == UUID(user_id),
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found."
        )
    return member


@router.patch("/{member_id}", response_model=FamilyMemberResponse)
async def update_member(
    member_id: UUID,
    payload: FamilyMemberUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a family member profile."""
    member = await _get_owned(member_id, user_id, db)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(member, field, value)
    await db.flush()
    await db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a family member profile."""
    member = await _get_owned(member_id, user_id, db)
    await db.delete(member)
