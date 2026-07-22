import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import logging

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import config

logger = logging.getLogger(__name__)


class SkillExtractor:
    def __init__(self):
        self.all_skills = set()
        self.skill_categories = {}
        self._build_skill_index()
        self.skill_aliases = self._build_aliases()

    def _build_skill_index(self):
        skills_cfg = config.skills
        for skill in skills_cfg.TECHNICAL_SKILLS:
            self.all_skills.add(skill.lower())
            self.skill_categories[skill.lower()] = "technical"
        for skill in skills_cfg.SOFT_SKILLS:
            self.all_skills.add(skill.lower())
            self.skill_categories[skill.lower()] = "soft"
        for skill in skills_cfg.DOMAIN_SKILLS:
            self.all_skills.add(skill.lower())
            self.skill_categories[skill.lower()] = "domain"

    def _build_aliases(self) -> Dict[str, str]:
        return {
            "js": "javascript", "ts": "typescript", "py": "python",
            "c plus plus": "c++", "c#": "c++", "csharp": "c++",
            "reactjs": "react", "react.js": "react",
            "vuejs": "vue.js", "vue.js": "vue.js",
            "nodejs": "node.js", "node.js": "node.js",
            "nextjs": "next.js", "next.js": "next.js",
            "ng": "angular", "angularjs": "angular", "angular.js": "angular",
            "tf": "tensorflow", "tensorflow": "tensorflow",
            "pytorch": "pytorch", "torch": "pytorch",
            "sklearn": "scikit-learn", "scikit learn": "scikit-learn",
            "postgres": "postgresql", "mongo": "mongodb",
            "k8s": "kubernetes", "gcp": "gcp",
            "amazon web services": "aws", "amazon cloud": "aws",
            "microsoft azure": "azure", "ms azure": "azure",
            "git version control": "git", "github": "git",
            "ci/cd pipeline": "ci/cd", "continuous integration": "ci/cd",
            "machine learning": "machine learning", "ml": "machine learning",
            "deep learning": "deep learning", "dl": "deep learning",
            "nlp": "nlp", "natural language processing": "nlp",
            "cv": "computer vision", "computer vision": "computer vision",
            "rest": "rest api", "restful": "rest api", "rest api": "rest api",
            "graphql": "graphql",
            "docker containerization": "docker", "docker": "docker",
            "tailwind css": "tailwind", "tailwindcss": "tailwind",
            "bootstrap framework": "bootstrap",
            "data analysis": "data analysis", "eda": "data analysis",
            "powerbi": "power bi",
            "excel spreadsheet": "excel",
            "pandas dataframe": "pandas", "numpy array": "numpy",
            "oop": "object oriented programming",
            "object-oriented programming": "object oriented programming",
            "object oriented": "object oriented programming",
            "dsa": "dsa", "data structures": "dsa",
            "algorithms": "dsa", "data structures and algorithms": "dsa",
            "dbms": "sql", "database": "sql",
            "spring": "spring boot", "spring framework": "spring boot",
            "microservice": "microservices",
            "terraform iac": "terraform",
            "devops practices": "devops",
            "linux administration": "linux",
            "system design": "system design",
            "site reliability": "site reliability engineering",
            "sre": "site reliability engineering",
            "r programming": "r", "r language": "r",
            "matlab programming": "matlab",
            "php web": "php", "ruby on rails": "ruby",
            "blockchain technology": "blockchain",
            "iot": "internet of things",
            "artificial intelligence": "artificial intelligence",
            "ai": "artificial intelligence",
            "software testing": "software testing",
            "qa": "software testing", "quality assurance": "software testing",
            "automation testing": "software testing",
        }

    def extract_skills(self, text: str) -> List[Dict[str, str]]:
        text_lower = text.lower()
        found_skills = {}

        for skill in self.all_skills:
            patterns = self._get_skill_patterns(skill)
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    canonical = self.skill_aliases.get(skill, skill)
                    if canonical not in found_skills:
                        found_skills[canonical] = self.skill_categories.get(
                            skill, "technical"
                        )
                    break

        for alias, canonical in self.skill_aliases.items():
            if canonical in self.all_skills:
                patterns = self._get_skill_patterns(alias)
                for pattern in patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        if canonical not in found_skills:
                            found_skills[canonical] = self.skill_categories.get(
                                canonical, "technical"
                            )
                        break

        result = [
            {"skill": skill.title(), "category": cat}
            for skill, cat in found_skills.items()
        ]
        result.sort(key=lambda x: x["skill"])
        return result

    def _get_skill_patterns(self, skill: str) -> List[str]:
        escaped = re.escape(skill)
        return [
            rf'\b{escaped}\b',
            rf'(?<![a-z]){escaped}(?![a-z])',
            rf'(?:^|\s|,|;|/|\||\+){escaped}(?:\s|,|;|/|\||\+|$)',
        ]

    def get_skill_list(self, text: str) -> List[str]:
        skills = self.extract_skills(text)
        return [s["skill"] for s in skills]

    def get_skills_by_category(self, text: str) -> Dict[str, List[str]]:
        skills = self.extract_skills(text)
        categorized = defaultdict(list)
        for s in skills:
            categorized[s["category"]].append(s["skill"])
        return dict(categorized)

    def compute_skill_match(
        self, resume_skills: List[str], job_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        resume_set = {s.lower() for s in resume_skills}
        job_set = {s.lower() for s in job_skills}

        matched = resume_set.intersection(job_set)
        missing = job_set - resume_set
        extra = resume_set - job_set

        if len(job_set) == 0:
            return 1.0, list(matched), list(missing)

        score = len(matched) / len(job_set)
        return score, list(matched), list(missing)

    def get_skill_gap_analysis(
        self, resume_skills: List[str], target_role_skills: List[str]
    ) -> Dict:
        score, matched, missing = self.compute_skill_match(
            resume_skills, target_role_skills
        )
        return {
            "match_score": round(score * 100, 2),
            "matched_skills": [s.title() for s in matched],
            "missing_skills": [s.title() for s in missing],
            "extra_skills": [
                s.title() for s in
                set(s.lower() for s in resume_skills) -
                set(s.lower() for s in target_role_skills)
            ],
            "recommendations": self._generate_recommendations(missing),
        }

    def _generate_recommendations(self, missing_skills: List[str]) -> List[Dict]:
        recommendations = []
        course_map = {
            "python": {"course": "Python for Everybody", "platform": "Coursera", "hours": 40},
            "java": {"course": "Java Programming Masterclass", "platform": "Udemy", "hours": 80},
            "javascript": {"course": "The Complete JavaScript Course", "platform": "Udemy", "hours": 60},
            "react": {"course": "React - The Complete Guide", "platform": "Udemy", "hours": 48},
            "angular": {"course": "Angular - The Complete Guide", "platform": "Udemy", "hours": 36},
            "node.js": {"course": "Node.js, Express, MongoDB Bootcamp", "platform": "Udemy", "hours": 40},
            "machine learning": {"course": "Machine Learning by Andrew Ng", "platform": "Coursera", "hours": 56},
            "deep learning": {"course": "Deep Learning Specialization", "platform": "Coursera", "hours": 120},
            "tensorflow": {"course": "TensorFlow Developer Certificate", "platform": "Coursera", "hours": 60},
            "pytorch": {"course": "PyTorch for Deep Learning", "platform": "Udemy", "hours": 44},
            "sql": {"course": "The Complete SQL Bootcamp", "platform": "Udemy", "hours": 30},
            "aws": {"course": "AWS Cloud Practitioner", "platform": "AWS", "hours": 40},
            "docker": {"course": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy", "hours": 24},
            "git": {"course": "Git & GitHub Crash Course", "platform": "Udemy", "hours": 8},
            "spring boot": {"course": "Spring Boot Masterclass", "platform": "Udemy", "hours": 36},
            "data analysis": {"course": "Google Data Analytics Certificate", "platform": "Coursera", "hours": 180},
            "system design": {"course": "System Design Interview Course", "platform": "Educative", "hours": 30},
            "dsa": {"course": "Data Structures & Algorithms Bootcamp", "platform": "Udemy", "hours": 100},
            "c++": {"course": "Beginning C++ Programming", "platform": "Udemy", "hours": 50},
            "kubernetes": {"course": "Kubernetes for Beginners", "platform": "Udemy", "hours": 20},
        }

        for skill in missing_skills:
            skill_lower = skill.lower()
            if skill_lower in course_map:
                rec = course_map[skill_lower]
                recommendations.append({
                    "skill": skill,
                    "course": rec["course"],
                    "platform": rec["platform"],
                    "estimated_hours": rec["hours"],
                })
            else:
                recommendations.append({
                    "skill": skill,
                    "course": f"Learn {skill} - Online Course",
                    "platform": "Various (Coursera, Udemy, edX)",
                    "estimated_hours": 30,
                })

        return recommendations
