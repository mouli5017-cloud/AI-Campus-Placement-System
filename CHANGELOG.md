# Changelog

All notable changes to the AI Campus Placement System are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2024-01-01

### Added
- **Placement Prediction** — Ensemble ML model (XGBoost + Random Forest + Gradient Boosting + Logistic Regression) predicting placement probability with ~87% accuracy
- **Salary Prediction** — Ensemble regressor estimating salary packages with ~96% R² score
- **Resume Parsing** — PDF/docx parsing with section detection, contact extraction, and structure analysis
- **ATS Scoring** — 10-section weighted scoring system evaluating resume against job requirements (0–100 scale, A–F grading)
- **Skill Extraction** — NLP-based extraction with 123+ technical skills, alias matching, and gap analysis
- **Job Matching** — Profile matching against 24 companies with weighted scoring across skills, CGPA, experience
- **Resume Ranking** — Batch ranking of multiple resumes for placement officer screening
- **Interview Preparation** — 35+ interview questions across 7 categories with difficulty levels, tips, and scoring
- **Email Notifications** — 6 email templates for placement updates, resume results, skill gap alerts
- **Analytics Dashboard** — 10 interactive Plotly charts (placement distribution, salary trends, skill demand, etc.)
- **Report Export** — CSV export for placement, salary, skill gap, and job matching reports
- **Three-Role Dashboards** — Student (8 tabs), Admin (4 tabs), Placement Officer (4 tabs)
- **MySQL Database** — 9 SQLAlchemy tables with full schema and seed data
- **Docker Support** — Dockerfile + docker-compose.yml with MySQL service
- **CI/CD Pipeline** — GitHub Actions workflow with testing, linting, Docker build
- **System Initialization** — Model pre-training, dependency checks, dataset generation
- **Comprehensive Tests** — 82 unit and integration tests

### Technical Details
- Python 3.9+ with Streamlit web framework
- Scikit-learn, XGBoost for ML ensemble models
- spaCy + NLTK for NLP pipeline
- pdfplumber + PyPDF2 for PDF parsing
- SQLAlchemy + PyMySQL for database
- Plotly + Matplotlib + Seaborn for visualizations
- bcrypt for password hashing
