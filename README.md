# FlameLens 🔥

**Explore microgravity combustion data and uncover evidence-based fire-safety insights.**

NASA Space Apps Challenge 2026 – *Flame in Freefall*

FlameLens is an interactive dashboard that explores flame behaviour under microgravity conditions using experimental data reported in NASA research publications. It combines data visualization, experimental filtering, heuristic risk analysis and AI-powered explanations to make combustion research easier to explore and understand.

## Features

- **Multi-Dataset Explorer:** Switch between Saffire and BASS-II experimental datasets while keeping their measurements separate.
- **Risk Overview:** Explore observed experimental outcomes and heuristic risk scores where sufficient paired measurements are available. Material ranking is disabled when the available data does not support a meaningful comparison.
- **Data Explorer:** Examine relationships between airflow, oxygen concentration and flame spread using available paired measurements.
- **AI Insights:** Generate plain-English explanations of the selected and filtered experimental data using Claude.
- **Ask the Data:** Ask questions about the currently selected dataset and receive data-grounded answers.
- **Method & Sources:** Review the methodology, research sources, data limitations and interpretation guidelines.
- **Custom CSV Upload:** Upload a compatible experimental CSV file for exploration.

## Datasets and Research Sources

FlameLens currently supports two separate experimental datasets:

### 1. Saffire

The Saffire dataset contains 11 experimental observations transcribed from Ferkul et al. (2017), NASA Glenn Research Center, covering Saffire-I and Saffire-II research results.

- 11 reported observations
- 4 observations with numerical flame-spread rates
- 4 material categories
- Missing measurements are preserved rather than replaced with fabricated values.

### 2. BASS-II

The BASS-II dataset contains segment-level observations extracted from NASA research documentation on the Burning and Suppression of Solids (BASS-II) experiments conducted aboard the International Space Station.

- Segment-level flame-spread and airflow observations are represented where reported.
- Oxygen values are populated only where segment-level estimates could be recovered.
- Initial and final oxygen readings are retained separately from segment oxygen estimates.
- Pressure measurements are not reported in the extracted records.

**Important:** Saffire and BASS-II are displayed separately because their experimental configurations, apparatus and reported conditions differ. Their records are not merged into a single dataset.

### Data integrity

- Directly reported values are distinguished from estimates.
- Missing measurements are not treated as zero.
- Initial/final oxygen readings are never substituted for missing segment oxygen estimates.
- Digitisation-derived estimates retain their classification and confidence information where available.
- Source references and provenance information are retained in the dataset.

## Risk Analysis and Methodology

FlameLens uses a heuristic score to explore observations where both oxygen concentration and flame-spread rate are available.

The score combines normalized flame-spread rate and a low-oxygen component using a user-adjustable weighting.

**Important limitations:**

- The score is an exploratory comparison aid, not a validated fire-risk prediction model.
- It does not establish causation between experimental conditions and flame behaviour.
- Material rankings are disabled when there are insufficient eligible observations or when the dataset does not support meaningful material-to-material comparison.
- The dashboard is not a substitute for NASA spacecraft fire-safety standards or expert engineering review.

## Project Structure

```text
FlameLens/
│
├── app.py
├── requirements.txt
├── README.md
│
└── data/
    ├── experiments.csv
    └── BASS_II_OBSERVATIONS.csv
```

Both repository datasets should be placed inside the `data/` directory.

## Run Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FlameLens
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Anthropic API key

For PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your_api_key"
```

Alternatively, create `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "your_api_key"
```

Never commit API keys or other secrets to GitHub.

### 4. Launch the application

```bash
streamlit run app.py
```

Without an Anthropic API key, FlameLens provides rule-based summaries instead of live Claude-generated insights.

## Deployment

FlameLens can be deployed using Streamlit Community Cloud.

1. Push the project repository to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **New App** and connect your GitHub repository.
4. Select the `main` branch and `app.py`.
5. Configure `ANTHROPIC_API_KEY` under the application's Secrets settings if live AI functionality is required.
6. Deploy and test the public application URL.

Ensure the repository includes the required data files and `requirements.txt`.

## Technologies Used

- **Python** – Application logic and data processing.
- **Streamlit** – Interactive web dashboard.
- **Pandas** – Dataset processing and filtering.
- **Plotly** – Interactive data visualizations.
- **Anthropic Claude API** – AI-powered explanations and question answering.
- **NASA research datasets** – Experimental combustion observations.

## Data and AI Disclosure

Experimental observations are transcribed from published NASA research sources. Data provenance and source references are retained wherever available.

AI-generated explanations use the currently selected and filtered experimental observations as context. Responses are intended for research exploration and education, and should be checked against the underlying source data.

Rule-based summaries are provided when live AI functionality is unavailable.

FlameLens is an independent student project developed for the NASA Space Apps Challenge 2026. NASA does not endorse this application.

## Limitations and Disclaimer

The available datasets contain incomplete measurements, a limited number of observations and, in some cases, digitisation uncertainty.

FlameLens is an analytical and educational tool. Its heuristic scores and AI-generated explanations must not be interpreted as certified spacecraft fire-safety assessments or engineering recommendations.
