# ============================================================
# HR4Techies Advanced People Analytics
# Streamlit MVP - AI-Powered Workforce Intelligence Platform
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# Optional ML imports. The app still works if sklearn is unavailable.
try:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


# CONFIGURACIÓN GENERAL


st.set_page_config(
    page_title="HR4Techies Advanced People Analytics",
    layout="wide"
)


# CSS CORPORATIVO


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

body, p, label, span {
    color: #263238;
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

.small-muted {
    color: #607D8B;
    font-size: 0.9rem;
}

</style>
""", unsafe_allow_html=True)


# PALETA CORPORATIVA Y MAPAS DE COLOR


CORPORATE_GREEN = "#2E7D32"
DARK_GREEN = "#1B5E20"
LIGHT_GREEN = "#A5D6A7"
SOFT_GREEN = "#E8F5E9"

BLUE = "#4C78A8"
YELLOW = "#F2C14E"
ORANGE = "#F28E2B"
RED = "#E15759"
GREY = "#8A9BA8"
PURPLE = "#8E6C8A"
TEAL = "#2A9D8F"

contribution_color_map = {
    "producer": CORPORATE_GREEN,
    "support": BLUE,
    "manager": ORANGE
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
    "Normal": GREY,
    "High Impact Talent": CORPORATE_GREEN,
    "Critical Retention Risk": RED,
    "Burnout Risk": ORANGE,
    "Hidden Potential": BLUE,
    "Economic Risk": YELLOW,
    "Silent Star": TEAL,
    "Talent Outlier": PURPLE
}

archetype_color_map = {
    "High Impact Talent": CORPORATE_GREEN,
    "Stable Core": BLUE,
    "Emerging Talent": YELLOW,
    "At-Risk Contributor": RED
}

engagement_segment_color_map = {
    "Champions": CORPORATE_GREEN,
    "Stable": BLUE,
    "Burnout Risk": ORANGE,
    "Disconnected": RED
}

promotion_color_map = {
    "Promotion Ready": CORPORATE_GREEN,
    "Emerging Leader": BLUE,
    "Needs Development": ORANGE
}

health_segment_color_map = {
    "Healthy Teams": CORPORATE_GREEN,
    "Burnout Risk": ORANGE,
    "Disconnected Teams": RED,
    "High Pressure Teams": YELLOW
}

location_color_sequence = [
    CORPORATE_GREEN,
    BLUE,
    ORANGE,
    YELLOW,
    PURPLE,
    TEAL,
    GREY,
    RED
]


# FUNCIONES AUXILIARES GENERALES


def format_money_compact(value: float) -> str:
    """Formatea importes grandes para KPIs ejecutivos."""
    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f} M€"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f} K€"

    return f"{value:,.0f} €"


def normalize_series(series: pd.Series) -> pd.Series:
    """Normaliza una serie entre 0 y 1 evitando divisiones por cero."""
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum) or maximum == minimum:
        return pd.Series(0.5, index=series.index)

    return (series - minimum) / (maximum - minimum)


def plot_chart(fig):
    """Aplica estilo global y renderiza gráficos Plotly."""
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#263238"),
        margin=dict(l=40, r=220, t=80, b=50),
        legend=dict(
            orientation="v",
            x=1.02,
            y=1,
            xanchor="left",
            yanchor="top",
            title_font=dict(size=13),
            font=dict(size=12)
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def show_dataframe(dataframe: pd.DataFrame, height: int | None = None):
    """Renderiza tablas con ancho responsive."""

    if height is None:
        st.dataframe(dataframe, use_container_width=True)

    else:
        st.dataframe(
            dataframe,
            use_container_width=True,
            height=height
        )


def show_dataset_preview(dataframe: pd.DataFrame):
    """Muestra una vista rápida de los primeros 10 empleados."""

    st.subheader("Vista previa del dataset")

    preview_columns = [
        "employee_name",
        "department",
        "role",
        "location",
        "seniority",
        "typeofcontribution",
        "contract_type",
        "salary",
        "real_salary_cost",
        "revenue_generated",
        "performance_score",
        "engagement_score"
    ]

    available_columns = [column for column in preview_columns if column in dataframe.columns]
    show_dataframe(dataframe[available_columns].head(10))


def contribution_filter(dataframe: pd.DataFrame, key: str) -> pd.DataFrame:
    """Filtro común por tipo de contribución."""
    options = ["All"] + sorted(dataframe["typeofcontribution"].dropna().unique().tolist())

    selected = st.selectbox(
        "Filtrar por tipo de contribución",
        options=options,
        key=key
    )

    if selected == "All":
        return dataframe.copy()

    return dataframe[dataframe["typeofcontribution"] == selected].copy()


def get_country_multiplier(location: str) -> float:
    """
    Estima coste empresa según ubicación.
    Multiplicador = salario bruto anual + costes sociales patronales aproximados.
    """
    if pd.isna(location):
        return 1.30

    location_clean = str(location).lower()

    multipliers = {
        "spain": 1.32,
        "españa": 1.32,
        "madrid": 1.32,
        "barcelona": 1.32,
        "germany": 1.28,
        "berlin": 1.28,
        "munich": 1.28,
        "uk": 1.18,
        "united kingdom": 1.18,
        "london": 1.18,
        "france": 1.45,
        "paris": 1.45,
        "portugal": 1.27,
        "lisbon": 1.27,
        "lisboa": 1.27,
        "netherlands": 1.30,
        "amsterdam": 1.30,
        "italy": 1.32,
        "milan": 1.32,
        "ireland": 1.12,
        "dublin": 1.12
    }

    for keyword, multiplier in multipliers.items():
        if keyword in location_clean:
            return multiplier

    return 1.30


def generate_attrition_recommendation(row: pd.Series) -> str:
    """Genera recomendación accionable según el driver principal de riesgo."""
    if row["engagement_score"] < 3.5:
        return "Revisar engagement con manager"

    if row["work_life_balance_score"] < 3.5:
        return "Revisar carga de trabajo y balance"

    if row["absenteeism_days"] > 10:
        return "Analizar absentismo y posibles causas"

    if row["performance_score"] < 3.5:
        return "Revisar objetivos, encaje y soporte"

    return "Revisión individual con manager"


def calculate_replacement_multiplier(seniority: str) -> float:
    """Multiplicador simplificado de coste potencial de reemplazo por seniority."""
    seniority_clean = str(seniority).lower()

    if "junior" in seniority_clean:
        return 0.5
    if "mid" in seniority_clean:
        return 1.0
    if "senior" in seniority_clean:
        return 1.5
    if "lead" in seniority_clean or "manager" in seniority_clean or "director" in seniority_clean:
        return 2.0

    return 1.0


# CARGA, VALIDACIÓN Y ENRIQUECIMIENTO DE DATOS


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


def enrich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y genera todos los scores derivados utilizados por los módulos."""
    df = df.copy()

    # -----------------------------
    # Normalización de tipos básicos
    # -----------------------------
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=numeric_columns).copy()

    df["typeofcontribution"] = (
        df["typeofcontribution"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df["department"] = df["department"].astype(str).str.strip()
    df["location"] = df["location"].astype(str).str.strip()
    df["seniority"] = df["seniority"].astype(str).str.strip()
    df["contract_type"] = df["contract_type"].astype(str).str.strip()

    # -----------------------------
    # Coste salarial real por ubicación
    # -----------------------------
    df["social_security_multiplier"] = df["location"].apply(get_country_multiplier)
    df["real_salary_cost"] = df["salary"] * df["social_security_multiplier"]
    df["employee_profit"] = df["revenue_generated"] - df["real_salary_cost"]
    df["revenue_salary_ratio"] = df["revenue_generated"] / df["real_salary_cost"].replace(0, np.nan)

    # -----------------------------
    # Attrition risk
    # -----------------------------
    df["attrition_risk_score"] = (
        (5 - df["engagement_score"]) * 0.35 +
        (5 - df["work_life_balance_score"]) * 0.25 +
        df["absenteeism_days"] * 0.15 +
        (5 - df["performance_score"]) * 0.15 +
        df["attrition_flag"] * 1.5
    )

    df["attrition_risk_level"] = pd.cut(
        df["attrition_risk_score"],
        bins=[-1, 1.5, 2.5, 100],
        labels=["Bajo", "Medio", "Alto"]
    ).astype(str)

    df["is_high_risk"] = df["attrition_risk_level"] == "Alto"

    df["replacement_multiplier"] = df["seniority"].apply(calculate_replacement_multiplier)
    df["potential_attrition_cost"] = np.where(
        df["is_high_risk"],
        df["real_salary_cost"] * df["replacement_multiplier"],
        0
    )

    # -----------------------------
    # Productivity risk
    # -----------------------------
    df["productivity_risk_score"] = (
        (5 - df["performance_score"]) * 0.30 +
        normalize_series(df["absenteeism_days"]) * 2.0 * 0.25 +
        (5 - df["engagement_score"]) * 0.20 +
        (5 - df["work_life_balance_score"]) * 0.15 +
        (1 - normalize_series(df["projects_completed"])) * 2.0 * 0.10
    )

    df["productivity_risk_level"] = pd.cut(
        df["productivity_risk_score"],
        bins=[-1, 1.4, 2.4, 100],
        labels=["Bajo", "Medio", "Alto"]
    ).astype(str)

    # -----------------------------
    # Engagement segmentation
    # -----------------------------
    df["engagement_segment"] = np.select(
        [
            (df["engagement_score"] >= 4.0) & (df["performance_score"] >= 4.0),
            (df["engagement_score"] >= 3.5) & (df["performance_score"] >= 3.5),
            (df["engagement_score"] < 3.5) & (df["performance_score"] >= 4.0),
            (df["engagement_score"] < 3.5)
        ],
        ["Champions", "Stable", "Burnout Risk", "Disconnected"],
        default="Stable"
    )

    df["burnout_risk"] = np.where(
        (df["performance_score"] >= 4.0) &
        (df["work_life_balance_score"] < 3.5) &
        ((df["engagement_score"] < 3.5) | (df["absenteeism_days"] > df["absenteeism_days"].median())),
        "Burnout Risk",
        "Normal"
    )

    # -----------------------------
    # Promotion readiness
    # -----------------------------
    df["promotion_score"] = (
        normalize_series(df["performance_score"]) * 0.30 +
        normalize_series(df["last_evaluation_score"]) * 0.20 +
        normalize_series(df["engagement_score"]) * 0.15 +
        normalize_series(df["training_hours"]) * 0.15 +
        normalize_series(df["projects_completed"]) * 0.10 +
        normalize_series(df["tenure_years"]) * 0.10 -
        normalize_series(df["absenteeism_days"]) * 0.10
    ).clip(0, 1)

    df["promotion_probability"] = df["promotion_score"] * 100

    df["promotion_readiness"] = pd.cut(
        df["promotion_probability"],
        bins=[-1, 45, 70, 100],
        labels=["Needs Development", "Emerging Leader", "Promotion Ready"]
    ).astype(str)

    # -----------------------------
    # Talent outliers
    # -----------------------------
    revenue_q75 = df["revenue_generated"].quantile(0.75)
    salary_q75 = df["real_salary_cost"].quantile(0.75)
    salary_median = df["real_salary_cost"].median()

    df["outlier_category"] = np.select(
        [
            (df["performance_score"] >= 4.5) & (df["revenue_generated"] >= revenue_q75),
            (df["performance_score"] >= 4.2) & (df["engagement_score"] < 3.4),
            (df["performance_score"] >= 4.3) & (df["real_salary_cost"] < salary_median),
            (df["engagement_score"] >= 4.2) & (df["training_hours"] >= df["training_hours"].quantile(0.75)) & (df["performance_score"] < 4.0),
            (df["real_salary_cost"] >= salary_q75) & (df["revenue_generated"] < df["revenue_generated"].median())
        ],
        [
            "High Impact Talent",
            "Burnout Risk",
            "Silent Star",
            "Hidden Potential",
            "Economic Risk"
        ],
        default="Normal"
    )

    df["talent_outlier_type"] = np.where(
        df["outlier_category"] == "Normal",
        "Normal",
        "Talent Outlier"
    )

    # -----------------------------
    # Workforce archetypes
    # -----------------------------
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

    # -----------------------------
    # Organizational Health & Friction proxies
    # -----------------------------
    df["organizational_health_score"] = (
        normalize_series(df["engagement_score"]) * 30 +
        normalize_series(df["work_life_balance_score"]) * 25 +
        normalize_series(df["performance_score"]) * 20 +
        (1 - normalize_series(df["absenteeism_days"])) * 15 +
        (1 - normalize_series(df["attrition_risk_score"])) * 10
    ).clip(0, 100)

    df["friction_score"] = (
        (1 - normalize_series(df["engagement_score"])) * 30 +
        normalize_series(df["absenteeism_days"]) * 25 +
        (1 - normalize_series(df["work_life_balance_score"])) * 25 +
        normalize_series(df["attrition_risk_score"]) * 20
    ).clip(0, 100)

    df["stability_score"] = (
        normalize_series(df["tenure_years"]) * 30 +
        normalize_series(df["engagement_score"]) * 30 +
        (1 - normalize_series(df["attrition_risk_score"])) * 25 +
        (1 - normalize_series(df["absenteeism_days"])) * 15
    ).clip(0, 100)

    df["health_segment"] = np.select(
        [
            df["organizational_health_score"] >= 70,
            df["burnout_risk"] == "Burnout Risk",
            df["engagement_score"] < 3.4,
            df["friction_score"] >= 60
        ],
        ["Healthy Teams", "Burnout Risk", "Disconnected Teams", "High Pressure Teams"],
        default="Healthy Teams"
    )

    # -----------------------------
    # Employee clustering IA
    # -----------------------------
    clustering_features = [
        "performance_score",
        "engagement_score",
        "revenue_generated",
        "real_salary_cost",
        "tenure_years",
        "training_hours",
        "absenteeism_days"
    ]

    if SKLEARN_AVAILABLE and len(df) >= 5:
        n_clusters = min(5, len(df))
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df[clustering_features])

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df["employee_cluster_raw"] = kmeans.fit_predict(scaled_features)

        pca = PCA(n_components=2, random_state=42)
        pca_features = pca.fit_transform(scaled_features)
        df["pca_x"] = pca_features[:, 0]
        df["pca_y"] = pca_features[:, 1]

        # Etiquetado narrativo simple de clusters según perfil medio.
        cluster_summary = df.groupby("employee_cluster_raw").agg(
            avg_performance=("performance_score", "mean"),
            avg_engagement=("engagement_score", "mean"),
            avg_absenteeism=("absenteeism_days", "mean"),
            avg_revenue=("revenue_generated", "mean")
        )

        labels = {}
        for cluster_id, row in cluster_summary.iterrows():
            if row["avg_performance"] >= 4.0 and row["avg_engagement"] >= 4.0:
                labels[cluster_id] = "High Impact Cluster"
            elif row["avg_performance"] >= 4.0 and row["avg_engagement"] < 3.6:
                labels[cluster_id] = "Burnout Risk Cluster"
            elif row["avg_engagement"] >= 3.8 and row["avg_performance"] < 4.0:
                labels[cluster_id] = "Emerging Talent Cluster"
            elif row["avg_absenteeism"] >= df["absenteeism_days"].median():
                labels[cluster_id] = "Operational Risk Cluster"
            else:
                labels[cluster_id] = "Stable Core Cluster"

        df["employee_cluster"] = df["employee_cluster_raw"].map(labels)
    else:
        df["employee_cluster_raw"] = 0
        df["employee_cluster"] = "Cluster no disponible"
        df["pca_x"] = 0
        df["pca_y"] = 0

    # -----------------------------
    # Isolation Forest opcional para outliers IA
    # -----------------------------
    if SKLEARN_AVAILABLE and len(df) >= 10:
        outlier_features = [
            "performance_score",
            "engagement_score",
            "revenue_generated",
            "real_salary_cost",
            "projects_completed",
            "training_hours"
        ]
        scaler = StandardScaler()
        scaled_outlier_features = scaler.fit_transform(df[outlier_features])
        model = IsolationForest(contamination=0.12, random_state=42)
        predictions = model.fit_predict(scaled_outlier_features)
        df["ai_outlier"] = np.where(predictions == -1, "Talent Outlier", "Normal")
    else:
        df["ai_outlier"] = df["talent_outlier_type"]

    return df


# EADER Y CARGA DE CSV


logo_path = Path("Positivo verde.png")

if logo_path.exists():
    logo = Image.open(logo_path)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo, width=250)

st.title("HR4Techies Advanced People Analytics")

st.write("""
Plataforma demo de Workforce Intelligence que convierte un CSV de empleados
en visualizaciones, insights y recomendaciones accionables para decisiones estratégicas de talento.
""")

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

raw_df = pd.read_csv(uploaded_file)

missing_columns = [column for column in required_columns if column not in raw_df.columns]

if missing_columns:
    st.error("❌ El CSV no tiene el formato correcto.")
    st.write("Faltan las siguientes columnas:")
    st.write(missing_columns)
    st.info("👉 Usa el dataset de ejemplo para probar la herramienta.")
    st.stop()

df = enrich_dataset(raw_df)

if df.empty:
    st.error("No hay datos válidos después de la limpieza del dataset.")
    st.stop()


# 7. SIDEBAR Y SELECTOR DE MÓDULOS


st.sidebar.title("Módulos de análisis")

module = st.sidebar.radio(
    "Selecciona un módulo",
    [
        "Performance & Productivity Intelligence",
        "Employee Attrition & Engagement",
        "Role Matching & Promotion",
        "Talent Outliers Analysis",
        "Employees Archetypes & Clustering",
        "Organizational Health & Friction"
    ]
)


# MÓDULO 1: PERFORMANCE & PRODUCTIVITY INTELLIGENCE


if module == "Performance & Productivity Intelligence":

    st.header("Performance & Productivity Intelligence")
    st.write("""
    Este módulo analiza la eficiencia económica de la plantilla, la productividad,
    el impacto de negocio y el riesgo de baja productividad.
    """)

    show_dataset_preview(df)

    filtered_df = contribution_filter(df, key="performance_contribution_filter")

    total_revenue = filtered_df["revenue_generated"].sum()
    total_real_salary_cost = filtered_df["real_salary_cost"].sum()
    workforce_profit = total_revenue - total_real_salary_cost
    avg_performance = filtered_df["performance_score"].mean()

    revenue_vs_cost_ratio = total_revenue / total_real_salary_cost if total_real_salary_cost else 0
    salary_roi = ((total_revenue - total_real_salary_cost) / total_real_salary_cost) * 100 if total_real_salary_cost else 0

    st.subheader("KPIs ejecutivos")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Facturación total anual", format_money_compact(total_revenue))
    col2.metric("Coste salarial anual real", format_money_compact(total_real_salary_cost))
    col3.metric("Beneficio workforce anual", format_money_compact(workforce_profit))
    col4.metric("Performance media", f"{avg_performance:.2f}")

    st.caption(
        "El coste salarial anual real incluye salario bruto y una estimación de coste empresa según la ubicación del empleado."
    )

    st.subheader("Eficiencia económica de la plantilla")
    colA, colB, colC = st.columns(3)
    colA.metric("Revenue / Coste salarial real", f"{revenue_vs_cost_ratio:.2f}x")
    colB.metric("ROI salarial real", f"{salary_roi:.1f}%")
    colC.metric("Margen bruto workforce", format_money_compact(workforce_profit))

    st.info(
        f"Por cada 1 € invertido en coste salarial real, la plantilla genera aproximadamente "
        f"{revenue_vs_cost_ratio:.2f} € de revenue. El margen bruto workforce estimado es "
        f"{format_money_compact(workforce_profit)}."
    )

    st.subheader("Ranking top performance + revenue")
    top_performers = filtered_df.sort_values(
        by=["performance_score", "revenue_generated"],
        ascending=False
    ).head(10)

    show_dataframe(
        top_performers[
            [
                "employee_name",
                "department",
                "role",
                "typeofcontribution",
                "performance_score",
                "revenue_generated",
                "real_salary_cost",
                "employee_profit"
            ]
        ]
    )

    st.subheader("Top 10 empleados por revenue generado")
    top_revenue = filtered_df.sort_values(by="revenue_generated", ascending=False).head(10)

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
            "real_salary_cost",
            "employee_profit",
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

    st.subheader("Revenue por departamento")
    revenue_by_department = (
        filtered_df.groupby("department")
        .agg(
            revenue=("revenue_generated", "sum"),
            real_salary_cost=("real_salary_cost", "sum"),
            employees=("employee_id", "count")
        )
        .reset_index()
    )
    revenue_by_department["profit"] = revenue_by_department["revenue"] - revenue_by_department["real_salary_cost"]

    fig = px.treemap(
        revenue_by_department,
        path=["department"],
        values="revenue",
        color="profit",
        color_continuous_scale="Greens",
        hover_data=["employees", "real_salary_cost", "profit"],
        title="Revenue anual por departamento"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=70, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Matriz performance vs absentismo")
    fig = px.scatter(
        filtered_df,
        x="absenteeism_days",
        y="performance_score",
        size="revenue_generated",
        color="productivity_risk_level",
        color_discrete_map=risk_color_map,
        hover_data=[
            "employee_name",
            "department",
            "role",
            "engagement_score",
            "work_life_balance_score",
            "revenue_generated",
            "productivity_risk_score"
        ],
        title="Performance vs absentismo"
    )
    fig.update_layout(
        xaxis_title="Días de absentismo",
        yaxis_title="Performance score",
        legend_title="Riesgo productivo"
    )
    plot_chart(fig)

    st.subheader("Top performers en 3D: Performance, Revenue y Coste real")
    fig = px.scatter_3d(
        top_performers,
        x="performance_score",
        y="revenue_generated",
        z="real_salary_cost",
        color="typeofcontribution",
        color_discrete_map=contribution_color_map,
        size="revenue_generated",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "seniority",
            "real_salary_cost",
            "revenue_generated",
            "employee_profit",
            "typeofcontribution"
        ],
        title="Top 10 empleados: Performance, Revenue anual y Coste salarial real"
    )
    fig.update_layout(
        scene=dict(
            xaxis_title="Performance",
            yaxis_title="Revenue anual (€)",
            zaxis_title="Coste salarial real (€)"
        ),
        legend_title="Tipo de contribución"
    )
    plot_chart(fig)

    st.subheader("Tabla de empleados con riesgo productivo")
    productivity_risk_df = filtered_df.sort_values(
        by="productivity_risk_score",
        ascending=False
    ).head(15)

    show_dataframe(
        productivity_risk_df[
            [
                "employee_name",
                "department",
                "role",
                "typeofcontribution",
                "performance_score",
                "engagement_score",
                "absenteeism_days",
                "work_life_balance_score",
                "productivity_risk_level",
                "productivity_risk_score"
            ]
        ]
    )

    st.subheader("Insight automático")
    high_impact_underpaid = filtered_df[
        (filtered_df["performance_score"] >= 4.5) &
        (filtered_df["revenue_generated"] >= filtered_df["revenue_generated"].quantile(0.75)) &
        (filtered_df["real_salary_cost"] < filtered_df["real_salary_cost"].median())
    ]

    if not high_impact_underpaid.empty:
        producer_share = (
            (high_impact_underpaid["typeofcontribution"] == "producer").mean() * 100
        )
        st.success(
            f"Se han detectado {len(high_impact_underpaid)} empleados con alto performance, "
            f"elevado impacto económico y coste salarial real inferior a la mediana. "
            f"El {producer_share:.0f}% pertenece a perfiles producer."
        )
    else:
        st.info("No se han detectado empleados de alto impacto infraremunerados según las reglas actuales.")


# MÓDULO 2: EMPLOYEE ATTRITION & FIDELIZACIÓN


elif module == "Employee Attrition & Engagement":

    st.header("Employee Attrition & Engagement")
    st.write("""
    Este módulo prioriza el riesgo de fuga desde una perspectiva accionable:
    impacto económico, engagement, burnout y fidelización del talento crítico.
    """)

    show_dataset_preview(df)
    filtered_df = contribution_filter(df, key="attrition_contribution_filter")

    high_risk_df = filtered_df[filtered_df["is_high_risk"]].copy()

    attrition_rate = filtered_df["attrition_flag"].mean()
    high_risk_count = len(high_risk_df)
    high_risk_revenue = high_risk_df["revenue_generated"].sum()
    top_department = high_risk_df["department"].value_counts().idxmax() if not high_risk_df.empty else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Attrition rate global", f"{attrition_rate:.1%}")
    col2.metric("Empleados riesgo alto", high_risk_count)
    col3.metric("Departamento más expuesto", top_department)
    col4.metric("Revenue en riesgo", format_money_compact(high_risk_revenue))

    st.caption("Revenue en riesgo = suma del revenue anual generado por empleados clasificados como riesgo alto.")

    st.subheader("Impacto económico vs engagement")
    fig = px.scatter(
        filtered_df,
        x="engagement_score",
        y="revenue_generated",
        color="attrition_risk_level",
        color_discrete_map=risk_color_map,
        size="real_salary_cost",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "typeofcontribution",
            "work_life_balance_score",
            "absenteeism_days",
            "real_salary_cost",
            "revenue_generated",
            "attrition_risk_score"
        ],
        title="Impacto económico vs engagement"
    )
    fig.add_vline(x=3.5, line_dash="dash", line_color=RED, annotation_text="Engagement bajo")
    fig.add_hline(
        y=filtered_df["revenue_generated"].quantile(0.75),
        line_dash="dash",
        line_color=CORPORATE_GREEN,
        annotation_text="Alto revenue"
    )
    fig.update_layout(
        xaxis_title="Engagement score",
        yaxis_title="Revenue anual (€)",
        legend_title="Nivel de riesgo"
    )
    plot_chart(fig)

    st.subheader("Engagement por departamento")
    engagement_by_department = (
        filtered_df.groupby("department")
        .agg(
            avg_engagement=("engagement_score", "mean"),
            employees=("employee_id", "count"),
            avg_attrition_risk=("attrition_risk_score", "mean")
        )
        .reset_index()
        .sort_values("avg_engagement", ascending=True)
    )

    fig = px.bar(
        engagement_by_department,
        x="avg_engagement",
        y="department",
        orientation="h",
        color="avg_attrition_risk",
        color_continuous_scale="RdYlGn_r",
        hover_data=["employees", "avg_attrition_risk"],
        title="Engagement medio por departamento"
    )
    fig.update_layout(
        xaxis_title="Engagement medio",
        yaxis_title="Departamento",
        coloraxis_colorbar_title="Riesgo medio"
    )
    plot_chart(fig)

    st.subheader("Attrition Risk Matrix")
    matrix_df = filtered_df.copy()
    matrix_df["revenue_segment"] = np.where(
        matrix_df["revenue_generated"] >= matrix_df["revenue_generated"].quantile(0.75),
        "Alto revenue",
        "Revenue medio/bajo"
    )
    matrix_df["engagement_segment_matrix"] = np.where(
        matrix_df["engagement_score"] < 3.5,
        "Bajo engagement",
        "Engagement saludable"
    )
    matrix_df["risk_quadrant"] = np.select(
        [
            (matrix_df["revenue_segment"] == "Alto revenue") & (matrix_df["engagement_segment_matrix"] == "Bajo engagement"),
            (matrix_df["revenue_segment"] == "Alto revenue") & (matrix_df["engagement_segment_matrix"] == "Engagement saludable"),
            (matrix_df["revenue_segment"] == "Revenue medio/bajo") & (matrix_df["engagement_segment_matrix"] == "Bajo engagement")
        ],
        ["Riesgo crítico", "Talento estratégico", "Riesgo moderado"],
        default="Talento estable"
    )

    quadrant_counts = matrix_df["risk_quadrant"].value_counts().reset_index()
    quadrant_counts.columns = ["Quadrant", "Employees"]

    fig = px.bar(
        quadrant_counts,
        x="Quadrant",
        y="Employees",
        color="Quadrant",
        color_discrete_map={
            "Riesgo crítico": RED,
            "Talento estratégico": CORPORATE_GREEN,
            "Riesgo moderado": ORANGE,
            "Talento estable": BLUE
        },
        title="Distribución de empleados por cuadrante de riesgo"
    )
    fig.update_layout(xaxis_title="Cuadrante", yaxis_title="Empleados", showlegend=False)
    plot_chart(fig)

    st.subheader("Segmentación de engagement")
    engagement_counts = filtered_df["engagement_segment"].value_counts().reset_index()
    engagement_counts.columns = ["Segment", "Employees"]

    fig = px.pie(
        engagement_counts,
        names="Segment",
        values="Employees",
        color="Segment",
        color_discrete_map=engagement_segment_color_map,
        hole=0.55,
        title="Segmentación de engagement"
    )
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(showlegend=True)
    plot_chart(fig)

    st.subheader("Coste potencial de attrition")
    potential_attrition_cost = filtered_df["potential_attrition_cost"].sum()
    st.metric("Coste potencial de reemplazo", format_money_compact(potential_attrition_cost))
    st.caption("Estimación basada en coste empresa y multiplicadores por seniority.")

    st.subheader("Burnout Risk Analysis")
    fig = px.scatter(
        filtered_df,
        x="work_life_balance_score",
        y="performance_score",
        size="absenteeism_days",
        color="burnout_risk",
        color_discrete_map={"Normal": BLUE, "Burnout Risk": ORANGE},
        hover_data=[
            "employee_name",
            "department",
            "role",
            "engagement_score",
            "absenteeism_days",
            "revenue_generated"
        ],
        title="Performance vs Work-Life Balance"
    )
    fig.update_layout(
        xaxis_title="Work-life balance",
        yaxis_title="Performance",
        legend_title="Burnout risk"
    )
    plot_chart(fig)

    st.subheader("Insight automático")
    critical = matrix_df[matrix_df["risk_quadrant"] == "Riesgo crítico"]
    if not critical.empty:
        main_contribution = critical["typeofcontribution"].value_counts().idxmax()
        st.warning(
            f"Se han detectado {len(critical)} empleados con bajo engagement y alto impacto económico. "
            f"La mayor concentración está en perfiles {main_contribution}."
        )
    else:
        st.success("No se detectan empleados en el cuadrante de riesgo crítico con las reglas actuales.")


# MÓDULO 3: ROLE MATCHING & PROMOTION


elif module == "Role Matching & Promotion":

    st.header("Role Matching & Promotion")
    st.write("""
    Este módulo recomienda movimientos internos y estima la preparación para promoción,
    combinando skills, performance, engagement, tenure y formación.
    """)

    show_dataset_preview(df)

    filtered_df = contribution_filter(
        df,
        key="role_matching_contribution_filter"
    )

    selected_employee = st.selectbox(
        "Selecciona un empleado",
        filtered_df["employee_name"].tolist()
    )

    employee = filtered_df[
        filtered_df["employee_name"] == selected_employee
    ].iloc[0]

    st.subheader("Perfil ejecutivo del empleado")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rol actual", employee["role"])
    col2.metric("Departamento", employee["department"])
    col3.metric("Performance", f"{employee['performance_score']:.2f}")
    col4.metric("Engagement", f"{employee['engagement_score']:.2f}")

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("Seniority", employee["seniority"])
    col6.metric("Training hours", f"{employee['training_hours']:.0f}")
    col7.metric("Promotion readiness", employee["promotion_readiness"])
    col8.metric("Promotion probability", f"{employee['promotion_probability']:.0f}%")

    st.markdown("**Skills actuales:**")
    st.write(employee["skills"])

    # --------------------------------------------------------
    # Role rules: skills requeridas por cada rol objetivo
    # --------------------------------------------------------

    role_rules = {
        "Data Engineer": ["Python", "SQL", "AWS"],
        "ML Engineer": ["Python", "ML", "Statistics"],
        "People Analytics Specialist": ["HR Strategy", "Analytics", "Python"],
        "Sales Manager": ["Sales", "CRM", "Negotiation"],
        "Finance Manager": ["Excel", "Forecasting", "Accounting"],
        "Marketing Analyst": ["SEO", "Analytics", "Content"],
        "Product Manager": ["Product", "Analytics", "Stakeholder Management"],
        "HR Business Partner": ["HR Strategy", "Coaching", "People Management"]
    }

    employee_skills = [
        skill.strip()
        for skill in str(employee["skills"]).split(";")
    ]

    recommendations = []

    tenure_score = min(employee["tenure_years"] / 5, 1)
    performance_component = employee["performance_score"] / 5
    engagement_component = employee["engagement_score"] / 5

    for target_role, required_skills in role_rules.items():

        matched = sorted(
            set(employee_skills).intersection(set(required_skills))
        )

        missing = sorted(
            set(required_skills) - set(employee_skills)
        )

        skills_match = len(matched) / len(required_skills)

        role_fit_score = (
            skills_match * 0.50
            + performance_component * 0.20
            + engagement_component * 0.15
            + tenure_score * 0.15
        )

        recommendations.append(
            {
                "recommended_role": target_role,
                "match_score": round(role_fit_score, 2),
                "skills_match": round(skills_match, 2),
                "matched_skills": ", ".join(matched) if matched else "-",
                "skill_gap": ", ".join(missing) if missing else "Sin gaps críticos",
                "promotion_readiness": employee["promotion_readiness"],
                "mobility_fit": (
                    "High"
                    if role_fit_score >= 0.70
                    else "Medium"
                    if role_fit_score >= 0.45
                    else "Low"
                )
            }
        )

    recommendations_df = (
        pd.DataFrame(recommendations)
        .sort_values(by="match_score", ascending=False)
    )

    best_match = recommendations_df.iloc[0]

    st.subheader("Mejor siguiente rol recomendado")

    st.metric(
        label="Rol recomendado",
        value=best_match["recommended_role"],
        delta=f"Match score: {best_match['match_score']:.2f}"
    )

    st.subheader("Ranking de roles recomendados")

    show_dataframe(recommendations_df)

    # --------------------------------------------------------
    # Promotion Readiness Gauge
    # --------------------------------------------------------

    st.subheader("Promotion Readiness Gauge")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(employee["promotion_probability"]),
            title={"text": "Promotion readiness (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": CORPORATE_GREEN},
                "steps": [
                    {"range": [0, 45], "color": "#FDEDEC"},
                    {"range": [45, 70], "color": "#FFF8E1"},
                    {"range": [70, 100], "color": "#E8F5E9"}
                ]
            }
        )
    )

    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=70, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # Promotion Matrix
    # --------------------------------------------------------

    st.subheader("Promotion Matrix")

    fig = px.scatter(
        filtered_df,
        x="tenure_years",
        y="performance_score",
        size="training_hours",
        color="promotion_readiness",
        color_discrete_map=promotion_color_map,
        hover_data=[
            "employee_name",
            "department",
            "role",
            "engagement_score",
            "promotion_probability",
            "training_hours"
        ],
        title="Tenure vs Performance por readiness de promoción"
    )

    fig.update_layout(
        xaxis_title="Tenure años",
        yaxis_title="Performance score",
        legend_title="Promotion readiness"
    )

    plot_chart(fig)

    # --------------------------------------------------------
    # Skill Gap Radar
    # --------------------------------------------------------

    st.subheader("Skill Gap Radar")

    top_roles_for_radar = recommendations_df.head(3)

    categories = top_roles_for_radar["recommended_role"].tolist()
    values = top_roles_for_radar["skills_match"].tolist()

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Skill match",
            line_color=CORPORATE_GREEN
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        title="Skill match por rol recomendado",
        height=500,
        margin=dict(l=80, r=80, t=80, b=80)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # Top talento promocionable
    # --------------------------------------------------------

    st.subheader("Top talento promocionable")

    promotable = (
        filtered_df
        .sort_values(
            "promotion_probability",
            ascending=False
        )
        .head(15)
    )

    show_dataframe(
        promotable[
            [
                "employee_name",
                "department",
                "role",
                "seniority",
                "performance_score",
                "engagement_score",
                "promotion_probability",
                "promotion_readiness",
                "attrition_risk_level"
            ]
        ]
    )

    # --------------------------------------------------------
    # Insight automático
    # --------------------------------------------------------

    st.subheader("Insight automático")

    ready = filtered_df[
        filtered_df["promotion_readiness"] == "Promotion Ready"
    ]

    st.success(
        f"Se han detectado {len(ready)} empleados en estado Promotion Ready. "
        f"El mejor siguiente rol para {selected_employee} es "
        f"{best_match['recommended_role']}."
    )


# MÓDULO 4: TALENT OUTLIERS ANALYSIS


elif module == "Talent Outliers Analysis":

    st.header("Talent Outliers Analysis")
    st.write("""
    Este módulo identifica talento diferencial, anomalías organizativas,
    hidden potential, burnout risk y perfiles con desajuste coste-impacto.
    """)

    show_dataset_preview(df)
    filtered_df = contribution_filter(df, key="outliers_contribution_filter")

    outliers = filtered_df[filtered_df["outlier_category"] != "Normal"].copy()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Outliers detectados", len(outliers))
    col2.metric("High Impact Talent", (outliers["outlier_category"] == "High Impact Talent").sum())
    col3.metric("Burnout Risk", (outliers["outlier_category"] == "Burnout Risk").sum())
    col4.metric("Economic Risk", (outliers["outlier_category"] == "Economic Risk").sum())

    st.subheader("Outlier Constellations")

    # Para un 3D con variables categóricas, se codifican como índices numéricos
    # y se muestran las etiquetas originales en hover.
    constellation_df = outliers.copy() if not outliers.empty else filtered_df.copy()
    constellation_df["department_axis"] = pd.Categorical(constellation_df["department"]).codes
    constellation_df["seniority_axis"] = pd.Categorical(constellation_df["seniority"]).codes
    constellation_df["contribution_axis"] = pd.Categorical(constellation_df["typeofcontribution"]).codes

    fig = px.scatter_3d(
        constellation_df,
        x="department_axis",
        y="seniority_axis",
        z="contribution_axis",
        color="location",
        color_discrete_sequence=location_color_sequence,
        size="revenue_generated",
        hover_data=[
            "employee_name",
            "department",
            "seniority",
            "typeofcontribution",
            "location",
            "outlier_category",
            "performance_score",
            "engagement_score",
            "revenue_generated"
        ],
        title="Outlier Constellations: Department, Seniority y Contribution Type"
    )
    fig.update_layout(
        scene=dict(
            xaxis_title="Department",
            yaxis_title="Seniority",
            zaxis_title="Type of Contribution"
        ),
        legend_title="Location"
    )
    plot_chart(fig)

    st.caption(
        "Cada punto representa un empleado outlier. La posición muestra su estructura organizativa, "
        "el color indica país/ubicación y el tamaño representa revenue generado."
    )

    st.subheader("Outliers por tipo de contribución")
    if not outliers.empty:
        outliers_by_contribution = outliers["typeofcontribution"].value_counts().reset_index()
        outliers_by_contribution.columns = ["typeofcontribution", "outliers"]
        fig = px.bar(
            outliers_by_contribution,
            x="outliers",
            y="typeofcontribution",
            orientation="h",
            color="typeofcontribution",
            color_discrete_map=contribution_color_map,
            title="Outliers por tipo de contribución"
        )
        fig.update_layout(xaxis_title="Outliers", yaxis_title="Tipo de contribución", showlegend=False)
        plot_chart(fig)

        st.subheader("Outliers por departamento")
        outliers_by_department = outliers["department"].value_counts().reset_index()
        outliers_by_department.columns = ["department", "outliers"]
        fig = px.bar(
            outliers_by_department,
            x="outliers",
            y="department",
            orientation="h",
            color="outliers",
            color_continuous_scale="Greens",
            title="Outliers por departamento"
        )
        fig.update_layout(xaxis_title="Outliers", yaxis_title="Departamento", showlegend=False)
        plot_chart(fig)

        st.subheader("Outliers por seniority")
        outliers_by_seniority = outliers["seniority"].value_counts().reset_index()
        outliers_by_seniority.columns = ["seniority", "outliers"]
        fig = px.bar(
            outliers_by_seniority,
            x="seniority",
            y="outliers",
            color="seniority",
            title="Outliers por seniority"
        )
        fig.update_layout(xaxis_title="Seniority", yaxis_title="Outliers", showlegend=False)
        plot_chart(fig)

    else:
        st.info("No se han detectado outliers con las reglas actuales.")

    st.subheader("Tabla de perfiles críticos")
    outlier_table = outliers.sort_values(by="revenue_generated", ascending=False)
    show_dataframe(
        outlier_table[
            [
                "employee_name",
                "department",
                "role",
                "location",
                "seniority",
                "typeofcontribution",
                "performance_score",
                "engagement_score",
                "revenue_generated",
                "real_salary_cost",
                "revenue_salary_ratio",
                "outlier_category",
                "ai_outlier"
            ]
        ]
    )

    st.subheader("Insight automático")
    if not outliers.empty:
        main_department = outliers["department"].value_counts().idxmax()
        main_seniority = outliers["seniority"].value_counts().idxmax()
        st.info(
            f"La mayor concentración de outliers se encuentra en {main_department}, "
            f"especialmente en perfiles {main_seniority}."
        )
    else:
        st.success("La organización no muestra concentraciones relevantes de outliers según las reglas actuales.")


# MÓDULO 5: EMPLOYEES ARCHETYPES & CLUSTERING


elif module == "Employees Archetypes & Clustering":

    st.header("Employees Archetypes & Clustering")

    st.write("""
    Este módulo segmenta la workforce mediante arquetipos HR, clustering IA,
    compensación, estructura organizativa y composición contractual.
    """)

    # --------------------------------------------------------
    # 1. Vista previa del dataset
    # --------------------------------------------------------

    show_dataset_preview(df)

    # --------------------------------------------------------
    # 2. Filtro por tipo de contribución
    # --------------------------------------------------------

    filtered_df = contribution_filter(
        df,
        key="archetypes_contribution_filter"
    )

    # --------------------------------------------------------
    # 3. Distribución de arquetipos
    # --------------------------------------------------------

    st.subheader("Distribución de arquetipos")

    archetype_counts = (
        filtered_df["archetype"]
        .value_counts()
        .reset_index()
    )

    archetype_counts.columns = ["archetype", "employees"]

    fig = px.bar(
        archetype_counts,
        x="employees",
        y="archetype",
        orientation="h",
        color="archetype",
        color_discrete_map=archetype_color_map,
        title="Distribución de empleados por arquetipo"
    )

    fig.update_layout(
        xaxis_title="Empleados",
        yaxis_title="Arquetipo",
        showlegend=False
    )

    plot_chart(fig)

    # --------------------------------------------------------
    # 4. Workforce Archetypes 3D
    # --------------------------------------------------------

    st.subheader("Workforce Archetypes 3D")

    fig = px.scatter_3d(
        filtered_df,
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
            "real_salary_cost",
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
        legend_title="Arquetipo"
    )

    plot_chart(fig)

    # --------------------------------------------------------
    # 5. PCA Employee Clustering Map
    # --------------------------------------------------------

    st.subheader("PCA Employee Clustering Map")

    fig = px.scatter(
        filtered_df,
        x="pca_x",
        y="pca_y",
        color="employee_cluster",
        size="revenue_generated",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "archetype",
            "performance_score",
            "engagement_score",
            "revenue_generated"
        ],
        title="Mapa IA de clusters de empleados"
    )

    fig.update_layout(
        xaxis_title="PCA 1",
        yaxis_title="PCA 2",
        legend_title="Employee Cluster"
    )

    plot_chart(fig)

    # --------------------------------------------------------
    # 6. Cluster Profiles
    # --------------------------------------------------------

    st.subheader("Cluster Profiles")

    cluster_profile = (
        filtered_df.groupby("employee_cluster")
        .agg(
            employees=("employee_id", "count"),
            avg_performance=("performance_score", "mean"),
            avg_engagement=("engagement_score", "mean"),
            avg_revenue=("revenue_generated", "mean"),
            avg_salary_cost=("real_salary_cost", "mean"),
            avg_tenure=("tenure_years", "mean"),
            avg_absenteeism=("absenteeism_days", "mean")
        )
        .reset_index()
    )

    show_dataframe(cluster_profile)

    # --------------------------------------------------------
    # 7. Cluster Comparison Radar
    # --------------------------------------------------------

    st.subheader("Cluster Comparison Radar")

    if len(cluster_profile) > 0:

        radar_metrics = [
            "avg_performance",
            "avg_engagement",
            "avg_revenue",
            "avg_salary_cost",
            "avg_tenure",
            "avg_absenteeism"
        ]

        radar_df = cluster_profile.copy()

        for metric in radar_metrics:
            radar_df[metric] = normalize_series(radar_df[metric])

        fig = go.Figure()

        for _, row in radar_df.iterrows():

            values = [row[metric] for metric in radar_metrics]

            fig.add_trace(
                go.Scatterpolar(
                    r=values + [values[0]],
                    theta=radar_metrics + [radar_metrics[0]],
                    fill="toself",
                    name=row["employee_cluster"]
                )
            )

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Comparativa normalizada de clusters",
            showlegend=True,
            height=650,
            margin=dict(
                l=80,
                r=80,
                t=90,
                b=150
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="center",
                x=0.5,
                title="Cluster"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # 8. Salary Distribution by Archetype
    # --------------------------------------------------------

    st.subheader("Salary Distribution by Archetype")

    fig = px.box(
        filtered_df,
        x="archetype",
        y="real_salary_cost",
        points="outliers",
        title="Distribución de coste salarial real por arquetipo"
    )

    fig.update_traces(
        fillcolor="rgba(46,125,50,0.25)",
        line=dict(color=CORPORATE_GREEN),
        opacity=0.7
    )

    fig.update_layout(
        xaxis_title="Arquetipo",
        yaxis_title="Coste salarial real (€)",
        margin=dict(l=40, r=40, t=80, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # 9. Role Concentration Heatmap
    # --------------------------------------------------------

    st.subheader("Role Concentration Heatmap")

    role_heatmap = pd.crosstab(
        filtered_df["role"],
        filtered_df["archetype"]
    )

    fig = px.imshow(
        role_heatmap,
        text_auto=True,
        color_continuous_scale="Greens",
        title="Concentración de roles por arquetipo"
    )

    fig.update_layout(
        xaxis_title="Arquetipo",
        yaxis_title="Rol"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # 10. Archetype Compensation Matrix
    # --------------------------------------------------------

    st.subheader("Archetype Compensation Matrix")

    fig = px.scatter(
        filtered_df,
        x="real_salary_cost",
        y="revenue_generated",
        color="archetype",
        color_discrete_map=archetype_color_map,
        size="tenure_years",
        hover_data=[
            "employee_name",
            "department",
            "role",
            "performance_score",
            "engagement_score",
            "employee_profit"
        ],
        title="Compensación vs revenue por arquetipo"
    )

    fig.update_layout(
        xaxis_title="Coste salarial real (€)",
        yaxis_title="Revenue anual (€)",
        legend_title="Arquetipo"
    )

    plot_chart(fig)

    # --------------------------------------------------------
    # 11. Contract Risk Analysis
    # --------------------------------------------------------

    st.subheader("Contract Risk Analysis")

    contract_risk = (
        filtered_df.groupby(
            ["contract_type", "attrition_risk_level"]
        )
        .size()
        .reset_index(name="employees")
    )

    fig = px.bar(
        contract_risk,
        x="contract_type",
        y="employees",
        color="attrition_risk_level",
        color_discrete_map=risk_color_map,
        title="Riesgo de fuga por tipo de contrato"
    )

    fig.update_layout(
        xaxis_title="Tipo de contrato",
        yaxis_title="Empleados",
        legend_title="Nivel de riesgo"
    )

    plot_chart(fig)

    # --------------------------------------------------------
    # 12. Insight automático
    # --------------------------------------------------------

    st.subheader("Insight automático")

    if not cluster_profile.empty:

        largest_cluster = (
            cluster_profile
            .sort_values("employees", ascending=False)
            .iloc[0]
        )

        st.success(
            f"El cluster más numeroso es "
            f"'{largest_cluster['employee_cluster']}' "
            f"con {int(largest_cluster['employees'])} empleados."
        )


# MÓDULO 6: ORGANIZATIONAL HEALTH & FRICTION


elif module == "Organizational Health & Friction":

    st.header("Organizational Health & Friction")
    st.write("""
    Este módulo simula una capa de organizational intelligence usando proxies derivados
    del dataset actual para detectar fricción, burnout estructural y estabilidad workforce.
    """)

    show_dataset_preview(df)
    filtered_df = contribution_filter(df, key="health_contribution_filter")

    avg_health = filtered_df["organizational_health_score"].mean()
    avg_friction = filtered_df["friction_score"].mean()
    avg_stability = filtered_df["stability_score"].mean()
    high_pressure_count = (filtered_df["friction_score"] >= 60).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Organizational Health", f"{avg_health:.0f}/100")
    col2.metric("Friction Score", f"{avg_friction:.0f}/100")
    col3.metric("Stability Score", f"{avg_stability:.0f}/100")
    col4.metric("High pressure employees", high_pressure_count)

    st.caption(
        "Estos scores son proxies demo derivados de engagement, work-life balance, absentismo, performance y attrition risk."
    )

    st.subheader("Organizational Friction Heatmap")
    friction_heatmap = (
        filtered_df.groupby(["location", "department"])
        .agg(avg_friction=("friction_score", "mean"))
        .reset_index()
        .pivot(index="location", columns="department", values="avg_friction")
    )

    fig = px.imshow(
        friction_heatmap,
        text_auto=".0f",
        color_continuous_scale="RdYlGn_r",
        title="Friction score medio por ubicación y departamento"
    )
    fig.update_layout(xaxis_title="Departamento", yaxis_title="Location")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Burnout Risk Matrix")
    fig = px.scatter(
        filtered_df,
        x="work_life_balance_score",
        y="performance_score",
        color="burnout_risk",
        color_discrete_map={"Normal": BLUE, "Burnout Risk": ORANGE},
        size="absenteeism_days",
        hover_data=[
            "employee_name",
            "department",
            "location",
            "role",
            "engagement_score",
            "friction_score"
        ],
        title="Burnout Risk Matrix"
    )
    fig.update_layout(
        xaxis_title="Work-life balance",
        yaxis_title="Performance",
        legend_title="Burnout risk"
    )
    plot_chart(fig)

    st.subheader("Workforce Stability Analysis")
    stability_by_department = (
        filtered_df.groupby("department")
        .agg(
            stability_score=("stability_score", "mean"),
            friction_score=("friction_score", "mean"),
            employees=("employee_id", "count")
        )
        .reset_index()
        .sort_values("stability_score", ascending=True)
    )

    fig = px.bar(
        stability_by_department,
        x="stability_score",
        y="department",
        orientation="h",
        color="friction_score",
        color_continuous_scale="RdYlGn_r",
        hover_data=["employees", "friction_score"],
        title="Stability score por departamento"
    )
    fig.update_layout(
        xaxis_title="Stability score",
        yaxis_title="Departamento",
        coloraxis_colorbar_title="Friction"
    )
    plot_chart(fig)

    st.subheader("Manager Pressure Proxy")
    manager_pressure = (
        filtered_df.groupby("department")
        .agg(
            managers=("typeofcontribution", lambda x: (x == "manager").sum()),
            employees=("employee_id", "count"),
            avg_engagement=("engagement_score", "mean"),
            avg_friction=("friction_score", "mean"),
            avg_attrition=("attrition_risk_score", "mean")
        )
        .reset_index()
    )
    manager_pressure["employees_per_manager_proxy"] = manager_pressure["employees"] / manager_pressure["managers"].replace(0, np.nan)
    manager_pressure["employees_per_manager_proxy"] = manager_pressure["employees_per_manager_proxy"].fillna(manager_pressure["employees"])
    manager_pressure["manager_pressure_score"] = (
        normalize_series(manager_pressure["employees_per_manager_proxy"]) * 40 +
        normalize_series(manager_pressure["avg_friction"]) * 40 +
        normalize_series(manager_pressure["avg_attrition"]) * 20
    )

    fig = px.bar(
        manager_pressure.sort_values("manager_pressure_score", ascending=True),
        x="manager_pressure_score",
        y="department",
        orientation="h",
        color="manager_pressure_score",
        color_continuous_scale="Oranges",
        hover_data=["managers", "employees", "employees_per_manager_proxy", "avg_engagement"],
        title="Manager Pressure Proxy por departamento"
    )
    fig.update_layout(
        xaxis_title="Manager pressure score",
        yaxis_title="Departamento",
        coloraxis_colorbar_title="Pressure"
    )
    plot_chart(fig)

    st.subheader("Organizational Risk Constellations")
    risk_constellation_df = filtered_df.copy()
    risk_constellation_df["department_axis"] = pd.Categorical(risk_constellation_df["department"]).codes

    fig = px.scatter_3d(
        risk_constellation_df,
        x="department_axis",
        y="engagement_score",
        z="work_life_balance_score",
        color="location",
        color_discrete_sequence=location_color_sequence,
        size="absenteeism_days",
        hover_data=[
            "employee_name",
            "department",
            "location",
            "role",
            "friction_score",
            "organizational_health_score",
            "absenteeism_days"
        ],
        title="Organizational Risk Constellations"
    )
    fig.update_layout(
        scene=dict(
            xaxis_title="Department",
            yaxis_title="Engagement",
            zaxis_title="Work-Life Balance"
        ),
        legend_title="Location"
    )
    plot_chart(fig)

    st.subheader("Organizational Health Segments")
    health_counts = filtered_df["health_segment"].value_counts().reset_index()
    health_counts.columns = ["Segment", "Employees"]

    fig = px.bar(
        health_counts,
        x="Employees",
        y="Segment",
        orientation="h",
        color="Segment",
        color_discrete_map=health_segment_color_map,
        title="Segmentación de salud organizativa"
    )
    fig.update_layout(xaxis_title="Empleados", yaxis_title="Segmento", showlegend=False)
    plot_chart(fig)

    st.subheader("Insight automático")
    highest_friction = stability_by_department.sort_values("friction_score", ascending=False).iloc[0]
    st.warning(
        f"El departamento con mayor fricción estimada es {highest_friction['department']} "
        f"con un friction score medio de {highest_friction['friction_score']:.0f}/100."
    )


# DESCARGA DEL CSV ENRIQUECIDO


st.sidebar.markdown("---")
st.sidebar.subheader("Descarga de resultados")

csv_output = df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="Descargar CSV enriquecido",
    data=csv_output,
    file_name="hr4techies_people_analytics_enriched.csv",
    mime="text/csv"
)
