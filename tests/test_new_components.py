"""
Tests for new modules: API, Dashboard, Email Templates, Architecture.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


try:
    import fastapi
    from fastapi.testclient import TestClient
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from src.api.placement_api import HAS_FASTAPI as API_HAS_FASTAPI


@unittest.skipUnless(HAS_FASTAPI and API_HAS_FASTAPI, "FastAPI not installed")
class TestAPIModule(unittest.TestCase):
    """Tests for the REST API module (requires fastapi + httpx)."""

    def setUp(self):
        from src.api.placement_api import app
        self.client = TestClient(app)
        self.app = app

    def test_api_import(self):
        from src.api import placement_app
        self.assertIsNotNone(placement_app)

    def test_api_app_exists(self):
        self.assertIsNotNone(self.app)

    def test_api_has_routes(self):
        routes = [r.path for r in self.app.routes]
        self.assertIn("/", routes)
        self.assertIn("/health", routes)
        self.assertIn("/predict/placement", routes)
        self.assertIn("/analyze/resume", routes)
        self.assertIn("/match/jobs", routes)

    def test_api_root_endpoint(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("message", data)
        self.assertIn("version", data)

    def test_api_health_endpoint(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")

    def test_api_predict_placement(self):
        resp = self.client.post("/predict/placement", json={
            "cgpa": 8.5,
            "skills_count": 8,
            "internships": 2,
            "projects": 4,
            "backlogs": 0,
            "communication_score": 80,
            "experience_months": 12,
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("placed", data)
        self.assertIn("probability", data)
        self.assertIn("risk_level", data)
        self.assertIn("suggestions", data)

    def test_api_analyze_resume(self):
        resp = self.client.post("/analyze/resume", json={
            "text": (
                "John Doe\njohn@email.com\n+91-9876543210\n\n"
                "EDUCATION\nB.Tech CSE, 8.5 CGPA\n\n"
                "SKILLS\nPython, Java, SQL, Machine Learning, TensorFlow\n\n"
                "EXPERIENCE\nSoftware Intern at TCS, Jan 2023 - Jun 2023\n\n"
                "PROJECTS\nResume Screening System using NLP\n"
                "E-Commerce Web Application using React and Node.js"
            ),
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("parsed", data)
        self.assertIn("skills", data)
        self.assertIn("ats_score", data)
        self.assertIsInstance(data["skills"], list)

    def test_api_match_jobs(self):
        resp = self.client.post("/match/jobs", json={
            "cgpa": 8.0,
            "skills": ["Python", "Java", "SQL"],
            "experience_months": 6,
            "preferred_role": "Software Engineer",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("matches", data)
        self.assertIn("total", data)

    def test_api_invalid_prediction(self):
        resp = self.client.post("/predict/placement", json={
            "cgpa": 15,
            "skills_count": -1,
        })
        self.assertIn(resp.status_code, [422, 400])


class TestDashboardModules(unittest.TestCase):
    """Tests for dashboard page modules (import validation only, no Streamlit)."""

    def test_student_dashboard_import(self):
        from src.dashboard.pages.student_dashboard import (
            render_placement_prediction,
            render_resume_analysis,
            render_job_matching,
            render_skill_gap_analysis,
            render_interview_prep,
            render_export_reports,
            render_prediction_history,
        )
        self.assertTrue(callable(render_placement_prediction))
        self.assertTrue(callable(render_resume_analysis))
        self.assertTrue(callable(render_job_matching))
        self.assertTrue(callable(render_skill_gap_analysis))
        self.assertTrue(callable(render_interview_prep))
        self.assertTrue(callable(render_export_reports))
        self.assertTrue(callable(render_prediction_history))

    def test_admin_dashboard_import(self):
        from src.dashboard.pages.admin_dashboard import (
            render_system_overview,
            render_analytics_dashboard,
            render_user_management,
            render_data_management,
        )
        self.assertTrue(callable(render_system_overview))
        self.assertTrue(callable(render_analytics_dashboard))
        self.assertTrue(callable(render_user_management))
        self.assertTrue(callable(render_data_management))

    def test_placement_officer_dashboard_import(self):
        from src.dashboard.pages.placement_officer_dashboard import (
            render_bulk_resume_screening,
            render_placement_drives,
            render_placement_statistics,
            render_student_lookup,
        )
        self.assertTrue(callable(render_bulk_resume_screening))
        self.assertTrue(callable(render_placement_drives))
        self.assertTrue(callable(render_placement_statistics))
        self.assertTrue(callable(render_student_lookup))

    def test_dashboard_package_init(self):
        from src.dashboard import (
            student_dashboard,
            admin_dashboard,
            placement_officer_dashboard,
        )
        self.assertIsNotNone(student_dashboard)
        self.assertIsNotNone(admin_dashboard)
        self.assertIsNotNone(placement_officer_dashboard)


class TestEmailTemplates(unittest.TestCase):
    """Tests for HTML email templates."""

    def test_placement_prediction_template_exists(self):
        path = os.path.join("templates", "placement_prediction.html")
        self.assertTrue(os.path.exists(path))

    def test_resume_analysis_template_exists(self):
        path = os.path.join("templates", "resume_analysis.html")
        self.assertTrue(os.path.exists(path))

    def test_placement_template_has_variables(self):
        path = os.path.join("templates", "placement_prediction.html")
        with open(path, 'r') as f:
            content = f.read()
        self.assertIn("{{ name }}", content)
        self.assertIn("{{ probability }}", content)
        self.assertIn("{{ status }}", content)
        self.assertIn("{{ risk_level }}", content)
        self.assertIn("Campus Placement AI", content)

    def test_resume_template_has_variables(self):
        path = os.path.join("templates", "resume_analysis.html")
        with open(path, 'r') as f:
            content = f.read()
        self.assertIn("{{ name }}", content)
        self.assertIn("{{ ats_score }}", content)
        self.assertIn("{{ grade }}", content)
        self.assertIn("Campus Placement AI", content)

    def test_templates_are_valid_html(self):
        for fname in ["placement_prediction.html", "resume_analysis.html"]:
            path = os.path.join("templates", fname)
            with open(path, 'r') as f:
                content = f.read()
            self.assertTrue(content.startswith("<!DOCTYPE html>"))
            self.assertIn("</html>", content)
            self.assertIn("<head>", content)
            self.assertIn("<body>", content)


class TestProjectConfig(unittest.TestCase):
    """Tests for project configuration files."""

    def test_pyproject_toml_exists(self):
        self.assertTrue(os.path.exists("pyproject.toml"))

    def test_pyproject_has_metadata(self):
        with open("pyproject.toml", 'r') as f:
            content = f.read()
        self.assertIn("campus-placement-ai", content)
        self.assertIn("1.0.0", content)
        self.assertIn("MIT", content)
        self.assertIn("streamlit", content)

    def test_license_exists(self):
        self.assertTrue(os.path.exists("LICENSE"))

    def test_license_is_mit(self):
        with open("LICENSE", 'r') as f:
            content = f.read()
        self.assertIn("MIT License", content)
        self.assertIn("Permission is hereby granted", content)

    def test_changelog_exists(self):
        self.assertTrue(os.path.exists("CHANGELOG.md"))

    def test_changelog_has_version(self):
        with open("CHANGELOG.md", 'r') as f:
            content = f.read()
        self.assertIn("1.0.0", content)
        self.assertIn("Added", content)

    def test_gitignore_exists(self):
        self.assertTrue(os.path.exists(".gitignore"))

    def test_gitignore_covers_common_patterns(self):
        with open(".gitignore", 'r') as f:
            content = f.read()
        self.assertIn("__pycache__/", content)
        self.assertIn("venv/", content)
        self.assertIn(".env", content)
        self.assertIn(".DS_Store", content)

    def test_env_example_exists(self):
        self.assertTrue(os.path.exists(".env.example"))

    def test_env_example_has_required_vars(self):
        with open(".env.example", 'r') as f:
            content = f.read()
        self.assertIn("DB_HOST", content)
        self.assertIn("SECRET_KEY", content)

    def test_streamlit_config_exists(self):
        self.assertTrue(os.path.exists(".streamlit/config.toml"))

    def test_streamlit_config_has_theme(self):
        with open(".streamlit/config.toml", 'r') as f:
            content = f.read()
        self.assertIn("[theme]", content)
        self.assertIn("#1E88E5", content)


class TestCSSStyles(unittest.TestCase):
    """Tests for the custom CSS file."""

    def test_css_file_exists(self):
        self.assertTrue(os.path.exists("static/css/styles.css"))

    def test_css_has_classes(self):
        with open("static/css/styles.css", 'r') as f:
            content = f.read()
        self.assertIn(".metric-card", content)
        self.assertIn(".section-header", content)
        self.assertIn(".success-box", content)
        self.assertIn(".warning-box", content)
        self.assertIn(".danger-box", content)
        self.assertIn(".info-box", content)

    def test_css_targets_streamlit(self):
        with open("static/css/styles.css", 'r') as f:
            content = f.read()
        self.assertIn(".stApp", content)
        self.assertIn("stMetric", content)


if __name__ == "__main__":
    unittest.main()
