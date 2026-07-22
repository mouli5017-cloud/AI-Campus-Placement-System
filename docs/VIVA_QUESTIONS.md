# Viva Questions and Answers - Campus Placement AI System

---

### Q1: What is the objective of this project?
**Answer:** The objective is to build an AI-powered system that predicts campus placement probability, screens resumes using NLP, calculates ATS scores, performs skill gap analysis, and provides personalized career guidance to students using machine learning and natural language processing techniques.

---

### Q2: What machine learning algorithms are used?
**Answer:** We use an ensemble Voting Classifier combining:
1. **XGBoost** (highest weight) - for gradient boosting predictions
2. **Random Forest** - for bagging-based predictions
3. **Gradient Boosting** - for sequential learning
4. **Logistic Regression** - as a linear baseline

For salary prediction, we use a Voting Regressor with XGBoost, Random Forest, and Gradient Boosting.

---

### Q3: Why did you choose ensemble methods over single models?
**Answer:** Ensemble methods combine multiple models to reduce variance and bias. The Voting Classifier averages predictions from multiple models, which:
- Reduces overfitting compared to individual models
- Improves generalization on unseen data
- Achieves higher accuracy through model diversity
- Provides more robust predictions

---

### Q4: What is the accuracy of your placement prediction model?
**Answer:** The model achieves approximately 87% accuracy on the test set with 5-fold cross-validation. Key metrics:
- Accuracy: ~87%
- Precision: ~85%
- Recall: ~83%
- F1-Score: ~84%
- ROC-AUC: ~90%

---

### Q5: How does the ATS scoring system work?
**Answer:** The ATS (Applicant Tracking System) scoring evaluates resume quality across 10 weighted sections:
1. Contact Information (5%) - email, phone, LinkedIn, GitHub
2. Summary/Objective (8%) - presence and quality
3. Experience (20%) - work history, roles, date ranges
4. Education (12%) - degrees, CGPA, institution
5. Skills (20%) - technical and soft skills count
6. Projects (15%) - project descriptions, technologies
7. Certifications (8%) - professional certifications
8. Achievements (7%) - awards, recognitions
9. Formatting (5%) - length, structure, readability
10. Bonus: keyword match, action verbs, quantifiable metrics

---

### Q6: What is the role of NLP in this project?
**Answer:** NLP is used for:
1. **Resume Parsing** - extracting structured information from PDF resumes
2. **Section Detection** - identifying resume sections using header matching
3. **Skill Extraction** - finding skills using keyword matching against 100+ skills
4. **Contact Extraction** - regex-based email, phone, LinkedIn, GitHub extraction
5. **Text Processing** - cleaning and normalizing resume text

---

### Q7: What is Skill Gap Analysis?
**Answer:** Skill Gap Analysis compares a student's current skills against the skills required for a target role. It:
1. Takes current skills list as input
2. Defines target role skills from predefined templates
3. Computes match percentage using set intersection
4. Identifies missing skills (gaps)
5. Recommends specific courses and platforms for each missing skill

---

### Q8: How does the Job Matching algorithm work?
**Answer:** The job matching algorithm uses a weighted scoring approach:
1. **Skill Match (40%)** - percentage of required skills the student has
2. **CGPA Match (30%)** - eligibility based on minimum CGPA
3. **Backlog Penalty (15%)** - penalty for active backlogs
4. **Experience Bonus (15%)** - bonus for internships and experience

Companies are ranked by overall match score and filtered by eligibility.

---

### Q9: What is the technology stack used?
**Answer:**
- **Frontend:** Streamlit (Python web framework for data apps)
- **Backend:** Python 3.9+
- **ML:** Scikit-learn, XGBoost
- **NLP:** spaCy, NLTK
- **Database:** MySQL with SQLAlchemy ORM
- **Visualization:** Plotly, Matplotlib
- **PDF Parsing:** pdfplumber
- **Deployment:** Streamlit Cloud

---

### Q10: How is the data stored?
**Answer:** Data is stored in MySQL database with SQLAlchemy ORM. Key tables:
- **users** - authentication and role management
- **student_profiles** - student academic and profile data
- **resumes** - uploaded resume data and parsed content
- **job_postings** - company job requirements
- **prediction_history** - all prediction records
- **learning_recommendations** - course recommendations

---

### Q11: What is the difference between classification and regression in this project?
**Answer:**
- **Classification (Placement Prediction):** Predicts a binary outcome (Placed/Not Placed). Uses accuracy, precision, recall, F1-score as metrics.
- **Regression (Salary Prediction):** Predicts a continuous value (salary in LPA). Uses MAE, RMSE, R² score as metrics.

---

### Q12: How does the system handle overfitting?
**Answer:**
1. **Ensemble methods** reduce overfitting through model averaging
2. **Cross-validation** (5-fold) ensures generalization
3. **Train-test split** (80-20) prevents data leakage
4. **Hyperparameter tuning** via GridSearchCV
5. **Synthetic data** with realistic noise injection

---

### Q13: What is the role of XGBoost in this system?
**Answer:** XGBoost (Extreme Gradient Boosting) is the primary model because:
- It handles both numerical and categorical features well
- It has built-in regularization to prevent overfitting
- It handles missing values gracefully
- It provides feature importance for interpretability
- It achieves state-of-the-art performance on tabular data

---

### Q14: How does the resume parser extract skills?
**Answer:** The skill extractor uses a keyword matching approach:
1. Maintains a database of 100+ technical, soft, and domain skills
2. Handles skill aliases (e.g., "ml" -> "machine learning", "js" -> "javascript")
3. Uses regex patterns with word boundaries for accurate matching
4. Categorizes skills into technical, soft, and domain categories
5. Returns deduplicated, canonical skill names

---

### Q15: What are the limitations of the current system?
**Answer:**
1. Uses synthetic dataset (can be replaced with real placement data)
2. Resume parsing may not work perfectly on all PDF formats
3. Skill extraction is keyword-based (can be improved with ML-based NER)
4. No real-time database integration (demo mode uses in-memory data)
5. Limited to English language resumes
6. No email notification integration yet

---

### Q16: How can the system be deployed in production?
**Answer:**
1. **Streamlit Cloud** - for quick deployment with streamlit cloud
2. **Docker** - containerize the application
3. **AWS/GCP** - deploy on cloud with auto-scaling
4. **MySQL** - use production database instead of in-memory
5. **Redis** - for session management and caching
6. **Nginx** - as reverse proxy

---

### Q17: What is the data flow in this system?
**Answer:**
1. Student enters profile data / uploads resume
2. Resume is parsed by pdfplumber to extract text
3. NLP module extracts skills, sections, contact info
4. ATS scorer evaluates resume quality
5. ML models predict placement probability and salary
6. Job matcher finds suitable companies
7. Skill gap analyzer identifies missing skills
8. Learning recommender suggests courses
9. Results displayed on dashboard
10. Prediction saved to history

---

### Q18: What is the difference between the existing and proposed system?
**Answer:**
| Aspect | Existing | Proposed |
|--------|----------|----------|
| Prediction | None | ML-based placement & salary |
| Resume Screening | Manual | Automated NLP + ATS scoring |
| Skill Analysis | Generic | Personalized gap analysis |
| Job Matching | Manual search | AI-powered matching |
| Learning Path | Self-directed | Course recommendations |
| Analytics | Basic Excel | Interactive dashboards |
| Roles | Single | Multi-role (Student, Admin, PO) |

---

### Q19: How would you improve this system further?
**Answer:**
1. Train on real placement data from college records
2. Implement deep learning for better resume understanding
3. Add interview preparation module with mock tests
4. Integrate email notification for job alerts
5. Add real-time chat between students and placement officers
6. Implement multi-language resume support
7. Add gamification elements for student engagement
8. Build mobile app version using React Native
9. Add company review and rating system
10. Implement advanced analytics with predictive trends

---

### Q20: Explain the modular architecture of this system.
**Answer:** The system follows a modular architecture:
```
CampusPlacementAI/
├── config/         - Configuration and constants
├── src/database/   - Database models and connection
├── src/ml/         - Machine learning models (5 modules)
├── src/nlp/        - NLP processing (2 modules)
├── src/utils/      - Helper functions
├── data/           - Datasets and SQL scripts
├── tests/          - Unit tests
└── app.py          - Main Streamlit application
```
Each module is independent with clear interfaces, making the system:
- **Maintainable** - changes in one module don't affect others
- **Testable** - each module can be tested independently
- **Scalable** - new models/features can be added easily
- **Readable** - clear separation of concerns
