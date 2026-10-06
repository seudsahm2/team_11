"""
Module: train.py
Description: Production model training, 5-fold cross-validation, and serialization.
Team: Team 11 | Ethiopian Smallholder Crop-Yield Challenge (Qiyas / AAU IADE 2026)
"""

import os
import sys
import time
import argparse
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor

CATEGORICAL_FEATURES = ['region', 'crop_type', 'planting_month']

NUMERIC_FEATURES = [
    'altitude_m',
    'rainfall_mm_season',
    'farm_size_ha',
    'fertilizer_kg_per_ha',
    'improved_seed_used',
    'pest_disease_flag',
    'soil_quality_index',
    'labor_days_per_ha',
    'weather_season_mean_temp',
    'weather_season_rainfall_mm',
    'weather_season_heat_days',
    'weather_temp_anomaly_c',
    'fertilizer_improved_seed_interaction',
    'weather_rain_discrepancy_ratio',
    'labor_intensity_per_farm_size',
    'is_meher_season',
    'altitude_temp_index'
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET = 'yield_tons_per_ha'


def build_pipeline():
    """Builds a leakage-free Scikit-Learn preprocessing and modeling pipeline."""
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUMERIC_FEATURES),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), CATEGORICAL_FEATURES)
        ]
    )

    model = HistGradientBoostingRegressor(
        max_iter=120,
        max_depth=9,
        learning_rate=0.08,
        min_samples_leaf=20,
        l2_regularization=0.1,
        random_state=42
    )

    return Pipeline([
        ('prep', preprocessor),
        ('model', model)
    ])


def train_and_evaluate(train_path: str = 'data/processed/master_train.csv',
                       model_out: str = 'models/final_model.joblib',
                       cv_folds: int = 5):
    """Trains the champion pipeline on master training data and serializes the artifact."""
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Training dataset not found at: {train_path}")

    print(f"[1/4] Ingesting training dataset from {train_path}...")
    df = pd.read_csv(train_path)
    X = df[ALL_FEATURES]
    y = df[TARGET]
    print(f"      Rows: {len(df):,} | Features: {len(ALL_FEATURES)} | Target: {TARGET}")

    pipeline = build_pipeline()

    print(f"[2/4] Running {cv_folds}-Fold Cross-Validation...")
    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
    scores = -cross_val_score(pipeline, X, y, cv=kf, scoring='neg_root_mean_squared_error')
    print(f"      CV RMSE Scores: {[round(s, 4) for s in scores]}")
    print(f"      Mean CV RMSE:   {scores.mean():.4f} t/ha (±{scores.std():.4f})")

    print(f"[3/4] Fitting final pipeline on all {len(df):,} observations...")
    t0 = time.time()
    pipeline.fit(X, y)
    print(f"      Training completed in {time.time() - t0:.2f} seconds.")

    print(f"[4/4] Serializing model artifact to {model_out}...")
    os.makedirs(os.path.dirname(model_out), exist_ok=True)
    joblib.dump(pipeline, model_out)
    print(f"[PASS] Final model successfully exported: {model_out} ({os.path.getsize(model_out) / 1024:.1f} KB)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train production crop-yield model.")
    parser.add_argument('--train-data', default='data/processed/master_train.csv', help='Path to master train CSV')
    parser.add_argument('--output-model', default='models/final_model.joblib', help='Path to output model joblib')
    parser.add_argument('--cv-folds', type=int, default=5, help='Number of CV folds')
    args = parser.parse_args()

    train_and_evaluate(args.train_data, args.output_model, args.cv_folds)
