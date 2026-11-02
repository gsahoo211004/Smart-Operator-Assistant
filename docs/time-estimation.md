# Smart Operator Assistant — task duration prediction

## Purpose

Estimate **actual job duration (minutes)** from dispatch metadata and jobsite context, so operators and supervisors can plan shifts more accurately.

## Inputs

| Field | Type | Notes |
|-------|------|--------|
| `task_type` | categorical | Earth Excavation, Trenching, Material Loading, Grading, Demolition |
| `weather` | categorical | Sunny, Rainy, Cloudy, Windy |
| `operator_skill` | ordinal | Beginner, Intermediate, Expert |
| `machine_age_yrs` | integer | Years since machine commission |
| `estimated_time_min` | float | Optional dispatch baseline |

## Output

`PredictionResult`:

- `predicted_minutes` — blended forecast
- `baseline_minutes` — dispatch estimate used
- `factor_breakdown` — interpretable weather, skill, and age effects
- `note` — model mode (Ridge + heuristic blend)

## Model approach

1. **Historical table** (`task_history`) seeds training with completed jobs (estimated vs actual).
2. **Ridge regression** on one-hot task/weather/skill plus numeric age and dispatch estimate (`sklearn` pipeline in `src/time_estimation.py`).
3. **Interpretable multipliers** for weather and skill, plus age adjustment, blended 50/50 with regression output for stability on small samples.
4. **Evaluation:** mean absolute error computed over historical task IDs in the Task Estimator UI.

## Limitations

- Small labeled dataset (five historical tasks in seed data); production would require continuous jobsite logging.
- Proximity and live telemetry are not yet fused into ETA (future work).
- Unknown categorical values fall back to conservative multipliers.

## Key functions

```python
from src.time_estimation import predict_task_duration, get_model

result = predict_task_duration(
    task_type="Trenching",
    weather="Rainy",
    operator_skill="Intermediate",
    machine_age_years=4,
    estimated_time_min=45,
)
```
