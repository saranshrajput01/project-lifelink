"""
Admin endpoints — manage users, view all documents, platform stats.
Restricted to admin role only.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.document import MedicalDocument
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", dependencies=[Depends(require_role("admin"))])
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    """Get platform-wide statistics."""
    total_users = (
        await db.execute(select(func.count()).select_from(User))
    ).scalar() or 0
    total_docs = (
        await db.execute(select(func.count()).select_from(MedicalDocument))
    ).scalar() or 0
    processed_docs = (
        await db.execute(
            select(func.count())
            .select_from(MedicalDocument)
            .where(MedicalDocument.processing_status == "completed")
        )
    ).scalar() or 0
    pending_docs = (
        await db.execute(
            select(func.count())
            .select_from(MedicalDocument)
            .where(MedicalDocument.processing_status == "pending")
        )
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_documents": total_docs,
        "processed_documents": processed_docs,
        "pending_documents": pending_docs,
    }


@router.get("/users", dependencies=[Depends(require_role("admin"))])
async def list_all_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only)."""
    count_query = select(func.count()).select_from(User)
    total = (await db.execute(count_query)).scalar() or 0

    query = select(User).order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/documents", dependencies=[Depends(require_role("admin"))])
async def list_all_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all documents across all users (admin only)."""
    count_query = select(func.count()).select_from(MedicalDocument)
    total = (await db.execute(count_query)).scalar() or 0

    query = select(MedicalDocument).order_by(MedicalDocument.uploaded_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    docs = result.scalars().all()

    return {
        "documents": [
            {
                "id": str(d.id),
                "patient_id": str(d.patient_id),
                "original_filename": d.original_filename,
                "doc_type": d.doc_type,
                "file_size_bytes": d.file_size_bytes,
                "processing_status": d.processing_status,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            }
            for d in docs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
