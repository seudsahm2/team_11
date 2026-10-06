# AgriYield Ethiopia — Frontend Architecture & Team Integration Guide
**Ethiopian Smallholder Crop-Yield Challenge | Qiyas / IADE Training Program — AAU Hackathon 2026 (Team 11)**

---

## 📌 Executive Summary for Teammates & AI Agents

This repository contains the complete end-to-end codebase for **Team 11** in the Ethiopian Smallholder Crop-Yield Challenge. 
The web application in `app/` is built as an **isolated, production-ready decision-support system** (satisfying **Deliverable E (5 pts)** and the **Interactive Decision-Support Stretch Goal (+5 bonus pts)**).

If you are a teammate, a developer on another PC, or an **AI Assistant** continuing work on this repository:
1. **The frontend lives entirely inside [`app/`](file:///f:/HHHHHHHHHHHHHHHHHHHHackaton/team_11/app) and [`.streamlit/`](file:///f:/HHHHHHHHHHHHHHHHHHHHackaton/team_11/.streamlit).**
2. **The model adapter [`app/predictor.py`](file:///f:/HHHHHHHHHHHHHHHHHHHHackaton/team_11/app/predictor.py) has dual-mode auto-detection:**
   - If `models/final_model.joblib` exists: it **automatically loads the real production ML model** and predicts with it.
   - If `models/final_model.joblib` is absent: it falls back to a calibrated agronomic heuristic simulation.
3. **Competition Rules Enforced:**
   - **Rule 5 Compliance (Strict):** Users **never** manually input weather (rainfall, temperature, heat days). Weather is looked up silently in the background based on `region`, `survey_year`, and `planting_month` (covering the 3-month growing season).
   - **No Data Leakage:** Market commodity prices are **never** fed as an input feature into the yield prediction model. Prices are strictly used downstream to calculate gross farmer revenue in Ethiopian Birr (`ETB`).

---

## 🚀 How to Run the Application on Any Machine

### 1. Requirements
Ensure you have the Python environment with required libraries:
```bash
pip install -r app/requirements.txt
```
*(Dependencies: `streamlit`, `pandas`, `numpy`, `scikit-learn`, `joblib`, `plotly`)*

### 2. Launching the App
From the repository root (`team_11/`):
```bash
streamlit run app/app.py
```
Open your browser at `http://localhost:8501`.

---

## 🏗️ What Has Been Implemented (Complete Inventory)

### 1. Visual Aesthetics & Design System
* **Light Theme Foundation:** Configured in [`.streamlit/config.toml`](file:///f:/HHHHHHHHHHHHHHHHHHHHackaton/team_11/.streamlit/config.toml) (`#faf9f5` warm linen canvas, `#143d2b` deep forest green, `#15803d` vibrant emerald, and `#0369a1` sky blue accents).
* **0-Top Flush Hero Landscape Banner:** Full-bleed panoramic header background (`assets/hero_bg.jpg`) with 0px top margin/padding flush to the viewport edge.
* **Frosted-Glass Floating Navbar:** Shows project branding and live indicator badge (`● Production ML Pipeline Active` or `● Smart Agronomic Engine (Autonomous Mode)`).
* **Live Plot Telemetry Glass Card:** Hero telemetry showing automated Soil Health Index, Auto-Synchronized Weather status, Regional Price Reference, and 88% Model Confidence Index.
* **Evernest Quick-Filter Pill Bar:** Floating horizontal preset bar (`📍 Location | 🌾 Crop | 📅 Season | 🧪 Input Scale → Quick Forecast`).
* **"WHAT WE OFFER" 4-Card Grid:** Crop Management, Weather Integration, Fertilizer & Soil Care, Market Insights.
* **Dark Forest Green Stats Ribbon:** Clean vector SVG icon badges representing the competition training dataset (`15,090+ Plots`, `5 Regions`, `+28.5% Seed Lift`, `5 Crops`).

### 2. Tab 1: Interactive Yield & Revenue Forecast (Core Engine)
* **12-Feature Plot Input Form:**
  - `region`: Oromia, Amhara, SNNPR, Tigray, Somali
  - `crop_type`: Teff, Wheat, Maize, Sorghum, Barley
  - `survey_year`: 2021–2024
  - `planting_month`: May through April (defaults to June *Meher*)
  - `farm_size_ha`: 0.1 to 8.0 ha (default: 1.5 ha)
  - `altitude_m`: 400 to 3,600 m
  - `fertilizer_kg_per_ha`: 0 to 250 kg/ha
  - `improved_seed_used`: Yes (1) / No (0)
  - `pest_disease_flag`: No (0) / Yes (1)
  - `soil_quality_index`: 0.0 to 1.0 (default: 0.65)
  - `labor_days_per_ha`: 5 to 150 days
  - `distance_to_market_km`: 0.5 to 60.0 km
* **Automated Context Retrieval Callout:** Displays the looked-up 3-month growing season mean temperature (°C), cumulative rainfall (mm), extreme heat days, and regional market price (ETB/quintal).
* **Economic KPI Output Cards:**
  1. **Predicted Harvest Yield:** Tons per hectare (`t/ha`), total metric tons, and quintals (`1 ton = 10 quintals`).
  2. **Estimated Gross Revenue:** Total gross earnings in Ethiopian Birr (`ETB`) and per-hectare earnings.
  3. **Regional Benchmark Comparison:** Compares plot performance against the historical regional average for that specific crop (e.g., `+67.1% vs Oromia average`).
* **What-If Simulator (Fertilizer Diminishing Returns Curve):**
  - Interactive dual-axis Plotly curve testing 25 simulation points from 0 to 200 kg/ha.
  - Green curve: Predicted Yield (`t/ha`).
  - Blue dotted curve: Projected Gross Revenue (`ETB`).
  - Orange star: Farmer's current plot setting.
  - Demonstrates the economic plateau where marginal fertilizer costs exceed marginal grain revenue.

### 3. Tab 2: Regional Market & Climate Explorer (Stretch Goal — 5 pts)
* **Commodity Price Hierarchy:** Plotly bar chart comparing prices across the 5 crops (highlighting Teff at 8,700+ Birr/quintal vs Maize at 3,450 Birr/quintal).
* **Regional Climate & Rainfall Regimes:** Plotly chart displaying distinct rainfall gradients across Oromia, Amhara, SNNPR, Tigray, and Somali.
* **Regional Price Volatility:** Compares commodity pricing variations by geographic region.

### 4. Tab 3: Field Handbook & Rubric Guide
* Detailed operational guidelines for extension agents: Ethiopian agro-ecological zones (*Dega, Weina Dega, Kolla, Berha*), seasonal calendars (*Meher* vs *Belg*), and fertilizer thresholds.
* Live scorecard audit table showing point distribution across Deliverables A through G (100 total points).

### 5. Agro-Ecological Belt Showcase & Signature Banner
* 3 benchmark preset cards:
  - *Oromia Central Teff Belt (Ada'a & Bishoftu)* — Best Cash Return (8,707 ETB/quintal)
  - *Gojjam Wheat & Barley Belt (Amhara)* — High Caloric Output (3.40 t/ha)
  - *Rift Valley Maize Corridor (SNNPR)* — High Tonnage Grain (4.20 t/ha)
* Team accreditation footer for AAU Hackathon 2026, Team 11.

---

## 🔌 Integration Contract: How the Frontend Connects to the ML Model

The bridge between the user interface and the ML model is **[`app/predictor.py`](file:///f:/HHHHHHHHHHHHHHHHHHHHackaton/team_11/app/predictor.py)**.

### Model Location:
```
models/final_model.joblib
```

### Feature Dictionary Passed to `model.predict(df)`:
When `models/final_model.joblib` is loaded, `app/predictor.py` constructs a single-row `pandas.DataFrame` with the following columns:
```python
feat_dict = {
    "region": [region],                                      # str: 'Oromia', 'Amhara', etc.
    "crop_type": [crop_type],                                # str: 'teff', 'wheat', etc.
    "planting_month": [month],                               # str: 'Jun', 'Jul', etc.
    "altitude_m": [altitude_m],                              # float
    "rainfall_mm_season": [rainfall_mm],                     # float (looked up or plot)
    "farm_size_ha": [farm_size_ha],                          # float
    "fertilizer_kg_per_ha": [fertilizer_kg],                  # float
    "improved_seed_used": [improved_seed_flag],              # int: 0 or 1
    "pest_disease_flag": [pest_flag],                        # int: 0 or 1
    "soil_quality_index": [soil_quality],                    # float: 0.0 to 1.0
    "labor_days_per_ha": [labor_days],                       # float
    "weather_season_mean_temp": [avg_temp_c],                # float (from weather lookup)
    "weather_season_rainfall_mm": [rainfall_mm_season],      # float (from weather lookup)
    "weather_season_heat_days": [heat_days],                 # float (from weather lookup)
    "weather_temp_anomaly_c": [temp_anomaly],                # float
    "fertilizer_improved_seed_interaction": [fert * seed],   # float
    "weather_rain_discrepancy_ratio": [ratio],               # float
    "labor_intensity_per_farm_size": [intensity],            # float
    "is_meher_season": [1 or 0],                             # int
    "altitude_temp_index": [alt_temp_idx]                    # float
}
```
**Status:** Tested and verified live. When `models/final_model.joblib` was merged into `master`, `app/predictor.py` immediately detected it, reported `Production model active: True`, and generated live predictions.

---

## 📊 Complete Competition Scorecard & Deliverables Status

| Deliverable | Description | Points | Location in Repo | Status |
| :--- | :--- | :---: | :--- | :---: |
| **A** | **Data Cleaning & Integration Pipeline** | 14 pts | `src/cleaning.py`, `notebooks/01_cleaning_and_integration.ipynb`, `data/processed/` | **COMPLETE** ✅ |
| **B** | **Agronomic EDA & Analysis Report** | 14 pts | `notebooks/02_analysis_report.ipynb`, `reports/B_analysis_report.md` | **COMPLETE** ✅ |
| **C** | **Visualization Pack (12 Figures)** | 14 pts | `figures/fig01` to `fig12`, `figures/figure_captions.md`, `notebooks/03_visualizations.ipynb` | **COMPLETE** ✅ |
| **D** | **ML Modeling, Weather Ablation & Leaderboard** | 34 pts | `models/final_model.joblib`, `reports/D_model_evaluation.md`, `submission/team_11_submission.csv` | **COMPLETE** ✅ |
| **E** | **Decision Support Application (Frontend)** | 5 pts | `app/app.py`, `app/predictor.py`, `app/assets/` | **COMPLETE** ✅ |
| **Stretch** | **Interactive Climate & Market Explorer** | +5 pts | `app/app.py` (Tab 2) | **COMPLETE** ✅ |
| **F** | **Pitch Deck Presentation** | 8 pts | `presentation/team_11_slides.pptx` | **NEXT STEP** ⏳ |
| **G** | **Final Audit & Pre-Submission Checklist** | 3 pts | `README.md`, repository cleanup | **NEXT STEP** ⏳ |

---

## 🎯 Next Steps for the Team

1. **Deliverable F (Pitch Deck Presentation — 8 pts):**
   - Create a clean 5-slide PowerPoint deck in `presentation/team_11_slides.pptx`:
     - **Slide 1:** Problem, Context & Team 11 Mission.
     - **Slide 2:** Data Engineering, Cleaning & Rule 5 Weather Integration (Deliverable A).
     - **Slide 3:** Key Agronomic Findings & Economic Insights (Deliverable B).
     - **Slide 4:** Modeling Benchmarks, Weather Ablation & Leaderboard Submission (Deliverable D).
     - **Slide 5:** AgriYield Live Decision Support Demo & Smallholder Impact (Deliverable E + Stretch).
2. **Deliverable G (Final Code Quality Audit — 3 pts):**
   - Verify `git status` is clean.
   - Run submission file format validation (`submission/team_11_submission.csv` has exactly 3,750 rows and columns `plot_id`, `yield_tons_per_ha`).
   - Confirm all paths use relative references.
