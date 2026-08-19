import os
import json
import joblib
import datetime
from typing import Dict, Any, Optional, Tuple

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "models")

class ModelRegistry:
    def __init__(self, storage_dir: str = MODEL_DIR):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_model(
        self,
        model: Any,
        model_name: str,
        model_version: str,
        model_type: str,
        features: list,
        metrics: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> str:
        version_dir = os.path.join(self.storage_dir, model_version)
        os.makedirs(version_dir, exist_ok=True)

        model_filepath = os.path.join(version_dir, f"{model_name}.joblib")
        metadata_filepath = os.path.join(version_dir, "metadata.json")

        joblib.dump(model, model_filepath)

        metadata = {
            "model_name": model_name,
            "model_version": model_version,
            "model_type": model_type,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "features": features,
            "metrics": metrics,
            "parameters": parameters,
            "filepath": model_filepath
        }

        with open(metadata_filepath, "w") as f:
            json.dump(metadata, f, indent=2)

        return version_dir

    def load_model(self, model_version: str) -> Tuple[Any, Dict[str, Any]]:
        version_dir = os.path.join(self.storage_dir, model_version)
        metadata_filepath = os.path.join(version_dir, "metadata.json")

        if not os.path.exists(metadata_filepath):
            raise FileNotFoundError(f"Model version {model_version} metadata not found.")

        with open(metadata_filepath, "r") as f:
            metadata = json.load(f)

        model_filepath = metadata["filepath"]
        model = joblib.load(model_filepath)

        return model, metadata

    def get_active_model_info(self) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.storage_dir):
            return None

        versions = [d for d in os.listdir(self.storage_dir) if os.path.isdir(os.path.join(self.storage_dir, d))]
        if not versions:
            return None

        # Sort by creation / directory name
        versions.sort(reverse=True)
        latest_version = versions[0]
        metadata_path = os.path.join(self.storage_dir, latest_version, "metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                return json.load(f)

        return None

model_registry = ModelRegistry()
