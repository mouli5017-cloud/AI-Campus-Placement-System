import os
import sys
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ml.placement_model import PlacementPredictor
from src.ml.salary_model import SalaryPredictor
from src.ml.ats_scorer import ATSScorer
from src.ml.job_matcher import JobMatcher
from src.ml.resume_ranker import ResumeRanker
from src.nlp.skill_extractor import SkillExtractor
from src.nlp.resume_parser import ResumeParser
from src.utils.helpers import (
    validate_email, validate_cgpa, hash_password,
    verify_password, format_currency, safe_divide
)


class TestPlacementModel(unittest.TestCase):
    def setUp(self):
        self.predictor = PlacementPredictor()

    def test_create_dataset(self):
        df = self.predictor.create_sample_dataset(100)
        self.assertEqual(len(df), 100)
        self.assertIn("placed", df.columns)
        self.assertIn("cgpa", df.columns)

    def test_train_model(self):
        df = self.predictor.create_sample_dataset(200)
        metrics = self.predictor.train(df)
        self.assertIn("accuracy", metrics)
        self.assertGreater(metrics["accuracy"], 50)
        self.assertTrue(self.predictor.is_trained)

    def test_predict(self):
        df = self.predictor.create_sample_dataset(200)
        self.predictor.train(df)
        features = {
            "cgpa": 8.5, "tenth_percentage": 85.0,
            "twelfth_percentage": 80.0, "backlogs": 0,
            "internships": 2, "num_technical_skills": 8,
            "num_soft_skills": 5, "num_projects": 4,
            "num_certifications": 3, "experience_years": 1.0,
            "num_programming_languages": 4,
            "department": "Computer Science", "gender": "Male",
        }
        result = self.predictor.predict(features)
        self.assertIn("placed", result)
        self.assertIn("probability_placed", result)
        self.assertIn("suggestions", result)
        self.assertGreater(result["probability_placed"], 0)

    def test_risk_levels(self):
        self.assertEqual(
            self.predictor._get_risk_level(0.9),
            "Low Risk (High Placement Chance)"
        )
        self.assertEqual(
            self.predictor._get_risk_level(0.3),
            "High Risk (Significant Improvement Needed)"
        )


class TestSalaryModel(unittest.TestCase):
    def setUp(self):
        self.predictor = SalaryPredictor()

    def test_create_dataset(self):
        df = self.predictor.create_sample_dataset(100)
        self.assertEqual(len(df), 100)
        self.assertIn("salary_lpa", df.columns)

    def test_train_model(self):
        df = self.predictor.create_sample_dataset(200)
        metrics = self.predictor.train(df)
        self.assertIn("r2_score", metrics)
        self.assertTrue(self.predictor.is_trained)

    def test_predict(self):
        df = self.predictor.create_sample_dataset(200)
        self.predictor.train(df)
        features = {
            "cgpa": 8.5, "tenth_percentage": 85.0,
            "twelfth_percentage": 80.0, "backlogs": 0,
            "internships": 2, "num_technical_skills": 8,
            "num_soft_skills": 5, "num_projects": 4,
            "num_certifications": 3, "experience_years": 1.0,
            "num_programming_languages": 4,
            "department": "Computer Science", "gender": "Male",
        }
        result = self.predictor.predict(features)
        self.assertIn("predicted_salary_lpa", result)
        self.assertGreater(result["predicted_salary_lpa"], 0)


class TestATSScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = ATSScorer()

    def test_basic_scoring(self):
        text = (
            "John Doe\njohn@email.com\n+91-9876543210\n"
            "linkedin.com/in/johndoe\ngithub.com/johndoe\n\n"
            "SUMMARY\nExperienced software developer with 3 years of experience.\n\n"
            "SKILLS\nPython, Java, React, SQL, Docker, AWS, Machine Learning\n\n"
            "EXPERIENCE\nSoftware Engineer at ABC Corp (Jan 2022 - Present)\n"
            "Developed microservices architecture reducing latency by 40%\n"
            "Led team of 5 engineers\n\n"
            "EDUCATION\nB.Tech Computer Science, XYZ University, CGPA: 8.5/10, 2022\n\n"
            "PROJECTS\nE-commerce Platform: Built using React, Node.js, MongoDB\n"
            "AI Chatbot: Developed using Python, TensorFlow, deployed on AWS\n\n"
            "CERTIFICATIONS\nAWS Certified Cloud Practitioner\n"
            "Google Professional Data Engineer\n"
        )
        result = self.scorer.compute_ats_score(text)
        self.assertIn("overall_score", result)
        self.assertIn("grade", result)
        self.assertIn("section_scores", result)
        self.assertGreater(result["overall_score"], 30)

    def test_empty_resume(self):
        result = self.scorer.compute_ats_score("")
        self.assertLess(result["overall_score"], 15)

    def test_grade_calculation(self):
        self.assertIn("Excellent", self.scorer._get_grade(95))
        self.assertIn("Very Good", self.scorer._get_grade(85))
        self.assertIn("Good", self.scorer._get_grade(75))


class TestSkillExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = SkillExtractor()

    def test_extract_skills(self):
        text = "I know Python, Java, React, and Docker. Also have experience with AWS and Machine Learning."
        skills = self.extractor.extract_skills(text)
        skill_names = [s["skill"].lower() for s in skills]
        self.assertIn("python", skill_names)
        self.assertIn("java", skill_names)
        self.assertGreater(len(skills), 3)

    def test_skill_match(self):
        resume_skills = ["Python", "Java", "SQL", "React"]
        job_skills = ["Python", "Java", "SQL", "React", "Docker", "AWS"]
        score, matched, missing = self.extractor.compute_skill_match(
            resume_skills, job_skills
        )
        self.assertAlmostEqual(score, 4 / 6, places=2)
        self.assertEqual(len(matched), 4)
        self.assertEqual(len(missing), 2)

    def test_skill_gap_analysis(self):
        current = ["Python", "Java", "SQL"]
        target = ["Python", "Java", "SQL", "React", "Docker", "AWS"]
        gap = self.extractor.get_skill_gap_analysis(current, target)
        self.assertIn("match_score", gap)
        self.assertIn("missing_skills", gap)
        self.assertIn("recommendations", gap)
        self.assertEqual(len(gap["missing_skills"]), 3)

    def test_aliases(self):
        text = "Experience with ml and ai, also know js and ts"
        skills = self.extractor.extract_skills(text)
        skill_names = [s["skill"].lower() for s in skills]
        self.assertIn("machine learning", skill_names)
        self.assertIn("artificial intelligence", skill_names)


class TestJobMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = JobMatcher()

    def test_match_jobs(self):
        profile = {
            "cgpa": 8.0,
            "backlogs": 0,
            "internships": 1,
            "technical_skills": ["Python", "Java", "SQL"],
            "programming_languages": ["Python", "Java"],
            "soft_skills": ["Communication"],
        }
        matches = self.matcher.match_jobs(profile)
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        self.assertIn("company", matches[0])
        self.assertIn("overall_match", matches[0])

    def test_eligibility(self):
        profile = {
            "cgpa": 5.0,
            "backlogs": 3,
            "internships": 0,
            "technical_skills": ["Python"],
            "programming_languages": ["Python"],
            "soft_skills": [],
        }
        matches = self.matcher.match_jobs(profile)
        high_cgpa_companies = [
            m for m in matches if m["min_cgpa_required"] > 5.0
        ]
        for m in high_cgpa_companies:
            self.assertEqual(m["eligibility"], "Not Eligible")


class TestResumeRanker(unittest.TestCase):
    def setUp(self):
        self.ranker = ResumeRanker()

    def test_rank_resumes(self):
        resumes = [
            {
                "name": "Alice",
                "skills": ["Python", "Java", "SQL", "React"],
                "cgpa": 8.5,
                "experience_years": 2,
                "ats_score": 80,
            },
            {
                "name": "Bob",
                "skills": ["Python", "Java"],
                "cgpa": 7.0,
                "experience_years": 0,
                "ats_score": 60,
            },
        ]
        job_req = {
            "required_skills": ["Python", "Java", "SQL", "React", "Docker"],
            "min_cgpa": 6.0,
        }
        ranked = self.ranker.rank_resumes(resumes, job_req)
        self.assertEqual(ranked[0]["name"], "Alice")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertIn("rank_score", ranked[0])


class TestHelpers(unittest.TestCase):
    def test_validate_email(self):
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co"))
        self.assertFalse(validate_email("invalid"))
        self.assertFalse(validate_email("@domain.com"))

    def test_validate_cgpa(self):
        self.assertTrue(validate_cgpa(8.5))
        self.assertTrue(validate_cgpa(0.0))
        self.assertTrue(validate_cgpa(10.0))
        self.assertFalse(validate_cgpa(-1.0))
        self.assertFalse(validate_cgpa(11.0))

    def test_password_hashing(self):
        hashed = hash_password("test123")
        self.assertTrue(verify_password("test123", hashed))
        self.assertFalse(verify_password("wrong", hashed))

    def test_format_currency(self):
        self.assertEqual(format_currency(5.5), "5.50 LPA")
        self.assertEqual(format_currency(0.5), "50000 INR")

    def test_safe_divide(self):
        self.assertEqual(safe_divide(10, 2), 5.0)
        self.assertEqual(safe_divide(10, 0), 0.0)


class TestResumeParser(unittest.TestCase):
    def setUp(self):
        self.parser = ResumeParser()

    def test_extract_email(self):
        text = "Contact me at john.doe@email.com for details"
        email = self.parser._extract_email(text)
        self.assertEqual(email, "john.doe@email.com")

    def test_extract_phone(self):
        text = "Call me at +91-9876543210"
        phone = self.parser._extract_phone(text)
        self.assertIn("9876543210", phone)

    def test_extract_github(self):
        text = "GitHub: github.com/johndoe"
        github = self.parser._extract_github(text)
        self.assertEqual(github, "https://github.com/johndoe")

    def test_parse_text(self):
        text = (
            "John Doe\njohn@email.com\n+91-9876543210\n\n"
            "SKILLS\nPython, Java, SQL\n\n"
            "EDUCATION\nB.Tech Computer Science\n"
        )
        resume = self.parser.parse_text(text)
        self.assertEqual(resume.email, "john@email.com")
        self.assertIn("skills", resume.sections)
        self.assertGreater(resume.total_words, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
