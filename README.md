# Smart Operator Assistant

Personal project — a web assistant for **construction equipment operators**. It combines daily task planning, safety telemetry, training resources, behavior analytics, and **machine-learning task duration prediction** in one Streamlit app.

## Features

- **Daily dashboard** — today’s scheduled tasks and quick safety stats  
- **Safety center** — seatbelt compliance, alert history, simulated proximity hazards, incident logging  
- **Training hub** — learning module catalog and instructor/simulation booking requests  
- **Behavior insights** — rule-based flags for excessive idling, seatbelt issues, and low fuel efficiency  
- **Task time estimator** — predicts actual job minutes from task type, weather, operator skill, and machine age (scikit-learn + interpretable factors)

## Tech stack

Python · Streamlit · pandas · SQLite · scikit-learn · Plotly · pytest

## Quick start

```bash
cd Smart-Operator-Assistant
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
streamlit run app/Home.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

## Tests

```bash
pytest
```

## Project layout

| Path | Description |
|------|-------------|
| `app/` | Streamlit UI (`Home.py` + `pages/`) |
| `src/` | Data, ML, safety, and behavior logic |
| `data/` | JSON seed datasets |
| `docs/` | Architecture and time-estimation notes |

See [docs/architecture.md](docs/architecture.md) and [docs/time-estimation.md](docs/time-estimation.md).

## Author

Gaurav Sahoo — personal portfolio project.
