import importlib.util
from pathlib import Path

import streamlit as st

_bootstrap_path = Path(__file__).resolve().parents[1] / "_bootstrap.py"
_spec = importlib.util.spec_from_file_location("bootstrap", _bootstrap_path)
_bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bootstrap)

from src.behavior import analyze_behavior, behavior_summary
from src.data_loader import ensure_data, load_telemetry

st.set_page_config(page_title="Behavior", layout="wide")
st.title("Behavior insights")

ensure_data()
telemetry = load_telemetry()
summary = behavior_summary(telemetry)
flagged = analyze_behavior(telemetry)

c1, c2 = st.columns(2)
c1.metric("Telemetry sessions", summary["telemetry_sessions"])
c2.metric("Flagged sessions", summary["flagged_sessions"])

st.subheader("Flagged usage patterns")
if flagged.empty:
    st.success("No unusual patterns in current telemetry sample.")
else:
    st.dataframe(flagged, use_container_width=True, hide_index=True)

st.subheader("Rules applied")
st.markdown(
    """
    - Idling ≥ **45 min** per session
    - Seatbelt **unfastened**
    - **Safety alert** triggered
    - Load cycles per liter of fuel below **0.5**
    """
)
