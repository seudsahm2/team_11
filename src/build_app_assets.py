"""
Module: build_app_assets.py
Description: Regenerates every data asset the Streamlit app displays, directly from the
             cleaned master tables and the serialized production model. Nothing shown in the
             app is typed in by hand: lookups, benchmarks and evaluation metrics all come from here.
Team: Team 11 | Ethiopian Smallholder Crop-Yield Challenge (Qiyas / AAU IADE 2026)

Usage (from repo root):
    python src/build_app_assets.py

Outputs (app/assets/):
    weather_lookup.csv   - growing-season weather features per region x year x planting month
                           (identical to the values the model was trained on)
    price_lookup.csv     - cleaned market price (Birr/quintal) per crop x region x year
    plot_profiles.csv    - median plot-level inputs per region x crop (UI defaults)
    rainfall_lookup.csv  - median self-reported plot rainfall per region x year x planting month
    coop_sample.csv      - 15 real leaderboard-test survey plots used as the cooperative demo portfolio
    stress_panel.csv     - up to 200 real training plots per region x crop for the climate stress radar
    figures/fig13_yield_tier_confusion_matrix.png (+ copy in app/assets/figures/)
    model_metrics.json   - honest 5-fold out-of-fold metrics, tier confusion matrix, per-slice errors
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_val_predict

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app" / "assets"
TRAIN = ROOT / "data" / "processed" / "master_train.csv"
TEST = ROOT / "data" / "processed" / "master_test.csv"
MODEL = ROOT / "models" / "final_model.joblib"
SUBMISSION = ROOT / "submission" / "team_11_submission.csv"

WEATHER_COLS = [
    "weather_season_mean_temp",
    "weather_season_rainfall_mm",
    "weather_season_heat_days",
    "weather_temp_anomaly_c",
]
TIER_EDGES = (2.0, 3.5)  # t/ha: Subsistence < 2.0 <= Standard <= 3.5 < Commercial
TIER_LABELS = ["Subsistence (<2.0)", "Standard (2.0–3.5)", "Commercial (>3.5)"]


def to_tier(y: np.ndarray) -> np.ndarray:
    return np.digitize(y, TIER_EDGES, right=False)


def render_fig13(cm: np.ndarray, tiers: dict) -> None:
    """Figure 13: food-security tier confusion matrix from 5-fold out-of-fold predictions."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    row_pct = cm / cm.sum(axis=1, keepdims=True) * 100
    fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=200)
    im = ax.imshow(row_pct, cmap="Greens", vmin=0, vmax=100)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{cm[i, j]:,}\n({row_pct[i, j]:.1f}%)", ha="center", va="center",
                    fontsize=11, color="white" if row_pct[i, j] > 55 else "#0f172a", fontweight="bold")
    ax.set_xticks(range(3), TIER_LABELS, fontsize=9)
    ax.set_yticks(range(3), TIER_LABELS, fontsize=9)
    ax.set_xlabel("Predicted tier (out-of-fold)", fontsize=10)
    ax.set_ylabel("Actual tier", fontsize=10)
    ax.set_title(
        f"Yield Tier Confusion Matrix — 5-fold out-of-fold, {int(cm.sum()):,} plots\n"
        f"Accuracy {tiers['accuracy']:.1%} · Subsistence precision {tiers['subsistence_precision']:.1%} · "
        f"Extreme errors {tiers['extreme_errors']} ({tiers['extreme_errors'] / cm.sum():.2%})",
        fontsize=10.5,
    )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Row %")
    fig.tight_layout()
    for out in (ROOT / "figures", ASSETS / "figures"):
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / "fig13_yield_tier_confusion_matrix.png", dpi=200)
    plt.close(fig)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    train = pd.read_csv(TRAIN)
    test = pd.read_csv(TEST)
    model = joblib.load(MODEL)
    features = list(model.feature_names_in_)

    assert "price_birr_per_quintal" not in features, "Market price must never be a model input."
    assert any(f.startswith("weather_") for f in features), "Rule 5: model must use a weather feature."

    # 1. Weather lookup: exactly the per-(region, year, month) values seen in training
    weather = (
        train.groupby(["region", "survey_year", "planting_month"])[WEATHER_COLS + ["weather_months_available"]]
        .first()
        .reset_index()
    )
    weather.to_csv(ASSETS / "weather_lookup.csv", index=False)

    # 2. Price lookup: cleaned prices joined during Deliverable A
    prices = (
        train.groupby(["crop_type", "region", "survey_year"])["price_birr_per_quintal"]
        .first()
        .reset_index()
        .rename(columns={"survey_year": "year"})
    )
    assert len(prices) == 100, f"Expected 5 crops x 5 regions x 4 years = 100 prices, got {len(prices)}"
    prices.to_csv(ASSETS / "price_lookup.csv", index=False)

    # 3. Typical plot profile per region x crop (used as neutral UI defaults)
    profiles = (
        train.groupby(["region", "crop_type"])
        .agg(
            altitude_m=("altitude_m", "median"),
            farm_size_ha=("farm_size_ha", "median"),
            fertilizer_kg_per_ha=("fertilizer_kg_per_ha", "median"),
            labor_days_per_ha=("labor_days_per_ha", "median"),
            soil_quality_index=("soil_quality_index", "median"),
            improved_seed_rate=("improved_seed_used", "mean"),
            pest_rate=("pest_disease_flag", "mean"),
            mean_yield=("yield_tons_per_ha", "mean"),
            n_plots=("plot_id", "count"),
        )
        .reset_index()
        .round(3)
    )
    profiles.to_csv(ASSETS / "plot_profiles.csv", index=False)

    # 4. Typical self-reported plot rainfall (model input that farmers report at survey time)
    rain = (
        train.groupby(["region", "survey_year", "planting_month"])["rainfall_mm_season"]
        .median()
        .round(1)
        .reset_index()
    )
    rain.to_csv(ASSETS / "rainfall_lookup.csv", index=False)

    # 5. Cooperative demo portfolio: 15 real (unlabelled) leaderboard-test plots, 3 per region
    raw_cols = [
        "plot_id", "region", "crop_type", "survey_year", "planting_month", "altitude_m",
        "rainfall_mm_season", "farm_size_ha", "fertilizer_kg_per_ha", "improved_seed_used",
        "pest_disease_flag", "soil_quality_index", "labor_days_per_ha", "distance_to_market_km",
    ]
    latest = test[test["survey_year"] == test["survey_year"].max()]
    coop = latest.groupby("region").sample(n=3, random_state=42)[raw_cols].round(2)
    coop.to_csv(ASSETS / "coop_sample.csv", index=False)

    # 5b. Stress-test panel: up to 200 real surveyed plots per region x crop (inputs only, no target)
    panel_cols = [c for c in raw_cols if c not in ("plot_id", "distance_to_market_km")]
    panel = (
        train.groupby(["region", "crop_type"])
        .sample(frac=1.0, random_state=42)
        .groupby(["region", "crop_type"])
        .head(200)[panel_cols]
        .round(3)
    )
    panel.to_csv(ASSETS / "stress_panel.csv", index=False)

    # 6. Honest evaluation: 5-fold out-of-fold predictions with the shipped configuration
    X, y = train[features], train["yield_tons_per_ha"].values
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = cross_val_predict(clone(model), X, y, cv=kf)
    fold_rmse = [
        float(root_mean_squared_error(y[va], oof[va])) for _, va in kf.split(X)
    ]
    baseline_rmse = float(root_mean_squared_error(y, np.full_like(y, y.mean())))

    # Weather ablation with the same configuration (Rule 5 evidence)
    non_weather = [f for f in features if not (
        f.startswith("weather_") or f in ("altitude_temp_index",)
    )]
    ablate = clone(model)
    prep = ablate.named_steps["prep"]
    prep.transformers = [
        (name, tr, [c for c in cols if c in non_weather]) for name, tr, cols in prep.transformers
    ]
    oof_nw = cross_val_predict(ablate, train[non_weather], y, cv=kf)

    # Out-of-time check: train on 2021-2023, evaluate on 2024
    is_last = (train["survey_year"] == train["survey_year"].max()).values
    oot_model = clone(model).fit(X[~is_last], y[~is_last])
    oot_pred = oot_model.predict(X[is_last])
    oot = {
        "train_years": sorted(int(v) for v in train.loc[~is_last, "survey_year"].unique()),
        "test_year": int(train["survey_year"].max()),
        "n_train": int((~is_last).sum()),
        "n_test": int(is_last.sum()),
        "rmse": round(float(root_mean_squared_error(y[is_last], oot_pred)), 4),
        "r2": round(float(r2_score(y[is_last], oot_pred)), 4),
    }

    true_t, pred_t = to_tier(y), to_tier(oof)
    cm = np.zeros((3, 3), dtype=int)
    for a, p in zip(true_t, pred_t):
        cm[a, p] += 1

    def slice_errors(col):
        out = {}
        for k, idx in train.groupby(col).indices.items():
            out[str(k)] = {
                "rmse": round(float(root_mean_squared_error(y[idx], oof[idx])), 3),
                "mae": round(float(mean_absolute_error(y[idx], oof[idx])), 3),
                "mean_yield": round(float(y[idx].mean()), 3),
                "n": int(len(idx)),
            }
        return out

    # Average model-estimated effects across all real training plots (used in advice cards)
    def avg_effect(col, a, b):
        Xa, Xb = X.copy(), X.copy()
        Xa[col], Xb[col] = a, b
        for frame in (Xa, Xb):
            frame["fertilizer_improved_seed_interaction"] = frame["fertilizer_kg_per_ha"] * frame["improved_seed_used"]
        pa, pb = model.predict(Xa), model.predict(Xb)
        return float(((pb - pa) / np.maximum(pa, 0.1)).mean())

    sub = pd.read_csv(SUBMISSION)
    sub_pred_col = [c for c in sub.columns if c != "plot_id"][0]
    model_test = model.predict(test[features])

    metrics = {
        "model_family": type(model.named_steps["model"]).__name__,
        "n_train_plots": int(len(train)),
        "n_test_plots": int(len(test)),
        "n_features": len(features),
        "weather_features": [f for f in features if f.startswith("weather_") or f == "altitude_temp_index"],
        "cv": {
            "folds": 5,
            "rmse": round(float(root_mean_squared_error(y, oof)), 4),
            "mae": round(float(mean_absolute_error(y, oof)), 4),
            "r2": round(float(r2_score(y, oof)), 4),
            "fold_rmse": [round(v, 4) for v in fold_rmse],
            "baseline_mean_rmse": round(baseline_rmse, 4),
            "error_reduction_vs_baseline": round(1 - root_mean_squared_error(y, oof) / baseline_rmse, 4),
            "no_weather_rmse": round(float(root_mean_squared_error(y, oof_nw)), 4),
        },
        "out_of_time": oot,
        "tiers": {
            "labels": TIER_LABELS,
            "edges_t_ha": list(TIER_EDGES),
            "confusion_matrix": cm.tolist(),
            "accuracy": round(float(np.trace(cm) / cm.sum()), 4),
            "extreme_errors": int(cm[0, 2] + cm[2, 0]),
            "subsistence_precision": round(float(cm[0, 0] / max(cm[:, 0].sum(), 1)), 4),
            "subsistence_recall": round(float(cm[0, 0] / max(cm[0, :].sum(), 1)), 4),
        },
        "by_crop": slice_errors("crop_type"),
        "by_region": slice_errors("region"),
        "effects": {
            "improved_seed_lift": round(avg_effect("improved_seed_used", 0, 1), 4),
            "pest_loss": round(-avg_effect("pest_disease_flag", 0, 1), 4),
        },
        "submission": {
            "rows": int(len(sub)),
            "nulls": int(sub[sub_pred_col].isna().sum()),
            "prediction_column": sub_pred_col,
            "max_abs_diff_vs_shipped_model": round(float(np.abs(np.clip(model_test, 0.1, 9.0) - sub[sub_pred_col].values).max()), 4),
        },
    }
    (ASSETS / "model_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    render_fig13(cm, metrics["tiers"])

    print(json.dumps({k: metrics[k] for k in ("cv", "out_of_time", "tiers", "effects", "submission")}, indent=2))
    print(f"[PASS] Assets written to {ASSETS}")


if __name__ == "__main__":
    sys.exit(main())
