# ============================================================
# HR4Techies Advanced People Analytics
# Streamlit MVP - People Analytics Dashboard
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="HR4Techies Advanced People Analytics",
    layout="wide"
)


# ============================================================
# CSS CORPORATIVO
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

body, p {
    color: #2E7D32;
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

.stAlert {
    border-radius: 14px;
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

[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 4px 16px rgba(0,0,0,0.06);
}

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
    "producer": CORPORATE_GREEN,
    "support": BLUE,
    "manager": YELLOW
}

contribution_labels = {
    "producer": "Producer",
    "support": "Support",
    "manager": "Manager"
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

def format_money_compact(value: float) -> str:
    """Formatea importes grandes para KPIs."""
    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f} M€"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f} K€"

    return f"{value:,.0f} €"


def generate_attrition_recommendation(row: pd.Series) -> str:
    """Genera una recomendación accionable según el principal driver de riesgo."""
    if row["engagement_score"] < 3.5:
        return "Revisar engagement con manager"

    if row["work_life_balance_score"] < 3.5:
        return "Revisar carga de trabajo y balance"

    if row["absenteeism_days"] > 10:
        return "Analizar absentismo y posibles causas"

    if row["performance_score"] < 3.5:
        return "Revisar objetivos, encaje y soporte"

    return "Revisión individual con manager"


def plot_chart(fig):
    """Renderiza gráficos Plotly con ancho responsive."""
    st.plotly_chart(fig, width="stretch")


def show_dataframe(dataframe: pd.DataFrame):
    """Renderiza tablas con ancho responsive."""
    st.dataframe(dataframe, width="stretch")


# ============================================================
# HEADER
# ============================================================

logo_path = Path("Positivo verde.png")

if logo_path.exists():
    logo = Image.open(logo_path)
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

demo_csv_path = Path("hr4techies_people_analytics_dataset.csv")

if demo_csv_path.exists():
    with open(demo_csv_path, "rb") as file:
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

missing_columns = [column for column in required_columns if column not in df.columns]

if missing_columns:
    st.error("❌ El CSV no tiene el formato correcto.")
    st.write("Faltan las siguientes columnas:")
    st.write(missing_columns)
    st.info("👉 Usa el dataset de ejemplo para probar la herramienta.")
    st.stop()


# ============================================================
# LIMPIEZA Y ENRIQUECIMIENTO DEL DATASET
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

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=numeric_columns).copy()

df["typeofcontribution"] = (
    df["typeofcontribution"]
    .astype(str)
    .str.lower()
    .str.strip()
)

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

df["is_high_risk"] = df["attrition_risk_level"] == "Alto"

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
show_dataframe(df.head())


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

    total_revenue = df["revenue_generated"].sum()
    total_salary_cost = df["salary"].sum()
    avg_salary = df["salary"].mean()
    avg_performance = df["performance_score"].mean()

    revenue_vs_cost_ratio = (
        total_revenue / total_salary_cost
        if total_salary_cost != 0
        else 0
    )

    salary_roi = (
        ((total_revenue - total_salary_cost) / total_salary_cost) * 100
        if total_salary_cost != 0
        else 0
    )

    margin = total_revenue - total_salary_cost

    st.subheader("KPIs ejecutivos")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue anual", format_money_compact(total_revenue))
    col2.metric("Coste salarial", format_money_compact(total_salary_cost))
    col3.metric("Salario medio", format_money_compact(avg_salary))
    col4.metric("Performance media", f"{avg_performance:.2f}")

    st.caption("Revenue, coste salarial y salario medio están expresados en términos anuales.")

    st.subheader("Eficiencia económica de la plantilla")

    colA, colB, colC = st.columns(3)

    colA.metric("Revenue / Coste salarial", f"{revenue_vs_cost_ratio:.2f}x")
    colB.metric("ROI salarial", f"{salary_roi:.1f}%")
    colC.metric("Margen bruto estimado", format_money_compact(margin))

    st.info(
        f"El ratio Revenue / Coste salarial indica cuántos euros de revenue genera "
        f"la plantilla por cada euro invertido en salario. En este caso, cada 1 € "
        f"de coste salarial genera aproximadamente {revenue_vs_cost_ratio:.2f} € de revenue."
    )

    st.subheader("Top 10 empleados por performance")

    top_performers = (
        df.sort_values(by="performance_score", ascending=False)
        .head(10)
    )

    show_dataframe(
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

    st.subheader("Top 10 empleados por revenue generado")

    top_revenue = (
        df.sort_values(by="revenue_generated", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_revenue,
        x="revenue_generated",
        y="employee_name",
        color="typeofcontribution",
        color_discrete_map=contribution_color_map,
        orientation="h",
        hover_data=[
            "department",
            "role",
            "performance_score",
            "salary",
            "typeofcontribution"
        ],
        title="Top 10 empleados por revenue anual"
    )

    fig.update_layout(
        xaxis_title="Revenue anual (€)",
        yaxis_title="Empleado",
        yaxis={"categoryorder": "total ascending"},
        legend_title="Tipo de contribución"
    )

    plot_chart(fig)

    st.subheader("Performance media por departamento")

    performance_by_department = (
        df.groupby("department")
        .agg(
            avg_performance=("performance_score", "mean"),
            employees=("employee_id", "count")
        )
        .reset_index()
        .sort_values(by="avg_performance", ascending=False)
    )

    fig = px.bar(
        performance_by_department,
        x="department",
        y="avg_performance",
        color="department",
        color_discrete_map=department_color_map,
        hover_data=["employees"],
        title="Performance media por departamento"
    )

    fig.update_layout(
        xaxis_title="Departamento",
        yaxis_title="Performance media",
        showlegend=False
    )

    plot_chart(fig)

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
            "revenue_generated",
            "typeofcontribution"
        ],
        title="Performance vs Revenue generado anual"
    )

    fig.update_layout(
        xaxis_title="Performance score",
        yaxis_title="Revenue generado anual (€)",
        legend_title="Tipo de contribución",
        margin=dict(l=0, r=180, t=80, b=40)
    )

    plot_chart(fig)

    if correlation >= 0.5:
        st.success("Existe una correlación positiva relevante: a mayor performance, mayor revenue generado.")
    elif correlation >= 0.2:
        st.info("Existe una correlación positiva moderada entre performance y revenue.")
    elif correlation > -0.2:
        st.warning("La correlación entre performance y revenue es débil. Puede haber otros factores explicando el revenue.")
    else:
        st.error("La correlación es negativa. Conviene revisar el modelo de revenue, roles o asignación de objetivos.")

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
            "revenue_generated",
            "typeofcontribution"
        ],
        title="Top 10 empleados: Performance, Revenue anual y Salario anual"
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Performance",
            yaxis_title="Revenue anual (€)",
            zaxis_title="Salario anual (€)"
        ),
        legend_title="Tipo de contribución",
        margin=dict(l=0, r=220, t=80, b=40),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.02
        )
    )

    plot_chart(fig)

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
    Este módulo prioriza el riesgo de fuga desde una perspectiva accionable:
    impacto económico, criticidad por departamento y drivers principales del riesgo.
    """)

    high_risk_df = df[df["is_high_risk"]].copy()

    attrition_rate = df["attrition_flag"].mean()
    high_risk_count = len(high_risk_df)
    high_risk_revenue = high_risk_df["revenue_generated"].sum()

    top_department = (
        high_risk_df["department"].value_counts().idxmax()
        if not high_risk_df.empty
        else "N/A"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Attrition rate global", f"{attrition_rate:.1%}")
    col2.metric("Empleados riesgo alto", high_risk_count)
    col3.metric("Departamento más expuesto", top_department)
    col4.metric("Revenue en riesgo", format_money_compact(high_risk_revenue))

    st.caption(
        "Revenue en riesgo = suma del revenue anual generado por empleados clasificados como riesgo alto."
    )

    st.subheader("Exposición al riesgo por departamento")

    department_risk = (
        df.groupby("department")
        .agg(
            employees=("employee_id", "count"),
            high_risk_employees=("is_high_risk", "sum"),
            revenue_at_risk=(
                "revenue_generated",
                lambda x: x[df.loc[x.index, "is_high_risk"]].sum()
            ),
            salary_at_risk=(
                "salary",
                lambda x: x[df.loc[x.index, "is_high_risk"]].sum()
            )
        )
        .reset_index()
    )

    department_risk["high_risk_rate"] = (
        department_risk["high_risk_employees"] / department_risk["employees"]
    )

    department_risk = department_risk.sort_values(
        by="revenue_at_risk",
        ascending=True
    )

    fig = px.bar(
        department_risk,
        x="revenue_at_risk",
        y="department",
        color="department",
        color_discrete_map=department_color_map,
        orientation="h",
        hover_data=[
            "employees",
            "high_risk_employees",
            "high_risk_rate",
            "salary_at_risk"
        ],
        title="Revenue anual en riesgo por departamento"
    )

    fig.update_layout(
        xaxis_title="Revenue anual en riesgo (€)",
        yaxis_title="Departamento",
        showlegend=False
    )

    plot_chart(fig)

    st.info(
        "Este gráfico prioriza dónde actuar primero: departamentos con más revenue anual "
        "concentrado en empleados de riesgo alto."
    )

    st.subheader("Principales drivers del riesgo de fuga")

    if not high_risk_df.empty:

        driver_data = pd.DataFrame({
            "driver": [
                "Bajo engagement",
                "Bajo work-life balance",
                "Alto absentismo",
                "Bajo performance"
            ],
            "employees_affected": [
                (high_risk_df["engagement_score"] < 3.5).sum(),
                (high_risk_df["work_life_balance_score"] < 3.5).sum(),
                (high_risk_df["absenteeism_days"] > df["absenteeism_days"].median()).sum(),
                (high_risk_df["performance_score"] < 3.5).sum()
            ]
        })

        driver_data = driver_data.sort_values("employees_affected", ascending=True)

        fig = px.bar(
            driver_data,
            x="employees_affected",
            y="driver",
            orientation="h",
            text="employees_affected",
            color="driver",
            color_discrete_map={
                "Bajo engagement": RED,
                "Bajo work-life balance": ORANGE,
                "Alto absentismo": YELLOW,
                "Bajo performance": GREY
            },
            title="Drivers más frecuentes entre empleados de riesgo alto"
        )

        fig.update_layout(
            xaxis_title="Empleados afectados",
            yaxis_title="Driver",
            showlegend=False
        )

        plot_chart(fig)

        main_driver = driver_data.sort_values(
            "employees_affected",
            ascending=False
        ).iloc[0]

        st.warning(
            f"Principal driver detectado: {main_driver['driver']} "
            f"({int(main_driver['employees_affected'])} empleados de riesgo alto)."
        )

    else:
        st.info("No hay empleados clasificados como riesgo alto.")

    st.subheader("Matriz de acción: impacto económico vs engagement")

    fig = px.scatter(
        df,
        x="engagement_score",
        y="revenue_generated",
        color="attrition_risk_level",
        color_discrete_map=risk_color_map,
        size="salary",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "work_life_balance_score",
            "absenteeism_days",
            "salary",
            "revenue_generated",
            "attrition_risk_score"
        ],
        title="Impacto económico vs engagement"
    )

    fig.add_vline(
        x=3.5,
        line_dash="dash",
        line_color=RED,
        annotation_text="Engagement bajo",
        annotation_position="top left"
    )

    fig.add_hline(
        y=df["revenue_generated"].quantile(0.75),
        line_dash="dash",
        line_color=CORPORATE_GREEN,
        annotation_text="Alto revenue",
        annotation_position="top right"
    )

    fig.update_layout(
        xaxis_title="Engagement score",
        yaxis_title="Revenue anual (€)",
        legend_title="Nivel de riesgo"
    )

    plot_chart(fig)

    st.info(
        "Prioridad máxima: empleados con bajo engagement y alto revenue. "
        "Son perfiles con impacto económico relevante y mayor sensibilidad de fuga."
    )

    st.subheader("Plan de acción recomendado")

    action_df = (
        df.sort_values(by="attrition_risk_score", ascending=False)
        .head(15)
        .copy()
    )

    action_df["recommendation"] = action_df.apply(
        generate_attrition_recommendation,
        axis=1
    )

    show_dataframe(
        action_df[
            [
                "employee_name",
                "department",
                "role",
                "revenue_generated",
                "salary",
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

    show_dataframe(
        pd.DataFrame(
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
        ).rename(columns={employee.name: "value"})
    )

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

    recommendations_df = (
        pd.DataFrame(recommendations)
        .sort_values(by="match_score", ascending=False)
    )

    best_match = recommendations_df.iloc[0]

    st.subheader("Mejor opción para siguiente puesto")

    st.metric(
        label="Rol recomendado",
        value=best_match["recommended_role"],
        delta=f"Match score: {best_match['match_score']:.2f}"
    )

    st.subheader("Recomendaciones de roles internos")

    show_dataframe(recommendations_df)

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

    outliers = (
        df[df["talent_outlier_type"] != "Normal"]
        .sort_values(by="revenue_generated", ascending=False)
        .copy()
    )

    outliers_by_contribution = outliers["typeofcontribution"].value_counts()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Outliers detectados", len(outliers))
    col2.metric("Outliers producer", outliers_by_contribution.get("producer", 0))
    col3.metric("Outliers support", outliers_by_contribution.get("support", 0))
    col4.metric("Outliers manager", outliers_by_contribution.get("manager", 0))

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
        legend_title="Tipo de outlier",
        margin=dict(l=0, r=240, t=80, b=40),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.02
        )
    )

    plot_chart(fig)

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
        legend_title="Tipo de contribución",
        margin=dict(l=0, r=220, t=80, b=40),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.02
        )
    )

    plot_chart(fig)

    st.subheader("Outliers detectados")

    show_dataframe(
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

    st.subheader("Distribución de outliers por tipo de contribución")

    if not outliers.empty:
        outliers_contribution = (
            outliers["typeofcontribution"]
            .value_counts()
            .reset_index()
        )

        outliers_contribution.columns = ["type", "count"]
        outliers_contribution["type_label"] = (
            outliers_contribution["type"]
            .map(contribution_labels)
            .fillna(outliers_contribution["type"])
        )

        fig = px.pie(
            outliers_contribution,
            names="type_label",
            values="count",
            color="type",
            color_discrete_map=contribution_color_map,
            hole=0.5,
            title="Proporción de outliers por tipo de contribución"
        )

        fig.update_traces(
            textinfo="label+percent",
            textfont_size=14,
            hovertemplate="<b>%{label}</b><br>Outliers: %{value}<extra></extra>"
        )

        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=80, b=20)
        )

        plot_chart(fig)

        top_type = outliers_contribution.sort_values(
            by="count",
            ascending=False
        ).iloc[0]

        st.info(
            f"La mayor concentración de outliers se encuentra en perfiles tipo "
            f"{top_type['type_label']}. Este grupo requiere mayor atención estratégica."
        )

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

    plot_chart(fig)

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
            zaxis_title="Tenure"
        ),
        legend_title="Arquetipo",
        margin=dict(l=0, r=240, t=80, b=40),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.02
        )
    )

    plot_chart(fig)

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

    show_dataframe(archetype_profile)

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