"""
Document endpoints — upload, list, get, delete medical documents.
"""

import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory, get_db
from app.core.dependencies import get_current_user_id
from app.models.document import MedicalDocument
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse, UploadResponse
from app.services.storage import (
    ensure_bucket_exists,
    generate_s3_key,
    get_download_url,
    get_file_from_s3,
    upload_file_to_s3,
)
from app.services.ai_processing import process_document
from app.services.report import build_health_report
from app.services.rag import index_document

logger = logging.getLogger(__name__)

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


@router.post(
    "/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Query(
        default="other",
        regex="^(prescription|lab_report|discharge_summary|doctor_notes|vaccination|insurance|other)$",
    ),
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
    success = await upload_file_to_s3(
        content, s3_key, file.content_type or "application/octet-stream"
    )

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
    await db.commit()  # commit now so the background task can see the row

    # AI processing (OCR + Groq) takes a while — run it after the response is sent
    # so the upload returns immediately. Status moves pending → completed/failed.
    background_tasks.add_task(_process_in_background, document.id, content)

    return UploadResponse(
        id=document.id,
        filename=document.original_filename,
        doc_type=document.doc_type,
        status=document.processing_status,
        message="Document uploaded. AI processing has started — refresh in a minute.",
    )


async def _process_in_background(document_id: UUID, content: bytes) -> None:
    """Run AI processing + RAG indexing in its own DB session after the response."""
    async with async_session_factory() as db:
        try:
            document = await db.get(MedicalDocument, document_id)
            if document is None:
                return
            document.processing_status = "processing"
            await db.commit()
            await _run_ai_processing(document, content, document.mime_type)
            await _index_for_rag(db, document)
            await db.commit()
        except Exception:
            logger.exception("[DOC] background processing failed for %s", document_id)
            await db.rollback()


async def _run_ai_processing(
    document: MedicalDocument, content: bytes, mime_type: str = "application/pdf"
) -> None:
    """Run the AI pipeline on a document and update its fields in place.

    Logs any failure and records the reason instead of silently swallowing it.
    """
    try:
        ai_result = await process_document(content, mime_type)

        # process_document returns ai_confidence 0.0 on read/AI failure
        if ai_result.get("extracted_data") is None:
            document.ocr_status = "failed"
            document.processing_status = "failed"
            document.summary_short = (
                ai_result.get("summary_short") or "AI processing failed"
            )
            document.summary_detailed = ai_result.get("summary_detailed") or ""
            document.raw_text = ai_result.get("raw_text")
            logger.warning(
                "[DOC] AI processing produced no data for %s: %s",
                document.id,
                document.summary_detailed,
            )
            return

        document.raw_text = ai_result.get("raw_text")
        document.extracted_data = ai_result.get("extracted_data")
        document.summary_short = ai_result.get("summary_short")
        document.summary_detailed = ai_result.get("summary_detailed")
        document.doctor_name = ai_result.get("doctor_name")
        document.hospital_name = ai_result.get("hospital_name")
        document.ai_confidence = ai_result.get("ai_confidence")
        document.ocr_status = "completed"
        document.processing_status = "completed"

        doc_date = ai_result.get("document_date")
        if doc_date:
            try:
                from datetime import datetime as dt

                document.document_date = dt.strptime(doc_date, "%Y-%m-%d")
            except (ValueError, TypeError):
                pass
    except Exception as e:
        logger.exception("[DOC] AI processing crashed for %s", document.id)
        document.ocr_status = "failed"
        document.processing_status = "failed"
        document.summary_short = "AI processing failed"
        document.summary_detailed = str(e)[:500]


async def _index_for_rag(db: AsyncSession, document: MedicalDocument) -> None:
    """Build pgvector embeddings for a processed document (best-effort)."""
    text = document.raw_text
    if not text:
        return
    try:
        await index_document(
            db,
            document_id=document.id,
            patient_id=document.patient_id,
            text=text,
        )
    except Exception:
        logger.exception("[DOC] RAG indexing failed for %s", document.id)


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    document_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Re-run AI processing on an already-uploaded document (for failed/pending ones)."""
    result = await db.execute(
        select(MedicalDocument).where(
            MedicalDocument.id == document_id,
            MedicalDocument.patient_id == UUID(user_id),
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found."
        )

    content = get_file_from_s3(document.s3_key)
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage.",
        )

    await _run_ai_processing(document, content, document.mime_type)
    await _index_for_rag(db, document)
    await db.flush()
    await db.refresh(document)
    return document


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


@router.get("/insights")
async def health_insights(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Compute a simple health score + AI insight highlights from processed docs.

    Heuristic score (not a medical score): starts at 100, minus points for
    abnormal lab values and risk keywords found in the user's records.
    """
    return await _compute_insights(user_id, db)


async def _compute_insights(user_id: str, db: AsyncSession) -> dict:
    """Shared insight computation used by the insights endpoint and PDF report."""
    result = await db.execute(
        select(MedicalDocument).where(
            MedicalDocument.patient_id == UUID(user_id),
            MedicalDocument.processing_status == "completed",
        )
    )
    docs = result.scalars().all()
    processed = len(docs)
    abnormal_labs: list[str] = []
    conditions: set[str] = set()
    medications: set[str] = set()

    # Total number of documents the user has uploaded (processed or not).
    total = (
        await db.execute(
            select(func.count(MedicalDocument.id)).where(
                MedicalDocument.patient_id == UUID(user_id)
            )
        )
    ).scalar() or 0

    # Go through each processed document and collect:
    #   - abnormal lab values   (e.g. "Hemoglobin: 10.8 g/dL")
    #   - diagnosed conditions  (e.g. "Type 2 Diabetes")
    #   - active medications    (e.g. "Metformin")
    for d in docs:
        data = d.extracted_data or {}

        for lab in data.get("lab_results") or []:
            if isinstance(lab, dict) and lab.get("is_abnormal"):
                name = lab.get("test_name")
                value = lab.get("value")
                unit = lab.get("unit", "")
                abnormal_labs.append(f"{name}: {value}{unit}")

        for dx in data.get("diagnosis") or []:
            if dx:
                conditions.add(str(dx))

        for m in data.get("medications") or []:
            if isinstance(m, dict) and m.get("name"):
                medications.add(m["name"])

    # ─── Health Score (simple 0-100 indicator, NOT a medical score) ───
    # Start at 100 (perfect). Subtract points for problems found:
    #   - each abnormal lab value  -> -8 points  (capped at -40 total)
    #   - each diagnosed condition -> -6 points  (capped at -30 total)
    # Never go below 30. If no records processed yet, score is unknown (None).
    if processed == 0:
        score = None
    else:
        penalty_from_labs = min(len(abnormal_labs) * 8, 40)
        penalty_from_conditions = min(len(conditions) * 6, 30)
        score = 100 - penalty_from_labs - penalty_from_conditions
        score = max(score, 30)

    insights: list[str] = []
    if abnormal_labs:
        insights.append(
            f"{len(abnormal_labs)} abnormal lab value(s) detected — review with your doctor."
        )
    if conditions:
        insights.append("Noted conditions: " + ", ".join(sorted(conditions)))
    if medications:
        insights.append("Active medications: " + ", ".join(sorted(medications)))
    if not insights and processed:
        insights.append("No abnormalities detected in processed records.")

    return {
        "total_documents": total,
        "processed_documents": processed,
        "health_score": score,
        "abnormal_labs": abnormal_labs,
        "conditions": sorted(conditions),
        "medications": sorted(medications),
        "insights": insights,
    }


@router.get("/report/pdf")
async def download_health_report(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Generate a health summary PDF (profile + insights + records) and stream it."""
    # User
    user = (
        await db.execute(select(User).where(User.id == UUID(user_id)))
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    # Profile (optional)
    profile = (
        await db.execute(
            select(UserProfile).where(UserProfile.user_id == UUID(user_id))
        )
    ).scalar_one_or_none()

    # Insights
    insights = await _compute_insights(user_id, db)

    # Documents (newest first)
    docs = (
        (
            await db.execute(
                select(MedicalDocument)
                .where(MedicalDocument.patient_id == UUID(user_id))
                .order_by(MedicalDocument.uploaded_at.desc())
            )
        )
        .scalars()
        .all()
    )

    user_d = {"full_name": user.full_name, "email": user.email}
    profile_d = None
    if profile:
        profile_d = {
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "blood_group": profile.blood_group,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "allergies": profile.allergies,
            "chronic_conditions": profile.chronic_conditions,
            "emergency_contact_name": profile.emergency_contact_name,
            "emergency_contact_phone": profile.emergency_contact_phone,
        }
    docs_d = [
        {
            "document_date": d.document_date,
            "uploaded_at": d.uploaded_at,
            "doc_type": d.doc_type,
            "summary_short": d.summary_short,
        }
        for d in docs
    ]

    pdf_bytes = build_health_report(
        user=user_d, profile=profile_d, insights=insights, documents=docs_d
    )
    filename = f"lifelink-health-report-{UUID(user_id).hex[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a pre-signed download URL for the document."""
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

    url = get_download_url(document.s3_key)
    return {"download_url": url, "filename": document.original_filename}
