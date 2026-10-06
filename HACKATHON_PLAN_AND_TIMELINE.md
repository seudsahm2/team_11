# 🚀 Ethiopian Smallholder Crop-Yield Challenge — Team 11
**Qiyas / IADE Training Program — Addis Ababa University AI Hackathon 2026**  
**Working Window:** 04:56 AM – 06:00 PM (13 Hours) | **Goal:** 100/100 Total Points & Top Leaderboard Rank

---

## 📌 Project Quick Summary
- **Challenge:** Predict smallholder crop yield (`yield_tons_per_ha`) across 5 Ethiopian regions (**Oromia, Amhara, SNNPR, Tigray, Somali**) and 5 crops (**teff, wheat, maize, sorghum, barley**).
- **Task Type:** Supervised Tabular Regression (scored on RMSE, secondary MAE and $R^2$).
- **Data Integration:** Survey plots (15,090 train / 3,750 test) + Regional monthly weather (232 rows) + Regional market prices (100 rows).
- **Key Constraints:**
  1. Final model **MUST** use at least 1 feature derived from the weather table.
  2. Imputers, scalers, and encoders must be fitted on **train only** (zero test leakage).
  3. Market price is strictly for revenue calculations and the demo app — **NEVER** an input to the yield prediction model.

---

## 👥 5-Member Team Role Classification & Responsibilities

```
                                ┌────────────────────────────────────────┐
                                │   Member 1: Data Pipeline Lead         │
                                │   (Deliverable A: Cleaning & Joins)    │
                                └───────────────────┬────────────────────┘
                                                    │ Exports master_train.csv
                                                    ▼
            ┌───────────────────────────────────────┼────────────────────────────────────────┐
            │                                       │                                        │
            ▼                                       ▼                                        ▼
┌───────────────────────┐               ┌───────────────────────┐                ┌───────────────────────┐
│ Member 2: EDA &       │               │ Member 4: ML &        │                │ Member 5: App &       │
│ Agronomic Insights    │               │ Evaluation Lead       │                │ Product / QA Lead     │
│ (Deliverable B: 14 Qs)│               │ (Deliverable D + Subm)│                │ (Deliverable E + G)   │
└───────────┬───────────┘               └───────────┬───────────┘                └───────────┬───────────┘
            │                                       │ Serializes final_model.joblib          │
            │ Feeds key charts & metrics            │                                        │
            ▼                                       ▼                                        ▼
┌───────────────────────────────────────────────────┴────────────────────────────────────────┐
│ Member 3: Visualization & Presentation Lead (Deliverable C: 12 Figures + F: 5-Slide Pitch) │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 🧑‍💻 Member 1: Data Engineering & Integration Lead
- **Primary Deliverables:** Deliverable A (14 pts) & Data Assets
- **Notebook/Code:** `notebooks/01_cleaning_and_integration.ipynb`, `src/cleaning.py`, `src/features.py`
- **Responsibilities:**
  - Standardize inconsistent `region` names across all 3 tables (`OROMIA`, `ORO`, `Oromia ` ➔ `Oromia`).
  - Standardize `crop_type` labels and strip whitespace (`' teff '`, `'Tef'` ➔ `'teff'`).
  - Join regional weather using a 3-month growing season window (planting month + 3 following months).
  - Clean `market_prices.csv` (fix unit errors to ensure Birr/quintal).
  - Engineer 6+ features: 3+ weather-derived (season mean temp, heat days, rainfall anomaly), 1+ interaction (fertilizer × seed), 1+ planting month.
  - Implement 5 automated integrity tests (row counts match, no NaNs, valid ranges).
  - Export `master_train.csv`, `master_test.csv`, and `data_dictionary_master.csv` into `data/processed/`.
- **🚨 Hard Deadline:** Handoff clean master tables by **09:00 AM**.

---

### 🧑‍🔬 Member 2: Agronomic EDA & Analytical Insights Lead
- **Primary Deliverables:** Deliverable B (14 pts: 14 Questions)
- **Notebook/Code:** `notebooks/02_analysis_report.ipynb`, `reports/B_analysis_report.md`
- **Responsibilities:**
  - **B1 Value & Prices:** Revenue per ha by crop (B1.1) and price trends 2021–2024 (B1.2).
  - **B2 Categories:** Yield by region (B2.1), yield by crop (B2.2), region × crop pivot (B2.3), improved seed lift (B2.4), pest impact (B2.5).
  - **B3 Agronomic Drivers:** Fertilizer curve & diminishing returns (B3.1), altitude response (B3.2), planting month effect (B3.3), market distance correlation (B3.4).
  - **B4 Time & Weather:** Yield trends (B4.1), temperature anomalies (B4.2), plot vs. station rainfall mismatch (B4.3).
  - Write concise 1–2 sentence interpretations for all 14 findings.
- **🚨 Hard Deadline:** Complete all 14 questions by **01:00 PM**.

---

### 🎨 Member 3: Data Visualization & Presentation Lead
- **Primary Deliverables:** Deliverable C (14 pts: 12 Figures) & Deliverable F (6 pts: 5 Slides)
- **Notebook/Code:** `notebooks/03_visualizations.ipynb`, `figures/*.png`, `figures/figure_captions.md`, `presentation/`
- **Responsibilities:**
  - Produce all 12 publication-grade figures (min 150 DPI) in `figures/`:
    - `fig01_missingness.png`: Missingness & sentinels across raw tables.
    - `fig02_before_after_cleaning.png`: Before/after distributions of cleaned features.
    - `fig03_yield_distribution.png`: Overall & per-crop yield distribution.
    - `fig04_region_crop_heatmap.png`: Mean yield heatmap by region × crop.
    - `fig05_correlation_heatmap.png`: Correlation matrix of plot & weather features.
    - `fig06_climate_by_region.png`: Monthly climate curves with shaded growing season.
    - `fig07_yield_vs_season_temp.png`: Yield vs. season temp per crop.
    - `fig08_price_trends.png`: Price per quintal 2021–2024 by crop.
    - `fig09_revenue_by_crop_region.png`: Revenue/ha by crop & region.
    - `fig10_model_comparison.png`: Validation RMSE comparison with baseline marker.
    - `fig11_predicted_vs_actual_residuals.png`: Predicted vs. Actual ($y=x$) + Residuals.
    - `fig12_feature_importance.png`: Top 10+ permutation importances (highlighting weather).
  - Write `figures/figure_captions.md` with explicit takeaways.
  - Build the **5-Slide Presentation Deck** (`presentation/team_11_slides.pptx`):
    - Slide 1: Problem & Data Overview
    - Slide 2: Cleaning & Integration Map
    - Slide 3: Agronomic Insights (from B/C)
    - Slide 4: Modeling, Cross-Validation & Weather Ablation
    - Slide 5: Error Analysis, Demo Overview & Recommendations
- **🚨 Hard Deadline:** Figures complete by **03:30 PM**, Slides complete by **04:30 PM**.

---

### 🤖 Member 4: Machine Learning & Evaluation Lead
- **Primary Deliverables:** Deliverable D (14 pts) & Leaderboard Prediction (20 pts)
- **Notebook/Code:** `notebooks/04_modeling_and_evaluation.ipynb`, `models/`, `submission/`
- **Responsibilities:**
  - Train baselines: DummyRegressor (mean) and Ridge Regression (D1).
  - Train candidate models: Random Forest, LightGBM, XGBoost, CatBoost (D2).
  - Run 5-fold cross-validation on the top models (D3).
  - Perform out-of-time evaluation: train on 2021–2023, validate on 2024 (D4).
  - Execute **Weather Ablation Study**: evaluate model with vs. without weather features (D5).
  - Hyperparameter tuning using Optuna / RandomizedSearchCV (D6).
  - Error & residual diagnostics by crop, region, and continuous extremes (D7, D8).
  - Compute farmer cooperative plain-language impact metrics (D9).
  - Export `submission/team_11_submission.csv` (validate exact 3,750 rows, no NaNs).
  - Save `models/final_model.joblib`.
- **🚨 Hard Deadline:** Best model locked by **01:30 PM**, Submission CSV verified by **04:30 PM**.

---

### 💻 Member 5: Deployment, Product & QA Lead
- **Primary Deliverables:** Deliverable E (8 pts: Streamlit Demo), Deliverable G (5 pts: Repo QA), Stretch Goal (5 pts)
- **Notebook/Code:** `app/app.py`, `app/assets/`, `app/requirements.txt`, repo sanity checks
- **Responsibilities:**
  - Build interactive Streamlit demo (`app/app.py`):
    - Input controls: Region, crop, year, planting month, and plot agronomic inputs.
    - Automated background lookup for weather features and market prices (user never inputs weather or price).
    - Output: Predicted yield (tons/ha) and Gross Revenue in Ethiopian Birr (`yield × size × 10 × price`).
    - Visual: What-if sensitivity curve (e.g., fertilizer response) or regional benchmark.
  - Bundle lookup tables into `app/assets/`.
  - Connect `models/final_model.joblib` into the Streamlit app.
  - Implement optional Stretch Goal (e.g. interactive multi-filter dashboard or regional equity memo).
  - Run pre-submission audit checklist: verify relative paths, no hardcoded local paths, test runs clean.
- **🚨 Hard Deadline:** Working app by **03:30 PM**, Full QA audit by **05:00 PM**.

---

## ⏰ Master Hour-by-Hour Timeline (04:56 AM – 06:00 PM)

| Time Window | Milestone / Focus | Member 1 (Data) | Member 2 (EDA) | Member 3 (Viz & Pitch) | Member 4 (ML) | Member 5 (App & QA) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **04:56 – 06:30** | **Phase 1: Setup & Data Profiling** | Profile raw data; identify spelling & unit issues | Review business questions B1–B4 | Set up plotting style & color palette | Set up ML pipeline skeleton & CV splits | Scaffold Streamlit app UI layout |
| **06:30 – 09:00** | **Phase 2: Cleaning & Integration** | Clean tables, formulate weather join, write assertions | Assist with EDA on price & crops | Draft figures fig01 & fig02 | Test baseline regressors | Finalize app input form & layout |
| **09:00 SHARP** | **🚨 MILESTONE 1: MASTER TABLES HANDOFF** | **Export `master_train.csv` and `master_test.csv` to `data/processed/`** | | | | |
| **09:00 – 11:30** | **Phase 3: Parallel Core Sprint** | Write Cleaning Log & Data Dictionary (A1–A8) | Solve Tasks B1.1 to B2.5 | Render figures fig03, fig04, fig05 | Train Random Forest & LightGBM/XGBoost | Build weather/price lookup functions |
| **11:30 – 01:00** | **Phase 4: Advanced ML & Analysis** | Verify schema & write Deliverable A report | Solve Tasks B3.1 to B4.3 | Render figures fig06, fig07, fig08 | Run 5-fold CV & Weather Ablation (D5) | Connect lookup logic into Streamlit app |
| **01:00 – 02:00** | **Phase 5: Midday Standup & Sync** | **TEAM SYNC: Select winning model; Member 4 exports `final_model.joblib` to Member 5; Lunch break** | | | | |
| **02:00 – 03:30** | **Phase 6: Visuals & App Binding** | Review documentation & join proofs | Finalize Deliverable B write-up | Render figures fig09 to fig12; write captions | Error analysis (D7–D8) & cooperative metric (D9) | Connect model into app; build what-if chart |
| **03:30 – 04:30** | **Phase 7: Pitch Deck & Submission** | Assist with presentation deck | Assist with presentation deck | Build 5 presentation slides (`team_11_slides.pptx`) | **Generate `team_11_submission.csv` & verify format** | Package `app/assets/` & test app locally |
| **04:30 – 05:30** | **Phase 8: Full Dry Run & Audit** | Run fresh environment execution checks | Review slide notes | Rehearse 5-min presentation | Double check submission file integrity | Full checklist QA run & live demo test |
| **05:30 – 06:00** | **Phase 9: Final Commit & Submission** | **GIT COMMIT, PUSH TO REPO, AND OFFICIAL HAND-IN BEFORE 06:00 PM** | | | | |

---

## 🏆 Deliverables & Grading Rubric (100 Points Total)

| Deliverable | Points | Key Scoring Requirement | Owner |
| :--- | :---: | :--- | :--- |
| **Leaderboard Prediction** | **20** | Valid CSV with 3,750 rows scored against hidden test labels | Member 4 |
| **A: Data Pipeline** | **14** | Clean log, join map, 3-plot proof, 6+ features, 5 assertions, master CSVs | Member 1 |
| **B: Analysis Report** | **14** | All 14 numbered tasks answered with data + 1–2 sentence takeaway | Member 2 |
| **C: Visualization Pack** | **14** | 12 PNG figures (min 150 DPI) + `figure_captions.md` | Member 3 |
| **D: Modeling & Evaluation** | **14** | Baselines, model table, CV, time split, weather ablation, error analysis | Member 4 |
| **E: Deployed Demo App** | **8** | Working Streamlit app with auto-lookup & revenue calculation | Member 5 |
| **F: 5-Slide Presentation** | **6** | 5 slides, 5 min presentation + 2 min Q&A with live demo | Member 3 |
| **G: Structure & Hygiene** | **5** | Correct folder layout, relative paths, clean README, pinned requirements | Member 5 |
| **Bonus: Stretch Goal** | **5** | Interactive multi-filter dashboard or regional equity memo | Member 5 |
| **TOTAL** | **100** | | |

---

## 📋 Pre-Submission Checklist (Run at 04:30 PM)

- [ ] `submission/team_11_submission.csv` exists, exactly 3,750 rows, no missing values.
- [ ] All 12 figures (`fig01_missingness.png` through `fig12_feature_importance.png`) exist in `figures/`.
- [ ] `figures/figure_captions.md` contains 12 clear, descriptive takeaways.
- [ ] `data/processed/` contains `master_train.csv`, `master_test.csv`, and `data_dictionary_master.csv`.
- [ ] All 4 notebooks run top-to-bottom without errors.
- [ ] Model uses at least 1 weather feature (Rule 5 compliance).
- [ ] Zero test leakage: test data was never used in fitting (Rule 6 compliance).
- [ ] Market price is not an input feature to the yield model.
- [ ] Streamlit demo launches locally with `streamlit run app/app.py`.
- [ ] Presentation slides are placed in `presentation/team_11_slides.pptx`.

---

## 📱 Quick Copy-Paste Message for Telegram / Social Media

*(Copy and send this directly to your team group)*

```text
🚨 TEAM 11 — HACKATHON BATTLE PLAN (04:56 AM – 06:00 PM) 🚨

Hey team! Our workspace is set up and datasets are staged in data/raw/.
Here is our official role division and schedule:

👥 ROLES:
• Member 1 (Data Lead): Cleaning, Weather Joins, Feature Engineering, Master Tables (Deliverable A)
• Member 2 (EDA Lead): 14 Business & Agronomic Questions (Deliverable B)
• Member 3 (Viz & Deck Lead): 12 Figures Pack + 5-Slide Deck (Deliverables C & F)
• Member 4 (ML Lead): Model Benchmarking, CV, Weather Ablation, Leaderboard Submission (Deliverable D)
• Member 5 (App & QA Lead): Streamlit Demo App + Revenue Lookup + Repo QA (Deliverables E & G)

⏰ KEY MILESTONES:
• 09:00 AM SHARP: Member 1 delivers master_train.csv & master_test.csv
• 01:00 PM: Member 2 finishes all 14 EDA questions
• 01:30 PM: Midday Sync — select winning model, Member 4 exports final_model.joblib
• 03:30 PM: 12 Figures complete + Streamlit demo integrated
• 04:30 PM: 5-Slide Deck ready + Submission CSV verified (3,750 rows)
• 04:30 – 05:30 PM: Rehearsal, full dry run & QA check
• 05:30 – 06:00 PM: Git push & official submission

⚠️ CRITICAL RULES:
1. Model MUST use at least 1 weather feature!
2. Zero leakage: fit only on train!
3. NEVER use market price as a feature in the yield model (price is for revenue calculation only)!

Let's crush this! 🔥
```
