"""Safety analytics from machine telemetry."""

from __future__ import annotations

import pandas as pd

from src.data_loader import load_telemetry


def seatbelt_violations(df: pd.DataFrame | None = None) -> pd.DataFrame:
    data = df if df is not None else load_telemetry()
    return data[data["seatbelt_status"].str.lower() == "unfastened"].copy()


def active_safety_alerts(df: pd.DataFrame | None = None) -> pd.DataFrame:
    data = df if df is not None else load_telemetry()
    return data[data["safety_alert_triggered"] == True].copy()  # noqa: E712


def proximity_hazards() -> pd.DataFrame:
    """Simulated proximity events for demo (no external sensors)."""
    return pd.DataFrame(
        [
            {
                "time": "2025-05-02 09:15:00",
                "machine_id": "EXC001",
                "hazard_type": "Personnel proximity",
                "distance_m": 4.2,
                "severity": "Warning",
            },
            {
                "time": "2025-05-01 10:05:00",
                "machine_id": "EXC001",
                "hazard_type": "Utility line clearance",
                "distance_m": 2.8,
                "severity": "Critical",
            },
        ]
    )


def compliance_summary(df: pd.DataFrame | None = None) -> dict[str, int | float]:
    data = df if df is not None else load_telemetry()
    total = len(data)
    fastened = int((data["seatbelt_status"].str.lower() == "fastened").sum())
    alerts = int(data["safety_alert_triggered"].sum())
    rate = round(100.0 * fastened / total, 1) if total else 0.0
    return {
        "sessions": total,
        "seatbelt_fastened_count": fastened,
        "seatbelt_compliance_pct": rate,
        "safety_alerts": alerts,
    }
