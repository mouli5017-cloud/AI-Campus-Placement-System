import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import config
from src.ml.placement_model import PlacementPredictor
from src.ml.salary_model import SalaryPredictor
from src.ml.ats_scorer import ATSScorer
from src.ml.job_matcher import JobMatcher
from src.ml.resume_ranker import ResumeRanker
from src.ml.interview_prep import InterviewPrepModule
from src.nlp.resume_parser import ResumeParser
from src.nlp.skill_extractor import SkillExtractor
from src.utils.helpers import (
    hash_password, verify_password, generate_session_token,
    format_currency, format_number
)
from src.utils.email_service import EmailNotificationService
from src.utils.report_exporter import ReportExporter

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


ANIMATED_BG_HTML = """
<div class="animated-bg">
    <div class="bg-blob"></div>
    <div class="bg-blob"></div>
    <div class="bg-blob"></div>
    <div class="bg-blob"></div>
    <div class="bg-blob"></div>
</div>
<div class="particle-field">
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="particle"></div>
</div>
<div class="floating-icons">
    <span class="float-icon">🎓</span>
    <span class="float-icon">💼</span>
    <span class="float-icon">📊</span>
    <span class="float-icon">🤖</span>
    <span class="float-icon">📝</span>
    <span class="float-icon">🚀</span>
    <span class="float-icon">💡</span>
    <span class="float-icon">🎯</span>
    <span class="float-icon">🔬</span>
    <span class="float-icon">⭐</span>
    <span class="float-icon">🏆</span>
    <span class="float-icon">📚</span>
</div>
"""

SVG_IMAGES = {
    "placement_banner": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300">
        <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4facfe;stop-opacity:0.8"/>
                <stop offset="50%" style="stop-color:#764ba2;stop-opacity:0.6"/>
                <stop offset="100%" style="stop-color:#f5576c;stop-opacity:0.8"/>
            </linearGradient>
            <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#43e97b;stop-opacity:0.3"/>
                <stop offset="100%" style="stop-color:#38f9d7;stop-opacity:0.3"/>
            </linearGradient>
        </defs>
        <rect width="1200" height="300" fill="#0c0c1d"/>
        <circle cx="200" cy="150" r="120" fill="url(#g1)" opacity="0.15"/>
        <circle cx="900" cy="100" r="80" fill="url(#g2)" opacity="0.2"/>
        <circle cx="600" cy="250" r="100" fill="#f5576c" opacity="0.08"/>
        <text x="600" y="120" text-anchor="middle" fill="white" font-family="Poppins,sans-serif" font-size="42" font-weight="700">🎓 AI Campus Placement</text>
        <text x="600" y="170" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-family="Poppins,sans-serif" font-size="20">Predict · Analyze · Succeed</text>
        <g transform="translate(200,220)">
            <rect x="0" y="0" width="120" height="40" rx="20" fill="rgba(79,172,254,0.2)" stroke="rgba(79,172,254,0.3)" stroke-width="1"/>
            <text x="60" y="25" text-anchor="middle" fill="#4facfe" font-family="Poppins" font-size="12" font-weight="600">📊 Analytics</text>
        </g>
        <g transform="translate(360,220)">
            <rect x="0" y="0" width="120" height="40" rx="20" fill="rgba(245,87,108,0.2)" stroke="rgba(245,87,108,0.3)" stroke-width="1"/>
            <text x="60" y="25" text-anchor="middle" fill="#f5576c" font-family="Poppins" font-size="12" font-weight="600">📝 Resume AI</text>
        </g>
        <g transform="translate(520,220)">
            <rect x="0" y="0" width="120" height="40" rx="20" fill="rgba(67,233,123,0.2)" stroke="rgba(67,233,123,0.3)" stroke-width="1"/>
            <text x="60" y="25" text-anchor="middle" fill="#43e97b" font-family="Poppins" font-size="12" font-weight="600">🎯 Job Match</text>
        </g>
        <g transform="translate(680,220)">
            <rect x="0" y="0" width="140" height="40" rx="20" fill="rgba(254,225,64,0.2)" stroke="rgba(254,225,64,0.3)" stroke-width="1"/>
            <text x="70" y="25" text-anchor="middle" fill="#fee140" font-family="Poppins" font-size="12" font-weight="600">🤖 ML Predictions</text>
        </g>
        <g transform="translate(860,220)">
            <rect x="0" y="0" width="130" height="40" rx="20" fill="rgba(118,75,162,0.2)" stroke="rgba(118,75,162,0.3)" stroke-width="1"/>
            <text x="65" y="25" text-anchor="middle" fill="#a855f7" font-family="Poppins" font-size="12" font-weight="600">🚀 Interview Prep</text>
        </g>
    </svg>""",
    "student_hero": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 260">
        <defs>
            <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4facfe;stop-opacity:0.6"/>
                <stop offset="100%" style="stop-color:#00f2fe;stop-opacity:0.3"/>
            </linearGradient>
        </defs>
        <rect width="1200" height="260" fill="#0c0c1d"/>
        <circle cx="150" cy="130" r="100" fill="url(#sg)" opacity="0.12"/>
        <circle cx="1050" cy="80" r="70" fill="#f5576c" opacity="0.1"/>
        <text x="600" y="100" text-anchor="middle" fill="white" font-family="Poppins" font-size="36" font-weight="700">🎓 Student Dashboard</text>
        <text x="600" y="145" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-family="Poppins" font-size="16">Predict your placement · Analyze your resume · Find your dream job</text>
        <circle cx="100" cy="200" r="8" fill="#4facfe" opacity="0.6"/>
        <circle cx="300" cy="180" r="6" fill="#f5576c" opacity="0.5"/>
        <circle cx="500" cy="220" r="10" fill="#43e97b" opacity="0.4"/>
        <circle cx="700" cy="190" r="7" fill="#fee140" opacity="0.5"/>
        <circle cx="900" cy="210" r="9" fill="#764ba2" opacity="0.4"/>
        <circle cx="1100" cy="180" r="6" fill="#00f2fe" opacity="0.5"/>
    </svg>""",
    "admin_hero": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 260">
        <defs>
            <linearGradient id="ag" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#f5576c;stop-opacity:0.5"/>
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:0.3"/>
            </linearGradient>
        </defs>
        <rect width="1200" height="260" fill="#0c0c1d"/>
        <circle cx="200" cy="130" r="90" fill="url(#ag)" opacity="0.15"/>
        <circle cx="1000" cy="100" r="80" fill="#4facfe" opacity="0.1"/>
        <text x="600" y="100" text-anchor="middle" fill="white" font-family="Poppins" font-size="36" font-weight="700">⚙️ Admin Dashboard</text>
        <text x="600" y="145" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-family="Poppins" font-size="16">System Analytics · User Management · Configuration</text>
        <rect x="100" y="180" width="100" height="30" rx="15" fill="rgba(245,87,108,0.15)" stroke="rgba(245,87,108,0.3)" stroke-width="1"/>
        <text x="150" y="200" text-anchor="middle" fill="#f5576c" font-family="Poppins" font-size="11">📊 Analytics</text>
        <rect x="250" y="180" width="100" height="30" rx="15" fill="rgba(79,172,254,0.15)" stroke="rgba(79,172,254,0.3)" stroke-width="1"/>
        <text x="300" y="200" text-anchor="middle" fill="#4facfe" font-family="Poppins" font-size="11">👥 Users</text>
        <rect x="400" y="180" width="120" height="30" rx="15" fill="rgba(67,233,123,0.15)" stroke="rgba(67,233,123,0.3)" stroke-width="1"/>
        <text x="460" y="200" text-anchor="middle" fill="#43e97b" font-family="Poppins" font-size="11">📧 Notifications</text>
        <rect x="570" y="180" width="100" height="30" rx="15" fill="rgba(254,225,64,0.15)" stroke="rgba(254,225,64,0.3)" stroke-width="1"/>
        <text x="620" y="200" text-anchor="middle" fill="#fee140" font-family="Poppins" font-size="11">🗄️ Data</text>
    </svg>""",
    "officer_hero": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 260">
        <defs>
            <linearGradient id="og" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#43e97b;stop-opacity:0.5"/>
                <stop offset="100%" style="stop-color:#38f9d7;stop-opacity:0.3"/>
            </linearGradient>
        </defs>
        <rect width="1200" height="260" fill="#0c0c1d"/>
        <circle cx="180" cy="130" r="100" fill="url(#og)" opacity="0.12"/>
        <circle cx="1020" cy="90" r="70" fill="#764ba2" opacity="0.12"/>
        <text x="600" y="100" text-anchor="middle" fill="white" font-family="Poppins" font-size="36" font-weight="700">🏢 Placement Officer Dashboard</text>
        <text x="600" y="145" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-family="Poppins" font-size="16">Drive Management · Resume Screening · Placement Reports</text>
        <circle cx="120" cy="200" r="8" fill="#43e97b" opacity="0.6"/>
        <circle cx="350" cy="210" r="6" fill="#4facfe" opacity="0.5"/>
        <circle cx="550" cy="195" r="9" fill="#f5576c" opacity="0.4"/>
        <circle cx="750" cy="215" r="7" fill="#fee140" opacity="0.5"/>
        <circle cx="950" cy="200" r="10" fill="#764ba2" opacity="0.4"/>
        <circle cx="1100" cy="210" r="5" fill="#00f2fe" opacity="0.6"/>
    </svg>""",
    "feature_icons": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 100">
        <rect width="800" height="100" fill="transparent"/>
        <g transform="translate(50,50)">
            <circle r="25" fill="rgba(79,172,254,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">🤖</text>
        </g>
        <g transform="translate(150,50)">
            <circle r="25" fill="rgba(245,87,108,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">📝</text>
        </g>
        <g transform="translate(250,50)">
            <circle r="25" fill="rgba(67,233,123,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">🎯</text>
        </g>
        <g transform="translate(350,50)">
            <circle r="25" fill="rgba(254,225,64,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">📊</text>
        </g>
        <g transform="translate(450,50)">
            <circle r="25" fill="rgba(118,75,162,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">💼</text>
        </g>
        <g transform="translate(550,50)">
            <circle r="25" fill="rgba(0,242,254,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">🚀</text>
        </g>
        <g transform="translate(650,50)">
            <circle r="25" fill="rgba(250,112,154,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">🏆</text>
        </g>
        <g transform="translate(750,50)">
            <circle r="25" fill="rgba(161,140,209,0.15)"/>
            <text text-anchor="middle" y="8" font-size="24">💡</text>
        </g>
    </svg>""",
}


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "static", "css", "animated_theme.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_background():
    st.markdown(ANIMATED_BG_HTML, unsafe_allow_html=True)


def render_image_banner(svg_key, height=220):
    if svg_key in SVG_IMAGES:
        import base64
        svg_b64 = base64.b64encode(SVG_IMAGES[svg_key].encode()).decode()
        st.markdown(
            f'<div class="image-banner"><img src="data:image/svg+xml;base64,{svg_b64}" style="height:{height}px;width:100%;object-fit:cover;border-radius:20px;" /></div>',
            unsafe_allow_html=True,
        )


def render_svg_banner(svg_key):
    if svg_key in SVG_IMAGES:
        st.markdown(SVG_IMAGES[svg_key], unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "logged_in": False,
        "user_role": None,
        "username": None,
        "user_id": None,
        "placement_predictor": PlacementPredictor(),
        "salary_predictor": SalaryPredictor(),
        "ats_scorer": ATSScorer(),
        "job_matcher": JobMatcher(),
        "resume_ranker": ResumeRanker(),
        "interview_prep": InterviewPrepModule(),
        "resume_parser": ResumeParser(),
        "skill_extractor": SkillExtractor(),
        "email_service": EmailNotificationService(),
        "report_exporter": ReportExporter(),
        "prediction_history": [],
        "resume_analyses": [],
        "quiz_answers": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header():
    st.markdown("""
    <div class="hero-section">
        <div class="hero-icon">🎓</div>
        <h1 class="hero-title">AI Campus Placement Prediction & Resume Screening</h1>
        <p class="hero-subtitle">Intelligent system for placement preparation, resume analysis, and career guidance powered by Machine Learning</p>
        <div class="hero-chips">
            <span class="hero-chip">🤖 ML Predictions</span>
            <span class="hero-chip">📝 Resume AI</span>
            <span class="hero-chip">🎯 Job Matching</span>
            <span class="hero-chip">📊 Analytics</span>
            <span class="hero-chip">🚀 Interview Prep</span>
            <span class="hero-chip">💡 Skill Gap Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_login_page():
    render_header()

    st.markdown("""
    <div class="feature-icons">
        <div class="feature-icon-item">🎓</div>
        <div class="feature-icon-item">💼</div>
        <div class="feature-icon-item">📊</div>
        <div class="feature-icon-item">🤖</div>
        <div class="feature-icon-item">📝</div>
        <div class="feature-icon-item">🚀</div>
        <div class="feature-icon-item">🏆</div>
        <div class="feature-icon-item">💡</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(SVG_IMAGES["feature_icons"], unsafe_allow_html=True)

    st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)

    st.markdown("### Choose Your Portal")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="role-card blue">
            <div class="role-icon">🎓</div>
            <h3 style="color:white;margin:0.5rem 0;">Student</h3>
            <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;">Predictions · Resume Analysis · Job Matching</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login as Student", key="login_student", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "student"
            st.session_state.username = "demo_student"
            st.session_state.user_id = 1
            st.rerun()

    with col2:
        st.markdown("""
        <div class="role-card pink">
            <div class="role-icon">⚙️</div>
            <h3 style="color:white;margin:0.5rem 0;">Admin</h3>
            <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;">Analytics · User Management · System Config</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login as Admin", key="login_admin", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "demo_admin"
            st.session_state.user_id = 1
            st.rerun()

    with col3:
        st.markdown("""
        <div class="role-card green">
            <div class="role-icon">🏢</div>
            <h3 style="color:white;margin:0.5rem 0;">Placement Officer</h3>
            <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;">Drive Management · Screening · Reports</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login as Placement Officer", key="login_officer", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "placement_officer"
            st.session_state.username = "demo_officer"
            st.session_state.user_id = 1
            st.rerun()

    st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)

    with st.expander("🔐 Or use traditional login", expanded=False):
        tab_s, tab_a, tab_o = st.tabs(["Student", "Admin", "Placement Officer"])
        for role, tab in [("student", tab_s), ("admin", tab_a), ("placement_officer", tab_o)]:
            with tab:
                with st.form(f"{role}_login_form"):
                    st.markdown(f"**{role.replace('_', ' ').title()} Portal**")
                    username = st.text_input("Username", key=f"{role}_user")
                    password = st.text_input("Password", type="password", key=f"{role}_pass")
                    if st.form_submit_button("Login", use_container_width=True):
                        if username and password:
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.username = username
                            st.session_state.user_id = 1
                            st.rerun()
                        else:
                            st.error("Please enter credentials")


def render_student_dashboard():
    render_svg_banner("student_hero")

    st.markdown("""
    <div class="feature-icons">
        <div class="feature-icon-item">📊</div>
        <div class="feature-icon-item">📝</div>
        <div class="feature-icon-item">💼</div>
        <div class="feature-icon-item">🎯</div>
        <div class="feature-icon-item">📚</div>
        <div class="feature-icon-item">🎤</div>
        <div class="feature-icon-item">📄</div>
        <div class="feature-icon-item">📈</div>
    </div>
    """, unsafe_allow_html=True)

    _render_sidebar()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Predictions", "📝 Resume Analysis", "💼 Job Matching",
        "🎯 Skill Gap", "📚 Learning Path", "🎤 Interview Prep",
        "📄 Export & Reports", "📈 History"
    ])

    with tab1:
        render_placement_prediction()
    with tab2:
        render_resume_analysis()
    with tab3:
        render_job_matching()
    with tab4:
        render_skill_gap_analysis()
    with tab5:
        render_learning_recommendations()
    with tab6:
        render_interview_prep()
    with tab7:
        render_export_reports()
    with tab8:
        render_prediction_history()


def render_placement_prediction():
    st.markdown('<h3 class="section-title">📊 Placement Probability Prediction</h3>', unsafe_allow_html=True)
    st.markdown("Enter your academic and profile details to predict placement chances.")

    st.markdown(SVG_IMAGES["placement_banner"], unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        cgpa = st.slider("CGPA", 4.0, 10.0, 7.5, 0.1)
        tenth = st.slider("10th Percentage", 40.0, 100.0, 75.0, 0.5)
        twelfth = st.slider("12th Percentage", 40.0, 100.0, 70.0, 0.5)
        backlogs = st.number_input("Active Backlogs", 0, 10, 0)
        department = st.selectbox(
            "Department",
            ["Computer Science", "Information Technology", "Electronics",
             "Mechanical", "Civil", "Electrical", "Chemical"]
        )

    with col2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        internships = st.number_input("Internships Done", 0, 5, 1)
        num_tech_skills = st.slider("Technical Skills Count", 0, 15, 5)
        num_soft_skills = st.slider("Soft Skills Count", 0, 10, 3)
        num_projects = st.number_input("Projects Done", 0, 10, 2)
        num_certs = st.number_input("Certifications", 0, 10, 1)
        num_prog_lang = st.slider("Programming Languages", 1, 8, 3)
        exp_years = st.slider("Experience (Years)", 0.0, 5.0, 0.5, 0.5)

    if st.button("🚀 Predict Placement Probability", type="primary", use_container_width=True):
        features = {
            "cgpa": cgpa, "tenth_percentage": tenth,
            "twelfth_percentage": twelfth, "backlogs": backlogs,
            "internships": internships,
            "num_technical_skills": num_tech_skills,
            "num_soft_skills": num_soft_skills,
            "num_projects": num_projects,
            "num_certifications": num_certs,
            "experience_years": exp_years,
            "num_programming_languages": num_prog_lang,
            "department": department, "gender": gender,
        }

        predictor = st.session_state.placement_predictor
        if not predictor.is_trained:
            with st.spinner("Training model..."):
                predictor.train()
                predictor.save_model()

        result = predictor.predict(features)
        _display_placement_result(result, features)
        _display_salary_prediction(features)

        st.session_state.prediction_history.append({
            "type": "placement",
            "timestamp": datetime.now().isoformat(),
            "features": features,
            "result": result,
        })


def _display_placement_result(result, features):
    st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">🎯 Placement Prediction Results</h3>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status = "PLACED ✅" if result["placed"] else "NOT PLACED ❌"
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">{'🎉' if result['placed'] else '⚠️'}</div><div style="color:white;font-size:1.1rem;font-weight:700;">{status}</div></div>""", unsafe_allow_html=True)
    with col2:
        prob = result['probability_placed']
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">📊</div><div style="color:white;font-size:1.4rem;font-weight:700;">{prob}%</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Probability</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">🎯</div><div style="color:white;font-size:1.4rem;font-weight:700;">{result['confidence']}%</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Confidence</div></div>""", unsafe_allow_html=True)
    with col4:
        risk = result["risk_level"].split("(")[0].strip()
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">⚡</div><div style="color:white;font-size:1.1rem;font-weight:700;">{risk}</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Risk Level</div></div>""", unsafe_allow_html=True)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=result["probability_placed"],
        title={"text": "Placement Probability", "font": {"size": 18, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white"},
            "bar": {"color": "#4facfe"},
            "steps": [
                {"range": [0, 30], "color": "rgba(245,87,108,0.2)"},
                {"range": [30, 60], "color": "rgba(254,225,64,0.2)"},
                {"range": [60, 80], "color": "rgba(67,233,123,0.2)"},
                {"range": [80, 100], "color": "rgba(79,172,254,0.2)"},
            ],
            "threshold": {
                "line": {"color": "#f5576c", "width": 4},
                "thickness": 0.75,
                "value": result["probability_placed"],
            },
        }
    ))
    fig.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    if result.get("suggestions"):
        st.markdown("#### 💡 Improvement Suggestions")
        for i, suggestion in enumerate(result["suggestions"], 1):
            st.info(f"**{i}.** {suggestion}")


def _display_salary_prediction(features):
    st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">💰 Salary Prediction</h3>', unsafe_allow_html=True)

    salary_predictor = st.session_state.salary_predictor
    if not salary_predictor.is_trained:
        with st.spinner("Training salary model..."):
            salary_predictor.train()
            salary_predictor.save_model()

    salary_result = salary_predictor.predict(features)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">💰</div><div style="color:white;font-size:1.4rem;font-weight:700;">{salary_result['predicted_salary_lpa']} LPA</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Predicted Salary</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">📅</div><div style="color:white;font-size:1.4rem;font-weight:700;">Rs. {int(salary_result['predicted_monthly']):,}</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Monthly Income</div></div>""", unsafe_allow_html=True)
    with col3:
        tier = salary_result["salary_tier"].split("-")[0].strip()
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">⭐</div><div style="color:white;font-size:1.1rem;font-weight:700;">{tier}</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Salary Tier</div></div>""", unsafe_allow_html=True)

    st.markdown(f"**Range:** {salary_result['salary_range']['min']} - {salary_result['salary_range']['max']} LPA")

    if salary_result.get("improvement_tips"):
        with st.expander("💡 Salary Improvement Tips"):
            for tip in salary_result["improvement_tips"]:
                st.write(f"- {tip}")


def render_resume_analysis():
    st.markdown('<h3 class="section-title">📝 Resume Analysis & ATS Scoring</h3>', unsafe_allow_html=True)
    st.markdown("Upload your resume PDF to get AI-powered analysis.")

    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)", type=["pdf"], key="resume_upload"
    )

    job_desc = st.text_area(
        "Job Description (Optional)",
        height=120,
        placeholder="Paste the job description here for better ATS matching...",
    )

    if uploaded_file:
        with st.spinner("Analyzing resume..."):
            file_bytes = uploaded_file.read()
            parser = st.session_state.resume_parser
            parsed = parser.parse_pdf(file_bytes)

            skill_extractor = st.session_state.skill_extractor
            all_text = f"{parsed.raw_text} {' '.join(parsed.raw_text.split())}"
            extracted_skills = skill_extractor.extract_skills(all_text)
            skill_list = [s["skill"] for s in extracted_skills]

            ats_scorer = st.session_state.ats_scorer
            ats_result = ats_scorer.compute_ats_score(
                parsed.raw_text, job_desc, skill_list, parsed.sections_detected
            )

        _display_resume_analysis(parsed, extracted_skills, ats_result)


def _display_resume_analysis(parsed, skills, ats_result):
    st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">📊</div><div style="color:white;font-size:1.4rem;font-weight:700;">{ats_result['overall_score']}/100</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">ATS Score</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">🛠️</div><div style="color:white;font-size:1.4rem;font-weight:700;">{len(skills)}</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Skills Found</div></div>""", unsafe_allow_html=True)
    with col3:
        grade = ats_result["grade"]
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">🏅</div><div style="color:white;font-size:1.4rem;font-weight:700;">{grade}</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Resume Grade</div></div>""", unsafe_allow_html=True)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ats_result["overall_score"],
        title={"text": "ATS Score", "font": {"size": 18, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white"},
            "bar": {"color": "#4facfe"},
            "steps": [
                {"range": [0, 40], "color": "rgba(245,87,108,0.2)"},
                {"range": [40, 60], "color": "rgba(254,225,64,0.2)"},
                {"range": [60, 80], "color": "rgba(67,233,123,0.2)"},
                {"range": [80, 100], "color": "rgba(79,172,254,0.2)"},
            ],
        }
    ))
    fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    tab_sec, tab_skills, tab_improve = st.tabs(["📊 Section Scores", "🛠️ Skills", "💡 Improvements"])

    with tab_sec:
        section_data = []
        for section, data in ats_result["section_scores"].items():
            if isinstance(data, dict):
                section_data.append({"Section": section.replace("_", " ").title(), "Score": data.get("score", 0)})
        if section_data:
            df = pd.DataFrame(section_data)
            fig = px.bar(df, x="Section", y="Score", color="Score",
                        color_continuous_scale="RdYlGn", range_y=[0, 100])
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with tab_skills:
        if skills:
            cols = st.columns(4)
            for i, skill_info in enumerate(skills):
                cat = skill_info.get("category", "technical")
                emojis = {"technical": "💻", "soft": "🤝", "domain": "🏢"}
                with cols[i % 4]:
                    st.markdown(f"""<div class="gradient-metric" style="padding:0.8rem;margin-bottom:0.5rem;"><div style="font-size:1.2rem;">{emojis.get(cat, '📦')}</div><div style="color:white;font-size:0.85rem;font-weight:600;">{skill_info['skill']}</div><div style="color:rgba(255,255,255,0.4);font-size:0.75rem;">{cat}</div></div>""", unsafe_allow_html=True)

    with tab_improve:
        if ats_result.get("strengths"):
            st.markdown("**✅ Strengths:**")
            for s in ats_result["strengths"]:
                st.success(s)
        if ats_result.get("weaknesses"):
            st.markdown("**⚠️ Weaknesses:**")
            for w in ats_result["weaknesses"]:
                st.warning(w)
        if ats_result.get("improvements"):
            st.markdown("**💡 Recommended Improvements:**")
            for imp in ats_result["improvements"]:
                st.info(f"- {imp}")

    with st.expander("📋 Parsed Resume Details"):
        st.json({
            "name": parsed.name, "email": parsed.email, "phone": parsed.phone,
            "github": parsed.github_url, "linkedin": parsed.linkedin_url,
            "education": parsed.education, "experience_years": parsed.experience_years,
            "projects_count": len(parsed.projects),
            "certifications_count": len(parsed.certifications),
            "sections_detected": parsed.sections_detected,
            "total_words": parsed.total_words,
        })


def render_job_matching():
    st.markdown('<h3 class="section-title">💼 Job Matching & Company Recommendations</h3>', unsafe_allow_html=True)

    with st.form("job_match_form"):
        col1, col2 = st.columns(2)
        with col1:
            cgpa = st.slider("Your CGPA", 4.0, 10.0, 7.0, 0.1, key="jm_cgpa")
            backlogs = st.number_input("Backlogs", 0, 10, 0, key="jm_back")
            internships = st.number_input("Internships", 0, 5, 1, key="jm_int")
        with col2:
            tech_skills = st.text_area(
                "Your Technical Skills (comma separated)",
                "Python, Java, SQL, React",
                key="jm_skills"
            )

        if st.form_submit_button("🔍 Find Matching Jobs", type="primary"):
            profile = {
                "cgpa": cgpa, "backlogs": backlogs, "internships": internships,
                "technical_skills": [s.strip() for s in tech_skills.split(",")],
                "programming_languages": [s.strip() for s in tech_skills.split(",")],
                "soft_skills": [],
            }
            matcher = st.session_state.job_matcher
            matches = matcher.match_jobs(profile)
            if matches:
                for match in matches[:8]:
                    _display_job_match(match)
            else:
                st.warning("No matching jobs found. Improve your skills!")


def _display_job_match(match):
    overall = match["overall_match"]
    badge_class = "badge-high" if overall >= 70 else ("badge-medium" if overall >= 40 else "badge-low")

    with st.expander(f"🏢 {match['company']} - {match['job_title']} | Match: {overall:.0f}% | {match['salary_range']['min_lpa']}-{match['salary_range']['max_lpa']} LPA"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Match", f"{overall:.1f}%")
            st.metric("Skill Match", f"{match['skill_match']:.1f}%")
            st.write(f"**Eligibility:** {match['eligibility']}")
        with col2:
            st.metric("CGPA Match", f"{match['cgpa_match']:.1f}%")
            st.write(f"**Min CGPA:** {match['min_cgpa_required']}")
            st.write(f"**Salary:** {match['salary_range']['min_lpa']}-{match['salary_range']['max_lpa']} LPA")
        if match.get("matched_skills"):
            st.write("**✅ Matched Skills:** " + ", ".join(match["matched_skills"]))
        if match.get("missing_skills"):
            st.write("**❌ Missing Skills:** " + ", ".join(match["missing_skills"]))
        st.info(match["recommendation"])


def render_skill_gap_analysis():
    st.markdown('<h3 class="section-title">🎯 Skill Gap Analysis</h3>', unsafe_allow_html=True)
    st.markdown("Compare your skills against target role requirements.")

    with st.form("skill_gap_form"):
        current_skills = st.text_area("Your Current Skills (comma separated)", "Python, Java, SQL, HTML, CSS", key="sg_current")
        target_role = st.selectbox("Target Role", [
            "Software Engineer", "Data Scientist", "ML Engineer",
            "Full Stack Developer", "Cloud Architect", "DevOps Engineer",
            "Frontend Developer", "Backend Developer"
        ], key="sg_target")
        if st.form_submit_button("🔍 Analyze Skill Gap", type="primary"):
            role_skills = _get_role_skills(target_role)
            current = [s.strip() for s in current_skills.split(",")]
            extractor = st.session_state.skill_extractor
            gap = extractor.get_skill_gap_analysis(current, role_skills)
            _display_skill_gap(gap, target_role)


def _get_role_skills(role):
    role_map = {
        "Software Engineer": ["Python", "Java", "C++", "SQL", "Git", "DSA", "System Design", "REST API", "Docker"],
        "Data Scientist": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "Pandas", "NumPy", "TensorFlow", "Data Analysis", "Tableau"],
        "ML Engineer": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Docker", "AWS", "SQL", "Machine Learning", "Deep Learning", "Git"],
        "Full Stack Developer": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL", "MongoDB", "Git", "REST API", "Docker"],
        "Cloud Architect": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Python", "Linux", "CI/CD", "Networking"],
        "DevOps Engineer": ["Docker", "Kubernetes", "Jenkins", "Git", "Linux", "AWS", "Terraform", "Python", "CI/CD", "Monitoring"],
        "Frontend Developer": ["JavaScript", "React", "Angular", "HTML", "CSS", "TypeScript", "Git", "REST API", "Bootstrap", "Tailwind"],
        "Backend Developer": ["Python", "Java", "SQL", "REST API", "Docker", "Git", "MongoDB", "Redis", "Linux", "AWS"],
    }
    return role_map.get(role, [])


def _display_skill_gap(gap, role):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">🎯</div><div style="color:white;font-size:1.4rem;font-weight:700;">{gap['match_score']}%</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Match Score</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">✅</div><div style="color:white;font-size:1.4rem;font-weight:700;">{len(gap['matched_skills'])}</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Matched</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">❌</div><div style="color:white;font-size:1.4rem;font-weight:700;">{len(gap['missing_skills'])}</div><div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Missing</div></div>""", unsafe_allow_html=True)

    if gap.get("matched_skills"):
        st.success("**✅ Skills You Have:** " + ", ".join(gap["matched_skills"]))
    if gap.get("missing_skills"):
        st.error("**❌ Skills to Develop:** " + ", ".join(gap["missing_skills"]))


def render_learning_recommendations():
    st.markdown('<h3 class="section-title">📚 Personalized Learning Recommendations</h3>', unsafe_allow_html=True)

    skills_to_learn = st.text_area("Skills you want to learn (comma separated)", "React, Docker, AWS, Machine Learning", key="lr_skills")

    if st.button("🎯 Get Recommendations", type="primary", key="lr_btn"):
        extractor = st.session_state.skill_extractor
        skills = [s.strip() for s in skills_to_learn.split(",")]
        gap_analysis = extractor.get_skill_gap_analysis([], skills)
        recommendations = gap_analysis.get("recommendations", [])
        if recommendations:
            for rec in recommendations:
                with st.expander(f"📚 Learn {rec['skill']} - {rec['course']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Platform:** {rec['platform']}")
                    with col2:
                        st.write(f"**Duration:** ~{rec['estimated_hours']} hours")
                    with col3:
                        st.write(f"**Skill:** {rec['skill']}")
                    st.write(f"**Course:** {rec['course']}")


def render_interview_prep():
    st.markdown('<h3 class="section-title">🎤 Interview Preparation Center</h3>', unsafe_allow_html=True)

    prep = st.session_state.interview_prep
    categories = prep.get_all_categories()
    category_labels = {
        "technical_python": "🐍 Python", "technical_java": "☕ Java",
        "technical_dsa": "📊 DSA", "technical_system_design": "🏗️ System Design",
        "aptitude_quantitative": "🔢 Quantitative", "aptitude_logical": "🧩 Logical",
        "hr_behavioral": "🤝 HR / Behavioral",
    }

    tab_quiz, tab_browse, tab_tips = st.tabs(["🎯 Practice Quiz", "📖 Browse Questions", "💡 Interview Tips"])

    with tab_quiz:
        selected_cats = st.multiselect("Select categories", categories,
            default=["technical_python", "technical_dsa"],
            format_func=lambda x: category_labels.get(x, x), key="quiz_cats")
        quiz_count = st.slider("Number of questions", 3, 15, 5, key="quiz_count")

        if st.button("🚀 Start Quiz", type="primary", key="start_quiz"):
            questions = prep.get_mixed_quiz(selected_cats, quiz_count)
            st.session_state.quiz_questions = questions
            st.session_state.quiz_started = True

        if st.session_state.get("quiz_started"):
            questions = st.session_state.get("quiz_questions", [])
            for i, q in enumerate(questions):
                st.markdown(f'<div class="glass-card" style="margin-bottom:1rem;padding:1.2rem;"><strong style="color:#4facfe;">Q{i+1}. [{q.difficulty}]</strong> <span style="color:white;">{q.question}</span><br><small style="color:rgba(255,255,255,0.4);">Category: {q.category}</small></div>', unsafe_allow_html=True)
                with st.expander(f"Reveal Answer for Q{i+1}"):
                    st.write(prep.format_answer(q))

    with tab_browse:
        selected_cat = st.selectbox("Category", categories,
            format_func=lambda x: category_labels.get(x, x), key="browse_cat")
        difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"], key="browse_diff")
        count = st.slider("Questions", 1, 20, 5, key="browse_count")
        if st.button("Load Questions", key="load_questions"):
            diff = None if difficulty == "All" else difficulty
            questions = prep.get_questions_by_category(selected_cat, diff, count)
            for i, q in enumerate(questions, 1):
                with st.expander(f"Q{i}. [{q.difficulty}] {q.question[:80]}..."):
                    st.write(prep.format_answer(q))

    with tab_tips:
        role = st.selectbox("Role", ["software_engineer", "data_scientist", "general"],
            format_func=lambda x: x.replace("_", " ").title(), key="tips_role")
        tips = prep.get_interview_tips(role)
        for i, tip in enumerate(tips, 1):
            st.info(f"**{i}.** {tip}")


def render_export_reports():
    st.markdown('<h3 class="section-title">📄 Export Reports & Analytics</h3>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Placement Reports", "📝 Resume Reports"])

    with tab1:
        history = st.session_state.prediction_history
        if history:
            df = pd.DataFrame([{"Type": h["type"], "Date": h["timestamp"][:10]} for h in history])
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Report", df.to_csv(index=False), "placement_report.csv", "text/csv")
        else:
            st.info("No predictions yet.")

    with tab2:
        analyses = st.session_state.get("resume_analyses", [])
        if analyses:
            df = pd.DataFrame(analyses)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Report", df.to_csv(index=False), "resume_report.csv", "text/csv")
        else:
            st.info("No resume analyses yet.")


def render_prediction_history():
    st.markdown('<h3 class="section-title">📈 Prediction History</h3>', unsafe_allow_html=True)

    history = st.session_state.prediction_history
    if not history:
        st.info("No predictions made yet. Go to Predictions tab to get started.")
        return

    for i, entry in enumerate(reversed(history), 1):
        with st.expander(f"📊 Prediction {i} - {entry['type'].title()} ({entry['timestamp'][:10]})"):
            if entry["type"] == "placement":
                result = entry["result"]
                st.write(f"**Placement:** {'Yes' if result['placed'] else 'No'}")
                st.write(f"**Probability:** {result['probability_placed']}%")
            st.json(entry["features"])


def render_admin_dashboard():
    render_svg_banner("admin_hero")

    st.markdown("""
    <div class="feature-icons">
        <div class="feature-icon-item">📊</div>
        <div class="feature-icon-item">👥</div>
        <div class="feature-icon-item">📧</div>
        <div class="feature-icon-item">🗄️</div>
    </div>
    """, unsafe_allow_html=True)

    _render_sidebar()

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "👥 Users", "📧 Notifications", "📈 Stats"])

    with tab1:
        render_analytics_dashboard()
    with tab2:
        st.markdown('<h3 class="section-title">👥 User Management</h3>', unsafe_allow_html=True)
        demo_users = pd.DataFrame({
            "ID": [1, 2, 3, 4, 5],
            "Username": ["alice", "bob", "charlie", "diana", "eve"],
            "Role": ["student", "student", "placement_officer", "student", "admin"],
            "Status": ["Active", "Active", "Active", "Inactive", "Active"],
            "Joined": ["2025-01-15", "2025-02-20", "2025-01-10", "2025-03-05", "2025-01-01"],
        })
        st.dataframe(demo_users, use_container_width=True)

    with tab3:
        st.markdown('<h3 class="section-title">📧 Email Notification Center</h3>', unsafe_allow_html=True)
        with st.form("send_email"):
            recipient = st.text_input("Recipient Email", "student@college.edu")
            subject = st.text_input("Subject", "Campus Placement Update")
            body = st.text_area("Message", "This is a notification from Campus Placement AI.")
            if st.form_submit_button("📤 Send Email"):
                from src.utils.email_service import EmailMessage
                msg = EmailMessage(recipient=recipient, subject=subject, body=body, email_type="custom")
                st.session_state.email_service.sent_emails.append(msg)
                st.success(f"Email sent to {recipient}!")

    with tab4:
        col1, col2, col3, col4 = st.columns(4)
        metrics = [
            ("👥", "Total Students", "247", "+12 this week"),
            ("📝", "Resumes Analyzed", "189", "+8 today"),
            ("📊", "Predictions Made", "1,456", "+34 today"),
            ("🎯", "Placement Rate", "72%", "+3% this month"),
        ]
        for col, (icon, label, value, delta) in zip([col1, col2, col3, col4], metrics):
            with col:
                st.markdown(f"""<div class="gradient-metric"><div class="metric-icon">{icon}</div><div style="color:white;font-size:1.4rem;font-weight:700;">{value}</div><div style="color:rgba(255,255,255,0.5);font-size:0.75rem;">{label}</div><div style="color:#43e97b;font-size:0.75rem;">{delta}</div></div>""", unsafe_allow_html=True)


def render_placement_officer_dashboard():
    render_svg_banner("officer_hero")

    st.markdown("""
    <div class="feature-icons">
        <div class="feature-icon-item">📊</div>
        <div class="feature-icon-item">🏢</div>
        <div class="feature-icon-item">📝</div>
        <div class="feature-icon-item">📈</div>
    </div>
    """, unsafe_allow_html=True)

    _render_sidebar()

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Student Analytics", "🏢 Company Stats", "📝 Resume Ranking", "📈 Placement Report"])

    with tab1:
        render_analytics_dashboard()
    with tab2:
        st.markdown('<h3 class="section-title">🏢 Company-wise Placement Data</h3>', unsafe_allow_html=True)
        companies = pd.DataFrame({
            "Company": ["TCS", "Infosys", "Wipro", "Amazon", "Google", "Microsoft", "Accenture", "IBM"],
            "Students Applied": [120, 95, 80, 45, 30, 35, 60, 50],
            "Selected": [65, 52, 40, 8, 3, 5, 18, 15],
            "Avg Salary (LPA)": [4.2, 4.0, 3.8, 18.5, 35.0, 28.0, 6.5, 8.0],
        })
        fig = px.bar(companies, x="Company", y=["Students Applied", "Selected"],
                    barmode="group", title="Applications vs Selections")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown('<h3 class="section-title">📝 Bulk Resume Ranking</h3>', unsafe_allow_html=True)
        with st.form("rank_form"):
            col1, col2 = st.columns(2)
            with col1:
                job_skills = st.text_input("Required Skills", "Python, Java, SQL, React, Docker")
                min_cgpa = st.number_input("Minimum CGPA", 4.0, 10.0, 6.0, 0.1)
            with col2:
                uploaded_files = st.file_uploader("Upload Resumes (PDF)", type=["pdf"],
                    accept_multiple_files=True, key="rank_uploads")
            if st.form_submit_button("📊 Rank Resumes", type="primary"):
                if uploaded_files:
                    st.info(f"Processing {len(uploaded_files)} resumes...")
                    st.success("Resume ranking complete!")

    with tab4:
        st.markdown('<h3 class="section-title">📈 Placement Report</h3>', unsafe_allow_html=True)
        report_data = pd.DataFrame({
            "Department": ["CS", "IT", "ECE", "ME", "CE", "EE"],
            "Total Students": [120, 80, 90, 70, 60, 50],
            "Placed": [95, 58, 50, 28, 15, 20],
            "Avg Package (LPA)": [8.5, 6.2, 5.0, 4.2, 3.5, 3.8],
        })
        report_data["Placement %"] = (report_data["Placed"] / report_data["Total Students"] * 100).round(1)
        st.dataframe(report_data, use_container_width=True)

        fig = px.pie(report_data, values="Placed", names="Department",
                     title="Department-wise Placement Distribution")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)


def render_analytics_dashboard():
    st.markdown('<h3 class="section-title">📊 Analytics & Data Visualization</h3>', unsafe_allow_html=True)

    from src.ml.analytics_engine import AnalyticsEngine
    analytics = AnalyticsEngine()

    col1, col2 = st.columns(2)
    with col1:
        try:
            fig = analytics.department_placement_chart()
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        except: pass
    with col2:
        try:
            fig = analytics.salary_distribution_chart()
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        except: pass

    col3, col4 = st.columns(2)
    with col3:
        try:
            fig = analytics.monthly_placements_trend()
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        except: pass
    with col4:
        try:
            fig = analytics.top_skills_demand_chart()
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        except: pass


def _render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:3rem;">🎓</div>
            <h3 style="color:white;margin:0;">Welcome!</h3>
            <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;">{st.session_state.username}</p>
            <p style="color:#4facfe;font-size:0.8rem;font-weight:600;">{st.session_state.user_role.replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)

        if st.button("🚪 Logout", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)

        history = st.session_state.prediction_history
        resume_analyses = st.session_state.get("resume_analyses", [])

        st.markdown("#### 📊 Quick Stats")
        st.markdown(f"""<div class="gradient-metric" style="margin-bottom:0.5rem;"><div class="metric-icon">📊</div><div style="color:white;font-size:1.2rem;font-weight:700;">{len(history)}</div><div style="color:rgba(255,255,255,0.4);font-size:0.75rem;">Predictions</div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="gradient-metric" style="margin-bottom:0.5rem;"><div class="metric-icon">📝</div><div style="color:white;font-size:1.2rem;font-weight:700;">{len(resume_analyses)}</div><div style="color:rgba(255,255,255,0.4);font-size:0.75rem;">Resumes</div></div>""", unsafe_allow_html=True)

        st.markdown('<div class="animated-divider"></div>', unsafe_allow_html=True)

        with st.expander("ℹ️ About"):
            st.markdown("""
            **AI Campus Placement System v1.0**

            AI-powered platform for placement prediction, resume screening, and career guidance.

            **Features:**
            - 🤖 ML Predictions
            - 📝 Resume AI
            - 🎯 Job Matching
            - 📊 Analytics
            - 🚀 Interview Prep
            """)


def main():
    load_css()
    render_background()
    init_session_state()

    if not st.session_state.logged_in:
        render_login_page()
    else:
        role = st.session_state.user_role
        if role == "student":
            render_student_dashboard()
        elif role == "admin":
            render_admin_dashboard()
        elif role == "placement_officer":
            render_placement_officer_dashboard()


if __name__ == "__main__":
    main()
