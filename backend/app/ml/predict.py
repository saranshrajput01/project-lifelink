"""
Prediction service — load trained risk models and produce explainable risk scores.

Models are loaded lazily and cached. Explainability uses a lightweight
feature-contribution approach (deviation from a healthy baseline weighted by the
model's feature importances) plus rule-based recommendations — no heavy SHAP
dependency needed, but conceptually similar (per-feature contribution to risk).
"""

import logging
import os

import joblib
import numpy as np

logger = logging.getLogger("ml.predict")

HERE = os.path.dirname(__file__)
MODELS_DIR = os.path.join(HERE, "models_store")

_cache: dict[str, dict] = {}

# Healthy baselines per feature (used to compute "how far from healthy" a value is).
HEALTHY_BASELINE = {
    "age": 40, "sex": 0, "cholesterol": 180, "systolic_bp": 115, "smoker": 0,
    "bmi": 23, "diabetic": 0, "glucose": 95, "insulin": 90, "diastolic_bp": 75,
    "pregnancies": 0, "family_history": 0,
    # CKD features
    "blood_glucose": 100, "blood_urea": 25, "serum_creatinine": 1.0,
    "hemoglobin": 14, "albumin": 0, "hypertension": 0,
}

# Human-readable labels + recommendation hints keyed by feature.
FEATURE_LABELS = {
    "age": "Age", "sex": "Male sex", "cholesterol": "Cholesterol", "systolic_bp": "Systolic BP",
    "smoker": "Smoking", "bmi": "BMI", "diabetic": "Diabetic status", "glucose": "Blood glucose",
    "insulin": "Insulin", "diastolic_bp": "Diastolic BP", "pregnancies": "Pregnancies",
    "family_history": "Family history",
    "blood_glucose": "Blood glucose", "blood_urea": "Blood urea", "serum_creatinine": "Serum creatinine",
    "hemoglobin": "Hemoglobin", "albumin": "Albumin (urine)", "hypertension": "Hypertension",
}

RECO_HINTS = {
    "cholesterol": "Lower cholesterol with diet changes and consider a lipid panel follow-up.",
    "systolic_bp": "Monitor blood pressure; reduce salt and manage stress.",
    "diastolic_bp": "Monitor blood pressure regularly.",
    "smoker": "Quitting smoking significantly reduces cardiovascular risk.",
    "bmi": "Aim for a healthy BMI through diet and 150 min/week of activity.",
    "glucose": "Control blood sugar; limit refined carbs and get HbA1c tested.",
    "blood_glucose": "Control blood sugar; limit refined carbs and get HbA1c tested.",
    "insulin": "Discuss insulin resistance markers with your doctor.",
    "diabetic": "Follow your diabetes management plan closely.",
    "age": "Age is non-modifiable; focus on controllable factors.",
    "family_history": "Family history is non-modifiable; prioritise regular screening.",
    "blood_urea": "Elevated urea may signal kidney strain; stay hydrated and get kidney function checked.",
    "serum_creatinine": "High creatinine suggests reduced kidney function; see a nephrologist.",
    "hemoglobin": "Low hemoglobin (anemia) is common in CKD; get iron/CBC evaluated.",
    "albumin": "Protein in urine is an early kidney marker; request a urine albumin test.",
    "hypertension": "Control blood pressure — it both causes and results from kidney disease.",
}

MODEL_NAMES = {"cardiovascular": "heart", "diabetes": "diabetes", "ckd": "ckd"}


def _load(name: str) -> dict | None:
    if name in _cache:
        return _cache[name]
    path = os.path.join(MODELS_DIR, f"{name}.joblib")
    if not os.path.exists(path):
        logger.warning("[predict] model file missing: %s", path)
        return None
    bundle = joblib.load(path)
    _cache[name] = bundle
    return bundle


def available() -> bool:
    return any(_load(n) is not None for n in MODEL_NAMES.values())


def _risk_level(score: float) -> str:
    if score < 0.25:
        return "low"
    if score < 0.5:
        return "moderate"
    if score < 0.75:
        return "high"
    return "critical"


def predict(disease_type: str, inputs: dict) -> dict:
    """Return a risk score, level, contributing factors and recommendations.

    disease_type: "cardiovascular" | "diabetes"
    inputs: dict of raw feature values (missing -> healthy baseline).
    """
    name = MODEL_NAMES.get(disease_type)
    bundle = _load(name) if name else None
    if bundle is None:
        raise ValueError(f"Model for '{disease_type}' not available. Run app.ml.train.")

    model = bundle["model"]
    features = bundle["features"]

    row = [float(inputs.get(f, HEALTHY_BASELINE.get(f, 0))) for f in features]
    X = np.array([row])
    score = float(model.predict_proba(X)[0, 1])

    # Per-feature contribution: importance * normalised deviation from baseline.
    importances = getattr(model, "feature_importances_", np.ones(len(features)) / len(features))
    contributions = []
    for f, val, imp in zip(features, row, importances):
        base = HEALTHY_BASELINE.get(f, 0)
        scale = abs(base) if abs(base) > 1 else 1.0
        deviation = (val - base) / scale
        impact = float(imp) * deviation
        if abs(impact) < 1e-6:
            continue
        contributions.append({
            "factor": FEATURE_LABELS.get(f, f),
            "value": round(val, 1),
            "impact": round(abs(impact), 3),
            "direction": "increases_risk" if impact > 0 else "lowers_risk",
        })
    contributions.sort(key=lambda c: c["impact"], reverse=True)
    top = contributions[:4]

    # Recommendations from the top risk-increasing modifiable factors.
    recs = []
    for c in top:
        if c["direction"] != "increases_risk":
            continue
        key = next((k for k, v in FEATURE_LABELS.items() if v == c["factor"]), None)
        hint = RECO_HINTS.get(key)
        if hint and hint not in recs:
            recs.append(hint)
    if not recs:
        recs = ["Maintain your healthy habits and keep up regular check-ups."]

    level = _risk_level(score)
    _labels = {"cardiovascular": "cardiovascular", "diabetes": "diabetes", "ckd": "chronic kidney disease"}
    disease_label = _labels.get(disease_type, disease_type)
    explanation = (
        f"Estimated {disease_label} risk is {round(score * 100)}% ({level}). "
        + (f"Main drivers: {', '.join(c['factor'] for c in top if c['direction'] == 'increases_risk')}. "
           if any(c['direction'] == 'increases_risk' for c in top) else "")
        + "This is a screening estimate, not a diagnosis — consult a doctor."
    )

    return {
        "disease_type": disease_type,
        "risk_score": round(score, 4),
        "risk_level": level,
        "contributing_factors": top,
        "recommendations": recs,
        "explanation": explanation,
        "model_version": bundle.get("version", "v1"),
        "model_confidence": bundle.get("auc"),
    }
