"""
Guards against train/serve skew: the Streamlit app must build exactly the same
model features as the training pipeline, and therefore reproduce its predictions.

Run from repo root:  python -m pytest tests -q   (or: python tests/test_app_parity.py)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from predictor import CropYieldPredictor  # noqa: E402

RAW_INPUTS = [
    "region", "crop_type", "survey_year", "planting_month", "altitude_m", "rainfall_mm_season",
    "farm_size_ha", "fertilizer_kg_per_ha", "improved_seed_used", "pest_disease_flag",
    "soil_quality_index", "labor_days_per_ha",
]

predictor = CropYieldPredictor()
train = pd.read_csv(ROOT / "data" / "processed" / "master_train.csv")
test = pd.read_csv(ROOT / "data" / "processed" / "master_test.csv")


def test_features_match_training_pipeline():
    X_app = predictor.build_features(train[RAW_INPUTS])
    X_train = train[predictor.feature_names]
    for col in predictor.feature_names:
        if X_train[col].dtype == object or str(X_train[col].dtype).startswith(("str", "string")):
            assert (X_app[col].astype(str).values == X_train[col].astype(str).values).all(), col
        else:
            np.testing.assert_allclose(X_app[col].values, X_train[col].values, rtol=1e-6, atol=1e-6, err_msg=col)


def test_app_reproduces_submission():
    sub = pd.read_csv(ROOT / "submission" / "team_11_submission.csv")
    res = predictor.predict_batch(test[RAW_INPUTS])
    assert (test["plot_id"].values == sub["plot_id"].values).all()
    np.testing.assert_allclose(res["predicted_yield_t_ha"].values, sub["predicted_yield_tons_per_ha"].values, atol=1e-3)


def test_revenue_formula_and_price_not_a_feature():
    assert "price_birr_per_quintal" not in predictor.feature_names
    r = predictor.predict({
        "region": "Oromia", "crop_type": "teff", "survey_year": 2024, "planting_month": "Jul",
        "farm_size_ha": 2.0, "altitude_m": 2100, "fertilizer_kg_per_ha": 50, "improved_seed_used": 1,
        "pest_disease_flag": 0, "soil_quality_index": 0.6, "labor_days_per_ha": 45,
    })
    expected = round(r["total_harvest_tons"] * 10 * r["price_birr_per_quintal"], 0)
    assert abs(r["gross_revenue_birr"] - expected) <= 1


if __name__ == "__main__":
    test_features_match_training_pipeline()
    test_app_reproduces_submission()
    test_revenue_formula_and_price_not_a_feature()
    print("[PASS] App features and predictions match the training pipeline exactly.")
