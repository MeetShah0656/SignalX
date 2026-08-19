import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from app.features.pipeline import FEATURE_COLUMNS, prepare_train_test_sets
from app.ml.model_registry import model_registry
from app.core.logging import logger

from sklearn.preprocessing import LabelEncoder

def train_and_evaluate_models(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Train LogisticRegression, RandomForest, and XGBoost models on historical features.
    Select the model with highest F1 score on validation set, evaluate on test set,
    and save to model registry.
    """
    train_df, val_df, test_df = prepare_train_test_sets(df)

    if len(train_df) < 50:
        raise ValueError(f"Insufficient historical data for training (got {len(train_df)} rows, minimum 50 required).")

    X_train, y_train = train_df[FEATURE_COLUMNS], train_df['target'].astype(int)
    X_val, y_val = val_df[FEATURE_COLUMNS], val_df['target'].astype(int)
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df['target'].astype(int)

    le = LabelEncoder()
    y_train_xgb = le.fit_transform(y_train)
    y_val_xgb = le.transform(y_val)
    y_test_xgb = le.transform(y_test)

    candidates = {
        "xgboost": XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.05,
            random_state=42,
            eval_metric="mlogloss"
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42
        ),
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    }

    best_score = -1.0
    best_name = ""
    best_model = None
    results = {}

    for name, model in candidates.items():
        try:
            if name == "xgboost":
                model.fit(X_train, y_train_xgb)
                y_val_pred = model.predict(X_val)
                val_f1 = f1_score(y_val_xgb, y_val_pred, average="macro", zero_division=0)
            else:
                model.fit(X_train, y_train)
                y_val_pred = model.predict(X_val)
                val_f1 = f1_score(y_val, y_val_pred, average="macro", zero_division=0)

            results[name] = val_f1
            logger.info(f"Model {name} Validation Macro F1: {val_f1:.4f}")

            if val_f1 > best_score:
                best_score = val_f1
                best_name = name
                best_model = model
        except Exception as e:
            logger.warning(f"Skipping candidate model {name} due to training error: {e}")

    # Evaluate best model on test set
    if best_name == "xgboost":
        y_test_pred = best_model.predict(X_test)
        y_test_eval = y_test_xgb
    else:
        y_test_pred = best_model.predict(X_test)
        y_test_eval = y_test

    acc = accuracy_score(y_test_eval, y_test_pred)
    prec = precision_score(y_test_eval, y_test_pred, average="macro", zero_division=0)
    rec = recall_score(y_test_eval, y_test_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test_eval, y_test_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_test_eval, y_test_pred).tolist()

    # Feature Importance if available
    feature_importance = {}
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
        for feat, imp in zip(FEATURE_COLUMNS, importances):
            feature_importance[feat] = round(float(imp), 4)

    timestamp_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    model_version = f"{best_name}_v_{timestamp_str}"

    metrics = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm,
        "validation_scores": results,
        "feature_importance": feature_importance,
        "train_samples": len(train_df),
        "test_samples": len(test_df)
    }

    parameters = {
        "prediction_horizon_minutes": 15,
        "timeframe": "5m",
        "random_seed": 42
    }

    registry_path = model_registry.save_model(
        model=best_model,
        model_name=best_name,
        model_version=model_version,
        model_type=best_name.upper(),
        features=FEATURE_COLUMNS,
        metrics=metrics,
        parameters=parameters
    )

    logger.info(f"Saved best model {model_version} to {registry_path} with test F1: {f1:.4f}")

    return {
        "model_name": best_name,
        "model_version": model_version,
        "metrics": metrics,
        "parameters": parameters
    }
