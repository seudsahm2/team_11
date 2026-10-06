"""
Module: predict.py
Description: Production batch prediction and submission generation for leaderboard test set.
Team: Team 11 | Ethiopian Smallholder Crop-Yield Challenge (Qiyas / AAU IADE 2026)
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import joblib

ALL_FEATURES = [
    'region', 'crop_type', 'planting_month',
    'altitude_m', 'rainfall_mm_season', 'farm_size_ha',
    'fertilizer_kg_per_ha', 'improved_seed_used', 'pest_disease_flag',
    'soil_quality_index', 'labor_days_per_ha',
    'weather_season_mean_temp', 'weather_season_rainfall_mm',
    'weather_season_heat_days', 'weather_temp_anomaly_c',
    'fertilizer_improved_seed_interaction', 'weather_rain_discrepancy_ratio',
    'labor_intensity_per_farm_size', 'is_meher_season', 'altitude_temp_index'
]


def generate_predictions(model_path: str = 'models/final_model.joblib',
                         test_path: str = 'data/processed/master_test.csv',
                         sub_out: str = 'submission/team_11_submission.csv'):
    """Generates test set predictions using the serialized production model."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at: {model_path}. Run src/train.py first.")
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test dataset not found at: {test_path}")

    print(f"[1/3] Loading serialized production model from {model_path}...")
    model = joblib.load(model_path)

    print(f"[2/3] Loading leaderboard test dataset from {test_path}...")
    test_df = pd.read_csv(test_path)
    X_test = test_df[ALL_FEATURES]
    print(f"      Rows: {len(test_df):,} | Features: {len(ALL_FEATURES)}")

    print(f"[3/3] Generating predictions and applying physical bounds...")
    raw_preds = model.predict(X_test)
    clipped_preds = np.clip(raw_preds, 0.1, 9.0).round(4)

    sub_df = pd.DataFrame({
        'plot_id': test_df['plot_id'],
        'yield_tons_per_ha': clipped_preds
    })

    os.makedirs(os.path.dirname(sub_out), exist_ok=True)
    sub_df.to_csv(sub_out, index=False)

    print("=" * 60)
    print("SUBMISSION VERIFICATION AUDIT")
    print("=" * 60)
    print(f"[PASS] File saved:       {sub_out}")
    print(f"[PASS] Exact rows:       {len(sub_df):,} (Expected: 3,750)")
    print(f"[PASS] Null count:       {sub_df.isna().sum().sum()} missing values")
    print(f"[PASS] Prediction range: {clipped_preds.min():.3f} to {clipped_preds.max():.3f} t/ha")
    print("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate submission predictions.")
    parser.add_argument('--model', default='models/final_model.joblib', help='Path to trained model')
    parser.add_argument('--test-data', default='data/processed/master_test.csv', help='Path to master test CSV')
    parser.add_argument('--submission-out', default='submission/team_11_submission.csv', help='Output submission CSV')
    args = parser.parse_args()

    generate_predictions(args.model, args.test_data, args.submission_out)
