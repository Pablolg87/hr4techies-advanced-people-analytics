# ============================================================
# HR4Techies Advanced People Analytics
# MVP Streamlit para análisis visual de datos de empleados
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="HR4Techies Advanced People Analytics",
    layout="wide"
)


# ============================================================
# ESTILOS CORPORATIVOS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4FDF7;
}

section[data-testid="stSidebar"] {
    background-color: #E8F5E9;
}

h1, h2, h3 {
    color: #1B5E20;
    font-family: Arial, sans-serif;
}

p, label, span {
    color: #2E7D32;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 4px 16px rgba(0,0,0,0.06);
}

[data-testid="stPlotlyChart"] {
    background-color: white;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.05);
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

.stAlert {
    border-radius: 14px;
}

.stButton > button,
.stDownloadButton > button {
    background-color: #2E7D32 !important;
    color: #FFFFFF !important;
    border-radius: 12px;
    border: none;
    padding: 10px 18px;
    font-weight: 700;
}

.stDownloadButton > button * {
    color: #FFFFFF !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #1B5E20 !important;
    color: #FFFFFF !important;
}

div[role="radiogroup"] > label {
    color: #1B5E20;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

try:
    logo = Image.open("Positivo verde.png")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo, width=260)
except FileNotFoundError:
    st.warning("Logo no encontrado. Revisa el nombre del archivo.")

st.title("HR4Techies Advanced People Analytics")

st.markdown("""
Plataforma demo de **People Analytics** que convierte un CSV de empleados en
visualizaciones, insights y recomendaciones accionables para decisiones de talento.
""")


# ============================================================
# FORMATO Y DATASET DEMO
# ============================================================

st.markdown("## 📋 Formato requerido del CSV")

st.info("""
Este MVP funciona con un modelo de datos específico de People Analytics.

Puedes descargar el dataset demo, subirlo en el uploader y probar todos los módulos.
""")

try:
    with open("hr4techies_people_analytics_dataset.csv", "rb") as file:
        st.download_button(
            label="📥 Descargar CSV demo",
            data=file,
            file_name="hr4techies_people_analytics_dataset.csv",
            mime="text/csv"
        )
except FileNotFoundError:
    st.error("No se ha encontrado el CSV demo en el repositorio.")


# ============================================================
# SUBIDA DEL CSV
# ============================================================

uploaded_file = st.file_uploader(
    "Sube tu archivo CSV",
    type=["csv"],
    key="main_csv_uploader"
)

if uploaded_file is None:
    st.info("Sube un CSV para comenzar el análisis.")
    st.stop()


# ============================================================
# LECTURA Y VALIDACIÓN DEL DATASET
# ============================================================

df = pd.read_csv(uploaded_file)

required_columns = [
    "employee_id",
    "employee_name",
    "department",
    "role",
    "location",
    "seniority",
    "typeofcontribution",
    "salary",
    "revenue_generated",
    "tenure_years",
    "contract_type",
    "performance_score",
    "projects_completed",
    "last_evaluation_score",
    "promotion_last_2_years",
    "engagement_score",
    "training_hours",
    "absenteeism_days",
    "work_life_balance_score",
    "skills",
    "attrition_flag"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error("❌ El CSV no tiene el formato correcto.")
    st.write("Columnas faltantes:")
    st.write(missing_columns)
    st.info("Descarga el CSV demo y usa esa estructura como plantilla.")
    st.stop()

numeric_columns = [
    "salary",
    "revenue_generated",
    "tenure_years",
    "performance_score",
    "projects_completed",
    "last_evaluation_score",
    "promotion_last_2_years",
    "engagement_score",
    "training_hours",
    "absenteeism_days",
    "work_life_balance_score",
    "attrition_flag"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

if df[numeric_columns].isnull().any().any():
    st.error("❌ Algunas columnas numéricas contienen valores no válidos.")
    st.info("Revisa el CSV o usa el dataset demo incluido.")
    st.stop()