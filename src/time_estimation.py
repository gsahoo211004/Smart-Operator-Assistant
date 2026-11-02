"""Task duration prediction with scikit-learn and interpretable adjustments."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.data_loader import load_task_history

SKILL_ORDER = {"Beginner": 0, "Intermediate": 1, "Expert": 2}

WEATHER_MULTIPLIERS = {
    "Sunny": 1.0,
    "Cloudy": 1.05,
    "Rainy": 1.15,
    "Windy": 1.12,
}

SKILL_MULTIPLIERS = {
    "Beginner": 1.2,
    "Intermediate": 1.08,
    "Expert": 1.0,
}


@dataclass
class PredictionResult:
    predicted_minutes: float
    baseline_minutes: float | None
    factor_breakdown: list[dict[str, str | float]] = field(default_factory=list)
    note: str = ""


class TaskDurationModel:
    """Ridge regression on historical tasks with heuristic fallback."""

    def __init__(self) -> None:
        self._pipeline: Pipeline | None = None
        self._history: pd.DataFrame = pd.DataFrame()
        self._feature_cols = ["task_type", "weather", "operator_skill", "machine_age_yrs", "estimated_time_min"]

    def fit(self, history: pd.DataFrame | None = None) -> "TaskDurationModel":
        self._history = history.copy() if history is not None else load_task_history()
        if self._history.empty:
            return self

        X = self._history[self._feature_cols]
        y = self._history["actual_time_min"]

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    ["task_type", "weather", "operator_skill"],
                ),
                ("num", "passthrough", ["machine_age_yrs", "estimated_time_min"]),
            ]
        )

        self._pipeline = Pipeline(
            steps=[
                ("prep", preprocessor),
                ("model", Ridge(alpha=1.0, random_state=42)),
            ]
        )
        self._pipeline.fit(X, y)
        return self

    def predict(
        self,
        task_type: str,
        weather: str,
        operator_skill: str,
        machine_age_years: int,
        estimated_time_min: float | None = None,
    ) -> PredictionResult:
        if estimated_time_min is None:
            estimated_time_min = float(
                self._history[self._history["task_type"] == task_type]["estimated_time_min"].mean()
                if not self._history.empty
                and task_type in self._history["task_type"].values
                else 45.0
            )

        breakdown: list[dict[str, str | float]] = []
        baseline = float(estimated_time_min)
        breakdown.append({"factor": "Dispatch estimate", "effect_min": baseline})

        weather_mult = WEATHER_MULTIPLIERS.get(weather, 1.08)
        skill_mult = SKILL_MULTIPLIERS.get(operator_skill, 1.1)
        age_adj = max(0, machine_age_years - 2) * 1.5

        heuristic = baseline * weather_mult * skill_mult + age_adj
        breakdown.append(
            {
                "factor": f"Weather ({weather})",
                "effect_min": round(baseline * (weather_mult - 1.0), 1),
            }
        )
        breakdown.append(
            {
                "factor": f"Operator skill ({operator_skill})",
                "effect_min": round(baseline * weather_mult * (skill_mult - 1.0), 1),
            }
        )
        breakdown.append({"factor": f"Machine age ({machine_age_years} yrs)", "effect_min": round(age_adj, 1)})

        ml_pred = heuristic
        note = "Heuristic blend (limited history)."
        if self._pipeline is not None:
            row = pd.DataFrame(
                [
                    {
                        "task_type": task_type,
                        "weather": weather,
                        "operator_skill": operator_skill,
                        "machine_age_yrs": machine_age_years,
                        "estimated_time_min": estimated_time_min,
                    }
                ]
            )
            ml_raw = float(self._pipeline.predict(row)[0])
            ml_pred = 0.5 * ml_raw + 0.5 * heuristic
            note = "Blend of Ridge regression on history and interpretable adjustments."

        breakdown.append({"factor": "Final predicted duration", "effect_min": round(ml_pred, 1)})

        return PredictionResult(
            predicted_minutes=round(ml_pred, 1),
            baseline_minutes=baseline,
            factor_breakdown=breakdown,
            note=note,
        )

    def evaluate_history(self) -> pd.DataFrame:
        if self._history.empty:
            return pd.DataFrame()

        rows = []
        for _, row in self._history.iterrows():
            pred = self.predict(
                task_type=row["task_type"],
                weather=row["weather"],
                operator_skill=row["operator_skill"],
                machine_age_years=int(row["machine_age_yrs"]),
                estimated_time_min=float(row["estimated_time_min"]),
            )
            rows.append(
                {
                    "task_id": row["task_id"],
                    "task_type": row["task_type"],
                    "estimated_time_min": row["estimated_time_min"],
                    "actual_time_min": row["actual_time_min"],
                    "predicted_time_min": pred.predicted_minutes,
                }
            )
        return pd.DataFrame(rows)


_default_model: TaskDurationModel | None = None


def get_model() -> TaskDurationModel:
    global _default_model
    if _default_model is None:
        _default_model = TaskDurationModel().fit()
    return _default_model


def predict_task_duration(
    task_type: str,
    weather: str,
    operator_skill: str,
    machine_age_years: int,
    estimated_time_min: float | None = None,
) -> PredictionResult:
    return get_model().predict(
        task_type=task_type,
        weather=weather,
        operator_skill=operator_skill,
        machine_age_years=machine_age_years,
        estimated_time_min=estimated_time_min,
    )


def mean_absolute_error_on_history() -> float:
    model = get_model()
    eval_df = model.evaluate_history()
    if eval_df.empty:
        return float("nan")
    return float(np.mean(np.abs(eval_df["actual_time_min"] - eval_df["predicted_time_min"])))
