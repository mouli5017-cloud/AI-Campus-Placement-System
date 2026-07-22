"""
Student Dashboard Page Module.
Extracts student-facing functionality into a reusable module.
Can be imported by app.py or run as a standalone Streamlit page.
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
from src.ml.placement_model import PlacementPredictor
from src.ml.salary_model import SalaryPredictor
from src.ml.ats_scorer import ATSScorer
from src.ml.job_matcher import JobMatcher
from src.ml.interview_prep import InterviewPrepModule
from src.nlp.resume_parser import ResumeParser
from src.nlp.skill_extractor import SkillExtractor
from src.utils.email_service import EmailNotificationService
from src.utils.report_exporter import ReportExporter


def render_placement_prediction():
    st.markdown("### Placement Probability Prediction")

    col1, col2 = st.columns(2)
    with col1:
        cgpa = st.slider("CGPA", 4.0, 10.0, 7.5, 0.1, key="dp_cgpa")
        tenth = st.slider("10th Percentage", 40.0, 100.0, 75.0, 0.5, key="dp_tenth")
        twelfth = st.slider("12th Percentage", 40.0, 100.0, 70.0, 0.5, key="dp_twelfth")
        backlogs = st.number_input("Active Backlogs", 0, 10, 0, key="dp_backlogs")

    with col2:
        skills_count = st.slider("Technical Skills Count", 0, 30, 8, key="dp_skills")
        internships = st.number_input("Internships", 0, 10, 1, key="dp_intern")
        projects = st.number_input("Projects", 0, 20, 2, key="dp_projects")
        communication = st.slider("Communication Score", 0, 100, 70, key="dp_comm")

    if st.button("Predict Placement", type="primary", key="dp_predict"):
        predictor = st.session_state.placement_predictor
        if not predictor.is_trained:
            with st.spinner("Training model..."):
                predictor.train_model()
                predictor.save_model()

        result = predictor.predict_single({
            "cgpa": cgpa,
            "10th_percentage": tenth,
            "12th_percentage": twelfth,
            "backlogs": backlogs,
            "technical_skills": skills_count,
            "internships": internships,
            "projects": projects,
            "communication_score": communication,
        })

        if result:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Placement Probability", f"{result['probability_placed']:.1f}%")
            with col_b:
                st.metric("Prediction", "PLACED" if result["placed"] else "NOT PLACED")
            with col_c:
                st.metric("Risk Level", result["risk_level"])

            if result.get("suggestions"):
                st.markdown("**Suggestions:**")
                for s in result["suggestions"]:
                    st.info(s)

            st.session_state.prediction_history.append({
                "timestamp": pd.Timestamp.now().isoformat(),
                "cgpa": cgpa,
                "skills": skills_count,
                "probability": result["probability_placed"],
                "placed": result["placed"],
                "risk_level": result["risk_level"],
            })


def render_resume_analysis():
    st.markdown("### Resume Analysis")
    st.markdown("Upload your resume (PDF/DOCX) or paste text for ATS scoring.")

    tab_upload, tab_paste = st.tabs(["Upload File", "Paste Text"])

    resume_text = None
    with tab_upload:
        uploaded = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="da_upload")
        if uploaded:
            parser = ResumeParser()
            resume_text = parser.extract_text_from_file(uploaded)
            if resume_text:
                st.success(f"Extracted {len(resume_text)} characters from {uploaded.name}")
            else:
                st.error("Could not extract text from file.")

    with tab_paste:
        resume_text_paste = st.text_area(
            "Paste resume text here", height=300, key="da_paste"
        )
        if resume_text_paste:
            resume_text = resume_text_paste

    if resume_text and st.button("Analyze Resume", type="primary", key="da_analyze"):
        extractor = SkillExtractor()
        skills = extractor.extract_skills(resume_text)

        parser = ResumeParser()
        parsed = parser.parse_text(resume_text)

        scorer = ATSScorer()
        ats_result = scorer.compute_ats_score(
            resume_text=resume_text,
            skill_names=skills,
            experience_years=parsed.experience_years,
        )

        col1, col2 = st.columns(2)
        with col1:
            score = ats_result.get("overall_score", 0)
            grade = ats_result.get("grade", "F")
            st.metric("ATS Score", f"{score:.0f}/100")
            st.metric("Grade", grade)

        with col2:
            st.metric("Skills Found", str(len(skills)))
            st.metric("Sections Detected", str(len(parsed.sections)))

        if skills:
            st.markdown("**Skills Detected:**")
            st.write(", ".join(skills))

        improvements = ats_result.get("improvements", [])
        if improvements:
            st.markdown("**Suggested Improvements:**")
            for imp in improvements:
                st.warning(imp)

        st.session_state.resume_analyses.append({
            "timestamp": pd.Timestamp.now().isoformat(),
            "score": score,
            "grade": grade,
            "skills": skills,
        })


def render_job_matching():
    st.markdown("### Job Matching")
    st.markdown("Find companies that match your profile.")

    col1, col2 = st.columns(2)
    with col1:
        cgpa = st.slider("Your CGPA", 4.0, 10.0, 7.5, 0.1, key="jm_cgpa")
        experience = st.number_input("Experience (months)", 0, 60, 0, key="jm_exp")

    with col2:
        all_skills = config.skills.TECHNICAL_SKILLS[:30]
        selected = st.multiselect("Your Skills", all_skills, key="jm_skills")

    if st.button("Find Matching Jobs", type="primary", key="jm_find"):
        matcher = JobMatcher()
        profile = {"cgpa": cgpa, "skills": selected, "experience_months": experience}
        matches = matcher.match_jobs(profile, top_n=10)

        if matches:
            df = pd.DataFrame(matches)
            st.dataframe(
                df[["company", "role", "overall_match", "eligibility", "salary_range"]].head(10),
                use_container_width=True,
            )
            fig = px.bar(
                df.head(10), x="company", y="overall_match",
                title="Job Match Scores", color="overall_match",
                color_continuous_scale="viridis",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.session_state.job_matches = matches
        else:
            st.info("No matching jobs found. Update your skills and try again.")


def render_skill_gap_analysis():
    st.markdown("### Skill Gap Analysis")
    st.markdown("Identify missing skills for your target role.")

    target_role = st.selectbox(
        "Target Role",
        ["Software Engineer", "Data Scientist", "ML Engineer",
         "Full Stack Developer", "Cloud Architect", "DevOps Engineer"],
        key="sg_role",
    )

    all_skills = config.skills.TECHNICAL_SKILLS[:40]
    current = st.multiselect("Your Current Skills", all_skills, key="sg_current")

    if st.button("Analyze Gap", type="primary", key="sg_analyze"):
        extractor = SkillExtractor()
        role_requirements = {
            "Software Engineer": ["Python", "Java", "SQL", "Git", "Docker", "REST API", "Linux"],
            "Data Scientist": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow"],
            "ML Engineer": ["Python", "TensorFlow", "PyTorch", "Docker", "AWS", "MLflow", "Kubernetes"],
            "Full Stack Developer": ["JavaScript", "React", "Node.js", "SQL", "HTML", "CSS", "Git"],
            "Cloud Architect": ["AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Linux", "CI/CD"],
            "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "Jenkins", "AWS", "Terraform", "CI/CD"],
        }
        required = role_requirements.get(target_role, [])
        missing = [s for s in required if s not in current]
        matched = [s for s in required if s in current]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Skills Matched", len(matched))
            for s in matched:
                st.success(f"✓ {s}")
        with col2:
            st.metric("Skills Missing", len(missing))
            for s in missing:
                st.error(f"✗ {s}")

        if missing:
            match_pct = (len(matched) / len(required)) * 100 if required else 0
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=match_pct,
                title={"text": "Skill Match Percentage"},
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#1E88E5"}},
            ))
            st.plotly_chart(fig, use_container_width=True)


def render_interview_prep():
    st.markdown("### Interview Preparation")

    prep = InterviewPrepModule()
    categories = prep.get_all_categories()

    col1, col2 = st.columns(2)
    with col1:
        selected_cat = st.selectbox("Category", categories, key="ip_cat")
    with col2:
        difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"], key="ip_diff")

    count = st.slider("Number of Questions", 1, 10, 5, key="ip_count")

    if st.button("Get Questions", type="primary", key="ip_get"):
        diff = None if difficulty == "All" else difficulty
        questions = prep.get_questions_by_category(selected_cat, difficulty=diff, count=count)

        for i, q in enumerate(questions, 1):
            with st.expander(f"Q{i}: {q.question} ({q.difficulty})"):
                st.markdown(f"**Answer:** {q.answer}")
                if q.tips:
                    st.markdown("**Tips:**")
                    for tip in q.tips:
                        st.markdown(f"- {tip}")
                st.caption(f"Expected duration: {q.expected_duration}")


def render_export_reports():
    st.markdown("### Export & Reports")

    exporter = ReportExporter()

    tab1, tab2 = st.tabs(["Placement History", "Resume Analyses"])

    with tab1:
        history = st.session_state.prediction_history
        if history:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False)
            st.download_button("Download Placement Report", csv, "placement_report.csv", "text/csv")
        else:
            st.info("No predictions made yet.")

    with tab2:
        analyses = st.session_state.get("resume_analyses", [])
        if analyses:
            df = pd.DataFrame(analyses)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False)
            st.download_button("Download Resume Report", csv, "resume_report.csv", "text/csv")
        else:
            st.info("No resume analyses yet.")


def render_prediction_history():
    st.markdown("### Prediction History")

    history = st.session_state.prediction_history
    if not history:
        st.info("No predictions made yet. Go to Predictions tab to get started.")
        return

    df = pd.DataFrame(history)
    st.dataframe(df, use_container_width=True)

    if len(df) > 1:
        fig = px.line(
            df, x="timestamp", y="probability",
            title="Prediction Probability Over Time",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.pie(
            df, names="placed", title="Placement Prediction Distribution",
            color_discrete_map={True: "#43A047", False: "#E53935"},
        )
        st.plotly_chart(fig2, use_container_width=True)
