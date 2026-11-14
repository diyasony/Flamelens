# FlameLens 🔥

**AI-powered fire safety insights from microgravity combustion data.**

NASA Space Apps Challenge 2026 – *Flame in Freefall*

FlameLens is an interactive dashboard that explores flame behaviour under microgravity conditions using experimental data reported in NASA research publications. It combines data visualization, experimental filtering, risk-analysis methodology and AI-powered explanations to make combustion research easier to understand.

## Features

- **Risk Analysis:** Explore experimental outcomes and risk indicators where sufficient measured data is available.
- **Data Explorer:** Examine relationships between oxygen concentration, airflow and flame spread.
- **AI Insights:** Generate plain-English explanations of the selected experimental data.
- **Ask the Data:** Ask questions about the loaded dataset.
- **Method & Sources:** Review the methodology, research sources and data limitations.
- **Custom CSV Upload:** Load your own compatible experimental dataset.

## Run Locally

```bash
pip install -r requirements.txt
```

Set your Anthropic API key:

```powershell
$env:ANTHROPIC_API_KEY="your_key"
```

Launch the application:

```bash
streamlit run app.py
```

Without an API key, the application uses rule-based summaries instead of live AI responses.

## Dataset and Research Sources

The current dataset contains 11 experimental observations transcribed from Ferkul et al. (2017), NASA Glenn Research Center, Saffire-I and Saffire-II research results.

- 11 reported observations
- 4 observations with numerical flame spread rates
- 4 material categories
- Missing measurements are preserved rather than estimated or replaced with fabricated values.

The dataset and its validation documentation are available in the `data/` directory.

**Important limitation:** The current dataset is relatively small and does not support statistically reliable material risk rankings. FlameLens therefore displays observed experimental outcomes instead of presenting an unsupported ranking.

## Deployment

1. Push the project repository to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select New App and connect your GitHub repository.
4. Choose the `main` branch and `app.py`.
5. Configure the `ANTHROPIC_API_KEY` secret if AI functionality is required.

## Data and AI Disclosure

Experimental data are transcribed from published NASA research sources. Missing measurements are not fabricated or estimated.

AI-generated explanations are based on the loaded experimental dataset and are intended for research exploration and educational purposes.

FlameLens is an independent student project. NASA does not endorse this application.

**FlameLens is an analytical and educational tool, not a substitute for official spacecraft fire-safety standards or expert engineering review.**
