"""
Document endpoints — upload, list, get, delete medical documents.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.document import MedicalDocument
from app.schemas.document import DocumentListResponse, DocumentResponse, UploadResponse
from app.services.storage import ensure_bucket_exists, generate_s3_key, upload_file_to_s3

router = APIRouter(prefix="/documents", tags=["Documents"])

# Allowed file types
ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff",
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Query(default="other", regex="^(prescription|lab_report|discharge_summary|doctor_notes|vaccination|insurance|other)$"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a medical document (PDF, image).
    AI will process it in the background (OCR → Extract → Summarize).
    """
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' not allowed. Use: PDF, JPEG, PNG, WebP, TIFF",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum 50MB allowed.",
        )

    # Upload to S3/MinIO
    ensure_bucket_exists()
    s3_key = generate_s3_key(user_id, file.filename or "document")
    success = await upload_file_to_s3(content, s3_key, file.content_type or "application/octet-stream")

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage.",
        )

    # Save document record in database
    document = MedicalDocument(
        patient_id=UUID(user_id),
        doc_type=doc_type,
        original_filename=file.filename or "unknown",
        file_size_bytes=len(content),
        mime_type=file.content_type or "application/octet-stream",
        s3_key=s3_key,
        ocr_status="pending",
        processing_status="pending",
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    # TODO: Phase 2 — Trigger background Celery task for OCR + AI processing

    return UploadResponse(
        id=document.id,
        filename=document.original_filename,
        doc_type=document.doc_type,
        status="uploaded",
        message="Document uploaded successfully. AI processing will begin shortly.",
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    doc_type: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all documents for the current user (paginated)."""
    query = select(MedicalDocument).where(MedicalDocument.patient_id == UUID(user_id))

    # Filter by type if specified
    if doc_type:
        query = query.where(MedicalDocument.doc_type == doc_type)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(MedicalDocument.uploaded_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document's details."""
    result = await db.execute(
        select(MedicalDocument).where(
            MedicalDocument.id == document_id,
            MedicalDocument.patient_id == UUID(user_id),
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document (soft delete — marks as inactive)."""
    result = await db.execute(
        select(MedicalDocument).where(
            MedicalDocument.id == document_id,
            MedicalDocument.patient_id == UUID(user_id),
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    await db.delete(document)
