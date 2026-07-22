"""
Placement Officer Dashboard Page Module.
Resume ranking, bulk screening, drive management, and placement statistics.
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
from src.ml.resume_ranker import ResumeRanker
from src.ml.job_matcher import JobMatcher
from src.nlp.skill_extractor import SkillExtractor
from src.nlp.resume_parser import ResumeParser


def render_bulk_resume_screening():
    st.markdown("### Bulk Resume Screening")
    st.markdown("Upload multiple resumes for batch ranking against job requirements.")

    col1, col2 = st.columns(2)
    with col1:
        target_role = st.selectbox(
            "Screen Against Role",
            ["Software Engineer", "Data Scientist", "ML Engineer",
             "Full Stack Developer", "DevOps Engineer"],
            key="po_role",
        )
    with col2:
        min_cgpa = st.slider("Minimum CGPA Filter", 4.0, 10.0, 6.0, 0.5, key="po_cgpa")

    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True, key="po_files"
    )

    if uploaded_files and st.button("Screen Resumes", type="primary", key="po_screen"):
        parser = ResumeParser()
        extractor = SkillExtractor()
        ranker = ResumeRanker()

        results = []
        progress = st.progress(0)
        for i, file in enumerate(uploaded_files):
            text = parser.extract_text_from_file(file)
            if text:
                parsed = parser.parse_text(text)
                skills = extractor.extract_skills(text)
                results.append({
                    "filename": file.name,
                    "name": parsed.name or "Unknown",
                    "skills": skills,
                    "cgpa": parsed.cgpa or 0,
                    "experience_years": parsed.experience_years,
                    "total_words": parsed.total_words,
                })
            progress.progress((i + 1) / len(uploaded_files))

        if results:
            ranked = ranker.rank_resumes(results, target_role=target_role)
            df = pd.DataFrame(ranked)
            st.dataframe(df, use_container_width=True)

            fig = px.bar(
                df.head(20), x="filename", y="score",
                title="Resume Ranking Results",
                color="score", color_continuous_scale="viridis",
            )
            st.plotly_chart(fig, use_container_width=True)

            csv = df.to_csv(index=False)
            st.download_button("Download Rankings (CSV)", csv, "resume_rankings.csv", "text/csv")


def render_placement_drives():
    st.markdown("### Placement Drive Management")

    drives = pd.DataFrame({
        "Company": ["TCS", "Infosys", "Amazon", "Google", "Microsoft"],
        "Role": ["Software Engineer", "Cloud Engineer", "SDE-1", "SDE-2", "SDE"],
        "Min CGPA": [6.0, 6.0, 7.0, 7.5, 7.0],
        "Salary (LPA)": ["3.36-7.0", "3.5-6.5", "12-30", "18-45", "15-40"],
        "Status": ["Scheduled", "Completed", "Upcoming", "Upcoming", "Scheduled"],
        "Applicants": [120, 95, 0, 0, 80],
    })

    st.dataframe(drives, use_container_width=True)

    status_counts = drives["Status"].value_counts()
    fig = px.pie(
        names=status_counts.index, values=status_counts.values,
        title="Drive Status Distribution",
        color_discrete_map={"Scheduled": "#1E88E5", "Completed": "#43A047", "Upcoming": "#FB8C00"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_placement_statistics():
    st.markdown("### Placement Statistics")

    stats = pd.DataFrame({
        "Branch": ["CSE", "ISE", "ECE", "EEE", "ME", "CE"],
        "Total Students": [120, 80, 90, 70, 60, 50],
        "Placed": [95, 55, 50, 30, 20, 15],
        "Avg Package (LPA)": [8.5, 7.2, 6.1, 5.5, 4.8, 4.2],
    })
    stats["Placement %"] = (stats["Placed"] / stats["Total Students"] * 100).round(1)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            stats, x="Branch", y=["Placed", "Total Students"],
            title="Branch-wise Placement", barmode="group",
            color_discrete_map={"Placed": "#43A047", "Total Students": "#90CAF9"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            stats, x="Branch", y="Avg Package (LPA)",
            title="Average Salary by Branch",
            color="Avg Package (LPA)", color_continuous_scale="viridis",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Overall Statistics")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Total Students", str(stats["Total Students"].sum()))
    with col_b:
        st.metric("Total Placed", str(stats["Placed"].sum()))
    with col_c:
        overall_pct = stats["Placed"].sum() / stats["Total Students"].sum() * 100
        st.metric("Overall Placement %", f"{overall_pct:.1f}%")
    with col_d:
        st.metric("Avg Package", f"{stats['Avg Package (LPA)'].mean():.1f} LPA")


def render_student_lookup():
    st.markdown("### Student Lookup")

    search = st.text_input("Search by Name or ID", key="po_search")

    if search:
        students = pd.DataFrame({
            "ID": ["STU001", "STU002", "STU003"],
            "Name": ["Alice", "Bob", "Charlie"],
            "CGPA": [8.5, 7.2, 9.1],
            "Status": ["Placed", "Pending", "Placed"],
            "Company": ["Amazon", "-", "Microsoft"],
        })
        filtered = students[students["Name"].str.contains(search, case=False)]
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True)
        else:
            st.info("No students found matching the search.")
