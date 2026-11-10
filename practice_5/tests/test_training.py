import json

import joblib
import pytest

from train_model import TrainingConfig, train_model


def test_training_creates_model_and_metrics(tmp_path):
    config = TrainingConfig(
        output_dir=tmp_path,
        n_estimators=10,
        test_size=0.2,
        random_state=42,
        model_version="test",
    )

    metrics = train_model(config)
    model_path = tmp_path / "iris_random_forest.joblib"
    metrics_path = tmp_path / "metrics.json"

    assert model_path.is_file()
    assert metrics_path.is_file()
    assert metrics["model_version"] == "test"
    assert metrics["n_estimators"] == 10
    assert 0 <= metrics["accuracy"] <= 1

    saved_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert saved_metrics == metrics

    model = joblib.load(model_path)
    assert model.predict([[5.1, 3.5, 1.4, 0.2]]).shape == (1,)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("n_estimators", 0, "N_ESTIMATORS must be at least 1"),
        ("test_size", 0, "TEST_SIZE must be greater than 0 and less than 1"),
        ("test_size", 1, "TEST_SIZE must be greater than 0 and less than 1"),
        ("model_version", "", "MODEL_VERSION must not be empty"),
    ],
)
def test_config_rejects_invalid_values(tmp_path, field, value, message):
    values = {"output_dir": tmp_path, field: value}

    with pytest.raises(ValueError, match=message):
        TrainingConfig(**values)


def test_config_reads_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_DIR", str(tmp_path))
    monkeypatch.setenv("N_ESTIMATORS", "25")
    monkeypatch.setenv("TEST_SIZE", "0.25")
    monkeypatch.setenv("RANDOM_STATE", "7")
    monkeypatch.setenv("MODEL_VERSION", "2.0.0")

    config = TrainingConfig.from_env()

    assert config.output_dir == tmp_path
    assert config.n_estimators == 25
    assert config.test_size == 0.25
    assert config.random_state == 7
    assert config.model_version == "2.0.0"


def test_config_rejects_non_numeric_environment_value(monkeypatch):
    monkeypatch.setenv("N_ESTIMATORS", "many")

    with pytest.raises(ValueError, match="N_ESTIMATORS must be an integer"):
        TrainingConfig.from_env()
