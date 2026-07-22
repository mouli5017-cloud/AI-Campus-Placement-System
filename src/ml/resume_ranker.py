import numpy as np
from typing import Dict, List
import logging

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.nlp.skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)


class ResumeRanker:
    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def rank_resumes(
        self, resumes: List[Dict], job_requirements: Dict
    ) -> List[Dict]:
        ranked = []
        for resume in resumes:
            score = self._compute_rank_score(resume, job_requirements)
            resume["rank_score"] = score["total_score"]
            resume["rank_details"] = score
            ranked.append(resume)

        ranked.sort(key=lambda x: x["rank_score"], reverse=True)
        for i, r in enumerate(ranked):
            r["rank"] = i + 1

        return ranked

    def _compute_rank_score(
        self, resume: Dict, job_req: Dict
    ) -> Dict:
        resume_skills = resume.get("skills", [])
        required_skills = job_req.get("required_skills", [])
        min_cgpa = job_req.get("min_cgpa", 6.0)

        skill_score, matched, missing = self.skill_extractor.compute_skill_match(
            resume_skills, required_skills
        )

        cgpa = resume.get("cgpa", 0)
        cgpa_score = min(1.0, cgpa / 10.0) if cgpa else 0.5

        experience = resume.get("experience_years", 0)
        exp_score = min(1.0, experience / 5.0)

        ats = resume.get("ats_score", 50)
        ats_normalized = ats / 100.0

        total = (
            skill_score * 0.35
            + cgpa_score * 0.25
            + exp_score * 0.15
            + ats_normalized * 0.25
        )

        return {
            "total_score": round(total * 100, 2),
            "skill_score": round(skill_score * 100, 2),
            "cgpa_score": round(cgpa_score * 100, 2),
            "experience_score": round(exp_score * 100, 2),
            "ats_score": round(ats, 2),
            "matched_skills": [s.title() for s in matched],
            "missing_skills": [s.title() for s in missing],
            "eligible": cgpa >= min_cgpa,
        }

    def get_resume_summary(self, ranked_resumes: List[Dict]) -> Dict:
        if not ranked_resumes:
            return {"total": 0, "eligible": 0, "avg_score": 0}

        eligible = sum(1 for r in ranked_resumes if r.get("rank_details", {}).get("eligible", False))
        scores = [r.get("rank_score", 0) for r in ranked_resumes]

        return {
            "total": len(ranked_resumes),
            "eligible": eligible,
            "not_eligible": len(ranked_resumes) - eligible,
            "avg_score": round(np.mean(scores), 2) if scores else 0,
            "top_score": round(max(scores), 2) if scores else 0,
            "bottom_score": round(min(scores), 2) if scores else 0,
        }
