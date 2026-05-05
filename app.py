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


# ============================================================
# ESTILOS CSS
# ============================================================

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

.stDownloadButton > button * {
    color: #FFFFFF !important;
}

.stButton > button:hover, 
.stDownloadButton > button:hover {
    background-color: #1B5E20 !important;
    color: #FFFFFF !important;
}

/* ===== BLOQUES ===== */
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

/* ===== RADIO BUTTON SIDEBAR ===== */
div[role="radiogroup"] > label {
    color: #1B5E20;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# PALETA CORPORATIVA
# ============================================================

CORPORATE_GREEN = "#2E7D32"
DARK_GREEN = "#1B5E20"
LIGHT_GREEN = "#A5D6A7"
SOFT_GREEN = "#E8F5E9"

BLUE = "#1976D2"
YELLOW = "#F9A825"
ORANGE = "#FB8C00"
RED = "#D32F2F"
GREY = "#78909C"

department_color_map = {
    "HR": CORPORATE_GREEN,
    "IT": BLUE,
    "Finance": GREY,
    "Sales": ORANGE,
    "Marketing": YELLOW
}

contribution_color_map = {
    "Producer": CORPORATE_GREEN,
    "Support": BLUE,
    "Hybrid": YELLOW
}

risk_color_map = {
    "Bajo": LIGHT_GREEN,
    "Medio": YELLOW,
    "Alto": RED
}

outlier_color_map = {
    "Normal": LIGHT_GREEN,
    "High Impact Talent": CORPORATE_GREEN,
    "Critical Retention Risk": RED
}

archetype_color_map = {
    "High Impact Talent": CORPORATE_GREEN,
    "Stable Core": BLUE,
    "Emerging Talent": YELLOW,
    "At-Risk Contributor": RED
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def format_euros(value):
    """Formatea valores numéricos como euros."""
    return f"{value:,.0f} €"


def generate_attrition_recommendation(row):
    """Genera una recomendación accionable según los drivers de riesgo."""
    if row["engagement_score"] < 3.5:
        return "Revisar engagement con manager"
    if row["work_life_balance_score"] < 3.5:
        return "Revisar carga de trabajo y balance"
    if row["absenteeism_days"] > 10:
        return "Analizar absentismo y posibles causas"
    if row["performance_score"] < 3.5:
        return "Revisar encaje, objetivos y soporte"
    return "Revisión individual con manager"


# ============================================================
# HEADER Y LOGO
# ============================================================

logo = Image.open("Positivo verde.png")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=250)

st.title("HR4Techies Advanced People Analytics")

st.write("""
Plataforma demo de People Analytics que convierte un CSV de empleados
en visualizaciones, insights y recomendaciones accionables para decisiones de talento.
""")


# ============================================================
# SUBIDA Y VALIDACIÓN DEL CSV
# ============================================================

st.markdown("### 📋 Formato requerido del CSV")

st.markdown("""
Este MVP funciona con un modelo de datos específico de People Analytics.

Descarga el dataset de ejemplo y súbelo para probar la herramienta.
""")

with open("hr4techies_people_analytics_dataset.csv", "rb") as file:
    st.download_button(
        label="📥 Descargar CSV demo",
        data=file,
        file_name="hr4techies_people_analytics_dataset.csv",
        mime="text/csv"
    )

uploaded_file = st.file_uploader(
    "Sube tu archivo CSV",
    type=["csv"],
    key="main_csv_uploader"
)

if uploaded_file is None:
    st.info("Sube un CSV para comenzar el análisis.")
    st.stop()

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
    st.write("Faltan las siguientes columnas:")
    st.write(missing_columns)
    st.info("👉 Usa el dataset de ejemplo para probar la herramienta.")
    st.stop()


# ============================================================
# LIMPIEZA BÁSICA Y VARIABLES ENRIQUECIDAS
# ============================================================

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

df = df.dropna(subset=numeric_columns)

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
    (df["performance_score"] >= 4.5) &
    (df["revenue_generated"] >= df["revenue_generated"].quantile(0.75)),
    "High Impact Talent",
    np.where(
        (df["engagement_score"] <= 3.3) &
        (df["revenue_generated"] >= df["revenue_generated"].quantile(0.75)),
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
# VISTA GENERAL DEL DATASET
# ============================================================

st.header("Vista general del dataset")

st.subheader("Vista previa de los datos")
st.dataframe(df.head())

st.subheader("KPIs generales")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Empleados", df.shape[0])
col2.metric("Salario medio anual", format_euros(df["salary"].mean()))
col3.metric("Revenue total anual", format_euros(df["revenue_generated"].sum()))
col4.metric("Performance medio", f"{df['performance_score'].mean():.2f}")
col5.metric("Engagement medio", f"{df['engagement_score'].mean():.2f}")


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
    Este módulo analiza la relación entre performance, revenue generado,
    coste salarial y tipo de contribución.
    """)

    # KPIs financieros

    total_revenue = df["revenue_generated"].sum()
    total_salary_cost = df["salary"].sum()
    avg_salary = df["salary"].mean()
    avg_performance = df["performance_score"].mean()
    revenue_vs_cost_ratio = total_revenue / total_salary_cost if total_salary_cost else 0
    margin = total_revenue - total_salary_cost

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue total anual", format_euros(total_revenue))
    col2.metric("Coste salarial total anual", format_euros(total_salary_cost))
    col3.metric("Salario medio anual", format_euros(avg_salary))
    col4.metric("Performance medio", f"{avg_performance:.2f}")

    st.caption("Todos los valores económicos están expresados en términos anuales.")

    st.subheader("Eficiencia económica de la plantilla")

    colA, colB = st.columns(2)

    colA.metric("Ratio Revenue / Coste salarial", f"{revenue_vs_cost_ratio:.2f}")
    colB.metric("Margen bruto estimado", format_euros(margin))

    if revenue_vs_cost_ratio >= 2:
        st.success("Modelo altamente rentable: el revenue duplica el coste salarial.")
    elif revenue_vs_cost_ratio >= 1.2:
        st.info("Modelo sostenible: el revenue cubre el coste salarial con margen moderado.")
    elif revenue_vs_cost_ratio >= 1:
        st.warning("Modelo ajustado: el revenue apenas cubre el coste salarial.")
    else:
        st.error("Modelo no rentable: el coste salarial supera el revenue generado.")

    # Top performers

    top_performers = df.sort_values(
        by="performance_score",
        ascending=False
    ).head(10)

    st.subheader("Top 10 empleados por performance")

    st.dataframe(
        top_performers[
            [
                "employee_name",
                "department",
                "role",
                "typeofcontribution",
                "performance_score",
                "revenue_generated",
                "salary"
            ]
        ]
    )

    # Distribución de performance

    st.subheader("Distribución de performance por departamento")

    fig = px.box(
        df,
        x="department",
        y="performance_score",
        color="department",
        color_discrete_map=department_color_map,
        points="all",
        hover_data=["employee_name", "role", "seniority", "typeofcontribution"],
        title="Distribución de performance por departamento"
    )

    fig.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Performance score",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Correlación Performance / Revenue

    st.subheader("Correlación entre performance y revenue generado")

    correlation = df["performance_score"].corr(df["revenue_generated"])

    st.metric(
        "Coeficiente de correlación Performance / Revenue",
        f"{correlation:.2f}"
    )

    fig = px.scatter(
        df,
        x="performance_score",
        y="revenue_generated",
        color="typeofcontribution",
        color_discrete_map=contribution_color_map,
        size="salary",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "seniority",
            "salary",
            "revenue_generated"
        ],
        trendline="ols",
        title="Performance vs Revenue generado anual"
    )

    fig.update_layout(
        xaxis_title="Performance score",
        yaxis_title="Revenue generado anual (€)",
        legend_title="Tipo de contribución"
    )

    st.plotly_chart(fig, use_container_width=True)

    if correlation >= 0.5:
        st.success("Existe una correlación positiva relevante: a mayor performance, mayor revenue generado.")
    elif correlation >= 0.2:
        st.info("Existe una correlación positiva moderada entre performance y revenue.")
    elif correlation > -0.2:
        st.warning("La correlación entre performance y revenue es débil. Puede haber otros factores explicando el revenue.")
    else:
        st.error("La correlación es negativa. Conviene revisar el modelo de revenue, roles o asignación de objetivos.")

    # Top 10 en 3D

    st.subheader("Top 10 performers en 3D: Revenue, Performance y Salario")

    fig = px.scatter_3d(
        top_performers,
        x="performance_score",
        y="revenue_generated",
        z="salary",
        color="typeofcontribution",
        color_discrete_map=contribution_color_map,
        size="revenue_generated",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "seniority",
            "salary",
            "revenue_generated"
        ],
        title="Top 10 empleados: Performance, Revenue anual y Salario anual"
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Performance score",
            yaxis_title="Revenue anual (€)",
            zaxis_title="Salario anual (€)"
        ),
        legend_title="Tipo de contribución"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Insight automático

    st.subheader("Insight automático")

    high_perf_low_salary = df[
        (df["performance_score"] >= 4.5) &
        (df["salary"] < df["salary"].median())
    ]

    st.success(
        f"Se han detectado {len(high_perf_low_salary)} empleados con alto performance "
        f"y salario anual por debajo de la mediana. Son candidatos a revisión salarial "
        f"o plan de retención."
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

    # KPIs de attrition

    attrition_rate = df["attrition_flag"].mean()
    high_risk_count = len(df[df["attrition_risk_level"] == "Alto"])

    top_department = (
        df.groupby("department")["attrition_flag"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    high_risk_engagement = df[df["attrition_risk_level"] == "Alto"]["engagement_score"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Attrition rate global", f"{attrition_rate:.2%}")
    col2.metric("Empleados riesgo alto", high_risk_count)
    col3.metric("Departamento crítico", top_department)
    col4.metric("Engagement riesgo alto", f"{high_risk_engagement:.2f}")

    # Attrition por departamento

    st.subheader("Attrition rate por departamento")

    attrition_by_department = (
        df.groupby("department")
        .agg(
            attrition_rate=("attrition_flag", "mean"),
            employees=("employee_id", "count")
        )
        .reset_index()
        .sort_values(by="attrition_rate", ascending=False)
    )

    fig = px.bar(
        attrition_by_department,
        x="department",
        y="attrition_rate",
        color="department",
        color_discrete_map=department_color_map,
        hover_data=["employees"],
        title="Tasa de attrition por departamento"
    )

    fig.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Attrition rate",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Heatmap Engagement vs Work-Life Balance

    st.subheader("Mapa de riesgo: Engagement vs Work-Life Balance")

    heatmap_df = df.copy()
    heatmap_df["engagement_range"] = pd.cut(
        heatmap_df["engagement_score"],
        bins=5
    ).astype(str)

    heatmap_df["wlb_range"] = pd.cut(
        heatmap_df["work_life_balance_score"],
        bins=5
    ).astype(str)

    heatmap_data = (
        heatmap_df.groupby(["engagement_range", "wlb_range"])
        .agg(
            employees=("employee_id", "count"),
            avg_risk=("attrition_risk_score", "mean")
        )
        .reset_index()
    )

    fig = px.density_heatmap(
        heatmap_data,
        x="engagement_range",
        y="wlb_range",
        z="avg_risk",
        color_continuous_scale=["#E8F5E9", "#F9A825", "#D32F2F"],
        title="Riesgo medio por combinación de engagement y work-life balance",
        hover_data=["employees", "avg_risk"]
    )

    fig.update_layout(
        xaxis_title="Rango de engagement",
        yaxis_title="Rango de work-life balance"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    Las zonas más intensas muestran combinaciones donde el riesgo medio de fuga es superior.
    """)

    # Top 15 riesgo

    st.subheader("Top 15 empleados con mayor riesgo de fuga")

    high_risk = df.sort_values(
        by="attrition_risk_score",
        ascending=False
    ).head(15).copy()

    fig = px.bar(
        high_risk,
        x="attrition_risk_score",
        y="employee_name",
        color="department",
        color_discrete_map=department_color_map,
        orientation="h",
        hover_data=[
            "department",
            "role",
            "engagement_score",
            "work_life_balance_score",
            "absenteeism_days",
            "attrition_risk_level"
        ],
        title="Ranking de riesgo de fuga"
    )

    fig.update_layout(
        xaxis_title="Attrition risk score",
        yaxis_title="Empleado",
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabla accionable

    st.subheader("Tabla accionable de empleados en riesgo")

    high_risk["recommendation"] = high_risk.apply(
        generate_attrition_recommendation,
        axis=1
    )

    st.dataframe(
        high_risk[
            [
                "employee_name",
                "department",
                "role",
                "engagement_score",
                "work_life_balance_score",
                "absenteeism_days",
                "attrition_risk_level",
                "recommendation"
            ]
        ]
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

    st.write(
        employee[
            [
                "employee_name",
                "role",
                "department",
                "seniority",
                "skills",
                "typeofcontribution",
                "performance_score"
            ]
        ]
    )

    # Reglas iniciales de matching.
    # En una versión futura, esto podría sustituirse por embeddings,
    # skill taxonomy o matching semántico.

    role_rules = {
        "Data Engineer": ["Python", "SQL", "AWS"],
        "ML Engineer": ["Python", "ML"],
        "People Analytics Specialist": ["HR Strategy", "Analytics"],
        "Sales Manager": ["Sales", "CRM", "Negotiation"],
        "Finance Manager": ["Excel", "Forecasting", "Accounting"],
        "Marketing Analyst": ["SEO", "Analytics", "Content"]
    }

    employee_skills = [
        skill.strip()
        for skill in str(employee["skills"]).split(";")
    ]

    recommendations = []

    for target_role, required_skills in role_rules.items():
        matched_skills = len(
            set(employee_skills).intersection(set(required_skills))
        )

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

    best_match = recommendations_df.iloc[0]

    st.subheader("Mejor opción para siguiente puesto")

    st.metric(
        label="Rol recomendado",
        value=best_match["recommended_role"],
        delta=f"Match score: {best_match['match_score']:.2f}"
    )

    st.subheader("Recomendaciones de roles internos")

    st.dataframe(recommendations_df)

    st.success(
        f"La mejor recomendación para {selected_employee} es "
        f"{best_match['recommended_role']} con un match score de "
        f"{best_match['match_score']:.2f}."
    )


# ============================================================
# MÓDULO 4: TALENT OUTLIERS
# ============================================================

elif module == "Talent Outliers":

    st.header("Talent Outliers")

    st.write("""
    Este módulo identifica empleados fuera del patrón normal combinando performance,
    revenue generado, salario, engagement y tipo de contribución.
    """)

    outliers = df[df["talent_outlier_type"] != "Normal"].sort_values(
        by="revenue_generated",
        ascending=False
    ).copy()

    # KPIs de outliers

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Outliers detectados", len(outliers))
    col2.metric(
        "Outliers Producer",
        len(outliers[outliers["typeofcontribution"] == "Producer"])
    )
    col3.metric(
        "Outliers Support",
        len(outliers[outliers["typeofcontribution"] == "Support"])
    )
    col4.metric(
        "Outliers Hybrid",
        len(outliers[outliers["typeofcontribution"] == "Hybrid"])
    )

    # 3D por tipo de outlier

    st.subheader("Mapa 3D de outliers")

    fig = px.scatter_3d(
        df,
        x="performance_score",
        y="revenue_generated",
        z="engagement_score",
        color="talent_outlier_type",
        color_discrete_map=outlier_color_map,
        size="salary",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "typeofcontribution",
            "salary",
            "revenue_generated"
        ],
        title="Talent Outliers 3D: Performance, Revenue y Engagement"
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Performance",
            yaxis_title="Revenue anual (€)",
            zaxis_title="Engagement"
        ),
        legend_title="Tipo de outlier"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 3D por tipo de contribución

    st.subheader("Mapa 3D por tipo de contribución")

    fig = px.scatter_3d(
        df,
        x="performance_score",
        y="revenue_generated",
        z="engagement_score",
        color="typeofcontribution",
        color_discrete_map=contribution_color_map,
        size="salary",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "seniority",
            "talent_outlier_type",
            "salary",
            "revenue_generated"
        ],
        title="Distribución del talento por tipo de contribución"
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Performance",
            yaxis_title="Revenue anual (€)",
            zaxis_title="Engagement"
        ),
        legend_title="Tipo de contribución"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabla de outliers

    st.subheader("Outliers detectados")

    st.dataframe(
        outliers[
            [
                "employee_name",
                "department",
                "role",
                "typeofcontribution",
                "performance_score",
                "engagement_score",
                "revenue_generated",
                "salary",
                "talent_outlier_type"
            ]
        ]
    )

    # Distribución de outliers por tipo de contribución

    st.subheader("Distribución de outliers por tipo de contribución")

    if len(outliers) > 0:
        outlier_contribution = (
            outliers["typeofcontribution"]
            .value_counts(normalize=True)
            .reset_index()
        )

        outlier_contribution.columns = ["typeofcontribution", "proportion"]
        outlier_contribution["percentage"] = outlier_contribution["proportion"] * 100

        fig = px.pie(
            outlier_contribution,
            names="typeofcontribution",
            values="percentage",
            hole=0.45,
            title="Proporción de outliers por tipo de contribución",
            color="typeofcontribution",
            color_discrete_map=contribution_color_map
        )

        fig.update_traces(
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Proporción: %{percent}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No se han detectado outliers con las reglas actuales.")

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

    # Distribución de arquetipos

    st.subheader("Distribución de arquetipos")

    archetype_counts = df["archetype"].value_counts().reset_index()
    archetype_counts.columns = ["archetype", "employees"]

    fig = px.bar(
        archetype_counts,
        x="archetype",
        y="employees",
        color="archetype",
        color_discrete_map=archetype_color_map,
        title="Distribución de empleados por arquetipo"
    )

    fig.update_layout(
        xaxis_title="Arquetipo",
        yaxis_title="Empleados",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Arquetipos en 3D

    st.subheader("Arquetipos en 3D")

    fig = px.scatter_3d(
        df,
        x="performance_score",
        y="engagement_score",
        z="tenure_years",
        color="archetype",
        color_discrete_map=archetype_color_map,
        size="revenue_generated",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "typeofcontribution",
            "salary",
            "revenue_generated"
        ],
        title="Workforce Archetypes 3D"
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Performance",
            yaxis_title="Engagement",
            zaxis_title="Tenure años"
        ),
        legend_title="Arquetipo"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Perfil medio por arquetipo

    st.subheader("Perfil medio por arquetipo")

    archetype_profile = (
        df.groupby("archetype")[
            [
                "performance_score",
                "engagement_score",
                "salary",
                "revenue_generated",
                "tenure_years",
                "training_hours"
            ]
        ]
        .mean()
        .reset_index()
    )

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