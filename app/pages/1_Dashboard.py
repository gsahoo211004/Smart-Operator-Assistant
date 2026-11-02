import importlib.util
from pathlib import Path

import streamlit as st

_bootstrap_path = Path(__file__).resolve().parents[1] / "_bootstrap.py"
_spec = importlib.util.spec_from_file_location("bootstrap", _bootstrap_path)
_bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bootstrap)

from src.data_loader import ensure_data, load_today_tasks
from src.safety import compliance_summary
from src.time_estimation import predict_task_duration

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Daily task dashboard")

ensure_data()
today = load_today_tasks()
safety = compliance_summary()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tasks today", len(today))
c2.metric("Seatbelt compliance", f"{safety['seatbelt_compliance_pct']}%")
c3.metric("Safety alerts (telemetry)", safety["safety_alerts"])
c4.metric("In progress", int((today["status"] == "In progress").sum()))

st.subheader("Scheduled tasks")
st.dataframe(today, use_container_width=True, hide_index=True)

st.subheader("Next task — predicted duration")
if not today.empty:
    next_task = today.iloc[0]
    pred = predict_task_duration(
        task_type=next_task["task_type"],
        weather=next_task["weather"],
        operator_skill=next_task["operator_skill"],
        machine_age_years=int(next_task["machine_age_yrs"]),
        estimated_time_min=float(next_task["estimated_time_min"]),
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Planned (min)", int(next_task["estimated_time_min"]))
    m2.metric("Predicted actual (min)", pred.predicted_minutes)
    m3.metric("Delta", round(pred.predicted_minutes - float(next_task["estimated_time_min"]), 1))
    st.caption(pred.note)
else:
    st.write("No tasks scheduled.")
