import pytest

from src.time_estimation import TaskDurationModel, predict_task_duration
from src.data_loader import load_task_history


def test_predict_returns_positive_minutes():
    result = predict_task_duration(
        task_type="Trenching",
        weather="Rainy",
        operator_skill="Intermediate",
        machine_age_years=4,
        estimated_time_min=45,
    )
    assert result.predicted_minutes > 0
    assert result.baseline_minutes == 45
    assert len(result.factor_breakdown) >= 3


def test_rainy_beginner_runs_longer_than_sunny_expert():
    rainy = predict_task_duration(
        task_type="Material Loading",
        weather="Rainy",
        operator_skill="Beginner",
        machine_age_years=3,
        estimated_time_min=30,
    )
    sunny = predict_task_duration(
        task_type="Material Loading",
        weather="Sunny",
        operator_skill="Expert",
        machine_age_years=3,
        estimated_time_min=30,
    )
    assert rainy.predicted_minutes > sunny.predicted_minutes


def test_evaluate_history_covers_all_tasks():
    history = load_task_history()
    model = TaskDurationModel().fit(history)
    eval_df = model.evaluate_history()
    assert len(eval_df) == len(history)


def test_mae_on_history_is_reasonable():
    model = TaskDurationModel().fit(load_task_history())
    eval_df = model.evaluate_history()
    mae = (eval_df["actual_time_min"] - eval_df["predicted_time_min"]).abs().mean()
    assert mae < 25
