import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


DEFAULT_MODEL_DIR = Path(__file__).resolve().parent / "models"


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer, got {raw_value!r}") from error


def _read_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} must be a number, got {raw_value!r}") from error


@dataclass(frozen=True)
class TrainingConfig:
    output_dir: Path = DEFAULT_MODEL_DIR
    n_estimators: int = 100
    test_size: float = 0.3
    random_state: int = 42
    model_version: str = "1.0.0"

    def __post_init__(self) -> None:
        if self.n_estimators < 1:
            raise ValueError("N_ESTIMATORS must be at least 1")
        if not 0 < self.test_size < 1:
            raise ValueError("TEST_SIZE must be greater than 0 and less than 1")
        if not self.model_version.strip():
            raise ValueError("MODEL_VERSION must not be empty")

    @classmethod
    def from_env(cls) -> "TrainingConfig":
        return cls(
            output_dir=Path(os.getenv("MODEL_DIR", str(DEFAULT_MODEL_DIR))),
            n_estimators=_read_int("N_ESTIMATORS", 100),
            test_size=_read_float("TEST_SIZE", 0.3),
            random_state=_read_int("RANDOM_STATE", 42),
            model_version=os.getenv("MODEL_VERSION", "1.0.0"),
        )


def train_model(config: TrainingConfig | None = None) -> dict:
    config = config or TrainingConfig.from_env()
    config.output_dir.mkdir(parents=True, exist_ok=True)

    iris = load_iris()
    x_train, x_test, y_train, y_test = train_test_split(
        iris.data,
        iris.target,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=iris.target,
    )

    model = RandomForestClassifier(
        n_estimators=config.n_estimators,
        random_state=config.random_state,
        n_jobs=1,
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    model_path = config.output_dir / "iris_random_forest.joblib"
    metrics_path = config.output_dir / "metrics.json"
    joblib.dump(model, model_path)

    metrics = {
        "model_version": config.model_version,
        "dataset": "iris",
        "accuracy": float(accuracy),
        "n_samples_train": int(len(x_train)),
        "n_samples_test": int(len(x_test)),
        "n_estimators": config.n_estimators,
        "test_size": config.test_size,
        "random_state": config.random_state,
        "classes": iris.target_names.tolist(),
        "feature_names": iris.feature_names,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Model saved to {model_path}")
    print(f"Metrics saved to {metrics_path}")
    print(f"Accuracy: {accuracy:.4f}")
    return metrics


if __name__ == "__main__":
    try:
        train_model()
    except ValueError as error:
        raise SystemExit(f"Configuration error: {error}")
