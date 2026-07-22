import pandas as pd
import io
import csv
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)


class ReportExporter:
    def __init__(self):
        self.reports_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'reports'
        )
        os.makedirs(self.reports_dir, exist_ok=True)

    def export_placement_report_csv(
        self, predictions: List[Dict], filename: str = None
    ) -> str:
        if not filename:
            filename = f"placement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        rows = []
        for i, pred in enumerate(predictions, 1):
            features = pred.get("features", {})
            result = pred.get("result", {})
            rows.append({
                "S.No": i,
                "CGPA": features.get("cgpa", ""),
                "10th %": features.get("tenth_percentage", ""),
                "12th %": features.get("twelfth_percentage", ""),
                "Backlogs": features.get("backlogs", ""),
                "Internships": features.get("internships", ""),
                "Tech Skills": features.get("num_technical_skills", ""),
                "Projects": features.get("num_projects", ""),
                "Department": features.get("department", ""),
                "Predicted": "Placed" if result.get("placed") else "Not Placed",
                "Probability %": result.get("probability_placed", ""),
                "Confidence %": result.get("confidence", ""),
                "Risk Level": result.get("risk_level", ""),
                "Date": pred.get("timestamp", "")[:10],
            })

        df = pd.DataFrame(rows)
        filepath = os.path.join(self.reports_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Placement report exported: {filepath}")
        return filepath

    def export_salary_report_csv(
        self, predictions: List[Dict], filename: str = None
    ) -> str:
        if not filename:
            filename = f"salary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        rows = []
        for i, pred in enumerate(predictions, 1):
            features = pred.get("features", {})
            result = pred.get("result", {})
            salary = result.get("predicted_salary_lpa", 0)
            rows.append({
                "S.No": i,
                "CGPA": features.get("cgpa", ""),
                "Department": features.get("department", ""),
                "Tech Skills": features.get("num_technical_skills", ""),
                "Experience": features.get("experience_years", ""),
                "Predicted Salary (LPA)": salary,
                "Monthly Income": result.get("predicted_monthly", 0),
                "Salary Tier": result.get("salary_tier", ""),
                "Date": pred.get("timestamp", "")[:10],
            })

        df = pd.DataFrame(rows)
        filepath = os.path.join(self.reports_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Salary report exported: {filepath}")
        return filepath

    def export_resume_report_csv(
        self, resume_data: List[Dict], filename: str = None
    ) -> str:
        if not filename:
            filename = f"resume_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        rows = []
        for i, data in enumerate(resume_data, 1):
            rows.append({
                "S.No": i,
                "Name": data.get("name", ""),
                "Email": data.get("email", ""),
                "ATS Score": data.get("ats_score", ""),
                "Grade": data.get("grade", ""),
                "Skills Count": data.get("skills_count", 0),
                "Strengths": "; ".join(data.get("strengths", [])),
                "Weaknesses": "; ".join(data.get("weaknesses", [])),
                "Date": data.get("date", ""),
            })

        df = pd.DataFrame(rows)
        filepath = os.path.join(self.reports_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Resume report exported: {filepath}")
        return filepath

    def export_job_matching_csv(
        self, matches: List[Dict], filename: str = None
    ) -> str:
        if not filename:
            filename = f"job_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        rows = []
        for i, m in enumerate(matches, 1):
            rows.append({
                "Rank": i,
                "Company": m.get("company", ""),
                "Job Title": m.get("job_title", ""),
                "Overall Match %": m.get("overall_match", 0),
                "Skill Match %": m.get("skill_match", 0),
                "CGPA Match %": m.get("cgpa_match", 0),
                "Min CGPA": m.get("min_cgpa_required", ""),
                "Eligibility": m.get("eligibility", ""),
                "Salary Range (LPA)": str(m.get("salary_range", "N/A")),
                "Matched Skills": "; ".join(m.get("matched_skills", [])),
                "Missing Skills": "; ".join(m.get("missing_skills", [])),
            })

        df = pd.DataFrame(rows)
        filepath = os.path.join(self.reports_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Job matching report exported: {filepath}")
        return filepath

    def export_skill_gap_csv(
        self, gap_data: Dict, role: str, filename: str = None
    ) -> str:
        if not filename:
            filename = f"skill_gap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        rows = []
        for i, skill in enumerate(gap_data.get("matched_skills", []), 1):
            rows.append({
                "S.No": i,
                "Skill": skill,
                "Status": "Matched",
                "Target Role": role,
                "Match Score": gap_data.get("match_score", 0),
            })
        for i, skill in enumerate(
            gap_data.get("missing_skills", []),
            len(gap_data.get("matched_skills", [])) + 1
        ):
            rows.append({
                "S.No": i,
                "Skill": skill,
                "Status": "Missing",
                "Target Role": role,
                "Match Score": gap_data.get("match_score", 0),
            })

        df = pd.DataFrame(rows)
        filepath = os.path.join(self.reports_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Skill gap report exported: {filepath}")
        return filepath

    def export_analytics_summary_csv(
        self, analytics_data: Dict, filename: str = None
    ) -> str:
        if not filename:
            filename = f"analytics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        rows = []
        for key, value in analytics_data.items():
            rows.append({"Metric": key, "Value": str(value)})

        df = pd.DataFrame(rows)
        filepath = os.path.join(self.reports_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Analytics summary exported: {filepath}")
        return filepath

    def export_full_student_report(
        self, student_data: Dict, filename: str = None
    ) -> str:
        if not filename:
            filename = f"student_report_{student_data.get('name', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        sections = []

        sections.append({"Section": "STUDENT INFORMATION", "Key": "Name", "Value": student_data.get("name", "")})
        sections.append({"Section": "STUDENT INFORMATION", "Key": "Department", "Value": student_data.get("department", "")})
        sections.append({"Section": "STUDENT INFORMATION", "Key": "CGPA", "Value": str(student_data.get("cgpa", ""))})
        sections.append({"Section": "STUDENT INFORMATION", "Key": "Roll Number", "Value": student_data.get("roll_number", "")})

        placement = student_data.get("placement_prediction", {})
        if placement:
            sections.append({"Section": "PLACEMENT PREDICTION", "Key": "Probability", "Value": f"{placement.get('probability_placed', 0)}%"})
            sections.append({"Section": "PLACEMENT PREDICTION", "Key": "Status", "Value": "Placed" if placement.get("placed") else "Not Placed"})
            sections.append({"Section": "PLACEMENT PREDICTION", "Key": "Risk Level", "Value": placement.get("risk_level", "")})

        salary = student_data.get("salary_prediction", {})
        if salary:
            sections.append({"Section": "SALARY PREDICTION", "Key": "Predicted (LPA)", "Value": str(salary.get("predicted_salary_lpa", 0))})
            sections.append({"Section": "SALARY PREDICTION", "Key": "Monthly", "Value": str(salary.get("predicted_monthly", 0))})
            sections.append({"Section": "SALARY PREDICTION", "Key": "Tier", "Value": salary.get("salary_tier", "")})

        ats = student_data.get("ats_result", {})
        if ats:
            sections.append({"Section": "RESUME ANALYSIS", "Key": "ATS Score", "Value": str(ats.get("overall_score", 0))})
            sections.append({"Section": "RESUME ANALYSIS", "Key": "Grade", "Value": ats.get("grade", "")})

        gap = student_data.get("skill_gap", {})
        if gap:
            sections.append({"Section": "SKILL GAP", "Key": "Match Score", "Value": f"{gap.get('match_score', 0)}%"})
            sections.append({"Section": "SKILL GAP", "Key": "Missing Skills", "Value": ", ".join(gap.get("missing_skills", []))})

        df = pd.DataFrame(sections)
        filepath = os.path.join(self.reports_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Full student report exported: {filepath}")
        return filepath

    def get_csv_download_button(
        self, df: pd.DataFrame, filename: str, button_text: str = "Download CSV"
    ) -> str:
        return df.to_csv(index=False)

    def create_downloadable_csv(self, data: List[Dict], columns: List[str]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
