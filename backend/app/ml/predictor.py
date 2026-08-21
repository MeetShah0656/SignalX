import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from app.ml.model_registry import model_registry
from app.features.pipeline import FEATURE_COLUMNS
from app.core.config import settings
from app.core.logging import logger

class Predictor:
    def __init__(self):
        self._cached_model = None
        self._cached_metadata = None
        self._cached_version = None

    def _get_active_model(self):
        info = model_registry.get_active_model_info()
        if not info:
            return None, None

        version = info["model_version"]
        if self._cached_version != version:
            model, metadata = model_registry.load_model(version)
            self._cached_model = model
            self._cached_metadata = metadata
            self._cached_version = version

        return self._cached_model, self._cached_metadata

    def predict(self, feature_row: pd.Series) -> Dict[str, Any]:
        """
        Run inference on a single feature row.
        Returns probabilities, signal, expected return, and metadata.
        """
        model, metadata = self._get_active_model()
        if not model or not metadata:
            return {
                "status": "MODEL_NOT_TRAINED",
                "signal": "HOLD",
                "buy_probability": 0.0,
                "sell_probability": 0.0,
                "hold_probability": 1.0,
                "expected_return": 0.0,
                "confidence": 0.0,
                "prediction_horizon_minutes": settings.PREDICTION_HORIZON_MINUTES,
                "model_version": "NONE",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "message": "Model not trained. Run training pipeline before enabling AI predictions."
            }

        # Prepare feature vector matching the model's trained schema
        model_features = getattr(model, "feature_names_in_", None)
        if model_features is None or len(model_features) == 0:
            model_features = metadata.get("feature_columns", FEATURE_COLUMNS)
        df_row = pd.DataFrame([feature_row]).reindex(columns=list(model_features), fill_value=0.0)

        probs = model.predict_proba(df_row)[0]
        classes = list(model.classes_)

        prob_dict = {}
        for cls, p in zip(classes, probs):
            # Class can be -1, 0, 1 or encoded 0, 1, 2
            prob_dict[int(cls)] = float(p)

        # Mapping for 1 (BUY), -1 (SELL), 0 (HOLD)
        buy_prob = prob_dict.get(1, 0.0)
        sell_prob = prob_dict.get(-1, 0.0)
        hold_prob = prob_dict.get(0, 0.0)

        # Fallback if binary/encoded classes present
        if buy_prob == 0.0 and sell_prob == 0.0 and len(probs) > 0:
            if len(probs) == 3:
                sell_prob = float(probs[0])
                hold_prob = float(probs[1])
                buy_prob = float(probs[2])
            elif len(probs) == 2:
                buy_prob = float(probs[1])
                sell_prob = float(probs[0])
                hold_prob = 1.0 - (buy_prob + sell_prob)

        # Generate Signal based on threshold
        if buy_prob >= settings.BUY_THRESHOLD:
            signal = "BUY"
            confidence = buy_prob
            expected_return = round(0.0042 * (buy_prob / settings.BUY_THRESHOLD), 4)  # Estimated positive move
        elif sell_prob >= settings.SELL_THRESHOLD:
            signal = "SELL"
            confidence = sell_prob
            expected_return = round(-0.0042 * (sell_prob / settings.SELL_THRESHOLD), 4) # Estimated negative move
        else:
            signal = "HOLD"
            confidence = hold_prob
            expected_return = 0.0

        return {
            "status": "SUCCESS",
            "signal": signal,
            "buy_probability": round(buy_prob, 4),
            "sell_probability": round(sell_prob, 4),
            "hold_probability": round(hold_prob, 4),
            "expected_return": expected_return,
            "confidence": round(confidence, 4),
            "prediction_horizon_minutes": settings.PREDICTION_HORIZON_MINUTES,
            "model_name": metadata.get("model_name", "Unknown"),
            "model_version": metadata.get("model_version", "v1"),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

predictor = Predictor()
