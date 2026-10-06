"""
Smart Prediction Adapter for Ethiopian Smallholder Crop-Yield Model
------------------------------------------------------------------
Supports dual-mode execution:
1. Production Mode: Automatically loads and predicts using `models/final_model.joblib`
2. Autonomous Mock Mode: Agronomic heuristic simulation calibrated to Ethiopian agro-ecological zones
"""

import os
import json
import math
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
MODEL_PATH = PROJECT_DIR / "models" / "final_model.joblib"

class CropYieldPredictor:
    def __init__(self):
        self.weather_lookup = self._load_json(ASSETS_DIR / "weather_lookup.json")
        self.price_lookup = self._load_json(ASSETS_DIR / "price_lookup.json")
        self.model = None
        self.is_production_model = False
        self._load_production_model_if_available()

    @property
    def is_production(self) -> bool:
        return self.is_production_model

    def _load_json(self, path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_production_model_if_available(self):
        """Attempts to load serialized production model pipeline from models/."""
        if MODEL_PATH.exists():
            try:
                import joblib
                self.model = joblib.load(MODEL_PATH)
                self.is_production_model = True
            except Exception as e:
                self.model = None
                self.is_production_model = False
        else:
            self.model = None
            self.is_production_model = False

    def get_weather_context(self, region: str, year: int, planting_month: str) -> dict:
        """Looks up growing season weather automatically without requiring user input."""
        r = region.title() if region.title() in self.weather_lookup else "Oromia"
        y = str(year)
        m = planting_month[:3].title()
        
        reg_data = self.weather_lookup.get(r, {})
        year_data = reg_data.get(y, {})
        month_data = year_data.get(m, {})
        
        if month_data:
            return month_data
        
        # Fallback averages
        return {
            "avg_temp_c": 19.5,
            "seasonal_rainfall_mm": 650.0,
            "extreme_heat_days": 2
        }

    def get_market_price(self, region: str, crop_type: str, year: int) -> float:
        """Looks up crop market price (Birr/quintal) automatically without user input."""
        r = region.title() if region.title() in self.price_lookup else "Oromia"
        c = crop_type.lower()
        y = str(year)
        
        reg_data = self.price_lookup.get(r, {})
        crop_data = reg_data.get(c, {})
        price = crop_data.get(y)
        if price is not None:
            return float(price)
            
        # Regional / crop fallback defaults (ETB / quintal)
        fallback_prices = {
            "teff": 7800.0,
            "wheat": 5200.0,
            "maize": 3400.0,
            "sorghum": 3600.0,
            "barley": 4200.0
        }
        return fallback_prices.get(c, 4500.0)

    def _mock_agronomic_prediction(self, inputs: dict, weather: dict) -> float:
        """
        Calibrated agronomic simulation matching Ethiopian survey statistics:
        - Teff: 1.2 - 2.0 t/ha
        - Wheat: 2.2 - 3.6 t/ha
        - Maize: 2.8 - 4.8 t/ha
        - Sorghum: 1.8 - 3.2 t/ha
        - Barley: 1.6 - 2.8 t/ha
        """
        crop = inputs["crop_type"].lower()
        base_yields = {
            "maize": 3.4,
            "wheat": 2.9,
            "barley": 2.2,
            "sorghum": 2.3,
            "teff": 1.55
        }
        base = base_yields.get(crop, 2.5)

        # 1. Soil quality index multiplier (0.0 to 1.0)
        sqi = max(0.0, min(1.0, float(inputs.get("soil_quality_index", 0.5))))
        soil_mult = 0.75 + (sqi * 0.5)  # 0.75x to 1.25x

        # 2. Fertilizer response (logarithmic diminishing returns)
        fert = max(0.0, float(inputs.get("fertilizer_kg_per_ha", 0.0)))
        # Saturates around 150-200 kg/ha
        fert_mult = 1.0 + (math.log1p(fert) * 0.075)

        # 3. Improved certified seed boost (+18% to +25%)
        seed_boost = 1.20 if int(inputs.get("improved_seed_used", 0)) == 1 else 1.0

        # 4. Pest / disease penalty (-15% to -25%)
        pest_penalty = 0.82 if int(inputs.get("pest_disease_flag", 0)) == 1 else 1.0

        # 5. Altitude suitability curve
        alt = float(inputs.get("altitude_m", 1800.0))
        optimal_alt = {
            "teff": 2000,
            "wheat": 2200,
            "barley": 2400,
            "maize": 1600,
            "sorghum": 1300
        }
        opt = optimal_alt.get(crop, 1800)
        alt_deviation = abs(alt - opt) / 1000.0
        alt_mult = max(0.70, 1.0 - (alt_deviation * 0.15))

        # 6. Weather heat penalty
        heat_days = weather.get("extreme_heat_days", 0)
        heat_penalty = max(0.80, 1.0 - (heat_days * 0.015))

        predicted = base * soil_mult * fert_mult * seed_boost * pest_penalty * alt_mult * heat_penalty
        return max(0.3, round(predicted, 2))

    def predict(self, inputs: dict) -> dict:
        """
        Takes raw plot characteristics, automatically looks up weather & price,
        and outputs predicted yield (tons/ha) and gross revenue in Birr.
        """
        region = inputs["region"]
        crop_type = inputs["crop_type"]
        year = int(inputs["survey_year"])
        month = inputs["planting_month"]
        farm_size = float(inputs.get("farm_size_ha", 1.0))

        # 1. Background automatic lookup
        weather = self.get_weather_context(region, year, month)
        price_per_quintal = self.get_market_price(region, crop_type, year)

        # Check if real production model became available
        self._load_production_model_if_available()

        if self.is_production_model and self.model is not None:
            try:
                # Prepare dataframe matching training schema
                avg_t = float(weather.get("avg_temp_c", 19.5))
                rain_w = float(weather.get("seasonal_rainfall_mm", 650.0))
                rain_p = float(inputs.get("rainfall_mm_season", rain_w))
                heat_d = float(weather.get("extreme_heat_days", 0))
                alt_m = float(inputs["altitude_m"])
                fert = float(inputs["fertilizer_kg_per_ha"])
                seed_cert = int(inputs["improved_seed_used"])
                labor_d = float(inputs["labor_days_per_ha"])

                # Normalize categories to match trained model pipeline
                norm_region = "SNNPR" if region.upper() == "SNNPR" else region.strip().title()
                norm_crop = crop_type.strip().lower()
                norm_month = month[:3].title()
                valid_months = ['Aug', 'Feb', 'Jul', 'Jun', 'Mar']
                if norm_month not in valid_months:
                    norm_month = 'Jun'  # Main Meher sowing default

                feat_dict = {
                    "region": [norm_region],
                    "crop_type": [norm_crop],
                    "planting_month": [norm_month],
                    "altitude_m": [alt_m],
                    "rainfall_mm_season": [rain_p],
                    "farm_size_ha": [farm_size],
                    "fertilizer_kg_per_ha": [fert],
                    "improved_seed_used": [seed_cert],
                    "pest_disease_flag": [int(inputs["pest_disease_flag"])],
                    "soil_quality_index": [float(inputs["soil_quality_index"])],
                    "labor_days_per_ha": [labor_d],
                    "weather_season_mean_temp": [avg_t],
                    "weather_season_rainfall_mm": [rain_w],
                    "weather_season_heat_days": [heat_d],
                    "weather_temp_anomaly_c": [float(weather.get("temp_anomaly_c", 0.0))],
                    "fertilizer_improved_seed_interaction": [fert * seed_cert],
                    "weather_rain_discrepancy_ratio": [rain_p / (rain_w + 1.0)],
                    "labor_intensity_per_farm_size": [labor_d / (farm_size + 0.1)],
                    "is_meher_season": [1 if month in ['Jun', 'Jul', 'Aug', 'Sep', 'Oct'] else 0],
                    "altitude_temp_index": [(100.0 * avg_t) / (alt_m + 1.0)]
                }
                df_input = pd.DataFrame(feat_dict)
                pred_yield = float(self.model.predict(df_input)[0])
                pred_yield = max(0.1, round(pred_yield, 2))
                engine = "Production ML Pipeline (final_model.joblib)"
            except Exception as e:
                pred_yield = self._mock_agronomic_prediction(inputs, weather)
                engine = f"Agronomic Heuristic Fallback (Pipeline Error: {str(e)[:40]})"
        else:
            pred_yield = self._mock_agronomic_prediction(inputs, weather)
            engine = "Agronomic Baseline Simulator (Pre-Production Mode)"

        # Economic calculation: 1 ton = 10 quintals
        # Revenue = yield (tons/ha) * farm_size (ha) * 10 (quintals/ton) * price_per_quintal
        total_tons = round(pred_yield * farm_size, 2)
        total_quintals = round(total_tons * 10, 1)
        gross_revenue_birr = round(total_quintals * price_per_quintal, 2)

        return {
            "predicted_yield_tons_per_ha": pred_yield,
            "total_harvest_tons": total_tons,
            "total_quintals": total_quintals,
            "price_birr_per_quintal": price_per_quintal,
            "gross_revenue_birr": gross_revenue_birr,
            "engine": engine,
            "is_production": self.is_production_model,
            "weather_looked_up": weather
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Runs fast batch inference across multiple smallholder survey plots."""
        results = []
        for _, row in df.iterrows():
            inputs = row.to_dict()
            res = self.predict(inputs)
            enriched = dict(inputs)
            enriched["predicted_yield_t_ha"] = res["predicted_yield_tons_per_ha"]
            enriched["total_harvest_tons"] = res["total_harvest_tons"]
            enriched["total_quintals"] = res["total_quintals"]
            enriched["price_birr_per_quintal"] = res["price_birr_per_quintal"]
            enriched["gross_revenue_birr"] = res["gross_revenue_birr"]
            enriched["engine"] = res["engine"]
            results.append(enriched)
        return pd.DataFrame(results)
