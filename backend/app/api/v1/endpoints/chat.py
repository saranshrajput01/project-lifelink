"""
AI Healthcare Assistant endpoint — Groq-powered chat grounded in the
patient's own uploaded medical records.

Not a diagnosis tool: the system prompt enforces safety guardrails
(no definitive diagnoses, always recommend seeing a doctor).
"""

import asyncio
import logging
import re
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.document import MedicalDocument
from app.services.groq_client import chat_with_rotation
from app.services.rag import retrieve
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

_FALLBACK_MODELS = [
    settings.GROQ_MODEL_STRONG,
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]

SYSTEM_PROMPT = """You are LIFELINK's AI Healthcare Assistant.

Rules you MUST follow:
- Help the user understand their own medical records in plain language.
- NEVER give a definitive diagnosis. Explain possibilities, not conclusions.
- NEVER prescribe or change medication/dosage.
- For anything serious or urgent, tell the user to consult a qualified doctor.
- If the question is an emergency (chest pain, severe bleeding, difficulty breathing,
  suicidal thoughts), tell them to contact emergency services immediately.
- Base answers on the CONTEXT (the user's records) when relevant. If the records
  don't contain the answer, say so and give safe general information.
- Be concise, warm, and easy to understand. Use short paragraphs or bullets.
- End medical explanations with a brief reminder to confirm with their doctor.
"""


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


def _strip_think(raw: str) -> str:
    return re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()


async def _build_context(user_id: str, db: AsyncSession) -> str:
    """Summarize the patient's processed documents into a compact context string."""
    result = await db.execute(
        select(MedicalDocument)
        .where(
            MedicalDocument.patient_id == user_id,
            MedicalDocument.processing_status == "completed",
        )
        .order_by(MedicalDocument.uploaded_at.desc())
        .limit(15)
    )
    docs = result.scalars().all()
    if not docs:
        return "The user has not uploaded any processed medical records yet."

    lines: list[str] = []
    for d in docs:
        date = d.document_date or d.uploaded_at
        date_str = date.strftime("%Y-%m-%d") if date else "unknown date"
        line = f"- [{d.doc_type}] {date_str}: {d.summary_short or d.original_filename}"
        ed = d.extracted_data or {}
        meds = ed.get("medications")
        if meds:
            names = ", ".join(m.get("name", "") for m in meds if isinstance(m, dict))
            if names:
                line += f" | Medications: {names}"
        labs = ed.get("lab_results")
        if labs:
            abn = [
                f"{lab.get('test_name')}={lab.get('value')}{lab.get('unit','')}"
                for lab in labs
                if isinstance(lab, dict) and lab.get("is_abnormal")
            ]
            if abn:
                line += f" | Abnormal labs: {'; '.join(abn)}"
        lines.append(line)
    return "User's recent medical records:\n" + "\n".join(lines)


def _call_groq(messages: list[dict]) -> str:
    seen: set = set()
    models = [m for m in _FALLBACK_MODELS if m and not (m in seen or seen.add(m))]
    for model in models:
        try:
            resp = chat_with_rotation(
                messages=messages, model=model, temperature=0.3, max_tokens=800
            )
            return _strip_think(resp.choices[0].message.content or "")
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                logger.warning("[CHAT] Rate limit on %s, trying next...", model)
                continue
            logger.exception("[CHAT] Groq call failed on %s", model)
            break
    return ""


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Chat with the AI assistant, grounded in the user's own records."""
    # Prefer real RAG (vector retrieval of relevant chunks); fall back to summaries.
    retrieved = await retrieve(
        db, patient_id=UUID(user_id), query=body.message, top_k=5
    )
    if retrieved:
        context = (
            "Relevant excerpts from the user's medical records:\n"
            + "\n---\n".join(retrieved)
        )
    else:
        context = await _build_context(user_id, db)

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"CONTEXT:\n{context}"},
    ]
    for m in body.history[-8:]:
        if m.role in ("user", "assistant"):
            messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": body.message})

    reply = await asyncio.to_thread(_call_groq, messages)
    if not reply:
        reply = (
            "Sorry, I'm having trouble reaching the AI service right now. "
            "Please try again in a moment."
        )
    return ChatResponse(reply=reply)
