import importlib.util
from pathlib import Path

import streamlit as st

# Load bootstrap from app/ without package name issues
_bootstrap_path = Path(__file__).resolve().parent / "_bootstrap.py"
_spec = importlib.util.spec_from_file_location("bootstrap", _bootstrap_path)
_bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bootstrap)

st.set_page_config(
    page_title="Smart Operator Assistant",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Smart Operator Assistant")
st.markdown(
    """
    Intelligent companion for construction equipment operators — daily work planning,
    safety awareness, skills development, usage insights, and **data-driven task time estimates**.

    Use the **sidebar** to open Dashboard, Safety, Training, Behavior insights, or Task Estimator.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("Machine", "EXC001")
col2.metric("Operator", "OP1001")
col3.metric("Shift", "Day")

st.info("Select a page from the left menu to get started.")
