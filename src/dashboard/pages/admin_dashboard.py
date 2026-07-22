"""
Admin Dashboard Page Module.
System overview, user management, analytics, and model monitoring.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from config.config import config
from src.ml.analytics_engine import AnalyticsEngine
from src.ml.placement_model import PlacementPredictor
from src.ml.salary_model import SalaryPredictor


def render_system_overview():
    st.markdown("### System Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", "500")
    with col2:
        st.metric("Resumes Analyzed", str(len(st.session_state.get("resume_analyses", []))))
    with col3:
        st.metric("Predictions Made", str(len(st.session_state.prediction_history)))
    with col4:
        st.metric("Emails Sent", str(st.session_state.email_service.get_email_count()))

    st.markdown("---")
    st.markdown("### Model Status")

    col_a, col_b = st.columns(2)
    with col_a:
        placement = st.session_state.placement_predictor
        st.info(f"Placement Model: {'Trained' if placement.is_trained else 'Not Trained'}")
        if placement.is_trained and hasattr(placement, 'metrics'):
            m = placement.metrics
            st.write(f"  - Accuracy: {m.get('accuracy', 0):.2%}")
            st.write(f"  - F1 Score: {m.get('f1_score', 0):.2%}")

    with col_b:
        salary = st.session_state.salary_predictor
        st.info(f"Salary Model: {'Trained' if salary.is_trained else 'Not Trained'}")
        if salary.is_trained and hasattr(salary, 'metrics'):
            m = salary.metrics
            st.write(f"  - R² Score: {m.get('r2_score', 0):.4f}")
            st.write(f"  - MAE: {m.get('mae', 0):.2f}")


def render_analytics_dashboard():
    st.markdown("### Analytics Dashboard")

    analytics = AnalyticsEngine()
    chart_types = [
        "Placement Distribution", "Salary Distribution", "Skill Demand",
        "Company-wise Comparison", "CGPA vs Placement", "Risk Analysis",
    ]

    selected = st.multiselect("Select Charts", chart_types, default=chart_types[:3])

    for chart_name in selected:
        try:
            method_map = {
                "Placement Distribution": "create_placement_distribution_chart",
                "Salary Distribution": "create_salary_distribution_chart",
                "Skill Demand": "create_skill_demand_chart",
                "Company-wise Comparison": "create_company_comparison_chart",
                "CGPA vs Placement": "create_cgpa_vs_placement_chart",
                "Risk Analysis": "create_risk_analysis_chart",
            }
            method_name = method_map.get(chart_name)
            if method_name and hasattr(analytics, method_name):
                fig = getattr(analytics, method_name)()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate {chart_name}: {e}")


def render_user_management():
    st.markdown("### User Management")

    users = pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],
        "Name": ["Alice Student", "Bob Student", "Carol Admin", "Dave Officer", "Eve Student"],
        "Role": ["student", "student", "admin", "placement_officer", "student"],
        "Status": ["Active", "Active", "Active", "Active", "Inactive"],
        "Predictions": [12, 8, 0, 3, 5],
    })

    st.dataframe(users, use_container_width=True)

    st.markdown("---")
    st.markdown("### System Configuration")
    with st.expander("View Configuration"):
        st.json({
            "APP_NAME": config.APP_NAME,
            "APP_VERSION": config.APP_VERSION,
            "MAX_UPLOAD_SIZE_MB": config.MAX_UPLOAD_SIZE_MB,
            "SESSION_TIMEOUT_MIN": config.SESSION_TIMEOUT_MIN,
            "ML_CV_FOLDS": config.ml.CV_FOLDS,
            "SPACY_MODEL": config.nlp.SPACY_MODEL,
            "COMPANIES_COUNT": len(config.companies.COMPANIES),
        })


def render_data_management():
    st.markdown("### Data Management")

    tab1, tab2, tab3 = st.tabs(["Datasets", "Models", "Logs"])

    with tab1:
        st.markdown("#### Generated Datasets")
        data_dir = os.path.join("data", "datasets")
        if os.path.exists(data_dir):
            for f in os.listdir(data_dir):
                if f.endswith(".csv"):
                    path = os.path.join(data_dir, f)
                    size = os.path.getsize(path) / 1024
                    st.write(f"📄 {f} ({size:.1f} KB)")
        else:
            st.info("No datasets found. Run initialize.py to generate them.")

    with tab2:
        st.markdown("#### Trained Models")
        model_dir = config.ml.MODEL_PATH
        if os.path.exists(model_dir):
            for f in os.listdir(model_dir):
                if f.endswith(('.pkl', '.joblib')):
                    path = os.path.join(model_dir, f)
                    size = os.path.getsize(path) / 1024
                    st.write(f"🤖 {f} ({size:.1f} KB)")
        else:
            st.info("No models found.")

    with tab3:
        st.markdown("#### Application Logs")
        log_dir = "logs"
        if os.path.exists(log_dir):
            for f in sorted(os.listdir(log_dir), reverse=True)[:5]:
                st.write(f"📋 {f}")
        else:
            st.info("No logs found.")
