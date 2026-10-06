"""
Streamlit Prediction Demo App — Team 11
Ethiopian Smallholder Crop-Yield Challenge
"""
import streamlit as st

st.set_page_config(page_title="Crop Yield and Revenue Predictor", layout="wide")
st.title("🌾 Smallholder Crop Yield and Revenue Forecaster")
st.write("Team 11 | Qiyas AAU IADE Hackathon 2026")

# UI Controls and Input Form
with st.sidebar:
    st.header("Plot and Agronomic Parameters")
    region = st.selectbox("Region", ["Oromia", "Amhara", "SNNPR", "Tigray", "Somali"])
    crop = st.selectbox("Crop Type", ["teff", "wheat", "maize", "sorghum", "barley"])
    year = st.selectbox("Survey Year", [2021, 2022, 2023, 2024])
    planting_month = st.selectbox("Planting Month", ["May", "Jun", "Jul", "Aug", "Sep"])

st.info("Model inference will load from models/final_model.joblib with automatic weather and price lookups.")
