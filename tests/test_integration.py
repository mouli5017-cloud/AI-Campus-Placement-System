"""
Comprehensive Integration Tests for Campus Placement AI System
Tests end-to-end workflows across all modules.
"""
import os
import sys
import unittest
import tempfile
import shutil
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestPlacementPredictionWorkflow(unittest.TestCase):
    """Tests the complete placement prediction workflow."""

    def setUp(self):
        from src.ml.placement_model import PlacementPredictor
        self.predictor = PlacementPredictor()
        self.sample_features = {
            "cgpa": 8.5,
            "tenth_percentage": 85.0,
            "twelfth_percentage": 80.0,
            "backlogs": 0,
            "internships": 2,
            "num_technical_skills": 8,
            "num_soft_skills": 5,
            "num_projects": 4,
            "num_certifications": 3,
            "experience_years": 1.0,
            "num_programming_languages": 4,
            "department": "Computer Science",
            "gender": "Male",
        }

    def test_full_workflow_train_predict(self):
        df = self.predictor.create_sample_dataset(300)
        metrics = self.predictor.train(df)
        self.assertGreater(metrics["accuracy"], 60)

        result = self.predictor.predict(self.sample_features)
        self.assertIn("placed", result)
        self.assertIn("probability_placed", result)
        self.assertIn("suggestions", result)
        self.assertGreater(result["probability_placed"], 0)
        self.assertLessEqual(result["probability_placed"], 100)

    def test_edge_cases(self):
        df = self.predictor.create_sample_dataset(200)
        self.predictor.train(df)

        min_features = {
            "cgpa": 4.0, "tenth_percentage": 40.0,
            "twelfth_percentage": 40.0, "backlogs": 10,
            "internships": 0, "num_technical_skills": 0,
            "num_soft_skills": 0, "num_projects": 0,
            "num_certifications": 0, "experience_years": 0,
            "num_programming_languages": 1,
            "department": "Civil", "gender": "Male",
        }
        result = self.predictor.predict(min_features)
        self.assertLess(result["probability_placed"], 30)

        max_features = {
            "cgpa": 10.0, "tenth_percentage": 99.0,
            "twelfth_percentage": 99.0, "backlogs": 0,
            "internships": 5, "num_technical_skills": 15,
            "num_soft_skills": 10, "num_projects": 10,
            "num_certifications": 6, "experience_years": 5.0,
            "num_programming_languages": 8,
            "department": "Computer Science", "gender": "Female",
        }
        result = self.predictor.predict(max_features)
        self.assertGreater(result["probability_placed"], 70)

    def test_save_and_load(self):
        df = self.predictor.create_sample_dataset(200)
        self.predictor.train(df)
        self.predictor.save_model()

        from src.ml.placement_model import PlacementPredictor as PP2
        new_predictor = PP2()
        loaded = new_predictor.load_model()
        self.assertTrue(loaded)
        self.assertTrue(new_predictor.is_trained)

        result = new_predictor.predict(self.sample_features)
        self.assertIn("placed", result)


class TestSalaryPredictionWorkflow(unittest.TestCase):
    """Tests the salary prediction workflow."""

    def setUp(self):
        from src.ml.salary_model import SalaryPredictor
        self.predictor = SalaryPredictor()
        self.sample_features = {
            "cgpa": 8.5,
            "tenth_percentage": 85.0,
            "twelfth_percentage": 80.0,
            "backlogs": 0,
            "internships": 2,
            "num_technical_skills": 8,
            "num_soft_skills": 5,
            "num_projects": 4,
            "num_certifications": 3,
            "experience_years": 1.0,
            "num_programming_languages": 4,
            "department": "Computer Science",
            "gender": "Male",
        }

    def test_train_and_predict(self):
        df = self.predictor.create_sample_dataset(300)
        metrics = self.predictor.train(df)
        self.assertGreater(metrics["r2_score"], 50)

        result = self.predictor.predict(self.sample_features)
        self.assertIn("predicted_salary_lpa", result)
        self.assertGreater(result["predicted_salary_lpa"], 2.0)
        self.assertIn("salary_tier", result)

    def test_salary_range(self):
        df = self.predictor.create_sample_dataset(200)
        self.predictor.train(df)

        low_result = self.predictor.predict({
            **self.sample_features, "cgpa": 5.0, "internships": 0
        })
        high_result = self.predictor.predict({
            **self.sample_features, "cgpa": 10.0, "internships": 4,
            "experience_years": 4.0
        })
        self.assertGreater(
            high_result["predicted_salary_lpa"],
            low_result["predicted_salary_lpa"]
        )


class TestResumeProcessingWorkflow(unittest.TestCase):
    """Tests resume parsing and analysis workflow."""

    def setUp(self):
        from src.nlp.resume_parser import ResumeParser
        from src.nlp.skill_extractor import SkillExtractor
        from src.ml.ats_scorer import ATSScorer
        self.parser = ResumeParser()
        self.extractor = SkillExtractor()
        self.scorer = ATSScorer()

    def test_full_resume_analysis(self):
        resume_text = (
            "John Doe\njohn.doe@email.com\n+91-9876543210\n"
            "linkedin.com/in/johndoe\ngithub.com/johndoe\n\n"
            "SUMMARY\n"
            "Software engineer with 2 years of experience in Python and React.\n"
            "Passionate about building scalable web applications.\n\n"
            "SKILLS\n"
            "Python, Java, React, Node.js, SQL, Docker, AWS, Git, HTML, CSS\n"
            "Communication, Team Work, Problem Solving\n\n"
            "EXPERIENCE\n"
            "Software Engineer at TechCorp (Jan 2023 - Present)\n"
            "- Developed microservices using Python and FastAPI\n"
            "- Led team of 3 engineers, improved performance by 40%\n"
            "- Deployed applications on AWS using Docker and Kubernetes\n\n"
            "Software Developer at StartupXYZ (Jun 2021 - Dec 2022)\n"
            "- Built React frontend serving 10,000+ daily users\n"
            "- Implemented REST API reducing response time by 60%\n\n"
            "EDUCATION\n"
            "B.Tech Computer Science, IIT Delhi, CGPA: 8.5/10, 2021\n\n"
            "PROJECTS\n"
            "E-Commerce Platform: Built with React, Node.js, MongoDB, deployed on AWS\n"
            "AI Chatbot: Developed using Python, TensorFlow, NLP\n"
            "Portfolio Website: HTML, CSS, JavaScript, responsive design\n\n"
            "CERTIFICATIONS\n"
            "AWS Certified Cloud Practitioner\n"
            "Google Professional Data Engineer\n"
            "MongoDB Certified Developer\n"
        )

        parsed = self.parser.parse_text(resume_text)
        self.assertEqual(parsed.email, "john.doe@email.com")
        self.assertIn("+91-9876543210", parsed.phone)
        self.assertEqual(parsed.name, "John Doe")
        self.assertIn("skills", parsed.sections)
        self.assertGreater(parsed.total_words, 50)

        skills = self.extractor.extract_skills(resume_text)
        skill_names = [s["skill"].lower() for s in skills]
        self.assertIn("python", skill_names)
        self.assertIn("react", skill_names)
        self.assertIn("docker", skill_names)

        ats = self.scorer.compute_ats_score(resume_text, "", skill_names)
        self.assertGreater(ats["overall_score"], 30)
        self.assertIn("section_scores", ats)
        self.assertIn("strengths", ats)
        self.assertIn("improvements", ats)

    def test_weak_resume(self):
        weak_resume = "Name: Student\nEmail: s@x.com\nSkills: nothing much"
        ats = self.scorer.compute_ats_score(weak_resume)
        self.assertLess(ats["overall_score"], 40)


class TestSkillGapWorkflow(unittest.TestCase):
    """Tests skill gap analysis and recommendations."""

    def setUp(self):
        from src.nlp.skill_extractor import SkillExtractor
        self.extractor = SkillExtractor()

    def test_full_gap_analysis(self):
        current = ["Python", "Java", "SQL", "HTML", "CSS"]
        target = ["Python", "Java", "SQL", "React", "Docker", "AWS", "ML"]

        gap = self.extractor.get_skill_gap_analysis(current, target)
        self.assertEqual(gap["match_score"], round(3 / 7 * 100, 2))
        self.assertEqual(len(gap["missing_skills"]), 4)
        self.assertIn("React", gap["missing_skills"])
        self.assertIn("Docker", gap["missing_skills"])

        self.assertGreater(len(gap["recommendations"]), 0)
        for rec in gap["recommendations"]:
            self.assertIn("skill", rec)
            self.assertIn("course", rec)
            self.assertIn("platform", rec)

    def test_perfect_match(self):
        skills = ["Python", "Java", "SQL"]
        gap = self.extractor.get_skill_gap_analysis(skills, skills)
        self.assertEqual(gap["match_score"], 100.0)
        self.assertEqual(len(gap["missing_skills"]), 0)


class TestJobMatchingWorkflow(unittest.TestCase):
    """Tests job matching across companies."""

    def setUp(self):
        from src.ml.job_matcher import JobMatcher
        self.matcher = JobMatcher()

    def test_strong_profile(self):
        profile = {
            "cgpa": 9.0,
            "backlogs": 0,
            "internships": 3,
            "technical_skills": ["Python", "Java", "React", "SQL", "Docker", "AWS"],
            "programming_languages": ["Python", "Java", "JavaScript"],
            "soft_skills": ["Communication", "Leadership"],
        }
        matches = self.matcher.match_jobs(profile)
        self.assertGreater(len(matches), 0)
        top = matches[0]
        self.assertGreater(top["overall_match"], 50)
        self.assertEqual(top["eligibility"], "Eligible")

    def test_weak_profile(self):
        profile = {
            "cgpa": 5.0,
            "backlogs": 5,
            "internships": 0,
            "technical_skills": ["HTML"],
            "programming_languages": ["HTML"],
            "soft_skills": [],
        }
        matches = self.matcher.match_jobs(profile)
        for m in matches:
            if m["min_cgpa_required"] > 5.0:
                self.assertEqual(m["eligibility"], "Not Eligible")

    def test_top_companies(self):
        profile = {
            "cgpa": 8.0, "backlogs": 0, "internships": 2,
            "technical_skills": ["Python", "Java", "React", "SQL"],
            "programming_languages": ["Python", "Java"],
            "soft_skills": ["Communication"],
        }
        top5 = self.matcher.get_top_companies(profile, top_n=5)
        self.assertEqual(len(top5), 5)
        self.assertEqual(top5[0]["overall_match"] >= top5[-1]["overall_match"], True)


class TestResumeRanking(unittest.TestCase):
    """Tests resume ranking system."""

    def setUp(self):
        from src.ml.resume_ranker import ResumeRanker
        self.ranker = ResumeRanker()

    def test_rank_ordering(self):
        resumes = [
            {"name": "Alice", "skills": ["Python", "Java", "SQL", "React", "Docker"],
             "cgpa": 9.0, "experience_years": 2, "ats_score": 90},
            {"name": "Bob", "skills": ["Python", "Java"],
             "cgpa": 7.0, "experience_years": 0, "ats_score": 60},
            {"name": "Charlie", "skills": ["Python", "Java", "SQL"],
             "cgpa": 8.0, "experience_years": 1, "ats_score": 75},
        ]
        job_req = {"required_skills": ["Python", "Java", "SQL", "React", "Docker"], "min_cgpa": 6.0}

        ranked = self.ranker.rank_resumes(resumes, job_req)
        self.assertEqual(ranked[0]["name"], "Alice")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertGreater(ranked[0]["rank_score"], ranked[1]["rank_score"])

    def test_eligibility_filtering(self):
        resumes = [
            {"name": "Low", "skills": [], "cgpa": 5.0, "experience_years": 0, "ats_score": 40},
            {"name": "High", "skills": ["Python"], "cgpa": 9.0, "experience_years": 2, "ats_score": 85},
        ]
        job_req = {"required_skills": ["Python"], "min_cgpa": 7.0}
        ranked = self.ranker.rank_resumes(resumes, job_req)
        self.assertTrue(ranked[0]["rank_details"]["eligible"])
        self.assertFalse(ranked[1]["rank_details"]["eligible"])

    def test_summary_statistics(self):
        resumes = [
            {"name": "A", "skills": ["Python"], "cgpa": 8.0,
             "experience_years": 1, "ats_score": 80, "rank_score": 75,
             "rank_details": {"eligible": True}},
            {"name": "B", "skills": ["Java"], "cgpa": 6.0,
             "experience_years": 0, "ats_score": 50, "rank_score": 45,
             "rank_details": {"eligible": False}},
        ]
        summary = self.ranker.get_resume_summary(resumes)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["eligible"], 1)
        self.assertEqual(summary["not_eligible"], 1)


class TestEmailServiceWorkflow(unittest.TestCase):
    """Tests email notification workflows."""

    def setUp(self):
        from src.utils.email_service import EmailNotificationService
        self.service = EmailNotificationService()

    def test_complete_notification_flow(self):
        result = {
            "placed": True, "probability_placed": 85.5,
            "risk_level": "Low Risk",
            "suggestions": ["Keep practicing", "Apply to companies"]
        }
        msg = self.service.send_placement_prediction(
            "Alice", "alice@college.edu", result
        )
        self.assertIsNotNone(msg)
        self.assertEqual(msg.recipient, "alice@college.edu")
        self.assertIn("85.5", msg.body)

        emails = self.service.get_sent_emails()
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]["type"], "placement_prediction")

    def test_multi_type_emails(self):
        self.service.send_placement_prediction(
            "A", "a@b.com",
            {"placed": True, "probability_placed": 80,
             "risk_level": "Low", "suggestions": []}
        )
        self.service.send_resume_analysis(
            "B", "b@b.com",
            {"overall_score": 75, "grade": "B+", "improvements": []}
        )
        self.service.send_job_matches(
            "C", "c@b.com",
            [{"company": "TCS", "overall_match": 80}]
        )

        self.assertEqual(self.service.get_email_count(), 3)
        self.assertEqual(len(self.service.get_emails_by_type("placement_prediction")), 1)
        self.assertEqual(len(self.service.get_emails_by_type("resume_analyzed")), 1)
        self.assertEqual(len(self.service.get_emails_by_type("job_match")), 1)


class TestReportExportWorkflow(unittest.TestCase):
    """Tests report export workflows."""

    def setUp(self):
        from src.utils.report_exporter import ReportExporter
        self.exporter = ReportExporter()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_export_cycle(self):
        predictions = [{
            "features": {
                "cgpa": 8.5, "tenth_percentage": 85,
                "twelfth_percentage": 80, "backlogs": 0,
                "internships": 2, "num_technical_skills": 8,
                "num_projects": 4, "department": "CS"
            },
            "result": {
                "placed": True, "probability_placed": 87.5,
                "confidence": 90, "risk_level": "Low Risk"
            },
            "timestamp": "2025-06-15"
        }]

        path = self.exporter.export_placement_report_csv(
            predictions, os.path.join(self.test_dir, "placement.csv")
        )
        self.assertTrue(os.path.exists(path))
        df = pd.read_csv(path)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Predicted"], "Placed")
        self.assertEqual(df.iloc[0]["Probability %"], 87.5)


class TestInterviewPrepWorkflow(unittest.TestCase):
    """Tests interview preparation workflows."""

    def setUp(self):
        from src.ml.interview_prep import InterviewPrepModule
        self.prep = InterviewPrepModule()

    def test_quiz_workflow(self):
        categories = self.prep.get_all_categories()
        self.assertGreater(len(categories), 0)

        quiz = self.prep.get_mixed_quiz(
            ["technical_python", "hr_behavioral"], count=3
        )
        self.assertGreaterEqual(len(quiz), 1)

        all_cats = set(self.prep.get_all_categories())
        for q in quiz:
            self.assertIsNotNone(q.category)
            self.assertIsNotNone(q.question)
            self.assertIsNotNone(q.answer)
            formatted = self.prep.format_question(q, 1)
            self.assertIn("Q1", formatted)
            answer = self.prep.format_answer(q)
            self.assertIn("Answer:", answer)

    def test_role_specific_tips(self):
        se_tips = self.prep.get_interview_tips("software_engineer")
        self.assertGreater(len(se_tips), 5)
        self.assertTrue(any("coding" in t.lower() or "leetcode" in t.lower() for t in se_tips))

        ds_tips = self.prep.get_interview_tips("data_scientist")
        self.assertGreater(len(ds_tips), 5)

    def test_difficulty_filtering(self):
        easy = self.prep.get_questions_by_category("technical_python", difficulty="Easy")
        for q in easy:
            self.assertEqual(q.difficulty, "Easy")

        medium = self.prep.get_questions_by_category("technical_dsa", difficulty="Medium")
        for q in medium:
            self.assertEqual(q.difficulty, "Medium")


class TestAnalyticsEngine(unittest.TestCase):
    """Tests analytics visualization engine."""

    def setUp(self):
        from src.ml.analytics_engine import AnalyticsEngine
        self.analytics = AnalyticsEngine()

    def test_all_charts_generate(self):
        charts = [
            self.analytics.department_placement_chart(),
            self.analytics.salary_distribution_chart(),
            self.analytics.monthly_placements_trend(),
            self.analytics.top_skills_demand_chart(),
            self.analytics.skill_demand_heatmap(),
            self.analytics.company_comparison_chart(),
            self.analytics.company_scatter(),
            self.analytics.placement_probability_gauge(75.0),
            self.analytics.ats_radar_chart({
                "contact": {"score": 80},
                "skills": {"score": 90},
                "experience": {"score": 70},
            }),
            self.analytics.comparison_bar(
                {"Accuracy": 87, "Precision": 85, "Recall": 83},
                "Model Metrics"
            ),
        ]
        for chart in charts:
            self.assertIsNotNone(chart)
            self.assertTrue(hasattr(chart, 'to_json'))


class TestDatabaseModels(unittest.TestCase):
    """Tests database model definitions."""

    def test_models_import(self):
        from src.database.models import (
            User, StudentProfile, Resume, JobPosting,
            JobApplication, PredictionHistory, LearningRecommendation,
            EmailLog, AnalyticsLog, UserRole, PlacementStatus
        )
        self.assertIsNotNone(User)
        self.assertIsNotNone(StudentProfile)
        self.assertIsNotNone(UserRole)
        self.assertIsNotNone(PlacementStatus)

    def test_user_roles(self):
        from src.database.models import UserRole
        self.assertEqual(UserRole.STUDENT.value, "student")
        self.assertEqual(UserRole.ADMIN.value, "admin")
        self.assertEqual(UserRole.PLACEMENT_OFFICER.value, "placement_officer")

    def test_placement_statuses(self):
        from src.database.models import PlacementStatus
        self.assertEqual(PlacementStatus.PLACED.value, "placed")
        self.assertEqual(PlacementStatus.NOT_PLACED.value, "not_placed")
        self.assertEqual(PlacementStatus.IN_PROCESS.value, "in_process")


class TestConfigSystem(unittest.TestCase):
    """Tests configuration system."""

    def test_config_loaded(self):
        from config.config import config
        self.assertEqual(config.APP_NAME, "AI Campus Placement Prediction & Resume Screening")
        self.assertEqual(config.APP_VERSION, "1.0.0")
        self.assertGreater(len(config.companies.COMPANIES), 0)
        self.assertGreater(len(config.skills.TECHNICAL_SKILLS), 0)

    def test_companies_have_required_fields(self):
        from config.config import config
        for company in config.companies.COMPANIES:
            self.assertIn("name", company)
            self.assertIn("min_cgpa", company)
            self.assertIn("min_salary", company)
            self.assertIn("max_salary", company)
            self.assertIn("skills", company)
            self.assertGreater(company["max_salary"], company["min_salary"])

    def test_skill_categories(self):
        from config.config import config
        self.assertGreater(len(config.skills.TECHNICAL_SKILLS), 50)
        self.assertGreater(len(config.skills.SOFT_SKILLS), 5)
        self.assertGreater(len(config.skills.DOMAIN_SKILLS), 5)


class TestHelperFunctions(unittest.TestCase):
    """Tests utility helper functions."""

    def test_password_lifecycle(self):
        from src.utils.helpers import hash_password, verify_password
        hashed = hash_password("secure_password_123")
        self.assertTrue(verify_password("secure_password_123", hashed))
        self.assertFalse(verify_password("wrong_password", hashed))

    def test_email_validation_comprehensive(self):
        from src.utils.helpers import validate_email
        valid = ["user@domain.com", "a.b@c.co", "user+tag@domain.org"]
        invalid = ["@", "user@", "@domain.com", "user@.com", ""]
        for e in valid:
            self.assertTrue(validate_email(e), f"Should be valid: {e}")
        for e in invalid:
            self.assertFalse(validate_email(e), f"Should be invalid: {e}")

    def test_cgpa_validation(self):
        from src.utils.helpers import validate_cgpa
        self.assertTrue(validate_cgpa(0.0))
        self.assertTrue(validate_cgpa(5.0))
        self.assertTrue(validate_cgpa(10.0))
        self.assertFalse(validate_cgpa(-0.1))
        self.assertFalse(validate_cgpa(10.1))

    def test_format_currency(self):
        from src.utils.helpers import format_currency
        self.assertEqual(format_currency(5.5), "5.50 LPA")
        self.assertEqual(format_currency(0.3), "30000 INR")

    def test_safe_divide(self):
        from src.utils.helpers import safe_divide
        self.assertEqual(safe_divide(10, 2), 5.0)
        self.assertEqual(safe_divide(10, 0), 0.0)
        self.assertEqual(safe_divide(10, 0, default=999), 999)


if __name__ == "__main__":
    unittest.main(verbosity=2)
