import numpy as np
from typing import Dict, List, Tuple
import logging

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import config
from src.nlp.skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)


class JobMatcher:
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.companies = config.companies.COMPANIES

    def match_jobs(
        self, student_profile: Dict, resume_skills: List[str] = None
    ) -> List[Dict]:
        matches = []

        for company in self.companies:
            match_result = self._match_company(student_profile, company, resume_skills)
            if match_result["overall_match"] > 20:
                matches.append(match_result)

        matches.sort(key=lambda x: x["overall_match"], reverse=True)
        return matches

    def _match_company(
        self, profile: Dict, company: Dict, resume_skills: List[str] = None
    ) -> Dict:
        cgpa = profile.get("cgpa", 0)
        min_cgpa = company.get("min_cgpa", 6.0)

        all_profile_skills = set()
        for skill_list_key in ["technical_skills", "programming_languages", "soft_skills"]:
            skills = profile.get(skill_list_key, [])
            if isinstance(skills, list):
                all_profile_skills.update(s.lower() for s in skills)
        if resume_skills:
            all_profile_skills.update(s.lower() for s in resume_skills)

        company_skills = [s.lower() for s in company.get("skills", [])]
        matched_skills = all_profile_skills.intersection(set(company_skills))
        missing_skills = set(company_skills) - all_profile_skills

        skill_match = (
            (len(matched_skills) / len(company_skills) * 100)
            if company_skills else 0
        )

        cgpa_match = 100 if cgpa >= min_cgpa else (cgpa / min_cgpa) * 100

        backlogs = profile.get("backlogs", 0)
        backlog_penalty = max(0, backlogs * 15)

        experience = profile.get("internships", 0)
        experience_bonus = min(20, experience * 7)

        overall = (
            skill_match * 0.40
            + cgpa_match * 0.30
            + max(0, 100 - backlog_penalty) * 0.15
            + min(100, 50 + experience_bonus) * 0.15
        )

        return {
            "company": company["name"],
            "job_title": "Software Engineer",
            "overall_match": round(overall, 2),
            "skill_match": round(skill_match, 2),
            "cgpa_match": round(cgpa_match, 2),
            "matched_skills": [s.title() for s in matched_skills],
            "missing_skills": [s.title() for s in missing_skills],
            "salary_range": {
                "min_lpa": company.get("min_salary", 0),
                "max_lpa": company.get("max_salary", 0),
            },
            "min_cgpa_required": min_cgpa,
            "eligibility": "Eligible" if cgpa >= min_cgpa else "Not Eligible",
            "recommendation": self._get_recommendation(overall, cgpa >= min_cgpa),
        }

    def _get_recommendation(self, match: float, eligible: bool) -> str:
        if not eligible:
            return "Improve CGPA to meet eligibility criteria"
        if match >= 80:
            return "Excellent match! Apply immediately"
        elif match >= 60:
            return "Good match. Prepare well for the interview"
        elif match >= 40:
            return "Moderate match. Work on missing skills first"
        else:
            return "Low match. Focus on building required skills"

    def get_top_companies(
        self, profile: Dict, resume_skills: List[str] = None, top_n: int = 5
    ) -> List[Dict]:
        matches = self.match_jobs(profile, resume_skills)
        return matches[:top_n]
