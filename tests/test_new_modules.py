import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.email_service import EmailNotificationService, EmailMessage
from src.utils.report_exporter import ReportExporter
from src.ml.interview_prep import InterviewPrepModule


class TestEmailService(unittest.TestCase):
    def setUp(self):
        self.service = EmailNotificationService()

    def test_send_notification(self):
        msg = self.service.send_notification(
            "placement_prediction",
            recipient="test@email.com",
            name="John",
            probability=85,
            status="PLACED",
            risk_level="Low Risk",
            suggestions="- Keep it up"
        )
        self.assertIsNotNone(msg)
        self.assertEqual(msg.recipient, "test@email.com")
        self.assertIn("placement", msg.email_type)

    def test_send_placement_prediction(self):
        result = {
            "placed": True,
            "probability_placed": 85.5,
            "risk_level": "Low Risk",
            "suggestions": ["Maintain CGPA", "Practice coding"]
        }
        msg = self.service.send_placement_prediction(
            "Alice", "alice@email.com", result
        )
        self.assertIsNotNone(msg)
        self.assertIn("85.5", msg.body)

    def test_send_resume_analysis(self):
        ats = {
            "overall_score": 78,
            "grade": "B+ (Good)",
            "improvements": ["Add more skills", "Improve formatting"]
        }
        msg = self.service.send_resume_analysis("Bob", "bob@email.com", ats)
        self.assertIsNotNone(msg)
        self.assertIn("78", msg.body)

    def test_send_job_matches(self):
        matches = [
            {"company": "TCS", "overall_match": 85},
            {"company": "Amazon", "overall_match": 62},
        ]
        msg = self.service.send_job_matches("Charlie", "c@email.com", matches)
        self.assertIsNotNone(msg)
        self.assertIn("2", msg.body)

    def test_send_skill_gap_alert(self):
        msg = self.service.send_skill_gap_alert(
            "Diana", "d@email.com", "Software Engineer",
            ["React", "Docker"],
            [{"course": "React Course", "platform": "Udemy"}]
        )
        self.assertIsNotNone(msg)
        self.assertIn("React", msg.body)

    def test_email_count(self):
        self.assertEqual(self.service.get_email_count(), 0)
        self.service.send_notification(
            "placement_prediction",
            recipient="test@email.com",
            name="Test", probability=50,
            status="Not Placed", risk_level="High",
            suggestions="Improve"
        )
        self.assertEqual(self.service.get_email_count(), 1)

    def test_emails_by_type(self):
        self.service.send_notification(
            "placement_prediction",
            recipient="a@b.com", name="A", probability=80,
            status="Placed", risk_level="Low", suggestions=""
        )
        self.service.send_notification(
            "resume_analyzed",
            recipient="b@b.com", name="B",
            ats_score=75, grade="B", skills_count=5, improvements=""
        )
        placement_emails = self.service.get_emails_by_type("placement_prediction")
        self.assertEqual(len(placement_emails), 1)

    def test_sent_emails_log(self):
        self.service.send_notification(
            "placement_prediction",
            recipient="x@y.com", name="X", probability=60,
            status="Not Placed", risk_level="Medium", suggestions=""
        )
        logs = self.service.get_sent_emails()
        self.assertEqual(len(logs), 1)
        self.assertIn("recipient", logs[0])


class TestReportExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = ReportExporter()

    def test_export_placement_report(self):
        predictions = [
            {
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
            }
        ]
        path = self.exporter.export_placement_report_csv(predictions, "test_placement.csv")
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_export_salary_report(self):
        predictions = [
            {
                "features": {"cgpa": 8.5, "department": "CS", "num_technical_skills": 8, "experience_years": 1},
                "result": {"predicted_salary_lpa": 8.5, "predicted_monthly": 70833, "salary_tier": "Good"},
                "timestamp": "2025-06-15"
            }
        ]
        path = self.exporter.export_salary_report_csv(predictions, "test_salary.csv")
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_export_job_matching_csv(self):
        matches = [
            {"company": "TCS", "job_title": "SE", "overall_match": 85, "skill_match": 80,
             "cgpa_match": 100, "min_cgpa_required": 6, "eligibility": "Eligible",
             "salary_range": "3.36-7.0 LPA", "matched_skills": ["Java"], "missing_skills": ["Docker"]}
        ]
        path = self.exporter.export_job_matching_csv(matches, "test_jobs.csv")
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_export_skill_gap_csv(self):
        gap = {
            "match_score": 60,
            "matched_skills": ["Python", "Java"],
            "missing_skills": ["React", "Docker"]
        }
        path = self.exporter.export_skill_gap_csv(gap, "Software Engineer", "test_gap.csv")
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_create_downloadable_csv(self):
        data = [{"name": "Alice", "score": 90}, {"name": "Bob", "score": 85}]
        csv_str = self.exporter.create_downloadable_csv(data, ["name", "score"])
        self.assertIn("Alice", csv_str)
        self.assertIn("90", csv_str)


class TestInterviewPrep(unittest.TestCase):
    def setUp(self):
        self.prep = InterviewPrepModule()

    def test_get_categories(self):
        cats = self.prep.get_all_categories()
        self.assertGreater(len(cats), 0)
        self.assertIn("technical_python", cats)
        self.assertIn("hr_behavioral", cats)

    def test_get_questions_by_category(self):
        questions = self.prep.get_questions_by_category("technical_python")
        self.assertGreater(len(questions), 0)
        self.assertTrue(all(q.category for q in questions))

    def test_filter_by_difficulty(self):
        easy = self.prep.get_questions_by_category("technical_python", difficulty="Easy")
        self.assertTrue(all(q.difficulty == "Easy" for q in easy))

    def test_mixed_quiz(self):
        quiz = self.prep.get_mixed_quiz(count=5)
        self.assertEqual(len(quiz), 5)

    def test_question_formatting(self):
        questions = self.prep.get_questions_by_category("technical_python", count=1)
        formatted = self.prep.format_question(questions[0], 1)
        self.assertIn("Q1", formatted)
        self.assertIn("[", formatted)

    def test_answer_formatting(self):
        questions = self.prep.get_questions_by_category("technical_python", count=1)
        answer = self.prep.format_answer(questions[0])
        self.assertIn("Answer:", answer)
        self.assertIn("Tips", answer)

    def test_difficulty_distribution(self):
        dist = self.prep.get_difficulty_distribution()
        self.assertIn("Easy", dist)
        self.assertIn("Medium", dist)
        self.assertIn("Hard", dist)
        self.assertGreater(sum(dist.values()), 0)

    def test_interview_tips(self):
        tips = self.prep.get_interview_tips("software_engineer")
        self.assertGreater(len(tips), 0)
        self.assertTrue(any("leetcode" in t.lower() or "coding" in t.lower() for t in tips))

    def test_question_count(self):
        counts = self.prep.get_question_count()
        self.assertGreater(len(counts), 0)
        for cat, count in counts.items():
            self.assertGreater(count, 0)

    def test_get_questions_limited(self):
        questions = self.prep.get_questions_by_category("technical_python", count=2)
        self.assertEqual(len(questions), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
