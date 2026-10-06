# Deliverable B — Data Analysis Report (14 Tasks)
**Team:** Team 11  
**Competition:** Ethiopian Smallholder Crop-Yield Challenge  
**Program:** Qiyas / IADE Training Program — Addis Ababa University AI Hackathon 2026  
**Data Foundation:** Cleaned & Integrated Master Table (`master_train.csv`, 15,090 plots)

---

## Executive Summary
This report presents the complete statistical, agronomic, and economic findings for **Deliverable B**. All 14 numbered questions are rigorously evaluated using empirical calculations, formatted tables, and structured takeaways. 

Key high-level takeaways:
1. **Economic vs. Physical Productivity:** Teff earns the highest gross revenue per hectare (**152,301 Birr/ha**) despite yielding the least (**2.00 t/ha**), owing to a 2.6× market price premium over Maize.
2. **Regional Disparities:** Tigray and Amhara lead in productivity (~3.13 t/ha), while pastoral lowland Somali severely lags (1.46 t/ha).
3. **Agronomic Interventions:** Certified improved seeds provide a reliable **~20% yield lift** across all five crops; pest pressure inflicts devastating penalties, particularly on Maize (**-28.8% loss**).
4. **Meteorological Disconnect:** Station-measured rainfall and farmer self-reported precipitation show virtually zero correlation ($r = 0.0056$), highlighting significant microclimatic variation in Ethiopia's highlands and differing perception thresholds.

---

## B1. Value & Prices

### B1.1 Revenue per Hectare by Crop
**Formula:** $\text{Revenue (Birr/ha)} = \text{yield\_tons\_per\_ha} \times 10 \times \text{price\_birr\_per\_quintal}$

| Crop Type | Mean Yield (t/ha) | Mean Price (Birr/quintal) | Mean Gross Revenue (Birr/ha) | Median Revenue (Birr/ha) | Economic Rank |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Teff** | 2.003 | 7,652.04 | **152,301.05** | 150,654.96 | **#1** |
| **Wheat** | 2.802 | 4,847.11 | **135,499.52** | 128,471.86 | **#2** |
| **Maize** | 3.904 | 2,927.18 | **114,336.38** | 109,689.21 | **#3** |
| **Barley** | 2.467 | 4,448.89 | **109,463.81** | 104,206.08 | **#4** |
| **Sorghum** | 2.611 | 3,192.51 | **83,622.87** | 80,091.16 | **#5** |

> **Interpretation (B1.1):**  
> **Teff** generates the highest estimated revenue per hectare (**152,301 Birr/ha**), followed by Wheat (135,500 Birr/ha), with Sorghum generating the lowest (83,623 Birr/ha).  
> **The crop earning the most per hectare is NOT the highest-yielding crop:** Maize produces nearly double the grain biomass of Teff (3.90 vs. 2.00 t/ha), but Teff's cultural staple status and inelastic urban demand drive a 2.6× price premium that outweighs its lower biological yield.

---

### B1.2 Price Trends (2021 to 2024)
Tracking farmgate commodity price trajectories over the four survey years.

| Crop Type | 2021 (Birr/qt) | 2022 (Birr/qt) | 2023 (Birr/qt) | 2024 (Birr/qt) | Absolute Change | Percentage Growth |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sorghum** | 2,686.58 | 3,118.23 | 3,478.25 | 3,486.97 | +800.39 Birr | **+29.79%** |
| **Wheat** | 4,297.79 | 4,715.15 | 4,816.03 | 5,559.55 | +1,261.76 Birr | **+29.36%** |
| **Maize** | 2,594.17 | 2,851.09 | 3,032.84 | 3,230.61 | +636.44 Birr | **+24.53%** |
| **Barley** | 3,939.75 | 4,188.66 | 4,825.10 | 4,842.06 | +902.31 Birr | **+22.90%** |
| **Teff** | 6,867.36 | 7,397.38 | 7,939.98 | 8,403.43 | +1,536.07 Birr | **+22.37%** |

> **Interpretation (B1.2):**  
> **Sorghum** experienced the fastest proportional price growth between 2021 and 2024 at **+29.79%**, closely followed by **Wheat (+29.36%)**, while Teff experienced the largest nominal rise (+1,536 Birr/quintal).  
> The 7.42 percentage point gap between the fastest (Sorghum: ~30%) and slowest (Teff: ~22%) is economically meaningful, highlighting rising demand for climate-resilient dryland staples alongside national wheat market pressures.

---

## B2. Category Breakdowns

### B2.1 Yield by Region
Performance metrics across the five administrative zones.

| Region | Mean Yield (t/ha) | Median Yield (t/ha) | Standard Deviation (t/ha) | Plot Count |
| :--- | :---: | :---: | :---: | :---: |
| **Tigray** | **3.131** | 2.932 | 1.309 | 3,090 |
| **Amhara** | **3.129** | 3.021 | 1.231 | 2,979 |
| **Oromia** | 3.073 | 2.893 | 1.292 | 2,969 |
| **SNNPR** | 3.041 | 2.741 | **1.472** | 2,983 |
| **Somali** | **1.464** | 1.294 | **0.771** | 3,069 |

> **Interpretation (B2.1):**  
> **Tigray** and **Amhara** achieve the highest regional average yields (**3.131 t/ha** and **3.129 t/ha**), whereas **Somali** yields are less than half (1.464 t/ha).  
> **SNNPR** exhibits the greatest yield dispersion ($\text{std} = 1.472\text{ t/ha}$) due to dramatic agro-ecological elevation gradients, while pastoral Somali shows the lowest absolute variance ($\text{std} = 0.771\text{ t/ha}$) constrained by persistent moisture limits.

---

### B2.2 Yield by Crop Type
Physiological yield distributions across the five target crops.

| Crop Type | Mean Yield (t/ha) | Median Yield (t/ha) | Standard Deviation (t/ha) | Plot Count |
| :--- | :---: | :---: | :---: | :---: |
| **Maize** | **3.904** | 3.781 | 1.584 | 3,059 |
| **Wheat** | 2.802 | 2.692 | 1.411 | 3,076 |
| **Sorghum** | 2.611 | 2.514 | 0.974 | 3,006 |
| **Barley** | 2.467 | 2.376 | 1.158 | 2,934 |
| **Teff** | **2.003** | 2.001 | 0.988 | 3,015 |

> **Interpretation (B2.2):**  
> Physical productivity follows: **Maize (3.90 t/ha) > Wheat (2.80 t/ha) > Sorghum (2.61 t/ha) > Barley (2.47 t/ha) > Teff (2.00 t/ha)**.  
> This hierarchy conforms fully with biological expectations: $C_4$ maize possesses superior photosynthetic radiation-use efficiency, while Teff is genetically constrained by small seed size, low harvest index, and vulnerability to stem lodging.

---

### B2.3 Region × Crop Pivot Table
Two-dimensional matrix of average yields ($\text{tons/ha}$).

| Region | Barley | Maize | Sorghum | Teff | Wheat | Regional Average |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Amhara** | 3.187 | 3.829 | 2.495 | 2.479 | 3.598 | 3.129 |
| **Oromia** | 2.675 | 4.450 | 2.955 | 2.288 | 3.120 | 3.073 |
| **SNNPR** | 2.289 | **4.797** | 3.106 | 2.104 | 2.668 | 3.041 |
| **Somali** | 1.123 | 2.320 | 1.793 | **0.831** | 1.281 | 1.464 |
| **Tigray** | 3.010 | 4.074 | 2.709 | 2.332 | 3.463 | 3.131 |

> **Interpretation (B2.3):**  
> The single best-performing combination is **SNNPR × Maize (4.797 tons/ha)**, whereas the single worst is **Somali × Teff (0.831 tons/ha)**.  
> *Agronomic Reason:* SNNPR provides fertile volcanic andosols combined with prolonged bimodal rainfall ideal for nutrient-demanding maize, whereas Teff fails in the arid, sandy soils and intense heat of Somali where rapid moisture evaporation prevents proper germination and tillering.

---

### B2.4 Improved Seed Yield Lift
Assessing the impact of certified seed varieties across crop types.

| Crop Type | Traditional Seed (t/ha) | Improved Seed (t/ha) | Absolute Yield Gap (t/ha) | Percentage Lift (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Teff** | 1.844 | 2.263 | +0.419 | **+22.75%** |
| **Maize** | 3.612 | 4.394 | **+0.783** | **+21.67%** |
| **Wheat** | 2.596 | 3.133 | +0.537 | **+20.66%** |
| **Sorghum** | 2.442 | 2.889 | +0.447 | **+18.31%** |
| **Barley** | 2.305 | 2.727 | +0.422 | **+18.30%** |

> **Interpretation (B2.4):**  
> **Teff** gains the highest proportional lift (**+22.75%**), while **Maize** achieves the highest absolute gain (**+0.783 t/ha**).  
> The percentage benefit is strikingly consistent across all five crops (tightly bounded between **18.3% and 22.8%**), providing robust evidence that certified improved seed varieties deliver a predictable ~20% productivity dividend regardless of crop choice.

---

### B2.5 Pest & Disease Impact by Crop
Quantifying yield penalties under biotic pest/disease infestations.

| Crop Type | Unaffected Yield (t/ha) | Pest-Infested Yield (t/ha) | Absolute Loss (t/ha) | Relative Yield Penalty (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Maize** | 4.175 | 2.972 | **-1.204** | **-28.83%** |
| **Sorghum** | 2.770 | 2.026 | -0.745 | -26.88% |
| **Barley** | 2.619 | 1.917 | -0.702 | -26.79% |
| **Wheat** | 2.975 | 2.191 | -0.784 | -26.35% |
| **Teff** | 2.125 | 1.568 | -0.557 | -26.22% |

> **Interpretation (B2.5):**  
> **Maize** is hit hardest in both absolute terms (**-1.204 t/ha**) and relative terms (**-28.83%**), suffering disproportionate damage compared to other grains.  
> Pest pressure consistently inflicts a ~26% to ~29% loss across all crops, but the acute devastation in maize highlights the destructive capacity of voracious defoliators like the Fall Armyworm on high-biomass crops.

---

## B3. Agronomic Drivers

### B3.1 Fertilizer Response Curve
Yield progression across chemical fertilizer quartiles ($kg/ha$).

| Fertilizer Quartile | Fertilizer Range | Overall Mean Yield (t/ha) | Barley | Maize | Sorghum | Teff | Wheat |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q1** | $0 - 18\text{ kg/ha}$ | 2.436 | 2.241 | 3.369 | 2.249 | 1.749 | 2.562 |
| **Q2** | $18 - 34\text{ kg/ha}$ | 2.691 | 2.318 | 3.827 | 2.536 | 2.011 | 2.706 |
| **Q3** | $34 - 51\text{ kg/ha}$ | 2.853 | 2.574 | 4.095 | 2.711 | 2.019 | 2.843 |
| **Q4** | $> 51\text{ kg/ha}$ | 3.086 | 2.772 | 4.346 | 2.975 | 2.223 | 3.106 |

> **Interpretation (B3.1):**  
> Yield increases monotonically with fertilizer application from 2.436 t/ha (Q1) to 3.086 t/ha (Q4).  
> The overall response displays **diminishing marginal returns (flattening)**: jumping from Q1 to Q2 yields +0.254 t/ha (+10.4%), whereas moving from Q2 to Q3 yields only +0.162 t/ha (+6.0%); in Teff, the curve nearly plateaus between Q2 and Q3 (2.011 to 2.019 t/ha) as excess nitrogen promotes vegetative lodging rather than grain yield.

---

### B3.2 Altitude Response by Crop
Performance across four elevation bands with sample reliability audits.

| Altitude Band | Elevation Range | Barley | Maize | Sorghum | Teff | Wheat |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Low** | $< 1800\text{ m}$ | 2.871 *(10 plots)* | 3.940 *(1,684)* | **2.665** *(1,945)* | 0.948 *(118)* | 2.192 *(16 plots)* |
| **Mid-Low** | $1800 - 2175\text{ m}$ | 0.933 *(80 plots)* | **4.020** *(1,271)* | 2.583 *(1,006)* | 2.042 *(1,244)* | 1.065 *(171 plots)* |
| **Mid-High** | $2175 - 2550\text{ m}$ | 2.259 *(957 plots)* | 1.962 *(101 plots)* | 1.235 *(54 plots)* | **2.231** *(1,373)* | **2.922** *(1,287)* |
| **High** | $> 2550\text{ m}$ | **2.635** *(1,887)* | 0.394 *(3 plots)* | 0.169 *(1 plot)* | 1.157 *(280)* | **2.897** *(1,602)* |

> **Interpretation (B3.2):**  
> Each crop possesses a distinct agro-ecological elevation sweet spot: **Barley** thrives in the High zone (>2550m: 2.635 t/ha), **Wheat** in Mid-High (2175–2550m: 2.922 t/ha), **Teff** in Mid-High (2.231 t/ha), **Maize** in Mid-Low (1800–2175m: 4.020 t/ha), and **Sorghum** in the Lowlands (<1800m: 2.665 t/ha).  
> **Four cells contain $< 30$ plots and cannot be trusted:** High-altitude Maize (3 plots), High-altitude Sorghum (1 plot), Lowland Barley (10 plots), and Lowland Wheat (16 plots)—reflecting natural thermal boundaries where Ethiopian smallholders rarely cultivate thermal-sensitive crops.

---

### B3.3 Planting Month Timing
Assessing planting month effects across Belg and Meher agricultural seasons.

| Planting Month | Season Classification | Overall Mean Yield (t/ha) | Barley | Maize | Sorghum | Teff | Wheat |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **June** | Meher (Main Rains) | **2.814** | 2.657 | 3.725 | 2.475 | 2.071 | **3.078** |
| **July** | Meher (Main Rains) | 2.789 | 2.573 | 3.846 | 2.526 | **2.107** | 2.932 |
| **August** | Meher (Late Rains) | 2.788 | 2.576 | 3.875 | 2.618 | 2.020 | 2.805 |
| **March** | Belg (Secondary Rains)| 2.728 | 2.313 | 3.956 | 2.701 | 1.960 | 2.687 |
| **February** | Belg (Early Sowing) | 2.695 | 2.241 | **4.118** | **2.729** | 1.852 | 2.495 |

> **Interpretation (B3.3):**  
> Timing exhibits a notable effect: main Meher plantings (**June: 2.814 t/ha**) systematically outperform early Belg plantings (**February: 2.695 t/ha**), generating an overall timing gap of **0.119 tons/ha**.  
> While the overall timing effect (0.12 t/ha) is secondary compared to crop choice (1.90 t/ha) and regional agro-ecology (1.67 t/ha), crop-specific timing is critical: for Wheat, sowing in June yields **+0.583 t/ha (+23.4%)** more than sowing in February.

---

### B3.4 Distance to Market Analysis
Evaluating whether road distance to marketplace correlates with harvested crop yields.

| Distance Quartile | Distance Range | Plot Count | Mean Yield (t/ha) | Standard Deviation (t/ha) |
| :--- | :---: | :---: | :---: | :---: |
| **Near** | $< 5.0\text{ km}$ | 3,773 | 2.769 | 1.401 |
| **Mid-Near** | $5.0 - 10.0\text{ km}$ | 3,772 | 2.730 | 1.398 |
| **Mid-Far** | $10.0 - 17.0\text{ km}$ | 3,772 | 2.775 | 1.399 |
| **Far** | $> 17.0\text{ km}$ | 3,773 | 2.777 | 1.401 |

> **Interpretation (B3.4):**  
> Distance to market is **completely unrelated to agricultural crop yield**, showing a Pearson correlation of $r = 0.0048$ and nearly identical average yields across all four distance quartiles (2.769 vs. 2.777 t/ha).  
> **Modeling Recommendation:** We recommend **dropping or penalizing** distance to market in the yield forecasting model; biological plot yield is dictated by environmental and management factors, and including an uninformative market proximity feature risks learning spurious noise.

---

## B4. Time & Weather

### B4.1 Yield Trend (2021 to 2024)
Tracking national and regional performance over time.

| Survey Year | National Mean Yield (t/ha) | Standard Deviation | Amhara | Oromia | SNNPR | Somali | Tigray |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2021** | 2.700 | 1.400 | 3.146 | 3.041 | 2.864 | 1.283 | 3.159 |
| **2022** | 2.778 | 1.377 | 3.080 | 3.031 | 3.024 | 1.671 | 3.139 |
| **2023** | 2.793 | 1.386 | 3.105 | 3.132 | 3.161 | 1.415 | 3.155 |
| **2024** | 2.779 | 1.434 | 3.181 | 3.089 | 3.105 | 1.478 | 3.068 |

> **Interpretation (B4.1):**  
> Average national yields remained nearly stationary between 2021 and 2024 (2.700 to 2.779 t/ha), exhibiting an inter-annual range of only 0.093 t/ha.  
> **The data simply bounces around with no secular trend:** Year-to-year shifts (< 0.09 t/ha) are negligible relative to within-year plot dispersion ($\text{std} \approx 1.40\text{ t/ha}$), indicating that smallholder yields fluctuate according to localized seasonal weather shocks rather than sustained technological progress.

---

### B4.2 Regional Weather Anomalies
Identifying extreme temperature departures from 4-year regional baselines.

| Region | Survey Year | Growing Season Mean Temp | Regional 4-Year Baseline Temp | Temperature Anomaly | Regional Yield (t/ha) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Somali** | **2022** | $25.92^\circ\text{C}$ | $28.74^\circ\text{C}$ | **-2.81°C** *(Cool/Wet)* | **1.671** *(Highest Somali year)* |
| **Tigray** | **2024** | $20.30^\circ\text{C}$ | $18.05^\circ\text{C}$ | **+2.25°C** *(Heatwave)* | **3.068** *(Lowest Tigray year)* |
| **Tigray** | **2022** | $16.34^\circ\text{C}$ | $18.05^\circ\text{C}$ | **-1.71°C** *(Cool anomaly)*| 3.139 |
| **Amhara** | **2023** | $15.51^\circ\text{C}$ | $17.09^\circ\text{C}$ | **-1.58°C** *(Cool anomaly)*| 3.105 |
| **Somali** | **2021** | $30.15^\circ\text{C}$ | $28.74^\circ\text{C}$ | **+1.41°C** *(Heat stress)* | **1.283** *(Lowest Somali year)* |

> **Interpretation (B4.2):**  
> The most abnormal region-year was **Somali in 2022** (-2.81°C below baseline), followed by **Tigray in 2024** (+2.25°C above baseline).  
> In Somali, the cooler 2022 season significantly attenuated heat stress and boosted yield to **1.671 t/ha** (a +30% surge over 2021), whereas in Tigray, the +2.25°C heat shock in 2024 depressed yields to **3.068 t/ha** (its lowest performance). This confirms that thermal anomalies exert asymmetric effects conditioned on whether the region operates near or above critical crop heat thresholds.

---

### B4.3 Plot-Reported vs. Station-Measured Rainfall
Evaluating consistency between farmer self-reported rainfall and meteorological station data.

| Metric | Computed Value | Interpretation |
| :--- | :---: | :--- |
| **Pearson Correlation ($r$)** | **0.0056** | Zero linear association between farmer reports and weather stations. |
| **Mean Absolute Difference (MAE)** | **483.04 mm** | Discrepancy exceeds total average seasonal precipitation. |
| **Plot-Reported Mean** | **856.26 mm** | Farmers systematically report ~2.2× higher precipitation levels. |
| **Station-Aggregated Mean** | **391.02 mm** | Measured cumulative station rainfall during growing window. |

> **Interpretation (B4.3):**  
> Self-reported and station-measured rainfall **diverge dramatically**, showing near-zero correlation ($r = 0.0056$) and an immense Mean Absolute Difference of **483.04 mm**.  
> *Underlying Reasons:* (1) Ethiopia's complex mountainous terrain causes localized convective microclimates and sharp rain-shadow effects that single regional stations cannot capture; and (2) Smallholders lack rain gauges and mentally estimate rainfall based on soil moisture saturation, runoff, and crop vigour rather than meteorological depth.
