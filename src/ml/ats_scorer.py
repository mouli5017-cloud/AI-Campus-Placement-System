import re
import math
from typing import Dict, List, Tuple
from collections import Counter
import logging

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import config

logger = logging.getLogger(__name__)

ACTION_VERBS = [
    "developed", "implemented", "designed", "built", "created", "optimized",
    "managed", "led", "achieved", "improved", "reduced", "increased",
    "automated", "deployed", "configured", "architected", "maintained",
    "analyzed", "tested", "debugged", "collaborated", "mentored",
    "delivered", "launched", "migrated", "integrated", "streamlined",
    "engineered", "programmed", "enhanced", "established", "coordinated",
    "supervised", "executed", "formulated", "generated", "produced",
    "orchestrated", "initiated", "spearheaded", "facilitated",
]

QUANTIFIABLE_KEYWORDS = [
    r'\d+%', r'\d+\+', r'\d+x', r'\$\d+', r'\d+\s*(?:users|customers|clients)',
    r'reduced\s+\w+\s+by\s+\d+', r'increased\s+\w+\s+by\s+\d+',
    r'improved\s+\w+\s+by\s+\d+', r'saved\s+\$?\d+',
    r'handled\s+\d+', r'managed\s+\d+', r'team\s+of\s+\d+',
]


class ATSScorer:
    def __init__(self):
        self.section_weights = {
            "contact": 5,
            "summary": 8,
            "experience": 20,
            "education": 12,
            "skills": 20,
            "projects": 15,
            "certifications": 8,
            "achievements": 7,
            "formatting": 5,
        }

    def compute_ats_score(
        self, resume_text: str, job_description: str = "",
        extracted_skills: List[str] = None,
        sections_detected: List[str] = None,
    ) -> Dict:
        scores = {}

        scores["contact"] = self._score_contact(resume_text)
        scores["formatting"] = self._score_formatting(resume_text)
        scores["skills"] = self._score_skills(
            resume_text, job_description, extracted_skills
        )
        scores["experience"] = self._score_experience(resume_text)
        scores["education"] = self._score_education(resume_text)
        scores["projects"] = self._score_projects(resume_text)
        scores["certifications"] = self._score_certifications(resume_text)
        scores["achievements"] = self._score_achievements(resume_text)
        scores["summary"] = self._score_summary(resume_text)
        scores["keyword_match"] = self._score_keyword_match(
            resume_text, job_description
        )
        scores["action_verbs"] = self._score_action_verbs(resume_text)
        scores["quantifiable"] = self._score_quantifiable(resume_text)

        weighted_score = 0.0
        total_weight = 0
        for section, weight in self.section_weights.items():
            if section in scores:
                weighted_score += scores[section]["score"] * (weight / 100)
                total_weight += weight

        if total_weight > 0:
            weighted_score = (weighted_score / total_weight) * 100

        bonus = 0
        if scores.get("keyword_match", {}).get("score", 0) > 70:
            bonus += 5
        if scores.get("action_verbs", {}).get("score", 0) > 60:
            bonus += 3
        if scores.get("quantifiable", {}).get("score", 0) > 50:
            bonus += 2

        final_score = min(100, round(weighted_score + bonus, 2))

        return {
            "overall_score": final_score,
            "grade": self._get_grade(final_score),
            "section_scores": scores,
            "strengths": self._get_strengths(scores),
            "weaknesses": self._get_weaknesses(scores),
            "improvements": self._get_improvements(scores, resume_text),
            "keyword_match_score": scores.get("keyword_match", {}).get("score", 0),
        }

    def _score_contact(self, text: str) -> Dict:
        score = 0
        details = []
        email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phone = re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}', text)

        if email:
            score += 3
            details.append("Email found")
        if phone:
            score += 3
            details.append("Phone found")
        if re.search(r'linkedin\.com/in/', text):
            score += 2
            details.append("LinkedIn found")
        if re.search(r'github\.com/', text):
            score += 2
            details.append("GitHub found")

        return {"score": min(100, score * 10), "details": details}

    def _score_formatting(self, text: str) -> Dict:
        score = 80
        details = []
        lines = text.split("\n")

        if len(text) > 5000:
            score -= 10
            details.append("Resume too long (>5000 words)")
        if len(text) < 500:
            score -= 20
            details.append("Resume too short (<500 words)")

        word_count = len(text.split())
        if 300 <= word_count <= 800:
            score += 20
            details.append("Good word count")
        else:
            score -= 10
            details.append(f"Word count: {word_count}")

        if text.isupper():
            score -= 20
            details.append("All caps detected")
        elif re.search(r'[A-Z]{5,}', text):
            score -= 5
            details.append("Excessive caps detected")

        return {"score": min(100, max(0, score)), "details": details}

    def _score_skills(
        self, text: str, job_desc: str, skills: List[str] = None
    ) -> Dict:
        score = 0
        details = []
        text_lower = text.lower()

        all_skills = config.skills.TECHNICAL_SKILLS + config.skills.SOFT_SKILLS
        found = sum(1 for s in all_skills if s.lower() in text_lower)
        if found >= 10:
            score = 90
            details.append(f"Strong skill set ({found} skills found)")
        elif found >= 6:
            score = 70
            details.append(f"Good skill set ({found} skills found)")
        elif found >= 3:
            score = 50
            details.append(f"Moderate skill set ({found} skills found)")
        else:
            score = 20
            details.append(f"Few skills found ({found})")

        if job_desc:
            job_lower = job_desc.lower()
            job_skills = [s for s in all_skills if s.lower() in job_lower]
            if job_skills:
                matched = sum(1 for s in job_skills if s.lower() in text_lower)
                job_score = (matched / len(job_skills)) * 100
                score = int((score + job_score) / 2)
                details.append(
                    f"Job keyword match: {matched}/{len(job_skills)}"
                )

        return {"score": min(100, score), "details": details}

    def _score_experience(self, text: str) -> Dict:
        score = 0
        details = []
        text_lower = text.lower()

        exp_indicators = [
            "experience", "work history", "employment",
            "internship", "worked at", "employed at"
        ]
        if any(ind in text_lower for ind in exp_indicators):
            score += 40
            details.append("Experience section found")

        date_patterns = re.findall(
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}'
            r'\s*[-–]\s*(?:Present|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}',
            text, re.IGNORECASE
        )
        if date_patterns:
            score += 30
            details.append(f"Date ranges found: {len(date_patterns)}")

        role_keywords = [
            "engineer", "developer", "analyst", "intern",
            "manager", "lead", "architect", "consultant"
        ]
        found_roles = sum(1 for kw in role_keywords if kw in text_lower)
        score += min(30, found_roles * 10)
        if found_roles:
            details.append(f"Role titles found: {found_roles}")

        return {"score": min(100, score), "details": details}

    def _score_education(self, text: str) -> Dict:
        score = 0
        details = []
        text_lower = text.lower()

        degrees = ["b.e.", "b.tech", "bachelor", "m.tech", "master", "ph.d", "diploma"]
        for d in degrees:
            if d in text_lower:
                score += 30
                details.append(f"Degree found: {d}")
                break

        if re.search(r'cgpa|gpa|grade|percentage', text_lower):
            score += 30
            details.append("Academic score mentioned")

        if re.search(r'university|college|institute|school', text_lower):
            score += 20
            details.append("Institution mentioned")

        if re.search(r'20\d{2}', text):
            score += 20
            details.append("Graduation year found")

        return {"score": min(100, score), "details": details}

    def _score_projects(self, text: str) -> Dict:
        score = 0
        details = []
        text_lower = text.lower()

        if "project" in text_lower:
            score += 40
            details.append("Projects section found")

        project_indicators = [
            "developed", "built", "designed", "implemented",
            "created", "deployed"
        ]
        found = sum(1 for ind in project_indicators if ind in text_lower)
        score += min(30, found * 10)
        if found:
            details.append(f"Project action verbs: {found}")

        tech_in_projects = [
            "using", "with", "built with", "developed using", "implemented using"
        ]
        tech_count = sum(1 for t in tech_in_projects if t in text_lower)
        score += min(30, tech_count * 10)
        if tech_count:
            details.append("Technologies mentioned in projects")

        return {"score": min(100, score), "details": details}

    def _score_certifications(self, text: str) -> Dict:
        score = 0
        details = []
        text_lower = text.lower()

        cert_keywords = [
            "certification", "certificate", "certified",
            "aws certified", "google certified", "microsoft certified"
        ]
        found = sum(1 for kw in cert_keywords if kw in text_lower)
        if found:
            score = min(100, found * 30)
            details.append(f"Certifications mentioned: {found}")
        else:
            score = 10
            details.append("No certifications found")

        return {"score": score, "details": details}

    def _score_achievements(self, text: str) -> Dict:
        score = 0
        details = []
        text_lower = text.lower()

        achievement_kw = [
            "award", "achievement", "prize", "winner", "first place",
            "scholarship", "honor", "distinction", "topper", "rank"
        ]
        found = sum(1 for kw in achievement_kw if kw in text_lower)
        if found:
            score = min(100, found * 25)
            details.append(f"Achievements found: {found}")
        else:
            score = 15
            details.append("No achievements found")

        return {"score": score, "details": details}

    def _score_summary(self, text: str) -> Dict:
        score = 0
        details = []
        text_lower = text.lower()

        summary_kw = ["summary", "objective", "profile", "about"]
        if any(kw in text_lower for kw in summary_kw):
            score = 70
            details.append("Summary/objective section found")

            first_200 = " ".join(text.split()[:200])
            if len(first_200) > 50:
                score += 30
                details.append("Summary has good content")

        return {"score": min(100, score), "details": details}

    def _score_keyword_match(self, resume: str, job_desc: str) -> Dict:
        if not job_desc:
            return {"score": 50, "details": ["No job description provided"]}

        resume_words = set(resume.lower().split())
        job_words = set(job_desc.lower().split())
        common = resume_words.intersection(job_words)

        if len(job_words) == 0:
            return {"score": 50, "details": ["Empty job description"]}

        score = round((len(common) / len(job_words)) * 100, 2)
        return {
            "score": min(100, score),
            "details": [f"Keyword overlap: {len(common)}/{len(job_words)} words"]
        }

    def _score_action_verbs(self, text: str) -> Dict:
        text_lower = text.lower()
        found = [v for v in ACTION_VERBS if v in text_lower]
        if len(found) >= 8:
            score = 90
        elif len(found) >= 5:
            score = 70
        elif len(found) >= 2:
            score = 50
        else:
            score = 20
        return {
            "score": score,
            "details": [f"Action verbs found: {len(found)}"]
        }

    def _score_quantifiable(self, text: str) -> Dict:
        count = 0
        for pattern in QUANTIFIABLE_KEYWORDS:
            count += len(re.findall(pattern, text, re.IGNORECASE))

        if count >= 5:
            score = 90
        elif count >= 3:
            score = 70
        elif count >= 1:
            score = 50
        else:
            score = 20

        return {
            "score": score,
            "details": [f"Quantifiable metrics found: {count}"]
        }

    def _get_grade(self, score: float) -> str:
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B+ (Good)"
        elif score >= 60:
            return "B (Above Average)"
        elif score >= 50:
            return "C (Average)"
        elif score >= 40:
            return "D (Below Average)"
        else:
            return "F (Needs Major Improvement)"

    def _get_strengths(self, scores: Dict) -> List[str]:
        strengths = []
        for section, data in scores.items():
            if isinstance(data, dict) and data.get("score", 0) >= 70:
                strengths.append(
                    f"Strong {section.replace('_', ' ')} section"
                )
        return strengths

    def _get_weaknesses(self, scores: Dict) -> List[str]:
        weaknesses = []
        for section, data in scores.items():
            if isinstance(data, dict) and data.get("score", 0) < 40:
                weaknesses.append(
                    f"Weak {section.replace('_', ' ')} section"
                )
        return weaknesses

    def _get_improvements(self, scores: Dict, text: str) -> List[str]:
        improvements = []
        if scores.get("contact", {}).get("score", 0) < 50:
            improvements.append("Add email, phone, LinkedIn, and GitHub links")
        if scores.get("skills", {}).get("score", 0) < 60:
            improvements.append(
                "Add more relevant technical and soft skills"
            )
        if scores.get("projects", {}).get("score", 0) < 50:
            improvements.append(
                "Include detailed project descriptions with technologies used"
            )
        if scores.get("certifications", {}).get("score", 0) < 40:
            improvements.append(
                "Add relevant certifications (AWS, Google, etc.)"
            )
        if scores.get("action_verbs", {}).get("score", 0) < 50:
            improvements.append(
                "Use more action verbs: developed, implemented, optimized"
            )
        if scores.get("quantifiable", {}).get("score", 0) < 50:
            improvements.append(
                "Add quantifiable achievements: %, numbers, metrics"
            )
        return improvements
