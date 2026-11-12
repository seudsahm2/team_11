# AgriYield Ethiopia: Frontend & Model Integration Guide
**Ethiopian Smallholder Crop-Yield Challenge | Qiyas / IADE Training Program, AAU Hackathon 2026 (Team 11)**

---

## 1. Run it

```bash
pip install -r app/requirements.txt      # pinned; scikit-learn must be 1.9.1 to load the model
streamlit run app/app.py                 # http://localhost:8501
```

The app is self-contained in `app/` (model, lookups and figures are bundled in `app/assets/`), so it can be deployed on its own.

## 2. Architecture

```
data/processed/master_train.csv ─┐
models/final_model.joblib ───────┼─► src/build_app_assets.py ─► app/assets/
                                 │     weather_lookup.csv   (4-month season weather, exactly as trained)
                                 │     rainfall_lookup.csv  (median plot-reported rainfall)
                                 │     price_lookup.csv     (cleaned Birr/quintal, revenue only)
                                 │     plot_profiles.csv    (median plot per region × crop)
                                 │     coop_sample.csv      (15 real unseen 2024 test plots)
                                 │     stress_panel.csv     (200 real plots per region × crop)
                                 │     model_metrics.json   (out-of-fold CV, tiers, ablation, OOT)
                                 │     figures/fig13_…png
                                 ▼
app/predictor.py  ── builds the 20 model features with the same formulas as src/features.py
app/app.py        ── Streamlit UI (4 tabs); every number is computed from the model or the assets
tests/test_app_parity.py ── asserts app features == training features and app == submission
```

**Rebuild after retraining:** `python src/train.py && python src/predict.py && python src/build_app_assets.py && python tests/test_app_parity.py`, then copy `models/final_model.joblib` to `app/assets/`.

## 3. Feature contract (`CropYieldPredictor.build_features`)

| Feature | Source in app | Formula (identical to training) |
| :--- | :--- | :--- |
| region, crop_type, planting_month | user | normalized; months limited to Feb, Mar, Jun, Jul, Aug |
| altitude_m, farm_size_ha, fertilizer_kg_per_ha, improved_seed_used, pest_disease_flag, soil_quality_index, labor_days_per_ha | user | as entered |
| rainfall_mm_season | user override, else median reported by surveyed plots for region/year/month | — |
| weather_season_mean_temp / rainfall_mm / heat_days / temp_anomaly_c | lookup (region, year, month) | planting month + 3 following months |
| fertilizer_improved_seed_interaction | derived | fert × seed |
| weather_rain_discrepancy_ratio | derived | plot rain / (station rain + 1e-5) |
| labor_intensity_per_farm_size | derived | labor / (farm size + 0.1) |
| is_meher_season | derived | month ∈ {Jun, Jul, Aug} |
| altitude_temp_index | derived | altitude / (season temp + 273.15) |

Predictions are clipped to [0.1, 9.0] t/ha, the same bounds as the submission. Revenue = yield × ha × 10 × price. **Market price is never a model input.**

## 4. What each tab computes

| Tab | Content |
| :--- | :--- |
| Farmgate Profit Studio | Yield ± crop-specific CV error, revenue and P&L (cost assumptions editable), auto-looked-up weather and price strip, model-estimated seed and pest effects for this plot, fertilizer profit curve (17 model predictions) |
| Cooperative Command Hub | 15 real unseen survey plots or an uploaded CSV (validated, template downloadable); totals, bags, trucks, revenue, input-credit ratio; downloadable forecasts |
| Climate Stress Radar | Heatwave (+2.25 °C, +5 heat days) or drought (−35% rain): the model re-run on 200 real plots for the region × crop. Fertilizer price shock (+50% cost) |
| System Audit | Out-of-fold metrics, tier confusion matrix, error by crop and region, out-of-time result, figure gallery, live compliance checks |

## 5. Headline metrics (5-fold out-of-fold)

CV RMSE **0.476 t/ha**, MAE 0.348, R² **0.885**; out-of-time 2024 RMSE 0.485; without weather 0.559 (+17.4%); tier accuracy **83.1%**, 6 extreme errors of 15,090.
