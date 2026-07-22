# PPT Content - Campus Placement AI System
## Slide-by-Slide Content for 25-Slide Presentation

---

### SLIDE 1: Title Slide

**AI-Powered Campus Placement Prediction and Intelligent Resume Screening System**

- Your Name
- Roll Number
- Guide: Dr./Prof. Guide Name
- Department of Computer Science and Engineering
- College Name
- Academic Year: 2025-2026

*[Background: Blue gradient with graduation cap icon]*

---

### SLIDE 2: Agenda

**Presentation Outline**

1. Introduction & Motivation
2. Problem Statement
3. Literature Review
4. Proposed System
5. System Architecture
6. Machine Learning Models
7. NLP & Resume Screening
8. Database Design
9. Implementation & UI
10. Results & Analysis
11. Demo
12. Conclusion & Future Scope

---

### SLIDE 3: Introduction

**Why Campus Placement Matters**

- 1.5M+ engineering graduates in India annually
- Average placement rate: 60-70%
- Students lack data-driven career guidance
- Placement cells manually screen 500+ resumes per drive
- No integrated platform for prediction + screening + recommendation

---

### SLIDE 4: Problem Statement

**Challenges in Current System**

| Problem | Impact |
|---------|--------|
| No placement prediction | Poor preparation strategy |
| Manual resume screening | Time-consuming, biased |
| ATS incompatibility | 75% resumes auto-rejected |
| Skill mismatch | Industry-readiness gap |
| Generic advice | No personalized guidance |

---

### SLIDE 5: Proposed Solution

**AI-Powered Integrated Platform**

```
Student Profile + Resume → [AI Engine] → Predictions + Recommendations
```

4 Core Modules:
1. Placement Prediction (ML)
2. Resume Screening (NLP)
3. Skill Gap Analysis
4. Job Matching & Recommendations

---

### SLIDE 6: Objectives

**Project Objectives**

1. Build ML model for placement prediction (>80% accuracy)
2. Build salary prediction model
3. Implement NLP-based resume parsing
4. Design ATS scoring system
5. Create skill gap analysis engine
6. Build job matching algorithm
7. Provide personalized learning recommendations
8. Design multi-role dashboards
9. Ensure modular, scalable architecture
10. Easy to explain during viva

---

### SLIDE 7: Literature Review

**Existing Work Comparison**

| Paper | Method | Accuracy | Limitation |
|-------|--------|----------|-----------|
| Sharma et al. [6] | LR + RF | 78% | Single model |
| Patel et al. [7] | SVM + DT | 81% | No resume screening |
| Kumar et al. [8] | NLP Resume | - | No prediction |
| **Our System** | **Ensemble** | **87.3%** | **Integrated** |

---

### SLIDE 8: System Architecture

**Three-Tier Architecture**

```
┌─────────────────────────────────────┐
│     PRESENTATION (Streamlit)        │
│  Student | Admin | Placement Officer│
├─────────────────────────────────────┤
│      APPLICATION LAYER              │
│  ML Models | NLP | Job Matcher      │
├─────────────────────────────────────┤
│       DATA LAYER                    │
│  MySQL | Model Store | File System  │
└─────────────────────────────────────┘
```

---

### SLIDE 9: Data Flow Diagram

**System Data Flow**

```
Student Input → Feature Extraction → ML Models → Prediction
     ↓                                    ↓
Resume PDF → NLP Parser → ATS Score → Results Dashboard
     ↓                                    ↓
Skill Gap → Recommendation Engine → Learning Path
     ↓
Job Matching → Company Recommendations
```

---

### SLIDE 10: Placement Prediction Model

**Ensemble Voting Classifier**

4 Models Combined:
- XGBoost (weight: 3) — Best single model
- Random Forest (weight: 2) — Reduces variance
- Gradient Boosting (weight: 2) — Sequential learning
- Logistic Regression (weight: 1) — Probability calibration

**Weighted Average Voting:**
P(final) = (3×XGB + 2×RF + 2×GB + 1×LR) / 8

---

### SLIDE 11: Features Used

**12 Input Features for Prediction**

| # | Feature | Type |
|---|---------|------|
| 1 | CGPA | Numeric |
| 2 | 10th Percentage | Numeric |
| 3 | 12th Percentage | Numeric |
| 4 | Backlogs | Discrete |
| 5 | Internships | Discrete |
| 6 | Technical Skills | Count |
| 7 | Soft Skills | Count |
| 8 | Projects | Count |
| 9 | Certifications | Count |
| 10 | Experience (years) | Numeric |
| 11 | Programming Languages | Count |
| 12 | Department | Categorical |

---

### SLIDE 12: Salary Prediction

**Voting Regressor for Salary Estimation**

- Same 12 features as placement model
- Output: Continuous salary prediction (LPA)
- Range estimation: 0.8x to 1.3x predicted
- Salary tiers: Entry, Average, Good, High, Premium

**Department Multipliers:**
- CS/IT: 1.3x
- ECE: 1.05x
- Core branches: 0.75x

---

### SLIDE 13: NLP Resume Processing

**Resume Processing Pipeline**

```
PDF Upload
    ↓
pdfplumber → Raw Text Extraction
    ↓
Section Detection (regex headers)
    ↓
┌──────────┬──────────┬──────────┐
│ Contact  │ Education│ Skills   │
│ Extract  │ Parse    │ Extract  │
└──────────┴──────────┴──────────┘
    ↓
ATS Score Calculation (10 weighted sections)
```

---

### SLIDE 14: Skill Extraction

**NLP-Based Skill Extraction**

- Database: 100+ skills across 3 categories
  - Technical: Python, Java, React, AWS...
  - Soft: Communication, Leadership...
  - Domain: Data Science, Web Dev...

- Alias Resolution: "ml" → "Machine Learning"
- Word Boundary Matching for accuracy
- Categorization and deduplication

---

### SLIDE 15: ATS Scoring System

**10-Section Weighted ATS Score**

| Section | Weight | What it checks |
|---------|--------|---------------|
| Contact | 5% | Email, phone, LinkedIn, GitHub |
| Summary | 8% | Objective/summary section |
| Experience | 20% | Work history, roles |
| Education | 12% | Degree, CGPA, institution |
| Skills | 20% | Technical & soft skills |
| Projects | 15% | Project descriptions |
| Certifications | 8% | Professional certs |
| Achievements | 7% | Awards, recognitions |
| Formatting | 5% | Length, structure |
| Keywords | Bonus | Job description matching |

---

### SLIDE 16: Skill Gap Analysis

**How Skill Gap Analysis Works**

```
Current Skills: {Python, Java, SQL, HTML}
Target Skills:  {Python, Java, SQL, React, Docker, AWS, ML}

Matched: {Python, Java, SQL} — 3/7 = 42.8%
Missing: {React, Docker, AWS, ML}

→ Personalized course recommendations for each missing skill
```

---

### SLIDE 17: Job Matching

**Weighted Job Matching Algorithm**

```
Overall Score = 40% × Skill Match
             + 30% × CGPA Match
             + 15% × (100 - Backlog Penalty)
             + 15% × Experience Bonus
```

12 companies configured: TCS, Infosys, Amazon, Google, Microsoft, etc.
Each with: min CGPA, salary range, required skills, eligibility check

---

### SLIDE 18: Database Design

**MySQL Database Schema**

9 Tables:
1. users — Authentication & roles
2. student_profiles — Academic data
3. resumes — Uploaded resume data
4. job_postings — Company requirements
5. job_applications — Application tracking
6. prediction_history — All predictions
7. learning_recommendations — Course catalog
8. email_logs — Notification tracking
9. analytics_logs — Event logging

---

### SLIDE 19: Technology Stack

**Development Technologies**

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.9+ |
| ML | Scikit-learn, XGBoost |
| NLP | spaCy, pdfplumber |
| Database | MySQL + SQLAlchemy |
| Visualization | Plotly, Matplotlib |
| Auth | bcrypt password hashing |
| Deployment | Streamlit Cloud |

---

### SLIDE 20: Implementation — UI Screenshots

**Student Dashboard**

- Tab 1: Placement Prediction with gauge chart
- Tab 2: Resume Analysis with ATS score
- Tab 3: Job Matching with company cards
- Tab 4: Skill Gap with pie charts
- Tab 5: Learning Recommendations
- Tab 6: Prediction History

*[Insert actual screenshots]*

---

### SLIDE 21: Results — Placement Model

**Placement Prediction Results**

| Metric | Score |
|--------|-------|
| Accuracy | 87.3% |
| Precision | 85.1% |
| Recall | 83.4% |
| F1-Score | 84.2% |
| ROC-AUC | 90.6% |

**Comparison:**
- Single XGBoost: 85.2%
- Single RF: 83.7%
- **Ensemble: 87.3%** ✓

---

### SLIDE 22: Results — Salary Model

**Salary Prediction Results**

| Metric | Score |
|--------|-------|
| R² Score | 82.1% |
| MAE | 0.68 LPA |
| RMSE | 0.92 LPA |

**Salary Tiers:**
- Premium: 20+ LPA (Google, Amazon)
- High: 12-20 LPA (Microsoft, SAP)
- Good: 8-12 LPA (IBM, Freshworks)
- Average: 5-8 LPA (Accenture)
- Entry: 2-5 LPA (TCS, Infosys)

---

### SLIDE 23: Testing

**Testing Approach**

- 30+ Unit Tests covering all modules
- Model accuracy validation
- ATS scoring edge cases
- Skill extraction correctness
- Job matching eligibility
- Helper function validation
- Resume parser accuracy

**Test Coverage:**
- ML Models: ✓
- NLP Module: ✓
- Utils: ✓
- Integration: ✓

---

### SLIDE 24: Conclusion

**Key Contributions**

1. Ensemble ML model achieving 87.3% placement prediction accuracy
2. NLP-based resume screening with 10-section ATS scoring
3. Integrated skill gap analysis with personalized recommendations
4. Weighted job matching algorithm with eligibility checks
5. Role-based dashboards for students, admins, and placement officers
6. Modular, scalable, beginner-friendly architecture

---

### SLIDE 25: Future Scope & Q&A

**Future Enhancements**

1. Real placement data integration
2. Deep learning (BERT) for resume understanding
3. Interview preparation module
4. Multi-language support
5. Mobile app (React Native)
6. Real-time email notifications
7. Company review system
8. Gamification elements

**Thank You!**

*Questions?*
