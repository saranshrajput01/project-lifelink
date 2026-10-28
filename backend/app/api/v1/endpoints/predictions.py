"""
Prediction endpoints — disease risk scoring (cardiovascular + diabetes).

Runs the trained ML models, returns an explainable risk assessment, and persists
it to risk_assessments so the dashboard can show history/trends.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.ml import predict as ml_predict
from app.models.risk_assessment import RiskAssessment

router = APIRouter(prefix="/predictions", tags=["Predictions"])


class HeartInput(BaseModel):
    age: float = 50
    sex: int = 0  # 1 = male
    cholesterol: float = 200
    systolic_bp: float = 120
    smoker: int = 0
    bmi: float = 25
    diabetic: int = 0


class DiabetesInput(BaseModel):
    glucose: float = 110
    bmi: float = 28
    age: float = 35
    insulin: float = 100
    diastolic_bp: float = 75
    pregnancies: int = 0
    family_history: int = 0


class CKDInput(BaseModel):
    age: float = 50
    systolic_bp: float = 80
    blood_glucose: float = 120
    blood_urea: float = 40
    serum_creatinine: float = 1.2
    hemoglobin: float = 13
    albumin: float = 0  # urine albumin level 0-5
    hypertension: int = 0
    diabetic: int = 0


class RiskResult(BaseModel):
    disease_type: str
    risk_score: float
    risk_level: str
    contributing_factors: list
    recommendations: list
    explanation: str
    model_version: str
    model_confidence: float | None = None


async def _run_and_store(
    disease_type: str, inputs: dict, user_id: str, db: AsyncSession
) -> dict:
    try:
        result = ml_predict.predict(disease_type, inputs)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )

    db.add(
        RiskAssessment(
            patient_id=UUID(user_id),
            disease_type=result["disease_type"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            contributing_factors=result["contributing_factors"],
            recommendations=result["recommendations"],
            explanation=result["explanation"],
            model_version=result["model_version"],
            model_confidence=result["model_confidence"],
        )
    )
    await db.flush()
    return result


@router.get("/status")
async def status_check():
    """Whether the ML models are loaded and ready."""
    return {"models_available": ml_predict.available()}


@router.post("/cardiovascular", response_model=RiskResult)
async def predict_cardiovascular(
    payload: HeartInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Predict 10-year cardiovascular risk."""
    return await _run_and_store("cardiovascular", payload.model_dump(), user_id, db)


@router.post("/diabetes", response_model=RiskResult)
async def predict_diabetes(
    payload: DiabetesInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Predict diabetes onset risk."""
    return await _run_and_store("diabetes", payload.model_dump(), user_id, db)


@router.post("/ckd", response_model=RiskResult)
async def predict_ckd(
    payload: CKDInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Predict chronic kidney disease risk (trained on UCI CKD dataset)."""
    return await _run_and_store("ckd", payload.model_dump(), user_id, db)


@router.get("/history")
async def prediction_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return the user's past risk assessments (newest first)."""
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.patient_id == UUID(user_id))
        .order_by(RiskAssessment.assessed_at.desc())
        .limit(50)
    )
    items = result.scalars().all()
    return {
        "assessments": [
            {
                "id": str(a.id),
                "disease_type": a.disease_type,
                "risk_score": a.risk_score,
                "risk_level": a.risk_level,
                "contributing_factors": a.contributing_factors,
                "recommendations": a.recommendations,
                "explanation": a.explanation,
                "model_version": a.model_version,
                "model_confidence": a.model_confidence,
                "assessed_at": a.assessed_at.isoformat() if a.assessed_at else None,
            }
            for a in items
        ],
        "total": len(items),
    }
