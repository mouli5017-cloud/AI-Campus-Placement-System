import numpy as np
import pandas as pd
import joblib
import os
import logging
from typing import Dict, Any, List

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
)
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score
)
from xgboost import XGBRegressor

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import config

logger = logging.getLogger(__name__)

NUMERIC_FEATURES_SALARY = [
    "cgpa", "tenth_percentage", "twelfth_percentage",
    "backlogs", "internships", "num_technical_skills",
    "num_soft_skills", "num_projects", "num_certifications",
    "experience_years", "num_programming_languages",
]

CATEGORICAL_FEATURES_SALARY = ["department", "gender"]

ALL_FEATURES_SALARY = NUMERIC_FEATURES_SALARY + CATEGORICAL_FEATURES_SALARY


class SalaryPredictor:
    def __init__(self):
        self.pipeline = None
        self.is_trained = False
        self.model_metrics = {}
        self.model_path = os.path.join(config.ml.MODEL_PATH, "salary_model.pkl")

    def create_sample_dataset(self, n_samples: int = 2000) -> pd.DataFrame:
        np.random.seed(config.ml.RANDOM_STATE)

        departments = [
            "Computer Science", "Information Technology",
            "Electronics", "Mechanical", "Civil",
            "Electrical", "Chemical"
        ]
        genders = ["Male", "Female"]

        data = {
            "cgpa": np.round(np.random.uniform(5.0, 10.0, n_samples), 2),
            "tenth_percentage": np.round(np.random.uniform(55.0, 99.0, n_samples), 2),
            "twelfth_percentage": np.round(np.random.uniform(50.0, 98.0, n_samples), 2),
            "backlogs": np.random.choice([0, 0, 0, 0, 0, 1, 1, 2, 3, 5], n_samples),
            "internships": np.random.choice([0, 0, 0, 1, 1, 1, 2, 2, 3], n_samples),
            "num_technical_skills": np.random.randint(1, 15, n_samples),
            "num_soft_skills": np.random.randint(0, 10, n_samples),
            "num_projects": np.random.randint(0, 8, n_samples),
            "num_certifications": np.random.randint(0, 6, n_samples),
            "experience_years": np.round(np.random.uniform(0, 4, n_samples), 1),
            "num_programming_languages": np.random.randint(1, 8, n_samples),
            "department": np.random.choice(departments, n_samples),
            "gender": np.random.choice(genders, n_samples),
        }

        df = pd.DataFrame(data)

        dept_mult = df["department"].apply(
            lambda x: 1.3 if x in ["Computer Science", "Information Technology"]
            else 1.0 if x == "Electronics" else 0.75
        )

        salary = (
            2.5
            + 0.8 * df["cgpa"]
            + 0.01 * df["tenth_percentage"]
            + 0.01 * df["twelfth_percentage"]
            - 0.3 * df["backlogs"]
            + 0.5 * df["internships"]
            + 0.1 * df["num_technical_skills"]
            + 0.05 * df["num_soft_skills"]
            + 0.15 * df["num_projects"]
            + 0.1 * df["num_certifications"]
            + 0.4 * df["experience_years"]
            + 0.15 * df["num_programming_languages"]
        ) * dept_mult + np.random.normal(0, 0.5, n_samples)

        df["salary_lpa"] = np.round(np.clip(salary, 2.0, 45.0), 2)

        return df

    def train(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        if df is None:
            logger.info("Creating synthetic salary dataset...")
            df = self.create_sample_dataset(2000)

        X = df[ALL_FEATURES_SALARY].copy()
        y = df["salary_lpa"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.ml.TEST_SIZE, random_state=config.ml.RANDOM_STATE
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERIC_FEATURES_SALARY),
                ("cat", OneHotEncoder(
                    handle_unknown="ignore", sparse_output=False
                ), CATEGORICAL_FEATURES_SALARY),
            ]
        )

        xgb_reg = XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=config.ml.RANDOM_STATE
        )
        rf_reg = RandomForestRegressor(
            n_estimators=200, max_depth=10, random_state=config.ml.RANDOM_STATE
        )
        gb_reg = GradientBoostingRegressor(
            n_estimators=150, max_depth=5, learning_rate=0.1,
            random_state=config.ml.RANDOM_STATE
        )

        self.pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", VotingRegressor(
                estimators=[
                    ("xgb", xgb_reg),
                    ("rf", rf_reg),
                    ("gb", gb_reg),
                ],
                weights=[3, 2, 2]
            ))
        ])

        self.pipeline.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.pipeline.predict(X_test)

        self.model_metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 2),
            "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
            "r2_score": round(r2_score(y_test, y_pred) * 100, 2),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

        cv_scores = cross_val_score(
            self.pipeline, X, y, cv=config.ml.CV_FOLDS, scoring="r2"
        )
        self.model_metrics["cv_mean_r2"] = round(cv_scores.mean() * 100, 2)
        self.model_metrics["cv_std_r2"] = round(cv_scores.std() * 100, 2)

        logger.info(f"Salary model trained. R2: {self.model_metrics['r2_score']}%")
        return self.model_metrics

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_trained:
            raise RuntimeError("Model not trained.")

        input_df = pd.DataFrame([features])[ALL_FEATURES_SALARY]
        predicted_salary = float(self.pipeline.predict(input_df)[0])
        predicted_salary = round(max(2.0, predicted_salary), 2)

        return {
            "predicted_salary_lpa": predicted_salary,
            "predicted_monthly": round(predicted_salary * 100000 / 12, 0),
            "salary_range": {
                "min": round(max(2.0, predicted_salary * 0.8), 2),
                "max": round(predicted_salary * 1.3, 2),
            },
            "salary_tier": self._get_salary_tier(predicted_salary),
            "improvement_tips": self._get_improvement_tips(features),
        }

    def _get_salary_tier(self, salary: float) -> str:
        if salary >= 20.0:
            return "Premium (20+ LPA) - Top Product Companies"
        elif salary >= 12.0:
            return "High (12-20 LPA) - MNCs & Product Companies"
        elif salary >= 8.0:
            return "Good (8-12 LPA) - Good MNCs"
        elif salary >= 5.0:
            return "Average (5-8 LPA) - Service Companies"
        else:
            return "Entry Level (2-5 LPA) - Startups & Service Companies"

    def _get_improvement_tips(self, features: Dict[str, Any]) -> List[str]:
        tips = []
        if features.get("cgpa", 0) < 8.0:
            tips.append("Improving CGPA above 8.0 can increase salary by 15-20%")
        if features.get("num_certifications", 0) < 3:
            tips.append("AWS/Azure/GCP certifications can boost salary significantly")
        if features.get("internships", 0) < 2:
            tips.append("Multiple internships demonstrate practical experience")
        if features.get("experience_years", 0) < 1:
            tips.append("Even 6 months of experience can improve starting salary")
        if not tips:
            tips.append("Your profile is strong! Target product companies.")
        return tips

    def save_model(self):
        os.makedirs(config.ml.MODEL_PATH, exist_ok=True)
        joblib.dump({
            "pipeline": self.pipeline,
            "metrics": self.model_metrics,
        }, self.model_path)
        logger.info(f"Salary model saved to {self.model_path}")

    def load_model(self) -> bool:
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.pipeline = data["pipeline"]
            self.model_metrics = data["metrics"]
            self.is_trained = True
            return True
        return False
