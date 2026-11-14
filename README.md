# FlameLens 🔥
AI-powered fire safety insights from microgravity combustion data. NASA Space Apps 2026, "Flame in Freefall".

## Run locally
```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key      # Windows PowerShell: $env:ANTHROPIC_API_KEY="your_key"
streamlit run app.py
```
Without a key the app still works (rule-based summaries instead of AI).

## Use real NASA data (REQUIRED before submitting)
Replace `data/experiments.csv` with real data using these columns:
`material, oxygen_pct, pressure_kpa, flow_cm_s, spread_rate_mm_s, source, notes`
Put the real dataset name or URL in `source` for every row. The app hides the placeholder warning automatically.

## Deploy free
1. Push this folder to GitHub.
2. share.streamlit.io -> New app -> pick the repo and `app.py`.
3. App settings -> Secrets -> add `ANTHROPIC_API_KEY = "your_key"`.

## Data and AI disclosure
Data: see the `source` column / "Method & sources" tab. AI: an LLM summarises and answers questions using only the filtered table.
