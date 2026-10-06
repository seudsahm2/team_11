"""
src/cleaning.py
Reusable cleaning and standardization pipeline functions for the Ethiopian Smallholder Crop-Yield Challenge.
Conforms strictly to Rule 6 (zero test leakage: learn statistics strictly from train).
"""
import pandas as pd
import numpy as np

ALLOWED_REGIONS = ['Amhara', 'Oromia', 'SNNPR', 'Somali', 'Tigray']
ALLOWED_CROPS = ['barley', 'maize', 'sorghum', 'teff', 'wheat']

def standardize_region(val: str) -> str:
    """Standardizes regional naming variants and abbreviations to the canonical set."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    mapping = {
        'AMH': 'Amhara',
        'ORO': 'Oromia',
        'SNNP': 'SNNPR',
        'SOM': 'Somali',
        'TIG': 'Tigray'
    }
    if s in mapping:
        return mapping[s]
    s_lower = s.lower()
    if 'oromia' in s_lower:
        return 'Oromia'
    if 'amhara' in s_lower:
        return 'Amhara'
    if 'snnpr' in s_lower or 'snnp' in s_lower:
        return 'SNNPR'
    if 'tigray' in s_lower:
        return 'Tigray'
    if 'somali' in s_lower:
        return 'Somali'
    return s

def standardize_crop(val: str) -> str:
    """Standardizes crop labels, removes whitespace, and corrects typos (e.g. Tef -> teff)."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip().lower()
    if s in ['tef', 'teff']:
        return 'teff'
    if s in ['wheat', 'wht']:
        return 'wheat'
    if s in ['maize', 'corn']:
        return 'maize'
    if s in ['sorghum', 'srghm']:
        return 'sorghum'
    if s in ['barley', 'brly']:
        return 'barley'
    return s

def clean_plot_data(df: pd.DataFrame, is_train: bool = True, stats: dict = None) -> tuple[pd.DataFrame, dict]:
    """
    Cleans plot-level data: standardizes strings, replaces -999 sentinels,
    and imputes missing values using statistics fitted strictly on train.
    """
    df = df.copy()
    
    # Standardize categoricals
    df['region'] = df['region'].apply(standardize_region)
    df['crop_type'] = df['crop_type'].apply(standardize_crop)
    
    # Handle -999 sentinels
    sentinel_cols = ['pest_disease_flag', 'labor_days_per_ha']
    for col in sentinel_cols:
        if col in df.columns:
            df[col] = df[col].replace([-999, -999.0, '-999'], np.nan)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure numeric types
    num_cols = [
        'altitude_m', 'rainfall_mm_season', 'farm_size_ha', 'fertilizer_kg_per_ha',
        'improved_seed_used', 'pest_disease_flag', 'soil_quality_index',
        'labor_days_per_ha', 'distance_to_market_km'
    ]
    if 'yield_tons_per_ha' in df.columns:
        num_cols.append('yield_tons_per_ha')
        
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Learn or apply statistics (Rule 6)
    if is_train:
        learned_stats = {
            'rainfall_mm_season_median': df['rainfall_mm_season'].median(),
            'soil_quality_index_median': df['soil_quality_index'].median(),
            'fertilizer_kg_per_ha_median': df['fertilizer_kg_per_ha'].median(),
            'labor_days_per_ha_median': df['labor_days_per_ha'].median(),
            'pest_disease_flag_mode': df['pest_disease_flag'].mode()[0] if not df['pest_disease_flag'].mode().empty else 0
        }
        stats = learned_stats
    else:
        assert stats is not None, "Must provide stats dictionary learned from train for test set cleaning!"

    # Impute missing values
    df['rainfall_mm_season'] = df['rainfall_mm_season'].fillna(stats['rainfall_mm_season_median'])
    df['soil_quality_index'] = df['soil_quality_index'].fillna(stats['soil_quality_index_median'])
    df['fertilizer_kg_per_ha'] = df['fertilizer_kg_per_ha'].fillna(stats['fertilizer_kg_per_ha_median'])
    df['labor_days_per_ha'] = df['labor_days_per_ha'].fillna(stats['labor_days_per_ha_median'])
    df['pest_disease_flag'] = df['pest_disease_flag'].fillna(stats['pest_disease_flag_mode'])
    
    # Sanity bounds (non-negative)
    df['fertilizer_kg_per_ha'] = df['fertilizer_kg_per_ha'].clip(lower=0.0)
    df['farm_size_ha'] = df['farm_size_ha'].clip(lower=0.01)
    df['labor_days_per_ha'] = df['labor_days_per_ha'].clip(lower=0.0)
    df['distance_to_market_km'] = df['distance_to_market_km'].clip(lower=0.0)
    
    if 'yield_tons_per_ha' in df.columns:
        df['yield_tons_per_ha'] = df['yield_tons_per_ha'].clip(lower=0.0)
        
    return df, stats

def clean_weather_data(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans regional weather data:
    1. Standardizes region names
    2. Drops duplicate readings (region, year, month)
    3. Imputes missing temperature and rainfall values with regional monthly medians
    """
    df = weather_df.copy()
    df['region'] = df['region'].apply(standardize_region)
    df = df.drop_duplicates(subset=['region', 'year', 'month']).copy()
    
    # Ensure numeric
    df['avg_temp_c'] = pd.to_numeric(df['avg_temp_c'], errors='coerce')
    df['monthly_rainfall_mm'] = pd.to_numeric(df['monthly_rainfall_mm'], errors='coerce')
    df['extreme_heat_days'] = pd.to_numeric(df['extreme_heat_days'], errors='coerce').fillna(0)
    
    # Impute any rare nulls using regional-monthly median
    df['avg_temp_c'] = df.groupby(['region', 'month'])['avg_temp_c'].transform(lambda x: x.fillna(x.median()))
    df['monthly_rainfall_mm'] = df.groupby(['region', 'month'])['monthly_rainfall_mm'].transform(lambda x: x.fillna(x.median()))
    
    return df

def clean_price_data(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans market price table:
    1. Standardizes crop_type and region
    2. Corrects unit mix-ups (prices in Birr/kg instead of Birr/quintal multiplied by 100)
    3. Imputes missing prices using crop-specific medians
    """
    df = price_df.copy()
    df['crop_type'] = df['crop_type'].apply(standardize_crop)
    df['region'] = df['region'].apply(standardize_region)
    df['price_birr_per_quintal'] = pd.to_numeric(df['price_birr_per_quintal'], errors='coerce')
    
    # Unit correction: prices < 500 Birr/quintal were entered per kg (1 quintal = 100 kg)
    unit_mask = (df['price_birr_per_quintal'] < 500) & (df['price_birr_per_quintal'].notna())
    df.loc[unit_mask, 'price_birr_per_quintal'] = df.loc[unit_mask, 'price_birr_per_quintal'] * 100.0
    
    # Impute remaining missing prices with median price for that crop_type
    crop_medians = df.groupby('crop_type')['price_birr_per_quintal'].transform('median')
    df['price_birr_per_quintal'] = df['price_birr_per_quintal'].fillna(crop_medians)
    
    return df

def validate_master_tables(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict:
    """
    Automated integrity validation suite (Deliverable A7).
    Runs 6 automated tests and returns PASS/FAIL status for each.
    """
    results = {}
    
    # 1. Uniqueness of plot_id
    u_train = train_df['plot_id'].nunique() == len(train_df)
    u_test = test_df['plot_id'].nunique() == len(test_df)
    results['1_plot_id_uniqueness'] = {
        'status': 'PASS' if (u_train and u_test) else 'FAIL',
        'detail': f'Train unique: {train_df["plot_id"].nunique()}/{len(train_df)}, Test unique: {test_df["plot_id"].nunique()}/{len(test_df)}'
    }
    
    # 2. Row count invariance
    r_train = len(train_df) == 15090
    r_test = len(test_df) == 3750
    results['2_row_count_invariance'] = {
        'status': 'PASS' if (r_train and r_test) else 'FAIL',
        'detail': f'Train rows: {len(train_df)} (expected 15090), Test rows: {len(test_df)} (expected 3750)'
    }
    
    # 3. Zero missing values in features
    features = [c for c in test_df.columns if c != 'plot_id']
    m_train = int(train_df[features].isnull().sum().sum())
    m_test = int(test_df[features].isnull().sum().sum())
    results['3_zero_missing_values'] = {
        'status': 'PASS' if (m_train == 0 and m_test == 0) else 'FAIL',
        'detail': f'Train feature nulls: {m_train}, Test feature nulls: {m_test}'
    }
    
    # 4. Canonical categories
    c_train_reg = set(train_df['region']).issubset(set(ALLOWED_REGIONS))
    c_test_reg = set(test_df['region']).issubset(set(ALLOWED_REGIONS))
    c_train_crop = set(train_df['crop_type']).issubset(set(ALLOWED_CROPS))
    c_test_crop = set(test_df['crop_type']).issubset(set(ALLOWED_CROPS))
    c_valid = c_train_reg and c_test_reg and c_train_crop and c_test_crop
    results['4_canonical_labels'] = {
        'status': 'PASS' if c_valid else 'FAIL',
        'detail': f'Regions: {sorted(list(set(train_df["region"])))}, Crops: {sorted(list(set(train_df["crop_type"])))}'
    }
    
    # 5. Physical ranges
    p_valid = (
        (train_df['yield_tons_per_ha'] >= 0).all() and
        (train_df['farm_size_ha'] > 0).all() and
        (test_df['farm_size_ha'] > 0).all() and
        (train_df['price_birr_per_quintal'] > 0).all() and
        (train_df['fertilizer_kg_per_ha'] >= 0).all()
    )
    results['5_physical_ranges'] = {
        'status': 'PASS' if p_valid else 'FAIL',
        'detail': 'yield >= 0, farm_size > 0, price > 0, fertilizer >= 0'
    }
    
    # 6. Schema alignment
    s_valid = set(test_df.columns).issubset(set(train_df.columns)) and ('yield_tons_per_ha' not in test_df.columns)
    results['6_schema_alignment'] = {
        'status': 'PASS' if s_valid else 'FAIL',
        'detail': f'Features aligned: {len(test_df.columns)} test cols vs {len(train_df.columns)} train cols'
    }
    
    return results

