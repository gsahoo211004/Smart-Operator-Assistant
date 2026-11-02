import importlib.util
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

_bootstrap_path = Path(__file__).resolve().parents[1] / "_bootstrap.py"
_spec = importlib.util.spec_from_file_location("bootstrap", _bootstrap_path)
_bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bootstrap)

from src.data_loader import load_task_history
from src.time_estimation import TaskDurationModel, mean_absolute_error_on_history, predict_task_duration

TASK_TYPES = [
    "Earth Excavation",
    "Trenching",
    "Material Loading",
    "Grading",
    "Demolition",
]
WEATHER_OPTIONS = ["Sunny", "Rainy", "Cloudy", "Windy"]
SKILL_OPTIONS = ["Beginner", "Intermediate", "Expert"]


@st.cache_resource
def load_model() -> TaskDurationModel:
    return TaskDurationModel().fit(load_task_history())


st.set_page_config(page_title="Task Estimator", layout="wide")
st.title("Task time estimator")

model = load_model()

st.subheader("Predict completion time")
col1, col2 = st.columns(2)
with col1:
    task_type = st.selectbox("Task type", TASK_TYPES)
    weather = st.selectbox("Weather", WEATHER_OPTIONS)
with col2:
    operator_skill = st.selectbox("Operator skill", SKILL_OPTIONS)
    machine_age = st.number_input("Machine age (years)", min_value=1, max_value=20, value=4)
    estimated = st.number_input("Dispatch estimate (minutes)", min_value=5, max_value=300, value=45)

if st.button("Estimate duration", type="primary"):
    result = predict_task_duration(
        task_type=task_type,
        weather=weather,
        operator_skill=operator_skill,
        machine_age_years=int(machine_age),
        estimated_time_min=float(estimated),
    )
    m1, m2 = st.columns(2)
    m1.metric("Predicted actual time (min)", result.predicted_minutes)
    m2.metric("Vs dispatch", round(result.predicted_minutes - estimated, 1))
    st.caption(result.note)
    st.subheader("Factor breakdown")
    st.dataframe(
        __import__("pandas").DataFrame(result.factor_breakdown),
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Historical tasks — estimated vs actual vs predicted")
eval_df = model.evaluate_history()
if not eval_df.empty:
    mae = mean_absolute_error_on_history()
    st.metric("Mean absolute error on history (min)", round(mae, 2))
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Estimated", x=eval_df["task_id"], y=eval_df["estimated_time_min"]))
    fig.add_trace(go.Bar(name="Actual", x=eval_df["task_id"], y=eval_df["actual_time_min"]))
    fig.add_trace(go.Bar(name="Predicted", x=eval_df["task_id"], y=eval_df["predicted_time_min"]))
    fig.update_layout(barmode="group", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(eval_df, use_container_width=True, hide_index=True)
