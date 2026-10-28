"""
AI Document Processing Service — Extracts structured medical data from documents.
AI provider: Groq (ported from bizmind-ai), with multi-key rotation + model fallback.

Reads PDF text → sends to Groq LLM → gets structured JSON (medications, diagnosis, etc).
"""

import asyncio
import json
import logging
import re

import fitz  # PyMuPDF — for PDF text extraction

from app.core.config import get_settings
from app.services.groq_client import chat_with_rotation

logger = logging.getLogger(__name__)
settings = get_settings()

# PaddleOCR is heavy (~hundreds of MB). Load it lazily & once (singleton).
_ocr_engine = None


def _get_ocr_engine():
    """Lazy-load a singleton PaddleOCR engine. Returns None if unavailable."""
    global _ocr_engine
    if _ocr_engine is not None:
        return _ocr_engine
    try:
        from paddleocr import PaddleOCR

        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        logger.info("[OCR] PaddleOCR engine initialized")
    except Exception as e:  # import or init failure — degrade gracefully
        logger.warning("[OCR] PaddleOCR unavailable: %s", e)
        _ocr_engine = None
    return _ocr_engine


def _ocr_image_sync(image_bytes: bytes) -> str:
    """Blocking OCR of an image byte stream. Returns extracted text (may be empty)."""
    engine = _get_ocr_engine()
    if engine is None:
        return ""
    import numpy as np
    from PIL import Image
    import io

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)
        result = engine.ocr(arr, cls=True)
    except Exception as e:
        logger.error("[OCR] image OCR failed: %s", e)
        return ""

    lines: list[str] = []
    # PaddleOCR returns [[ [box, (text, conf)], ... ]]
    for page in result or []:
        for item in page or []:
            try:
                txt = item[1][0]
                if txt:
                    lines.append(txt)
            except (IndexError, TypeError):
                continue
    return "\n".join(lines).strip()


async def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text from an image using PaddleOCR (runs off the event loop)."""
    return await asyncio.to_thread(_ocr_image_sync, image_bytes)


def _ocr_pdf_pages_sync(file_content: bytes) -> str:
    """Render each PDF page to an image and OCR it (for scanned PDFs)."""
    engine = _get_ocr_engine()
    if engine is None:
        return ""
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
    except Exception as e:
        logger.error("[OCR] could not open PDF for OCR: %s", e)
        return ""

    parts: list[str] = []
    try:
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            txt = _ocr_image_sync(img_bytes)
            if txt:
                parts.append(txt)
    finally:
        doc.close()
    return "\n".join(parts).strip()


async def _ocr_pdf_pages(file_content: bytes) -> str:
    """Async wrapper — OCR a scanned PDF page by page."""
    return await asyncio.to_thread(_ocr_pdf_pages_sync, file_content)


# Model fallback chain (same pattern as bizmind-ai orchestrator)
_FALLBACK_MODELS = [
    settings.GROQ_MODEL_STRONG,
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]


def _models_to_try() -> list[str]:
    seen: set = set()
    out: list[str] = []
    for m in _FALLBACK_MODELS:
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


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


def _clean_llm_json(raw: str) -> str:
    """Strip Qwen <think>...</think> chain-of-thought and markdown fences."""
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    if raw.startswith("```"):
        raw = "\n".join(
            line for line in raw.split("\n") if not line.startswith("```")
        ).strip()
    return raw


def _extract_sync(text: str) -> dict:
    """Blocking Groq call with model fallback. Runs in a thread via asyncio."""
    messages = [
        {"role": "system", "content": EXTRACTION_PROMPT},
        {
            "role": "user",
            "content": f"Extract data from this medical document:\n\n{text[:4000]}",
        },
    ]

    raw = ""
    for model in _models_to_try():
        try:
            response = chat_with_rotation(
                messages=messages,
                model=model,
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )
            raw = (response.choices[0].message.content or "").strip()
            if model != settings.GROQ_MODEL_STRONG:
                logger.info(f"[AI] Used fallback model: {model}")
            break
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                logger.warning(f"[AI] Rate limit on {model}, trying next...")
                continue
            logger.error(f"[AI] Extraction failed on {model}: {e}")
            return {"error": str(e)}

    raw = _clean_llm_json(raw)
    if not raw:
        return {"error": "Empty AI response"}

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"error": "Failed to parse AI response", "raw": raw}


async def process_document_with_ai(text: str) -> dict:
    """Send document text to Groq and get structured extraction."""
    if not text or len(text.strip()) < 10:
        return {"error": "No readable text found in document"}
    # Groq SDK is sync — run off the event loop.
    return await asyncio.to_thread(_extract_sync, text)


async def process_document(
    file_content: bytes, mime_type: str = "application/pdf"
) -> dict:
    """Full pipeline: (PDF text | image OCR) → AI → Structured Data.

    - PDFs: PyMuPDF text extraction. If a PDF has no selectable text (scanned),
      fall back to rendering each page to an image and OCR-ing it.
    - Images: PaddleOCR directly.
    """
    is_image = (mime_type or "").startswith("image/")

    if is_image:
        text = await extract_text_from_image(file_content)
    else:
        text = await extract_text_from_pdf(file_content)
        # Scanned PDF (no selectable text) → render pages → OCR
        if not text:
            text = await _ocr_pdf_pages(file_content)

    if not text:
        hint = (
            "The image could not be read by OCR."
            if is_image
            else "The document appears to be empty or is a scanned PDF OCR could not read."
        )
        return {
            "raw_text": "",
            "extracted_data": None,
            "summary_short": "Could not read document (no text found)",
            "summary_detailed": hint,
            "ai_confidence": 0.0,
        }

    extracted = await process_document_with_ai(text)

    if "error" in extracted:
        return {
            "raw_text": text,
            "extracted_data": None,
            "summary_short": "AI processing failed",
            "summary_detailed": extracted.get("error", "Unknown error"),
            "ai_confidence": 0.0,
        }

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
