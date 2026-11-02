import importlib.util
from pathlib import Path

import streamlit as st

_bootstrap_path = Path(__file__).resolve().parents[1] / "_bootstrap.py"
_spec = importlib.util.spec_from_file_location("bootstrap", _bootstrap_path)
_bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bootstrap)

from src.data_loader import ensure_data, insert_training_booking, load_training_bookings
from src.training import get_modules

st.set_page_config(page_title="Training", layout="wide")
st.title("Operator training hub")

ensure_data()
modules = get_modules()

st.subheader("Learning catalog")
st.dataframe(modules, use_container_width=True, hide_index=True)

st.subheader("Book instructor / simulation slot")
with st.form("booking_form", clear_on_submit=True):
    module_id = st.selectbox("Module", modules["module_id"].tolist())
    operator_id = st.text_input("Operator ID", value="OP1001")
    preferred_date = st.date_input("Preferred date")
    notes = st.text_input("Notes")
    if st.form_submit_button("Request booking"):
        insert_training_booking(
            module_id,
            operator_id,
            str(preferred_date),
            notes,
        )
        st.success("Booking request saved.")

st.subheader("Your booking requests")
bookings = load_training_bookings()
if bookings.empty:
    st.caption("No bookings yet.")
else:
    st.dataframe(bookings, use_container_width=True, hide_index=True)
