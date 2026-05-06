# HR4Techies Advanced People Analytics

## Overview

HR4Techies Advanced People Analytics is a Streamlit-based People Analytics MVP designed to transform employee datasets into executive dashboards, advanced HR insights and AI-driven talent intelligence.

The platform combines:

* People Analytics
* HR Intelligence
* Workforce Segmentation
* Talent Risk Detection
* Internal Mobility Analytics
* Organizational Health Analytics
* AI-driven Clustering and Outlier Detection

The objective is to provide HR teams, Talent leaders and business stakeholders with actionable insights from a simple CSV employee dataset.

---

# Main Features

## Executive Dashboard

The application converts employee data into:

* Executive KPIs
* Interactive visualizations
* Strategic workforce insights
* Talent segmentation
* Risk detection
* Organizational intelligence

---

# Final Modules

## 1. Performance & Productivity Intelligence

Analyzes:

* Employee performance
* Revenue generation
* Salary costs
* Workforce productivity
* Economic efficiency
* Productivity risk

### Main Visualizations

* Executive KPIs
* Revenue vs salary efficiency
* Top performers ranking
* Revenue by department
* Performance vs revenue scatter plot
* Performance vs absenteeism matrix
* Productivity risk table
* 3D productivity visualization

### Advanced Logic

* Salary cost adjusted by country social security burden
* Revenue efficiency calculations
* Productivity risk scoring
* Contribution type segmentation:

  * Producer
  * Support
  * Manager

---

## 2. Employee Attrition & Fidelización

Prioritizes employee attrition risk using:

* Engagement
* Work-life balance
* Absenteeism
* Performance
* Revenue impact

### Main Visualizations

* Attrition KPIs
* Revenue at risk
* Risk exposure by department
* Engagement vs economic impact matrix
* Engagement distribution
* High-risk employees table
* Action recommendation engine

### Advanced Logic

* Attrition risk scoring
* Revenue-at-risk estimation
* High-value low-engagement detection
* Strategic attrition prioritization

---

## 3. Role Matching & Promotion

Recommends:

* Internal mobility opportunities
* Promotion readiness
* Career path alignment
* Role fit by skills

### Main Visualizations

* Employee selector
* Individual employee profile
* Internal role recommendations
* Promotion readiness score
* Promotion candidates ranking
* Performance vs tenure matrix
* Skills radar chart

### Advanced Logic

* Skill matching engine
* Promotion scoring
* Readiness segmentation
* Internal talent mobility analysis

---

## 4. Employees Archetypes & Clustering

Segments the workforce into:

* Strategic archetypes
* Employee clusters
* Workforce behavior patterns

### Main Visualizations

* Archetype distribution
* Workforce 3D visualization
* Employee clustering map
* Cluster distribution
* Archetype profiles
* Contract type analysis
* Salary distribution by cluster
* Role and location segmentation

### Advanced Logic

* KMeans clustering
* Workforce segmentation
* Archetype classification
* Cluster profiling
* Organizational segmentation analytics

---

## 5. Talent Outliers Analysis

Detects:

* High-impact talent
* Critical retention risks
* Hidden talent
* Burnout risks
* Talent anomalies

### Main Visualizations

* Outlier KPIs
* Outlier Constellations visualization
* Outliers by contribution type
* Outliers by department
* Outliers by seniority
* Critical talent table

### Advanced Logic

* Isolation Forest anomaly detection
* High-impact employee detection
* Revenue vs engagement anomalies
* Strategic talent prioritization

---

## 6. Organizational Health & Friction

Simulates organizational friction and health indicators.

### Main Visualizations

* Organizational health KPIs
* Friction hotspots
* Department friction analysis
* Workload imbalance analysis
* Organizational stability indicators
* Heatmaps and risk matrices

### Advanced Logic

* Organizational health scoring
* Friction simulation models
* Cross-variable organizational analysis
* Workforce stability indicators

---

# Technologies Used

## Frontend

* Streamlit
* Plotly

## Data Processing

* Pandas
* NumPy

## Machine Learning

* Scikit-learn

  * KMeans
  * Isolation Forest
  * PCA
  * StandardScaler

## Visualization

* Plotly Express
* Interactive 2D and 3D visualizations

---

# Project Structure

```bash
HR4Techies/
│
├── app.py
├── requirements.txt
├── README.md
├── hr4techies_people_analytics_dataset.csv
├── Positivo verde.png
└── .streamlit/
    └── config.toml
```

---

# Installation

## 1. Clone repository

```bash
git clone <repository_url>
cd HR4Techies
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Run application

```bash
streamlit run app.py
```

---

# Required Dataset Structure

The application works with a People Analytics dataset including:

* Employee data
* Salary data
* Performance metrics
* Engagement scores
* Revenue generated
* Skills
* Attrition indicators
* Organizational variables

A demo dataset is included.

---

# Design Principles

The application follows:

* Corporate green visual identity
* Executive dashboard aesthetics
* Minimalist visualizations
* Low saturation color palette
* Consistent visual hierarchy
* Responsive layout
* HR executive-oriented storytelling

---

# Future Roadmap

Potential future improvements:

* Real AI recommendations
* LLM-based HR copilots
* Predictive workforce planning
* Real-time integrations
* ATS integrations
* HRIS integrations
* Organizational network analysis
* Advanced succession planning
* AI-powered workforce simulations

---

# Author

Pablo Lozano Garnacho

Founder of HR4Techies

People Analytics · HR Intelligence · AI for HR · Talent Strategy
