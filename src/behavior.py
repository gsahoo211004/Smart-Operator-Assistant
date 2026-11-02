"""Rule-based unusual machine usage detection."""

from __future__ import annotations

import pandas as pd

from src.data_loader import load_telemetry

IDLING_THRESHOLD_MIN = 45
LOW_CYCLES_PER_LITER = 0.5


def analyze_behavior(df: pd.DataFrame | None = None) -> pd.DataFrame:
    data = df if df is not None else load_telemetry()
    flags: list[dict] = []

    for _, row in data.iterrows():
        issues: list[str] = []
        if row["idling_time_min"] >= IDLING_THRESHOLD_MIN:
            issues.append(f"Excessive idling ({row['idling_time_min']} min)")
        if str(row["seatbelt_status"]).lower() == "unfastened":
            issues.append("Seatbelt unfastened")
        if row["safety_alert_triggered"]:
            issues.append("Safety alert triggered")
        if row["fuel_used_l"] > 0:
            ratio = row["load_cycles"] / row["fuel_used_l"]
            if ratio < LOW_CYCLES_PER_LITER:
                issues.append(f"Low productivity ({ratio:.2f} cycles/L fuel)")

        if issues:
            flags.append(
                {
                    "timestamp": row["timestamp"],
                    "machine_id": row["machine_id"],
                    "operator_id": row["operator_id"],
                    "issues": "; ".join(issues),
                    "idling_time_min": row["idling_time_min"],
                    "load_cycles": row["load_cycles"],
                }
            )

    return pd.DataFrame(flags)


def behavior_summary(df: pd.DataFrame | None = None) -> dict[str, int]:
    flagged = analyze_behavior(df)
    data = df if df is not None else load_telemetry()
    return {
        "telemetry_sessions": len(data),
        "flagged_sessions": len(flagged),
    }
