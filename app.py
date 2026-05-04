# ============================================================
# HR4Techies Advanced People Analytics
# Prototipo Streamlit para análisis visual de datos de empleados
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image

# ============================================================
# CONFIGURACIÓN GENERAL DE LA APP
# ============================================================

st.set_page_config(
    page_title="HR4Techies Advanced People Analytics",
    layout="wide"
)

st.markdown("""
<style>

/* ===== FONDO GENERAL ===== */
.stApp {
    background-color: #F4FDF7;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background-color: #E8F5E9;
}

/* ===== TÍTULOS ===== */
h1, h2, h3 {
    color: #1B5E20;
    font-family: 'Arial', sans-serif;
}

/* ===== TEXTO NORMAL ===== */
body, p {
    color: #2E7D32;
}

/* ===== BOTONES ===== */
.stButton > button, 
.stDownloadButton > button {
    background-color: #2E7D32 !important;
    color: #FFFFFF !important;
    border-radius: 12px;
    border: none;
    padding: 10px 18px;
    font-weight: 700;
}

/* Texto interno del botón de descarga */
.stDownloadButton > button * {
    color: #FFFFFF !important;
}

/* Hover */
.stButton > button:hover, 
.stDownloadButton > button:hover {
    background-color: #1B5E20 !important;
    color: #FFFFFF !important;
}

/* ===== BLOQUES (INSIGHTS / ALERTAS) ===== */
.stAlert {
    border-radius: 14px;
}

/* ===== GRÁFICOS ===== */
[data-testid="stPlotlyChart"] {
    background-color: white;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.05);
}

/* ===== DATAFRAMES ===== */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* ===== MÉTRICAS ===== */
[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 4px 16px rgba(0,0,0,0.06);
}

/* ===== RADIO BUTTON (SIDEBAR) ===== */
div[role="radiogroup"] > label {
    color: #1B5E20;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)

# AQUÍ VA EL LOGO
logo = Image.open("Positivo verde.png")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(logo, width=250)

st.title("HR4Techies Advanced People Analytics")

st.write("""
Plataforma demo de People Analytics que convierte un CSV de empleados
en visualizaciones, insights y recomendaciones accionables para decisiones de talento.
""")


# ============================================================
# SUBIDA DEL CSV
# ============================================================

# INFORMACIÓN SOBRE EL FORMATO
st.markdown("### 📋 Formato requerido del CSV")

st.markdown("""
Este MVP funciona con un modelo de datos específico de People Analytics.

👉 Puedes usar el dataset de ejemplo para probar la herramienta:
https://raw.githubusercontent.com/Pablolg87/hr4techies-advanced-people-analytics/main/hr4techies_people_analytics_dataset.csv
""")

uploaded_file = st.file_uploader(
    "Sube tu archivo CSV",
    type=["csv"],
    key="main_csv_uploader"
)

if uploaded_file is None:
    st.info("Sube un CSV para comenzar el análisis.")
    st.stop()


# LEER CSV
df = pd.read_csv(uploaded_file)

# VALIDACIÓN DE COLUMNAS
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
    st.error("❌ El CSV no tiene el formato correcto")
    st.write("Faltan las siguientes columnas:")
    st.write(missing_columns)
    st.info("👉 Usa el dataset de ejemplo para probar la herramienta")
    st.stop()

# ============================================================
# LECTURA DEL DATASET
# ============================================================

uploaded_file.seek(0)
df = pd.read_csv(uploaded_file)


# ============================================================
# VALIDACIÓN BÁSICA DE COLUMNAS
# ============================================================

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
    st.error("El CSV no contiene todas las columnas necesarias.")
    st.write("Columnas que faltan:")
    st.write(missing_columns)
    st.stop()


# ============================================================
# VISTA GENERAL DEL DATASET
# ============================================================

st.header("Vista general del dataset")

st.subheader("Vista previa de los datos")
st.dataframe(df.head())

st.subheader("KPIs generales")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Empleados", df.shape[0])
col2.metric("Salario medio", f"{df['salary'].mean():,.0f} €")
col3.metric("Revenue total", f"{df['revenue_generated'].sum():,.0f} €")
col4.metric("Performance medio", f"{df['performance_score'].mean():.2f}")
col5.metric("Engagement medio", f"{df['engagement_score'].mean():.2f}")


# ============================================================
# CREACIÓN DE VARIABLES ENRIQUECIDAS
# ============================================================

df["revenue_salary_ratio"] = df["revenue_generated"] / df["salary"]

df["attrition_risk_score"] = (
    (5 - df["engagement_score"]) * 0.35 +
    (5 - df["work_life_balance_score"]) * 0.25 +
    df["absenteeism_days"] * 0.15 +
    (5 - df["performance_score"]) * 0.15 +
    df["attrition_flag"] * 1.5
)

df["attrition_risk_level"] = pd.cut(
    df["attrition_risk_score"],
    bins=[-1, 1.5, 2.5, 10],
    labels=["Bajo", "Medio", "Alto"]
)

df["talent_outlier_type"] = np.where(
    (df["performance_score"] >= 4.5) & (df["revenue_generated"] >= df["revenue_generated"].quantile(0.75)),
    "High Impact Talent",
    np.where(
        (df["engagement_score"] <= 3.3) & (df["revenue_generated"] >= df["revenue_generated"].quantile(0.75)),
        "Critical Retention Risk",
        "Normal"
    )
)

df["archetype"] = np.where(
    (df["performance_score"] >= 4.3) & (df["engagement_score"] >= 4.0),
    "High Impact Talent",
    np.where(
        (df["performance_score"] >= 3.8) & (df["engagement_score"] >= 3.8),
        "Stable Core",
        np.where(
            (df["performance_score"] < 3.5) & (df["engagement_score"] < 3.5),
            "At-Risk Contributor",
            "Emerging Talent"
        )
    )
)


# ============================================================
# SELECTOR DE MÓDULO
# ============================================================

st.sidebar.title("Módulos de análisis")

module = st.sidebar.radio(
    "Selecciona un módulo",
    [
        "Performance Analytics",
        "Strategic Attrition",
        "Intelligent Role Matching",
        "Talent Outliers",
        "Workforce Archetypes"
    ]
)


# ============================================================
# MÓDULO 1: PERFORMANCE ANALYTICS
# ============================================================

if module == "Performance Analytics":

    st.header("Performance Analytics")

    st.write("""
    Este módulo analiza el desempeño de los empleados combinando performance,
    evaluación, proyectos completados, revenue generado y salario.
    """)

    top_performers = df.sort_values(
        by="performance_score",
        ascending=False
    ).head(10)

    st.subheader("Top 10 empleados por performance")
    st.dataframe(
        top_performers[
            ["employee_name", "department", "role", "performance_score", "revenue_generated", "salary"]
        ]
    )

    st.subheader("Distribución de performance")
    fig = px.histogram(
        df,
        x="performance_score",
        nbins=20,
        color="department",
        title="Distribución de performance por departamento"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Performance vs Revenue")
    fig = px.scatter(
        df,
        x="performance_score",
        y="revenue_generated",
        color="department",
        size="salary",
        hover_data=["employee_name", "role", "seniority"],
        title="Performance vs Revenue generado"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Insight automático")
    high_perf_low_salary = df[
        (df["performance_score"] >= 4.5) &
        (df["salary"] < df["salary"].median())
    ]

    st.success(
        f"Se han detectado {len(high_perf_low_salary)} empleados con alto performance "
        f"y salario por debajo de la mediana. Son candidatos a revisión salarial o plan de retención."
    )


# ============================================================
# MÓDULO 2: STRATEGIC ATTRITION
# ============================================================

elif module == "Strategic Attrition":

    st.header("Strategic Attrition")

    st.write("""
    Este módulo identifica riesgo de fuga combinando engagement, work-life balance,
    absentismo, performance y señal histórica de attrition.
    """)

    st.subheader("Attrition rate por departamento")
    attrition_by_department = (
        df.groupby("department")["attrition_flag"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        attrition_by_department,
        x="department",
        y="attrition_flag",
        title="Tasa de attrition por departamento",
        labels={"attrition_flag": "Attrition rate"}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Engagement vs Work-Life Balance")
    fig = px.scatter(
        df,
        x="engagement_score",
        y="work_life_balance_score",
        color="attrition_risk_level",
        size="absenteeism_days",
        hover_data=["employee_name", "department", "role"],
        title="Riesgo de fuga: Engagement vs Work-Life Balance"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Empleados con mayor riesgo de fuga")
    high_risk = df.sort_values(
        by="attrition_risk_score",
        ascending=False
    ).head(15)

    st.dataframe(
        high_risk[
            [
                "employee_name",
                "department",
                "role",
                "engagement_score",
                "work_life_balance_score",
                "absenteeism_days",
                "attrition_risk_level"
            ]
        ]
    )

    st.warning(
        f"Se han identificado {len(df[df['attrition_risk_level'] == 'Alto'])} empleados "
        f"con riesgo alto de fuga."
    )


# ============================================================
# MÓDULO 3: INTELLIGENT ROLE MATCHING
# ============================================================

elif module == "Intelligent Role Matching":

    st.header("Intelligent Role Matching")

    st.write("""
    Este módulo recomienda posibles movimientos internos usando skills,
    seniority, performance y tipo de contribución.
    """)

    selected_employee = st.selectbox(
        "Selecciona un empleado",
        df["employee_name"].tolist()
    )

    employee = df[df["employee_name"] == selected_employee].iloc[0]

    st.subheader("Perfil del empleado")
    st.write(employee[["employee_name", "role", "department", "seniority", "skills", "performance_score"]])

    role_rules = {
        "Data Engineer": ["Python", "SQL", "AWS"],
        "ML Engineer": ["Python", "ML"],
        "People Analytics Specialist": ["HR Strategy", "Analytics"],
        "Sales Manager": ["Sales", "CRM", "Negotiation"],
        "Finance Manager": ["Excel", "Forecasting", "Accounting"],
        "Marketing Analyst": ["SEO", "Analytics", "Content"]
    }

    employee_skills = str(employee["skills"]).split(";")

    recommendations = []

    for target_role, required_skills in role_rules.items():
        matched_skills = len(set(employee_skills).intersection(set(required_skills)))
        match_score = matched_skills / len(required_skills)

        recommendations.append({
            "recommended_role": target_role,
            "match_score": round(match_score, 2),
            "matched_skills": matched_skills,
            "required_skills": ", ".join(required_skills)
        })

    recommendations_df = pd.DataFrame(recommendations).sort_values(
        by="match_score",
        ascending=False
    )

    st.subheader("Recomendaciones de roles internos")
    st.dataframe(recommendations_df)

    fig = px.bar(
        recommendations_df,
        x="recommended_role",
        y="match_score",
        title=f"Match score para {selected_employee}"
    )
    st.plotly_chart(fig, use_container_width=True)

    best_match = recommendations_df.iloc[0]

    st.success(
        f"Mejor recomendación: {best_match['recommended_role']} "
        f"con un match score de {best_match['match_score']}."
    )


# ============================================================
# MÓDULO 4: TALENT OUTLIERS
# ============================================================

elif module == "Talent Outliers":

    st.header("Talent Outliers")

    st.write("""
    Este módulo identifica empleados fuera del patrón normal combinando performance,
    revenue generado, salario y engagement.
    """)

    st.subheader("Mapa 3D de talento")

    fig = px.scatter_3d(
        df,
        x="performance_score",
        y="revenue_generated",
        z="engagement_score",
        color="talent_outlier_type",
        size="salary",
        hover_data=["employee_name", "department", "role", "typeofcontribution"],
        title="Talent Outliers 3D: Performance, Revenue y Engagement"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Outliers detectados")

    outliers = df[df["talent_outlier_type"] != "Normal"].sort_values(
        by="revenue_generated",
        ascending=False
    )

    st.dataframe(
        outliers[
            [
                "employee_name",
                "department",
                "role",
                "performance_score",
                "engagement_score",
                "revenue_generated",
                "salary",
                "talent_outlier_type"
            ]
        ]
    )

    st.info(
        "Los outliers permiten identificar talento diferencial, perfiles críticos "
        "o empleados con alto impacto económico pero posible riesgo de fuga."
    )


# ============================================================
# MÓDULO 5: WORKFORCE ARCHETYPES
# ============================================================

elif module == "Workforce Archetypes":

    st.header("Workforce Archetypes")

    st.write("""
    Este módulo segmenta la plantilla en arquetipos estratégicos según performance,
    engagement, revenue, tenure y tipo de contribución.
    """)

    st.subheader("Distribución de arquetipos")

    archetype_counts = df["archetype"].value_counts().reset_index()
    archetype_counts.columns = ["archetype", "employees"]

    fig = px.bar(
        archetype_counts,
        x="archetype",
        y="employees",
        title="Distribución de empleados por arquetipo"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Arquetipos en 3D")

    fig = px.scatter_3d(
        df,
        x="performance_score",
        y="engagement_score",
        z="tenure_years",
        color="archetype",
        size="revenue_generated",
        hover_data=["employee_name", "department", "role"],
        title="Workforce Archetypes 3D"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Perfil medio por arquetipo")

    archetype_profile = df.groupby("archetype")[
        [
            "performance_score",
            "engagement_score",
            "salary",
            "revenue_generated",
            "tenure_years",
            "training_hours"
        ]
    ].mean().reset_index()

    st.dataframe(archetype_profile)

    st.success(
        "Estos arquetipos ayudan a priorizar decisiones de retención, desarrollo, "
        "movilidad interna y planes de sucesión."
    )


# ============================================================
# DESCARGA DEL CSV ENRIQUECIDO
# ============================================================

st.sidebar.markdown("---")
st.sidebar.subheader("Descarga de resultados")

csv_output = df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="Descargar CSV enriquecido",
    data=csv_output,
    file_name="hr4techies_people_analytics_enriched.csv",
    mime="text/csv"
)