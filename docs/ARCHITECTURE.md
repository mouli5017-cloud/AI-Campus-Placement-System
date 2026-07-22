# System Architecture

## Overview

The AI Campus Placement System is a multi-layered application with ML/NLP pipelines, a Streamlit web frontend, optional REST API, and MySQL persistence.

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Streamlit    │  │  REST API    │  │  Email/CSV    │  │
│  │  Dashboard    │  │  (FastAPI)   │  │  Reports      │  │
│  │  app.py       │  │  src/api/    │  │  exporters    │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │
├─────────┼─────────────────┼───────────────────┼─────────┤
│         │          Business Logic Layer       │          │
│  ┌──────┴───────────────────────────────────┴───────┐  │
│  │              src/ml/  &  src/nlp/                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │  │
│  │  │ Placement │ │  Salary  │ │  ATS Scorer      │  │  │
│  │  │ Predictor │ │ Predictor│ │  (10 sections)   │  │  │
│  │  └──────────┘ └──────────┘ └──────────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │  │
│  │  │   Job    │ │ Resume   │ │  Interview Prep  │  │  │
│  │  │ Matcher  │ │ Ranker   │ │  (35+ questions) │  │  │
│  │  └──────────┘ └──────────┘ └──────────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────────────────┐  │  │
│  │  │ Resume Parser│  │ Skill Extractor           │  │  │
│  │  │ (PDF/docx)   │  │ (123+ skills, aliases)   │  │  │
│  │  └──────────────┘  └──────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    Data Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  MySQL   │  │  CSV     │  │  Pickle Models       │  │
│  │  (9 tbl) │  │  Datasets│  │  (.pkl saved_models) │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Module Dependency Graph

```
app.py
├── config.config ────────────── config.py (dataclasses)
├── src.ml.placement_model ──── Ensemble (XGB+RF+GB+LR)
├── src.ml.salary_model ─────── Ensemble Regressor
├── src.ml.ats_scorer ───────── 10-section weighted scorer
├── src.ml.job_matcher ──────── 26-company matching engine
├── src.ml.resume_ranker ────── Batch resume ranking
├── src.ml.interview_prep ───── Question bank + quiz gen
├── src.ml.analytics_engine ─── Plotly chart generators
├── src.nlp.resume_parser ───── PDF/docx text extraction
├── src.nlp.skill_extractor ─── NLP skill identification
├── src.utils.email_service ─── Template-based emails
├── src.utils.report_exporter ─ CSV report generation
├── src.utils.helpers ───────── Password hashing, validation
└── src.database.db_manager ─── SQLAlchemy DB operations
```

## ML Pipeline

### Placement Prediction (`placement_model.py`)
1. Synthetic dataset generation (5000 samples)
2. Feature engineering (14 features)
3. Ensemble voting: XGBoost + Random Forest + Gradient Boosting + Logistic Regression
4. Cross-validation (5-fold)
5. Accuracy: ~87%, F1: ~86%

### Salary Prediction (`salary_model.py`)
1. Synthetic dataset generation (5000 samples)
2. Feature engineering (12 features)
3. Ensemble regressor: XGBoost + Random Forest + Gradient Boosting
4. R² Score: ~96%, MAE: ~0.8 LPA

### ATS Scoring (`ats_scorer.py`)
10 weighted sections:
| Section | Weight | Description |
|---------|--------|-------------|
| Contact Info | 8% | Email, phone, LinkedIn |
| Education | 12% | Degree, CGPA, institution |
| Skills Match | 25% | Target role skill overlap |
| Experience | 15% | Internships, work history |
| Projects | 12% | Project count and quality |
| Certifications | 8% | Professional certifications |
| Achievements | 5% | Awards, publications |
| Formatting | 8% | Structure, sections, length |
| Keywords | 5% | Industry keyword density |
| Recency | 2% | Latest activity relevance |

## NLP Pipeline

1. **Text Extraction**: pdfplumber for PDF, python-docx for DOCX
2. **Section Detection**: Regex-based heading identification
3. **Skill Extraction**: 123+ skills with alias map (e.g., "ML" → "Machine Learning")
4. **Gap Analysis**: Compare extracted skills vs target role requirements

## Database Schema (9 Tables)

```
users ──────────── students ──────── placement_applications
    │                  │                      │
    ├── admin_actions  ├── resume_analyses    ├── company_drives
    │                  │                      │
    └── activity_logs  └── skill_assessments  └── notifications
```

## Deployment

- **Local**: `python setup.py setup` then `python setup.py run`
- **Docker**: `docker-compose up` (includes MySQL)
- **Cloud**: Streamlit Cloud (auto-deploys from GitHub)
- **API**: `uvicorn src.api.placement_api:app --host 0.0.0.0`
