"""
Document schemas — request/response models for file upload and document listing.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Response model for a medical document."""
    id: UUID
    patient_id: UUID
    doc_type: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    ocr_status: str
    processing_status: str
    summary_short: str | None = None
    document_date: datetime | None = None
    doctor_name: str | None = None
    hospital_name: str | None = None
    tags: list[str] | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Response for listing documents with pagination."""
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int


class UploadResponse(BaseModel):
    """Response after successful file upload."""
    id: UUID
    filename: str
    doc_type: str
    status: str
    message: str
