"""
src/features.py
Feature engineering and table integration module for the Ethiopian Smallholder Crop-Yield Challenge.
Handles the 4-month growing season window weather join and agronomic interactions.
"""
import pandas as pd
import numpy as np

MONTH_ORDER = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTH_TO_NUM = {m: i + 1 for i, m in enumerate(MONTH_ORDER)}
NUM_TO_MONTH = {i + 1: m for i, m in enumerate(MONTH_ORDER)}

def get_growing_season_months(planting_month: str, duration: int = 4) -> list[str]:
    """Returns the sequence of months corresponding to the growing season."""
    if planting_month not in MONTH_TO_NUM:
        return []
    start_num = MONTH_TO_NUM[planting_month]
    months = []
    for i in range(duration):
        m_num = ((start_num - 1 + i) % 12) + 1
        months.append(NUM_TO_MONTH[m_num])
    return months

def aggregate_growing_season_weather(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-computes seasonal weather aggregations for every (region, year, planting_month).
    Normalizes total rainfall and extreme heat days proportionally if fewer than 4 months exist.
    """
    regions = weather_df['region'].unique()
    years = weather_df['year'].unique()
    planting_months = ['Feb', 'Mar', 'Jun', 'Jul', 'Aug']
    
    # Pre-calculate 4-year regional baseline mean temperature for anomaly calculations
    region_baseline_temp = weather_df.groupby('region')['avg_temp_c'].mean().to_dict()
    
    rows = []
    for r in regions:
        for y in years:
            for pm in planting_months:
                season_months = get_growing_season_months(pm, duration=4)
                sub = weather_df[
                    (weather_df['region'] == r) &
                    (weather_df['year'] == y) &
                    (weather_df['month'].isin(season_months))
                ]
                
                k = len(sub)
                if k > 0:
                    mean_temp = sub['avg_temp_c'].mean()
                    # Scale to 4-month equivalent if gaps exist
                    season_rainfall = (sub['monthly_rainfall_mm'].sum() / k) * 4.0
                    season_heat_days = (sub['extreme_heat_days'].sum() / k) * 4.0
                else:
                    # Fallback to region-year general average
                    sub_fallback = weather_df[(weather_df['region'] == r) & (weather_df['year'] == y)]
                    mean_temp = sub_fallback['avg_temp_c'].mean() if len(sub_fallback) > 0 else 20.0
                    season_rainfall = (sub_fallback['monthly_rainfall_mm'].mean() * 4.0) if len(sub_fallback) > 0 else 500.0
                    season_heat_days = 0.0
                    k = 0

                temp_anomaly = mean_temp - region_baseline_temp.get(r, mean_temp)
                
                rows.append({
                    'region': r,
                    'survey_year': y,
                    'planting_month': pm,
                    'weather_season_mean_temp': mean_temp,
                    'weather_season_rainfall_mm': season_rainfall,
                    'weather_season_heat_days': season_heat_days,
                    'weather_temp_anomaly_c': temp_anomaly,
                    'weather_months_available': k
                })
                
    return pd.DataFrame(rows)

def build_master_table(plot_df: pd.DataFrame, weather_df: pd.DataFrame, price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Integrates plot survey data with aggregated seasonal weather and market prices.
    Computes 8+ engineered features while avoiding duplicate row inflation.
    """
    df = plot_df.copy()
    initial_rows = len(df)
    
    # 1. Join Regional Seasonal Weather (Many-to-One join)
    weather_agg = aggregate_growing_season_weather(weather_df)
    df = pd.merge(
        df,
        weather_agg,
        on=['region', 'survey_year', 'planting_month'],
        how='left'
    )
    assert len(df) == initial_rows, f"Weather join expanded rows! Before: {initial_rows}, After: {len(df)}"
    
    # 2. Join Market Prices (Many-to-One join on crop_type, region, survey_year)
    price_cols = price_df[['crop_type', 'region', 'year', 'price_birr_per_quintal']].copy()
    price_cols = price_cols.rename(columns={'year': 'survey_year'})
    df = pd.merge(
        df,
        price_cols,
        on=['crop_type', 'region', 'survey_year'],
        how='left'
    )
    assert len(df) == initial_rows, f"Price join expanded rows! Before: {initial_rows}, After: {len(df)}"
    
    # 3. Feature Engineering
    # Interaction: Fertilizer application x Improved seed
    df['fertilizer_improved_seed_interaction'] = df['fertilizer_kg_per_ha'] * df['improved_seed_used']
    
    # Discrepancy ratio: self-reported plot rainfall vs station rainfall
    df['weather_rain_discrepancy_ratio'] = df['rainfall_mm_season'] / (df['weather_season_rainfall_mm'] + 1e-5)
    
    # Labor intensity per unit farm size
    df['labor_intensity_per_farm_size'] = df['labor_days_per_ha'] / (df['farm_size_ha'] + 0.1)
    
    # Planting timing feature: Meher season flag (Jun-Aug)
    df['is_meher_season'] = df['planting_month'].isin(['Jun', 'Jul', 'Aug']).astype(int)
    
    # Agro-climatic elevation-temperature index
    df['altitude_temp_index'] = df['altitude_m'] / (df['weather_season_mean_temp'] + 273.15)
    
    return df
