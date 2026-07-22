"""
REST API module for the Campus Placement AI system.
Provides FastAPI endpoints for ML predictions, resume analysis, and job matching.

Install: pip install fastapi uvicorn
Run: uvicorn src.api.placement_api:app --reload
"""

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    from typing import List, Optional, Dict
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

if HAS_FASTAPI:
    app = FastAPI(
        title="Campus Placement AI API",
        description="AI-Powered Placement Prediction and Resume Screening",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class PredictionRequest(BaseModel):
        cgpa: float = Field(..., ge=0, le=10, description="CGPA (0-10)")
        skills_count: int = Field(..., ge=0, description="Number of technical skills")
        internships: int = Field(default=0, ge=0, description="Number of internships")
        projects: int = Field(default=0, ge=0, description="Number of projects")
        backlogs: int = Field(default=0, ge=0, description="Number of active backlogs")
        communication_score: float = Field(default=70.0, ge=0, le=100)
        experience_months: int = Field(default=0, ge=0)

    class PredictionResponse(BaseModel):
        placed: bool
        probability: float
        risk_level: str
        suggestions: List[str]

    class ResumeRequest(BaseModel):
        text: str = Field(..., min_length=50, description="Resume text content")

    class JobMatchRequest(BaseModel):
        cgpa: float = Field(..., ge=0, le=10)
        skills: List[str] = Field(default_factory=list)
        experience_months: int = Field(default=0)
        preferred_role: str = Field(default="")

    @app.get("/")
    def root():
        return {"message": "Campus Placement AI API", "version": "1.0.0"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "models_loaded": True}

    @app.post("/predict/placement", response_model=PredictionResponse)
    def predict_placement(request: PredictionRequest):
        from src.ml.placement_model import PlacementPredictor
        predictor = PlacementPredictor()
        if not predictor.load_model():
            raise HTTPException(status_code=503, detail="Model not loaded. Run initialize.py first.")
        result = predictor.predict_single({
            "cgpa": request.cgpa,
            "technical_skills": request.skills_count,
            "internships": request.internships,
            "projects": request.projects,
            "backlogs": request.backlogs,
            "communication_score": request.communication_score,
            "experience_months": request.experience_months,
        })
        if not result:
            raise HTTPException(status_code=500, detail="Prediction failed")
        return PredictionResponse(
            placed=result.get("placed", False),
            probability=result.get("probability_placed", 0),
            risk_level=result.get("risk_level", "Unknown"),
            suggestions=result.get("suggestions", []),
        )

    @app.post("/analyze/resume")
    def analyze_resume(request: ResumeRequest):
        from src.ml.ats_scorer import ATSScorer
        from src.nlp.skill_extractor import SkillExtractor
        from src.nlp.resume_parser import ResumeParser

        parser = ResumeParser()
        parsed = parser.parse_text(request.text)

        extractor = SkillExtractor()
        skills = extractor.extract_skills(request.text)

        scorer = ATSScorer()
        ats_result = scorer.compute_ats_score(
            resume_text=request.text,
            skill_names=skills,
            experience_years=parsed.experience_years,
        )
        return {
            "parsed": {
                "name": parsed.name,
                "email": parsed.email,
                "phone": parsed.phone,
                "sections": list(parsed.sections.keys()),
                "total_words": parsed.total_words,
            },
            "skills": skills,
            "ats_score": ats_result,
        }

    @app.post("/match/jobs")
    def match_jobs(request: JobMatchRequest):
        from src.ml.job_matcher import JobMatcher
        matcher = JobMatcher()
        profile = {
            "cgpa": request.cgpa,
            "skills": request.skills,
            "experience_months": request.experience_months,
        }
        matches = matcher.match_jobs(profile, top_n=10)
        return {"matches": matches, "total": len(matches)}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)

else:
    app = None
