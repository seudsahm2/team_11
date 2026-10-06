# Deliverable A — Data Cleaning & Integration Pipeline Report
**Team:** Team 11  
**Competition:** Ethiopian Smallholder Crop-Yield Challenge  
**Program:** Qiyas / IADE Training Program — Addis Ababa University AI Hackathon 2026  

---

## Executive Summary
This document provides the formal audit and methodology report for **Deliverable A (Data Cleaning & Integration Pipeline)**. Our primary objective is to transform three real-world, uncurated raw datasets (`crop_yield_train.csv`, `regional_weather.csv`, and `market_prices.csv`) along with the test evaluation file (`crop_yield_leaderboard_test.csv`) into clean, verified, leakage-free master tables:
1. `data/processed/master_train.csv` (15,090 plots × 26 columns)
2. `data/processed/master_test.csv` (3,750 plots × 25 columns)
3. `data/processed/data_dictionary_master.csv` (26 documented columns)

All cleaning, transformations, and joining operations are fully automated in reproducible code ([notebooks/01_cleaning_and_integration.ipynb](file:///c:/Users/hp/Downloads/Projects/Hackaton/team_11/notebooks/01_cleaning_and_integration.ipynb), [src/cleaning.py](file:///c:/Users/hp/Downloads/Projects/Hackaton/team_11/src/cleaning.py), and [src/features.py](file:///c:/Users/hp/Downloads/Projects/Hackaton/team_11/src/features.py)) adhering strictly to **Rule 6 (Zero Test Leakage)**.

---

## A1. Data Cleaning Log
The table below logs every issue identified across all three raw data sources, including count, percentage, applied resolution, and technical/agronomic justification.

| File | Column(s) | Issue Type | Affected Rows (Count & %) | Fix Applied | Technical & Agronomic Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `crop_yield_train.csv` | `region` | Case & Whitespace Inconsistencies | 4,482 rows (29.7%) | `str.strip()`, lowercase mapping to canonical set (`'Amhara'`, `'Oromia'`, `'SNNPR'`, `'Somali'`, `'Tigray'`). | Standardizes the foreign key to prevent join drops and artificial categorical fragmentation. |
| `crop_yield_train.csv` | `crop_type` | Typos, Whitespace & Mixed Case | 5,120 rows (33.9%) | Stripped whitespace, lowered case, corrected spelling variants (e.g. `'Tef'`, `' teff '` $\rightarrow$ `'teff'`). | Unifies crop labels with regional market price records and agronomic classifications. |
| `crop_yield_train.csv` | `pest_disease_flag`, `labor_days_per_ha` | Sentinel Values (`-999`) | 788 rows (5.2%): 300 in pest flag, 488 in labor days | Replaced `-999` with `NaN`. Imputed `pest_disease_flag` with mode (`0`), and `labor_days_per_ha` with train median (`45.04`). | Sentinel values severely distort regression loss functions and tree split metrics if treated as numeric quantities. |
| `crop_yield_train.csv` | `rainfall_mm_season`, `soil_quality_index`, `fertilizer_kg_per_ha` | Missing Values (`NaN`) | 1,805 total entries (12.0% of plots) | Imputed with training set medians (rainfall: `848.76 mm`, soil: `0.565`, fertilizer: `33.83 kg/ha`). Non-negative bounds applied. | Median imputation is robust to skewed distributions. Fitting strictly on train prevents leakage to test set (Rule 6). |
| `regional_weather.csv` | `region` | Abbreviated & Non-Standard Codes | 56 rows (24.1%) | Mapped `'AMH'` $\rightarrow$ `'Amhara'`, `'ORO'` $\rightarrow$ `'Oromia'`, `'SNNP'` $\rightarrow$ `'SNNPR'`, `'SOM'` $\rightarrow$ `'Somali'`, `'TIG'` $\rightarrow$ `'Tigray'`. | Resolves key mismatch between monthly climate stations and administrative plot survey locations. |
| `regional_weather.csv` | `region`, `year`, `month` | Exact Duplicate Monthly Observations | 6 duplicate pairs (12 rows total, 5.2%) | Removed exact duplicates via `drop_duplicates(subset=['region', 'year', 'month'])`. | Duplicate station readings cause uncontrolled cartesian explosion during many-to-one left joins. |
| `market_prices.csv` | `price_birr_per_quintal` | Unit Scale Mix-up (Birr/kg vs Birr/quintal) | 4 rows (4.0%) | Detected prices $< 500$ Birr/quintal (e.g. 34–49 Birr) and multiplied by 100 ($1\text{ quintal} = 100\text{ kg}$). | Field survey recorded Birr/kg instead of Birr/quintal; scaling by 100 aligns with market price distribution (~3,400–4,900 Birr). |
| `market_prices.csv` | `price_birr_per_quintal` | Missing Price Values (`NaN`) | 4 rows (4.0%) | Imputed missing values using the median price of that specific `crop_type`. | Ensures complete pricing coverage for post-model economic revenue calculation. |

---

## A2. Key Standardization Proof
To prove that our pipeline guarantees 100% key consistency across all tables without manual data editing:

### Region Keys
- **Before Cleaning:**
  - `crop_yield_train.csv` (19 variants): `['AMHARA', 'Amhara', 'Amhara ', 'OROMIA', 'Oromia', 'Oromia ', 'SNNPR', 'SNNPR ', 'SOMALI', 'Somali', 'Somali ', 'TIGRAY', 'Tigray', 'Tigray ', 'amhara', 'oromia', 'snnpr', 'somali', 'tigray']`
  - `regional_weather.csv` (20 variants): `['AMH', 'Amhara', 'Amhara ', 'ORO', 'Oromia', 'Oromia ', 'SNNP', 'SNNPR', 'SNNPR ', 'SOM', 'Somali', 'Somali ', 'TIG', 'Tigray', 'Tigray ', 'amhara', 'oromia', 'snnpr', 'somali', 'tigray']`
  - `market_prices.csv` (5 variants): `['Amhara', 'Oromia', 'SNNPR', 'Somali', 'Tigray']`
- **After Cleaning (Identical Canonical Set in All Tables):**
  - Canonical Region Set: `['Amhara', 'Oromia', 'SNNPR', 'Somali', 'Tigray']`
  - **Match Status:** **100% Alignment across all 3 tables.**

### Crop Type Keys
- **Before Cleaning:**
  - `crop_yield_train.csv` (21 variants): `[' barley ', ' maize ', ' sorghum ', ' teff ', ' wheat ', 'BARLEY', 'Barley', 'MAIZE', 'Maize', 'SORGHUM', 'Sorghum', 'TEFF', 'Tef', 'Teff', 'WHEAT', 'Wheat', 'barley', 'maize', 'sorghum', 'teff', 'wheat']`
  - `market_prices.csv` (14 variants): `[' barley ', ' maize ', ' sorghum ', ' teff ', ' wheat ', 'Barley', 'Maize', 'Sorghum', 'Wheat', 'barley', 'maize', 'sorghum', 'teff', 'wheat']`
- **After Cleaning (Identical Canonical Set in Both Tables):**
  - Canonical Crop Set: `['barley', 'maize', 'sorghum', 'teff', 'wheat']`
  - **Match Status:** **100% Alignment across both tables.**

---

## A3. Join Map & Architecture Diagram

```mermaid
graph TD
    subgraph Plot Survey Data (Core Left Table)
        P[crop_yield_train / leaderboard_test<br>Keys: plot_id, region, crop_type, survey_year, planting_month]
    end

    subgraph Regional Weather Ingestion
        W1[regional_weather.csv<br>Monthly climate observations] --> W2[Standardize Region Codes & Deduplicate]
        W2 --> W3[4-Month Growing Season Window Aggregation<br>Window: planting_month + 3 consecutive months<br>Grouped by: region, survey_year, planting_month]
    end

    subgraph Market Price Ingestion
        M1[market_prices.csv] --> M2[Unit Correction *100 & Median Imputation]
        M2 --> M3[Price Reference Table<br>Keys: crop_type, region, survey_year]
    end

    P -->|Many-to-One Left Join on region, survey_year, planting_month| J1[Plot + Weather Joined]
    W3 --> J1
    J1 -->|Many-to-One Left Join on crop_type, region, survey_year| J2[Master Modeling Table]
    M3 --> J2
```

### Architectural Decisions:
1. **Left Table Designation:** The plot survey dataset (`crop_yield_train.csv` / `crop_yield_leaderboard_test.csv`) is selected as the primary left table. In this hackathon, our unit of analysis and evaluation is the individual agricultural plot (`plot_id`). Performing left joins ensures that every single plot is preserved and evaluated without accidental record loss or duplication.
2. **Growing Season Window Rule:** In Ethiopia, crops are planted in two primary seasons: **Belg** (Feb–Mar) and **Meher** (Jun–Aug). Agronomic growth requires 3 to 4 months from sowing to physiological maturity. We define each plot's growing season window as **the planting month plus the subsequent 3 consecutive calendar months** (4 months total). Monthly weather variables are dynamically aggregated across this window for each `(region, survey_year, planting_month)` combination.

---

## A4. Join Audit
Both joins were rigorously verified against record counts, match rates, and cardinalities:

| Join Path | Join Keys | Expected Cardinality | Match Rate | Rows Before | Rows After | Unmatched Plots |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Plot $\rightarrow$ Weather** | `region`, `survey_year`, `planting_month` | Many-to-One ($N:1$) | **100.0%** | 15,090 | 15,090 | **0** |
| **Plot $\rightarrow$ Price** | `crop_type`, `region`, `survey_year` | Many-to-One ($N:1$) | **100.0%** | 15,090 | 15,090 | **0** |
| **Test $\rightarrow$ Pipeline** | Both keys as above | Many-to-One ($N:1$) | **100.0%** | 3,750 | 3,750 | **0** |

### Weather Month Coverage Analysis:
Due to natural data collection gaps in the regional meteorological network, some region-year periods contained fewer than 4 months in the targeted window:
- **Plots with all 4 months available:** 12,084 plots (**80.1%**)
- **Plots with 3 months available:** 2,548 plots (**16.9%**)
- **Plots with 2 months available:** 458 plots (**3.0%**)
- **Plots with $<2$ months:** 0 plots (**0.0%**)

**Handling Strategy:** When 2 or 3 months are available, mean temperature is computed over the available readings, while cumulative rainfall and heat day totals are scaled proportionally to a 4-month equivalent:
$$\text{weather\_season\_rainfall\_mm} = \left(\frac{\sum_{m \in \text{available}} \text{monthly\_rainfall\_mm}}{k}\right) \times 4$$
This prevents artificial underestimation of cumulative precipitation in plots with missing station months.

---

## A5. Join Proof (3 Sample Plots Traced Row-by-Row)
To prove the join logic at the individual plot level:

### Case 1: `PLOT-000339`
- **Plot Inputs:** Region = `Oromia`, Survey Year = `2024`, Planting Month = `Aug`
- **Growing Season Window:** `['Aug', 'Sep', 'Oct', 'Nov']`
- **Monthly Weather Station Rows Pulled:**
  - `Aug 2024`: Temp = $19.1^\circ\text{C}$, Rainfall = $185.1\text{ mm}$, Extreme Heat Days = $0$
  - `Sep 2024`: Temp = $15.1^\circ\text{C}$, Rainfall = $147.1\text{ mm}$, Extreme Heat Days = $0$
  - `Nov 2024`: Temp = $19.4^\circ\text{C}$, Rainfall = $20.8\text{ mm}$, Extreme Heat Days = $0$ *(Oct missing in source)*
- **Engineered Seasonal Outputs:**
  - Mean Temp = $\frac{19.1 + 15.1 + 19.4}{3} = \mathbf{17.87^\circ\text{C}}$
  - Season Rainfall = $\frac{185.1 + 147.1 + 20.8}{3} \times 4 = \mathbf{470.67\text{ mm}}$
  - Extreme Heat Days = $0.0$
  - Temperature Anomaly = $17.87 - 19.05 = \mathbf{-1.18^\circ\text{C}}$ (relative to Oromia 4-year baseline)

### Case 2: `PLOT-007457`
- **Plot Inputs:** Region = `Amhara`, Survey Year = `2023`, Planting Month = `Jun`
- **Growing Season Window:** `['Jun', 'Jul', 'Aug', 'Sep']`
- **Monthly Weather Station Rows Pulled:**
  - `Jun 2023`: Temp = $17.0^\circ\text{C}$, Rainfall = $118.5\text{ mm}$, Extreme Heat Days = $0$
  - `Jul 2023`: Temp = $14.9^\circ\text{C}$, Rainfall = $244.6\text{ mm}$, Extreme Heat Days = $0$
  - `Aug 2023`: Temp = $14.5^\circ\text{C}$, Rainfall = $192.8\text{ mm}$, Extreme Heat Days = $0$
  - `Sep 2023`: Temp = $14.4^\circ\text{C}$, Rainfall = $153.5\text{ mm}$, Extreme Heat Days = $0$ *(Complete 4-month window)*
- **Engineered Seasonal Outputs:**
  - Mean Temp = $\frac{17.0 + 14.9 + 14.5 + 14.4}{4} = \mathbf{15.20^\circ\text{C}}$
  - Season Rainfall = $118.5 + 244.6 + 192.8 + 153.5 = \mathbf{709.40\text{ mm}}$
  - Extreme Heat Days = $0.0$
  - Temperature Anomaly = $15.20 - 17.09 = \mathbf{-1.89^\circ\text{C}}$

### Case 3: `PLOT-002298`
- **Plot Inputs:** Region = `Oromia`, Survey Year = `2024`, Planting Month = `Jul`
- **Growing Season Window:** `['Jul', 'Aug', 'Sep', 'Oct']`
- **Monthly Weather Station Rows Pulled:**
  - `Jul 2024`: Temp = $17.0^\circ\text{C}$, Rainfall = $205.7\text{ mm}$, Extreme Heat Days = $0$
  - `Aug 2024`: Temp = $19.1^\circ\text{C}$, Rainfall = $185.1\text{ mm}$, Extreme Heat Days = $0$
  - `Sep 2024`: Temp = $15.1^\circ\text{C}$, Rainfall = $147.1\text{ mm}$, Extreme Heat Days = $0$
- **Engineered Seasonal Outputs:**
  - Mean Temp = $\frac{17.0 + 19.1 + 15.1}{3} = \mathbf{17.07^\circ\text{C}}$
  - Season Rainfall = $\frac{205.7 + 185.1 + 147.1}{3} \times 4 = \mathbf{717.20\text{ mm}}$
  - Extreme Heat Days = $0.0$
  - Temperature Anomaly = $17.07 - 19.05 = \mathbf{-1.98^\circ\text{C}}$

---

## A6. Feature Engineering Table
We engineered 8 domain-specific features spanning weather signals, agronomic inputs, and seasonal management:

| Feature Name | Mathematical Formula | Source Columns | Agronomic Rationale & Expected Benefit |
| :--- | :--- | :--- | :--- |
| `weather_season_mean_temp` | $\frac{1}{k}\sum_{m=1}^{k} \text{avg\_temp\_c}_m$ | `regional_weather.csv` | Captures cumulative heat units required for crop phenological development. |
| `weather_season_rainfall_mm` | $\frac{\sum \text{monthly\_rainfall\_mm}}{k} \times 4$ | `regional_weather.csv` | Represents total meteorological precipitation during vegetative and grain-filling phases. |
| `weather_season_heat_days` | $\frac{\sum \text{extreme\_heat\_days}}{k} \times 4$ | `regional_weather.csv` | Quantifies acute heat stress events that induce pollen sterility and yield reduction. |
| `weather_temp_anomaly_c` | $\text{mean\_temp} - \overline{\text{temp}}_{\text{region}}$ | `regional_weather.csv` | Measures climate shock severity relative to local regional adaptation baselines. |
| `fertilizer_improved_seed_interaction` | $\text{fertilizer\_kg\_per\_ha} \times \text{improved\_seed\_used}$ | `crop_yield_train.csv` | Captures synergistic yield gains: certified seeds maximize response to chemical nutrients. |
| `weather_rain_discrepancy_ratio` | $\frac{\text{rainfall\_mm\_season}}{\text{weather\_season\_rainfall\_mm} + 10^{-5}}$ | Plot Survey + Weather | Detects microclimatic plot variability or farmer recall bias against station recordings. |
| `labor_intensity_per_farm_size` | $\frac{\text{labor\_days\_per\_ha}}{\text{farm\_size\_ha} + 0.1}$ | `crop_yield_train.csv` | Measures management intensity and labor density across small vs larger smallholder plots. |
| `is_meher_season` | $\mathbb{I}(\text{planting\_month} \in \{\text{Jun, Jul, Aug}\})$ | `crop_yield_train.csv` | Differentiates main rainy season (Meher) from short secondary season (Belg). |

---

## A7. Automated Integrity Checks
All master tables must pass our automated validation suite before being handed off to downstream teams:

```text
============================================================
AUTOMATED INTEGRITY VALIDATION SUITE (PASS/FAIL REPORT)
============================================================
[PASS] 1_plot_id_uniqueness    -> Train unique: 15,090/15,090, Test unique: 3,750/3,750
[PASS] 2_row_count_invariance   -> Train: 15,090 rows (expected 15,090), Test: 3,750 rows (expected 3,750)
[PASS] 3_zero_missing_values    -> Train feature nulls: 0, Test feature nulls: 0
[PASS] 4_canonical_labels       -> Regions: ['Amhara', 'Oromia', 'SNNPR', 'Somali', 'Tigray'], Crops: ['barley', 'maize', 'sorghum', 'teff', 'wheat']
[PASS] 5_physical_ranges        -> yield >= 0, farm_size > 0, price > 0, fertilizer >= 0
[PASS] 6_schema_alignment       -> Features aligned: 25 test cols vs 26 train cols
============================================================
>>> ALL 6 INTEGRITY CHECKS PASSED WITH ZERO ERRORS!
```

---

## A8. Master Tables & Data Dictionary Export
The processed datasets have been exported to `data/processed/`:
1. `data/processed/master_train.csv`: 15,090 rows × 26 columns (includes target `yield_tons_per_ha`)
2. `data/processed/master_test.csv`: 3,750 rows × 25 columns (target excluded, identical feature columns)
3. `data/processed/data_dictionary_master.csv`: Comprehensive schema table documenting all 26 columns, data types, source provenance, and derivation formulas.

### Method Hygiene Confirmation:
- **Zero Test Leakage (Rule 6):** All imputation medians, modes, bounds, and baseline climate averages were calculated strictly on `crop_yield_train.csv` and applied without modification to `crop_yield_leaderboard_test.csv`.
- **Weather Feature Integration (Rule 5):** Four distinct weather-derived features are integrated into the master tables.
- **Market Price Discipline:** Market price is included for economic valuation in Deliverable B and Deliverable E, but is flagged as an excluded predictor for the yield forecasting model in Deliverable D.
