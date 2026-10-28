"""
Train disease-risk models (heart disease + diabetes).

Uses sklearn GradientBoostingClassifier (already installed; no xgboost download).
If real UCI CSVs are placed in app/ml/datasets/ they are used; otherwise the
script falls back to realistic synthetic data so the pipeline is demo-ready today
and can be swapped to real data later without code changes.

Run inside the backend container:
    python -m app.ml.train
"""

import logging
import os

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml.train")

HERE = os.path.dirname(__file__)
MODELS_DIR = os.path.join(HERE, "models_store")
DATASETS_DIR = os.path.join(HERE, "datasets")
os.makedirs(MODELS_DIR, exist_ok=True)

# Feature order MUST match the prediction service.
HEART_FEATURES = [
    "age",
    "sex",
    "cholesterol",
    "systolic_bp",
    "smoker",
    "bmi",
    "diabetic",
]
DIABETES_FEATURES = [
    "glucose",
    "bmi",
    "age",
    "insulin",
    "diastolic_bp",
    "pregnancies",
    "family_history",
]
CKD_FEATURES = [
    "age",
    "systolic_bp",
    "blood_glucose",
    "blood_urea",
    "serum_creatinine",
    "hemoglobin",
    "albumin",
    "hypertension",
    "diabetic",
]

# Map our CKD feature names -> column index in the UCI ARFF data rows (0-based).
# ARFF order: age,bp,sg,al,su,rbc,pc,pcc,ba,bgr,bu,sc,sod,pot,hemo,pcv,wbcc,rbcc,htn,dm,cad,appet,pe,ane,class
_CKD_ARFF_IDX = {
    "age": 0,
    "systolic_bp": 1,
    "albumin": 3,
    "blood_glucose": 9,
    "blood_urea": 10,
    "serum_creatinine": 11,
    "hemoglobin": 14,
    "hypertension": 18,
    "diabetic": 19,
}


def _load_ckd_arff(path: str):
    """Parse the UCI CKD ARFF into (X, y) using CKD_FEATURES. Returns None if unusable."""
    rows_X, rows_y = [], []
    data_started = False
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            if not data_started:
                if s.lower().startswith("@data"):
                    data_started = True
                continue
            if not s or s.startswith("%"):
                continue
            cells = [c.strip().strip("'\"") for c in s.split(",")]
            if len(cells) < 25:
                continue
            label = cells[24].lower()
            if "ckd" not in label:
                continue
            y = 1 if label == "ckd" else 0

            def num(idx, default):
                v = cells[idx]
                if v in ("?", "", "nan"):
                    return default
                try:
                    return float(v)
                except ValueError:
                    return default

            feat = {
                "age": num(0, 50),
                "systolic_bp": num(1, 80),
                "albumin": num(3, 0),
                "blood_glucose": num(9, 120),
                "blood_urea": num(10, 40),
                "serum_creatinine": num(11, 1.2),
                "hemoglobin": num(14, 13),
                "hypertension": 1.0 if cells[18].lower() == "yes" else 0.0,
                "diabetic": 1.0 if cells[19].lower() == "yes" else 0.0,
            }
            rows_X.append([feat[f] for f in CKD_FEATURES])
            rows_y.append(y)
    if len(rows_X) < 20:
        return None
    return np.array(rows_X), np.array(rows_y)


def _load_heart_cleveland(path: str):
    """Parse the real UCI Cleveland heart dataset into (X, y) using HEART_FEATURES.

    Cleveland columns (0-based):
      0 age, 1 sex, 2 cp, 3 trestbps(systolic_bp), 4 chol(cholesterol),
      5 fbs(fasting blood sugar >120 -> diabetic proxy), 6 restecg, 7 thalach,
      8 exang, 9 oldpeak, 10 slope, 11 ca, 12 thal, 13 num(target).
    'smoker' and 'bmi' are NOT in this dataset, so they are filled with the
    column median (kept only to preserve the 7-feature API/form contract).
    Target 'num' > 0 means heart disease present. '?' cells are skipped.
    Returns None if unusable.
    """
    rows_X, rows_y = [], []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            cells = [c.strip() for c in s.split(",")]
            if len(cells) < 14 or "?" in (
                cells[0],
                cells[1],
                cells[3],
                cells[4],
                cells[5],
            ):
                continue
            try:
                age = float(cells[0])
                sex = float(cells[1])  # 1 = male, 0 = female
                systolic_bp = float(cells[3])
                cholesterol = float(cells[4])
                diabetic = 1.0 if float(cells[5]) == 1.0 else 0.0  # fbs > 120 mg/dl
                y = 1 if float(cells[13]) > 0 else 0
            except ValueError:
                continue
            # smoker/bmi absent in Cleveland -> placeholder, filled with median below.
            rows_X.append([age, sex, cholesterol, systolic_bp, None, None, diabetic])
            rows_y.append(y)
    if len(rows_X) < 20:
        return None
    Xarr = np.array(rows_X, dtype=object)
    # Fill the two absent columns (index 4 smoker, 5 bmi) with sensible medians.
    for col, default in ((4, 0.0), (5, 26.0)):
        Xarr[:, col] = default
    return np.array(Xarr, dtype=float), np.array(rows_y)


def _load_pima_diabetes(path: str):
    """Parse the real Pima Indians Diabetes dataset into (X, y) using DIABETES_FEATURES.

    Pima columns (0-based):
      0 pregnancies, 1 glucose, 2 diastolic_bp, 3 skin, 4 insulin, 5 bmi,
      6 diabetes-pedigree(family_history proxy), 7 age, 8 outcome(target).
    DIABETES_FEATURES order: glucose, bmi, age, insulin, diastolic_bp,
    pregnancies, family_history. Returns None if unusable.
    """
    rows_X, rows_y = [], []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            cells = [c.strip() for c in s.split(",")]
            if len(cells) < 9:
                continue
            try:
                pregnancies = float(cells[0])
                glucose = float(cells[1])
                diastolic_bp = float(cells[2])
                insulin = float(cells[4])
                bmi = float(cells[5])
                pedigree = float(cells[6])
                age = float(cells[7])
                y = int(float(cells[8]))
            except ValueError:
                continue
            # Pedigree is a continuous risk score; treat >0.5 as a positive family history.
            family_history = 1.0 if pedigree > 0.5 else 0.0
            rows_X.append(
                [glucose, bmi, age, insulin, diastolic_bp, pregnancies, family_history]
            )
            rows_y.append(y)
    if len(rows_X) < 20:
        return None
    return np.array(rows_X), np.array(rows_y)


def _synth_heart(n: int = 4000, seed: int = 42):
    """Generate realistic synthetic heart-disease data with a plausible risk model."""
    rng = np.random.default_rng(seed)
    age = rng.normal(54, 12, n).clip(20, 90)
    sex = rng.integers(0, 2, n)  # 1 = male
    cholesterol = rng.normal(210, 45, n).clip(120, 400)
    systolic_bp = rng.normal(132, 18, n).clip(90, 210)
    smoker = rng.integers(0, 2, n)
    bmi = rng.normal(27, 5, n).clip(15, 50)
    diabetic = rng.integers(0, 2, n)

    # Latent risk (clinically-inspired weights) -> probability -> label
    z = (
        0.045 * (age - 50)
        + 0.5 * sex
        + 0.010 * (cholesterol - 200)
        + 0.030 * (systolic_bp - 120)
        + 0.9 * smoker
        + 0.07 * (bmi - 25)
        + 0.8 * diabetic
        - 2.2
    )
    prob = 1 / (1 + np.exp(-z))
    y = (rng.random(n) < prob).astype(int)
    X = np.column_stack([age, sex, cholesterol, systolic_bp, smoker, bmi, diabetic])
    return X, y


def _synth_diabetes(n: int = 4000, seed: int = 7):
    """Generate realistic synthetic diabetes data (Pima-inspired)."""
    rng = np.random.default_rng(seed)
    glucose = rng.normal(120, 32, n).clip(50, 300)
    bmi = rng.normal(32, 7, n).clip(15, 60)
    age = rng.normal(41, 13, n).clip(18, 90)
    insulin = rng.normal(120, 90, n).clip(0, 600)
    diastolic_bp = rng.normal(72, 12, n).clip(40, 120)
    pregnancies = rng.poisson(2.5, n).clip(0, 15)
    family_history = rng.integers(0, 2, n)

    z = (
        0.030 * (glucose - 110)
        + 0.06 * (bmi - 28)
        + 0.025 * (age - 35)
        + 0.002 * (insulin - 100)
        + 0.01 * (diastolic_bp - 70)
        + 0.12 * pregnancies
        + 0.7 * family_history
        - 2.0
    )
    prob = 1 / (1 + np.exp(-z))
    y = (rng.random(n) < prob).astype(int)
    X = np.column_stack(
        [glucose, bmi, age, insulin, diastolic_bp, pregnancies, family_history]
    )
    return X, y


def _train_one(name: str, X, y, features: list[str]) -> float:
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=1, stratify=y
    )
    # Smaller real datasets (e.g. Cleveland heart, 303 rows) overfit with deep trees;
    # a shallower, lightly-regularised model generalises better. Larger synthetic/CKD
    # sets are unaffected by these conservative settings.
    clf = GradientBoostingClassifier(
        n_estimators=150, max_depth=2, learning_rate=0.05, subsample=0.9, random_state=1
    )
    clf.fit(X_tr, y_tr)
    auc = roc_auc_score(y_te, clf.predict_proba(X_te)[:, 1])
    bundle = {
        "model": clf,
        "features": features,
        "version": f"{name}-gb-v1",
        "auc": round(float(auc), 4),
    }
    path = os.path.join(MODELS_DIR, f"{name}.joblib")
    joblib.dump(bundle, path)
    logger.info("[train] %s: AUC=%.4f  saved -> %s", name, auc, path)
    return auc


def main():
    logger.info(
        "[train] datasets dir: %s (real CSVs override synthetic if present)",
        DATASETS_DIR,
    )
    # Heart — use real UCI Cleveland data if present, else synthetic.
    heart_path = os.path.join(DATASETS_DIR, "heart_cleveland.data")
    loaded_h = _load_heart_cleveland(heart_path) if os.path.exists(heart_path) else None
    if loaded_h is not None:
        Xh, yh = loaded_h
        logger.info("[train] heart: using REAL UCI Cleveland data (%d rows)", len(Xh))
    else:
        Xh, yh = _synth_heart()
        logger.info("[train] heart: no real dataset, using synthetic")
    _train_one("heart", Xh, yh, HEART_FEATURES)

    # Diabetes — use real Pima data if present, else synthetic.
    pima_path = os.path.join(DATASETS_DIR, "pima_diabetes.csv")
    loaded_d = _load_pima_diabetes(pima_path) if os.path.exists(pima_path) else None
    if loaded_d is not None:
        Xd, yd = loaded_d
        logger.info("[train] diabetes: using REAL Pima data (%d rows)", len(Xd))
    else:
        Xd, yd = _synth_diabetes()
        logger.info("[train] diabetes: no real dataset, using synthetic")
    _train_one("diabetes", Xd, yd, DIABETES_FEATURES)

    # CKD — use real UCI ARFF if present
    ckd_arff = os.path.join(DATASETS_DIR, "ckd.arff")
    if os.path.exists(ckd_arff):
        loaded = _load_ckd_arff(ckd_arff)
        if loaded is not None:
            Xc, yc = loaded
            logger.info("[train] ckd: using REAL UCI data (%d rows)", len(Xc))
            _train_one("ckd", Xc, yc, CKD_FEATURES)
        else:
            logger.warning("[train] ckd: ARFF unusable, skipping")
    else:
        logger.info(
            "[train] ckd: no dataset found, skipping (place ckd.arff in datasets/)"
        )
    logger.info("[train] done.")


if __name__ == "__main__":
    main()
