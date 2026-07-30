"""
AI Document Processing Service — Extracts structured medical data from documents using OpenAI.
Reads PDF text → sends to GPT → gets structured JSON with medications, diagnosis, etc.
"""

import json
from datetime import datetime

import fitz  # PyMuPDF — for PDF text extraction
from openai import AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

EXTRACTION_PROMPT = """You are a medical document AI. Extract structured data from this medical document text.

Return a JSON object with these fields (use null if not found):
{
  "document_type": "prescription | lab_report | discharge_summary | doctor_notes | other",
  "patient_name": "string",
  "patient_age": "string",
  "patient_gender": "string",
  "doctor_name": "string",
  "hospital_name": "string",
  "document_date": "YYYY-MM-DD or null",
  "diagnosis": ["list of diagnoses"],
  "medications": [
    {"name": "drug name", "dosage": "dose", "frequency": "timing", "duration": "days/months"}
  ],
  "lab_results": [
    {"test_name": "name", "value": "result", "unit": "unit", "normal_range": "range", "is_abnormal": true/false}
  ],
  "vitals": {"bp": "", "pulse": "", "temperature": "", "spo2": ""},
  "procedures": ["list of procedures done"],
  "advice": ["list of advice/instructions"],
  "summary_short": "One-line summary of the document",
  "summary_detailed": "2-3 sentence detailed summary"
}

Only return valid JSON. No markdown, no explanation."""


async def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    doc = fitz.open(stream=file_content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


async def process_document_with_ai(text: str) -> dict:
    """Send document text to OpenAI and get structured extraction."""
    if not text or len(text.strip()) < 10:
        return {"error": "No readable text found in document"}

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"Extract data from this medical document:\n\n{text[:4000]}"},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    result_text = response.choices[0].message.content
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response", "raw": result_text}


async def process_document(file_content: bytes) -> dict:
    """Full pipeline: PDF → Text → AI → Structured Data."""
    # Step 1: Extract text
    text = await extract_text_from_pdf(file_content)

    if not text:
        return {
            "raw_text": "",
            "extracted_data": None,
            "summary_short": "Could not read document (no text found)",
            "summary_detailed": "The document appears to be empty or contains only images. OCR processing may be needed.",
            "ai_confidence": 0.0,
        }

    # Step 2: AI extraction
    extracted = await process_document_with_ai(text)

    if "error" in extracted:
        return {
            "raw_text": text,
            "extracted_data": None,
            "summary_short": "AI processing failed",
            "summary_detailed": extracted.get("error", "Unknown error"),
            "ai_confidence": 0.0,
        }

    # Step 3: Return structured result
    return {
        "raw_text": text,
        "extracted_data": extracted,
        "summary_short": extracted.get("summary_short", "Document processed"),
        "summary_detailed": extracted.get("summary_detailed", ""),
        "doctor_name": extracted.get("doctor_name"),
        "hospital_name": extracted.get("hospital_name"),
        "document_date": extracted.get("document_date"),
        "ai_confidence": 0.85,
    }
