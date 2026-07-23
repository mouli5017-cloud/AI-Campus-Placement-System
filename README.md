<<<<<<< HEAD
# AI Campus Placement Prediction & Resume Screening System

A comprehensive machine learning-based system for campus placement prediction, resume screening, ATS scoring, skill gap analysis, job matching, and interview preparation. Built as a final-year B.E. Computer Science project.

## Features

| Module | Description |
|--------|-------------|
| **Placement Prediction** | Ensemble ML model (XGBoost + RF + GB + LR) with ~87% accuracy |
| **Salary Prediction** | Ensemble regressor estimating salary packages (~96% R²) |
| **Resume ATS Scoring** | 10-section weighted scoring (0–100, A–F grade) |
| **Skill Extraction** | NLP-based extraction with 123+ skills and alias matching |
| **Job Matching** | Profile matching against 24 companies with weighted scoring |
| **Resume Ranking** | Batch ranking for placement officer bulk screening |
| **Interview Prep** | 35+ questions across 7 categories with tips and quizzes |
| **Skill Gap Analysis** | Compare current skills vs target role requirements |
| **Email Notifications** | 6 template-based email types for alerts and updates |
| **Analytics Dashboard** | 10 interactive Plotly charts for data visualization |
| **Report Export** | CSV export for placement, salary, skill gap, job matching |
| **REST API** | FastAPI endpoints (optional, for headless integration) |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.31+ |
| Backend | Python 3.9+ |
| ML Ensemble | XGBoost, Scikit-learn (Random Forest, Gradient Boosting, Logistic Regression) |
| NLP | spaCy, NLTK, pdfplumber, PyPDF2, python-docx |
| Database | MySQL (SQLAlchemy ORM, PyMySQL) |
| Visualization | Plotly, Matplotlib, Seaborn |
| API | FastAPI (optional) |
| Deployment | Docker, Streamlit Cloud |
| Testing | pytest |

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/campus-placement-ai.git
cd campus-placement-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm

# Initialize system (generate datasets + train models)
python initialize.py

# Run application
streamlit run app.py
```

The app opens at `http://localhost:8501`. Use **Demo Login** on any role tab for quick access.

### Docker Setup

```bash
docker-compose up
```

Includes MySQL service with automatic schema initialization.

## Project Structure

```
CampusPlacementAI/
├── app.py                              # Main Streamlit app (1248 lines, 3 role dashboards)
├── initialize.py                       # System init: health check + model pre-training
├── setup.py                            # CLI setup/run/test helper
├── pyproject.toml                      # Modern Python packaging + tool config
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Container build
├── docker-compose.yml                  # Multi-service Docker (app + MySQL)
│
├── config/
│   ├── config.py                       # App config, 24 companies, 123+ skills
│   └── logging_config.py              # Rotating file log handlers
│
├── src/
│   ├── ml/
│   │   ├── placement_model.py          # Ensemble placement predictor (~87% acc)
│   │   ├── salary_model.py             # Ensemble salary regressor (~96% R²)
│   │   ├── ats_scorer.py               # 10-section ATS scoring engine
│   │   ├── job_matcher.py              # 26-company matching with weighted scoring
│   │   ├── resume_ranker.py            # Batch resume ranking
│   │   ├── interview_prep.py           # 35+ questions, quiz generation
│   │   └── analytics_engine.py         # 10 Plotly chart generators
│   ├── nlp/
│   │   ├── resume_parser.py            # PDF/docx parsing, section detection
│   │   └── skill_extractor.py          # 123+ skills, aliases, gap analysis
│   ├── utils/
│   │   ├── helpers.py                  # Password hashing, validation, formatting
│   │   ├── email_service.py            # 6 email templates, notification service
│   │   └── report_exporter.py          # CSV export for all report types
│   ├── database/
│   │   ├── db_manager.py               # SQLAlchemy connection manager
│   │   └── models.py                   # 9 database tables
│   ├── api/
│   │   └── placement_api.py            # FastAPI REST endpoints (optional)
│   └── dashboard/
│       └── pages/
│           ├── student_dashboard.py    # Modular student page components
│           ├── admin_dashboard.py      # Modular admin page components
│           └── placement_officer_dashboard.py
│
├── data/
│   ├── database_init.sql               # MySQL schema + seed data (24 companies)
│   ├── generate_datasets.py            # Synthetic data generation
│   └── datasets/                       # Generated CSVs (5000 samples each)
│
├── tests/
│   ├── test_models.py                  # 26 unit tests (ML, NLP, helpers)
│   ├── test_new_modules.py             # 23 tests (email, reports, interview prep)
│   ├── test_integration.py             # 33 end-to-end workflow tests
│   └── test_new_components.py          # 33 tests (API, dashboard, templates, config)
│
├── templates/
│   ├── placement_prediction.html       # HTML email template
│   └── resume_analysis.html            # HTML email template
│
├── static/css/styles.css               # Streamlit custom styling
├── .streamlit/config.toml              # Streamlit theme + server config
├── .github/workflows/ci.yml            # GitHub Actions CI/CD pipeline
│
├── docs/
│   ├── ARCHITECTURE.md                 # System architecture diagrams
│   ├── PROJECT_DOCUMENTATION.md        # Full project documentation
│   ├── IEEE_PAPER.md                   # IEEE-format research paper
│   ├── PPT_CONTENT.md                  # 25-slide presentation content
│   └── VIVA_QUESTIONS.md              # 20 viva Q&A pairs
│
├── LICENSE                             # MIT License
├── README.md                           # This file
├── CHANGELOG.md                        # Version history
└── CONTRIBUTING.md                     # Development guide
```

## Usage

### Student Dashboard (8 tabs)
- **Predictions** — Enter academic profile, get placement probability
- **Resume Analysis** — Upload PDF/paste text, get ATS score and improvements
- **Job Matching** — Find matching companies based on skills and CGPA
- **Skill Gap** — Identify missing skills for target role
- **Learning Path** — Personalized course recommendations
- **Interview Prep** — Practice questions by category and difficulty
- **Export & Reports** — Download CSV reports
- **History** — View all past predictions and analyses

### Admin Dashboard (4 tabs)
- **System Overview** — Model status, user counts, system health
- **Analytics** — 10 interactive charts (placement trends, salary distribution, etc.)
- **User Management** — View users, system configuration
- **Data Management** — Datasets, trained models, application logs

### Placement Officer Dashboard (4 tabs)
- **Bulk Resume Screening** — Upload multiple PDFs, get ranked list
- **Placement Drives** — Manage upcoming company drives
- **Placement Statistics** — Branch-wise placement data and charts
- **Student Lookup** — Search and view student profiles

## Model Performance

| Model | Metric | Score |
|-------|--------|-------|
| Placement Prediction | Accuracy | ~87% |
| Placement Prediction | F1 Score | ~86% |
| Salary Prediction | R² Score | ~96% |
| Salary Prediction | MAE | ~0.8 LPA |
| ATS Scoring | Sections | 10 weighted categories |

## Testing

```bash
# Run all tests (106 passing, 9 skipped without FastAPI)
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src

# Run specific test file
python -m pytest tests/test_models.py -v
```

## Optional: REST API

```bash
# Install API dependencies
pip install fastapi uvicorn

# Start API server
uvicorn src.api.placement_api:app --reload

# Endpoints:
# GET  /                    — API info
# GET  /health              — Health check
# POST /predict/placement   — Placement prediction
# POST /analyze/resume      — Resume ATS analysis
# POST /match/jobs          — Job matching
```

## License

MIT License — see [LICENSE](LICENSE) for details.
=======
# AI-Campus-Placement-System
AI-powered platform for placement prediction, resume screening, and career guidance, using Python and Streamlit.
>>>>>>> 48a70f9e928c81dd1ce6ed612581a4b1a017e72e
