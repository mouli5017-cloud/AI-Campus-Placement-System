import numpy as np
import pandas as pd
import joblib
import os
import logging
from typing import Dict, List, Tuple, Optional, Any

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    VotingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix, roc_auc_score
)
from xgboost import XGBClassifier

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import config

logger = logging.getLogger(__name__)

NUMERIC_FEATURES = [
    "cgpa", "tenth_percentage", "twelfth_percentage",
    "backlogs", "internships", "num_technical_skills",
    "num_soft_skills", "num_projects", "num_certifications",
    "experience_years", "num_programming_languages",
]

CATEGORICAL_FEATURES = ["department", "gender"]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


class PlacementPredictor:
    def __init__(self):
        self.pipeline = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_metrics = {}
        self.feature_importance = {}
        self.model_path = os.path.join(config.ml.MODEL_PATH, "placement_model.pkl")

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
            "backlogs": np.random.choice(
                [0, 0, 0, 0, 0, 1, 1, 2, 3, 5], n_samples
            ),
            "internships": np.random.choice(
                [0, 0, 0, 1, 1, 1, 2, 2, 3], n_samples
            ),
            "num_technical_skills": np.random.randint(1, 15, n_samples),
            "num_soft_skills": np.random.randint(0, 10, n_samples),
            "num_projects": np.random.randint(0, 8, n_samples),
            "num_certifications": np.random.randint(0, 6, n_samples),
            "experience_years": np.round(
                np.random.uniform(0, 4, n_samples), 1
            ),
            "num_programming_languages": np.random.randint(1, 8, n_samples),
            "department": np.random.choice(departments, n_samples),
            "gender": np.random.choice(genders, n_samples),
        }

        df = pd.DataFrame(data)

        placement_prob = (
            0.25 * (df["cgpa"] / 10.0)
            + 0.10 * (df["tenth_percentage"] / 100.0)
            + 0.08 * (df["twelfth_percentage"] / 100.0)
            - 0.12 * (df["backlogs"] / 5.0)
            + 0.10 * (df["internships"] / 3.0)
            + 0.08 * (df["num_technical_skills"] / 15.0)
            + 0.05 * (df["num_soft_skills"] / 10.0)
            + 0.06 * (df["num_projects"] / 8.0)
            + 0.04 * (df["num_certifications"] / 6.0)
            + 0.06 * (df["experience_years"] / 4.0)
            + 0.08 * (df["num_programming_languages"] / 7.0)
            + 0.05 * (df["department"].apply(
                lambda x: 1.0 if x == "Computer Science" else
                0.8 if x == "Information Technology" else 0.5
            ))
            + np.random.normal(0, 0.08, n_samples)
        )

        df["placed"] = (placement_prob > 0.48).astype(int)

        cs_bonus = df["department"].apply(
            lambda x: 0.15 if x in ["Computer Science", "Information Technology"] else 0
        )
        df.loc[(df["cgpa"] > 8.0) & (cs_bonus > 0), "placed"] = 1
        df.loc[(df["cgpa"] < 6.0) & (df["backlogs"] > 2), "placed"] = 0

        return df

    def train(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        if df is None:
            logger.info("No dataset provided. Creating synthetic dataset...")
            df = self.create_sample_dataset(2000)

        logger.info(f"Training on {len(df)} samples")

        X = df[ALL_FEATURES].copy()
        y = df["placed"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.ml.TEST_SIZE,
            random_state=config.ml.RANDOM_STATE, stratify=y
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERIC_FEATURES),
                ("cat", OneHotEncoder(
                    handle_unknown="ignore", sparse_output=False
                ), CATEGORICAL_FEATURES),
            ]
        )

        xgb_model = XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=config.ml.RANDOM_STATE,
            use_label_encoder=False, eval_metric="logloss"
        )
        rf_model = RandomForestClassifier(
            n_estimators=200, max_depth=10,
            random_state=config.ml.RANDOM_STATE
        )
        gb_model = GradientBoostingClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.1,
            random_state=config.ml.RANDOM_STATE
        )
        lr_model = LogisticRegression(
            max_iter=1000, random_state=config.ml.RANDOM_STATE
        )

        self.pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", VotingClassifier(
                estimators=[
                    ("xgb", xgb_model),
                    ("rf", rf_model),
                    ("gb", gb_model),
                    ("lr", lr_model),
                ],
                voting="soft",
                weights=[3, 2, 2, 1]
            ))
        ])

        self.pipeline.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)[:, 1]

        self.model_metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
            "precision": round(precision_score(y_test, y_pred) * 100, 2),
            "recall": round(recall_score(y_test, y_pred) * 100, 2),
            "f1_score": round(f1_score(y_test, y_pred) * 100, 2),
            "roc_auc": round(roc_auc_score(y_test, y_proba) * 100, 2),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(
                y_test, y_pred, output_dict=True
            ),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

        cv_scores = cross_val_score(
            self.pipeline, X, y, cv=config.ml.CV_FOLDS, scoring="accuracy"
        )
        self.model_metrics["cv_mean_accuracy"] = round(cv_scores.mean() * 100, 2)
        self.model_metrics["cv_std_accuracy"] = round(cv_scores.std() * 100, 2)

        logger.info(f"Model trained. Accuracy: {self.model_metrics['accuracy']}%")
        return self.model_metrics

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        input_df = pd.DataFrame([features])[ALL_FEATURES]
        prediction = self.pipeline.predict(input_df)[0]
        probability = self.pipeline.predict_proba(input_df)[0]

        return {
            "placed": bool(prediction),
            "probability_placed": round(float(probability[1]) * 100, 2),
            "probability_not_placed": round(float(probability[0]) * 100, 2),
            "confidence": round(float(max(probability)) * 100, 2),
            "risk_level": self._get_risk_level(probability[1]),
            "suggestions": self._generate_suggestions(features, probability[1]),
        }

    def _get_risk_level(self, prob: float) -> str:
        if prob >= 0.8:
            return "Low Risk (High Placement Chance)"
        elif prob >= 0.6:
            return "Medium Risk (Good Chance)"
        elif prob >= 0.4:
            return "Moderate Risk (Need Improvement)"
        else:
            return "High Risk (Significant Improvement Needed)"

    def _generate_suggestions(
        self, features: Dict[str, Any], prob: float
    ) -> List[str]:
        suggestions = []
        if features.get("cgpa", 0) < 7.0:
            suggestions.append("Focus on improving CGPA to above 7.0")
        if features.get("backlogs", 0) > 0:
            suggestions.append(
                f"Clear {features['backlogs']} backlogs immediately"
            )
        if features.get("internships", 0) == 0:
            suggestions.append("Gain at least one internship experience")
        if features.get("num_technical_skills", 0) < 5:
            suggestions.append("Learn more technical skills (aim for 5+)")
        if features.get("num_projects", 0) < 2:
            suggestions.append("Work on at least 2-3 academic/personal projects")
        if features.get("num_certifications", 0) < 2:
            suggestions.append("Obtain at least 2 relevant certifications")
        if features.get("num_soft_skills", 0) < 3:
            suggestions.append("Develop soft skills: communication, teamwork")
        if features.get("num_programming_languages", 0) < 3:
            suggestions.append("Learn at least 3 programming languages")
        if prob < 0.5:
            suggestions.append(
                "Consider preparing for aptitude tests and group discussions"
            )
        if not suggestions:
            suggestions.append(
                "You have a good profile! Focus on interview preparation."
            )
        return suggestions

    def save_model(self):
        os.makedirs(config.ml.MODEL_PATH, exist_ok=True)
        joblib.dump({
            "pipeline": self.pipeline,
            "metrics": self.model_metrics,
        }, self.model_path)
        logger.info(f"Model saved to {self.model_path}")

    def load_model(self) -> bool:
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.pipeline = data["pipeline"]
            self.model_metrics = data["metrics"]
            self.is_trained = True
            logger.info("Model loaded successfully")
            return True
        return False
