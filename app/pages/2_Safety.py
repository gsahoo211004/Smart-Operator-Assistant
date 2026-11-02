import importlib.util
from pathlib import Path

import streamlit as st

_bootstrap_path = Path(__file__).resolve().parents[1] / "_bootstrap.py"
_spec = importlib.util.spec_from_file_location("bootstrap", _bootstrap_path)
_bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bootstrap)

from src.data_loader import ensure_data, insert_incident, load_incidents, load_telemetry
from src.safety import (
    active_safety_alerts,
    compliance_summary,
    proximity_hazards,
    seatbelt_violations,
)

st.set_page_config(page_title="Safety", layout="wide")
st.title("Safety center")

ensure_data()
telemetry = load_telemetry()
summary = compliance_summary(telemetry)

c1, c2, c3 = st.columns(3)
c1.metric("Compliance rate", f"{summary['seatbelt_compliance_pct']}%")
c2.metric("Unfastened events", len(seatbelt_violations(telemetry)))
c3.metric("Active alert rows", len(active_safety_alerts(telemetry)))

st.subheader("Telemetry — seatbelt & alerts")
st.dataframe(telemetry, use_container_width=True, hide_index=True)

st.subheader("Proximity hazards (simulated)")
st.dataframe(proximity_hazards(), use_container_width=True, hide_index=True)

st.subheader("Log incident")
with st.form("incident_form", clear_on_submit=True):
    machine_id = st.text_input("Machine ID", value="EXC001")
    operator_id = st.text_input("Operator ID", value="OP1001")
    description = st.text_area("Description")
    working_conditions = st.text_input("Working conditions (weather, visibility, ground)")
    severity = st.selectbox("Severity", ["Low", "Medium", "High"])
    submitted = st.form_submit_button("Submit incident")
    if submitted:
        if not description.strip():
            st.error("Description is required.")
        else:
            insert_incident(machine_id, operator_id, description, working_conditions, severity)
            st.success("Incident logged.")

st.subheader("Incident log")
incidents = load_incidents()
if incidents.empty:
    st.caption("No incidents logged yet.")
else:
    st.dataframe(incidents, use_container_width=True, hide_index=True)
