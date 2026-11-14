"""FlameLens - AI-powered fire safety insights from microgravity combustion data.
NASA Space Apps Challenge 2026: "Flame in Freefall".

Run:  streamlit run app.py
"""
import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="FlameLens", page_icon="🔥", layout="wide")

REQUIRED = ["material", "oxygen_pct", "pressure_kpa", "flow_cm_s", "spread_rate_mm_s"]
DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "data", "experiments.csv")
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

SYSTEM_PROMPT = """You are FlameLens, an assistant that explains microgravity combustion \
experiment data for fire safety on crewed space missions.
Rules:
- Use ONLY the data tables given in the message. Never invent numbers, experiments or sources.
- If the answer is not in the data, say: "That isn't in the loaded dataset."
- Quote numbers exactly as given and name the material and conditions.
- Be concise (under 150 words unless asked) and use plain English for non-experts.
- You are an analysis aid, not a safety certification. When you give a recommendation, \
remind the user that real mission decisions need NASA safety standards and expert review."""


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_csv(file_or_path) -> pd.DataFrame:
    df = pd.read_csv(file_or_path)
    df.columns = [c.strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}. Required: {REQUIRED}")
    for c in REQUIRED[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["material"]).reset_index(drop=True)  # blanks stay NaN, never 0
    for c in ("source", "notes"):
        if c not in df.columns:
            df[c] = ""
    return df


def _norm(s: pd.Series) -> pd.Series:
    rng = s.max() - s.min()
    return (s - s.min()) / rng if rng > 0 else s * 0.0


def add_risk(df: pd.DataFrame, w_spread: float) -> pd.DataFrame:
    """Risk (0-100) = w * normalised spread rate + (1-w) * (1 - normalised oxygen).
    Faster flame spread = riskier. Low oxygen only counts as risky when a flame still spreads,
    so the oxygen term is multiplied by a 'flame present' flag."""
    out = df.copy()
    spread = _norm(out["spread_rate_mm_s"])
    low_o2 = (1 - _norm(out["oxygen_pct"])) * (out["spread_rate_mm_s"] > 0)
    out["risk_score"] = (100 * (w_spread * spread + (1 - w_spread) * low_o2)).round(1)
    return out


def rank_materials(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("material")
    out = g.agg(
        mean_risk=("risk_score", "mean"),
        max_spread_mm_s=("spread_rate_mm_s", "max"),
        runs=("material", "size"),
    ).reset_index()
    burned = (
        df[df["spread_rate_mm_s"] > 0].groupby("material")["oxygen_pct"].min().rename("lowest_o2_that_burned_pct")
    )
    out = out.merge(burned, on="material", how="left")
    out["risk_level"] = pd.cut(out["mean_risk"], [-1, 33, 66, 101], labels=["Low", "Medium", "High"])
    return out.sort_values("mean_risk", ascending=False).round(2).reset_index(drop=True)


# ----------------------------------------------------------------------------
# AI (Claude) with an offline fallback so the demo never breaks
# ----------------------------------------------------------------------------
def _api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def ai_available() -> bool:
    return bool(_api_key())


def build_context(df: pd.DataFrame, ranking: pd.DataFrame) -> str:
    return (
        "EXPERIMENT DATA (CSV, up to 150 rows):\n"
        + df.head(150).to_csv(index=False)
        + "\nMATERIAL RISK RANKING (CSV):\n"
        + ranking.to_csv(index=False)
        + "\nRisk score = 0-100 heuristic from flame spread rate and oxygen level (see app methodology)."
    )


def call_claude(messages, max_tokens=500) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=_api_key())
    resp = client.messages.create(model=MODEL, max_tokens=max_tokens, system=SYSTEM_PROMPT, messages=messages)
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def answer_question(df: pd.DataFrame, question: str) -> str:
    """Answer common FlameLens questions using only the selected data."""
    if df.empty:
        return "No experimental records are available for the current selection."

    q = question.lower()
    measured = df.dropna(subset=["spread_rate_mm_s"])
    rates = measured["spread_rate_mm_s"]
    records = len(df)

    def fmt(value):
        return f"{value:.2f}".rstrip("0").rstrip(".")

    # Number of records
    if any(x in q for x in ["how many", "number of", "count"]):
        return f"There are **{records} experimental records** in the selected dataset."

    # Pressure availability
    if "pressure" in q:
        valid = df.dropna(subset=["pressure_kpa"])
        if valid.empty:
            return (
                "Pressure data is unavailable for all "
                f"**{records} records**. Therefore, the experiment "
                "with the highest pressure cannot be identified."
            )
        if any(x in q for x in ["highest", "maximum", "maximum", "max"]):
            r = valid.loc[valid["pressure_kpa"].idxmax()]
            return f"Highest recorded pressure: **{r['pressure_kpa']} kPa**, for {r['material']}."
        return f"Pressure is reported in {len(valid)} of {records} records."

    # Missing data
    if any(x in q for x in ["missing", "not reported", "unavailable", "absent"]):
        missing_spread = int(df["spread_rate_mm_s"].isna().sum())
        missing_pressure = int(df["pressure_kpa"].isna().sum())
        return (
            f"**Missing data summary:**\n"
            f"- Spread rate missing in {missing_spread} records.\n"
            f"- Pressure missing in {missing_pressure} records.\n\n"
            "Missing values are not zero. They must remain missing and "
            "be excluded from calculations that require those measurements."
        )

    # Major observations
    if any(x in q for x in ["major observation", "key observation", "summarize", "summary"]):
        if measured.empty:
            return f"There are {records} records, but no numerical spread rates."
        return (
            f"**Major observations:**\n"
            f"- Total records: {records}\n"
            f"- Numerical spread measurements: {len(measured)}\n"
            f"- Highest spread: {fmt(rates.max())} mm/s\n"
            f"- Lowest spread: {fmt(rates.min())} mm/s\n"
            f"- Missing spread rates: {int(df['spread_rate_mm_s'].isna().sum())}\n"
            f"- Missing pressure values: {int(df['pressure_kpa'].isna().sum())}\n"
            "A reliable material risk ranking cannot be established from this small dataset."
        )

    # Material comparison
    materials = df["material"].dropna().unique().tolist()
    aliases = {
        "cotton-fiberglass": "Cotton-fiberglass fabric (SIBAL)",
        "cotton fiberglass": "Cotton-fiberglass fabric (SIBAL)",
        "silicone": "Silicone sheet",
        "pmma slab": "PMMA slab",
        "pmma/nomex": "PMMA/Nomex composite",
    }

    matched = [m for m in materials if m.lower() in q]

    for alias, full_name in aliases.items():
        if alias in q and full_name in materials and full_name not in matched:
            matched.append(full_name)
    if "compare" in q and len(matched) >= 2:
        results = []
        for material in matched[:2]:
            subset = df[df["material"] == material]
            values = subset["spread_rate_mm_s"].dropna()
            if values.empty:
                results.append(f"- **{material}:** No numerical spread rates reported.")
            else:
                results.append(
                    f"- **{material}:** {', '.join(fmt(v) for v in values)} mm/s "
                    f"({len(values)} measured records)."
                )
        return "\n".join(results) + (
            "\n\nMissing measurements must not be interpreted as zero."
        )

    # Highest / lowest / average spread rate
    # Low-oxygen spread analysis
    if "oxygen" in q and any(x in q for x in ["low oxygen", "below 22", "under 22"]):
        low_oxygen = measured[measured["oxygen_pct"] < 22]

        if low_oxygen.empty:
            return "No numerical spread measurements are available below 22% oxygen."

        avg = low_oxygen["spread_rate_mm_s"].mean()
        materials = low_oxygen["material"].unique()

        return (
            f"Below 22% oxygen, **{materials[0]}** has the highest "
            f"available average spread rate of **{fmt(avg)} mm/s**, "
            f"based on {len(low_oxygen)} measurements. "
            "This is a very small sample and does not establish a general trend."
        )

    
    if "spread" in q or "flame" in q:
        if measured.empty:
            return "No numerical flame spread rates are available."

        if any(x in q for x in ["average", "mean"]):
            if "material" in q:
                means = measured.groupby("material")["spread_rate_mm_s"].mean()
                if len(means) == 1:
                    return (
                        f"Only **{means.index[0]}** has numerical spread measurements. "
                        f"Its average is **{fmt(means.iloc[0])} mm/s**. "
                        "A comparison between materials is not possible."
                    )
                return "Material averages:\n" + "\n".join(
                    f"- {m}: {fmt(v)} mm/s" for m, v in means.items()
                )
            return (
                f"The average spread rate is **{fmt(rates.mean())} mm/s**, "
                f"calculated from {len(rates)} numerical measurements. "
                f"{int(df['spread_rate_mm_s'].isna().sum())} missing values were excluded."
            )

        if any(x in q for x in ["highest", "maximum", "fastest", "max"]):
            r = measured.loc[rates.idxmax()]
            return (
                f"**Highest recorded spread rate: {fmt(r['spread_rate_mm_s'])} mm/s.**\n"
                f"- Material: {r['material']}\n"
                f"- Oxygen: {r['oxygen_pct']}%\n"
                f"- Airflow: {r['flow_cm_s']} cm/s\n"
                f"- Record: {r.get('record_id', 'Not available')}"
            )

        if any(x in q for x in ["lowest", "minimum", "slowest", "min"]):
            r = measured.loc[rates.idxmin()]
            return (
                f"**Lowest recorded spread rate: {fmt(r['spread_rate_mm_s'])} mm/s.**\n"
                f"- Material: {r['material']}\n"
                f"- Oxygen: {r['oxygen_pct']}%\n"
                f"- Airflow: {r['flow_cm_s']} cm/s\n"
                f"- Record: {r.get('record_id', 'Not available')}"
            )

    # Highest / lowest oxygen
    if "oxygen" in q:
        valid = df.dropna(subset=["oxygen_pct"])
        if valid.empty:
            return "Oxygen measurements are unavailable."
        if any(x in q for x in ["highest", "maximum", "max"]):
            value = valid["oxygen_pct"].max()
            rows = valid[valid["oxygen_pct"] == value]
            return (
                f"Highest oxygen concentration: **~{fmt(value)}%**. "
                f"Records: {', '.join(rows.get('record_id', rows.index.astype(str)).astype(str))}."
            )
        if any(x in q for x in ["lowest", "minimum", "min"]):
            r = valid.loc[valid["oxygen_pct"].idxmin()]
            return (
                f"Lowest oxygen concentration: **~{fmt(r['oxygen_pct'])}%**, "
                f"record {r.get('record_id', 'Not available')} ({r['material']})."
            )

        return (
            "The measured spread rates vary across the available oxygen "
            "concentrations. However, there are too few measurements and "
            "other experimental conditions differ, so a causal oxygen effect "
            "cannot be established."
        )

    # Airflow relationship
    if "airflow" in q or "flow" in q:
        if measured.empty:
            return "No numerical spread rates are available for airflow analysis."
        grouped = measured.groupby("flow_cm_s")["spread_rate_mm_s"].agg(["mean", "count"])
        details = [
            f"- {flow:g} cm/s: average {fmt(row['mean'])} mm/s "
            f"({int(row['count'])} measurements)"
            for flow, row in grouped.iterrows()
        ]
        return (
            "**Observed airflow and spread rates:**\n"
            + "\n".join(details)
            + "\n\nThese observations are too limited to establish a causal "
            "relationship between airflow and flame spread."
        )

    return (
        "I couldn't identify that question. Try asking about spread rate, "
        "oxygen, airflow, pressure, material comparison, missing data, "
        "or the number of experiments."
    )



def offline_summary(df: pd.DataFrame, ranking: pd.DataFrame) -> str:
    """Generate useful descriptive insights without an AI API."""
    if df.empty:
        return "No data selected."

    measured = df.dropna(subset=["spread_rate_mm_s"])
    missing_spread = int(df["spread_rate_mm_s"].isna().sum())
    missing_pressure = int(df["pressure_kpa"].isna().sum())

    lines = [
        "### Dataset overview",
        f"- Total experimental records: **{len(df)}**",
        f"- Records with numerical spread rates: **{len(measured)}**",
        f"- Missing spread rates: **{missing_spread}**",
        f"- Missing pressure measurements: **{missing_pressure}**",
    ]

    if not measured.empty:
        fastest = measured.loc[measured["spread_rate_mm_s"].idxmax()]
        slowest = measured.loc[measured["spread_rate_mm_s"].idxmin()]

        lines += [
            "",
            "### Flame spread observations",
            f"- Highest recorded spread: **{fastest['spread_rate_mm_s']} mm/s** "
            f"({fastest['material']}, record {fastest.get('record_id', 'N/A')}).",
            f"- Lowest recorded spread: **{slowest['spread_rate_mm_s']} mm/s** "
            f"({slowest['material']}, record {slowest.get('record_id', 'N/A')}).",
            f"- Average of the {len(measured)} numerical measurements: "
            f"**{measured['spread_rate_mm_s'].mean():.2f} mm/s**.",
        ]

        material_counts = measured.groupby("material")["spread_rate_mm_s"].count()

        if len(material_counts) == 1:
            lines.append(
                f"- Numerical spread measurements are available only for "
                f"**{material_counts.index[0]}**."
            )

    if missing_pressure == len(df):
        lines.append("- Pressure is not reported in any selected experiment.")

    if "outcome" in df.columns:
        no_spread = int((df["outcome"].astype(str).str.lower() == "no_spread").sum())
        if no_spread:
            lines.append(
                f"- **{no_spread} records** report no flame spread."
            )

    lines += [
        "",
        "### Interpretation and limitations",
        "- The dataset is too small for a reliable material risk ranking.",
        "- Oxygen and airflow effects cannot be established conclusively "
        "from these limited observations.",
        "- Missing measurements are not zero and are excluded from numerical calculations.",
        "",
        "_Rule-based insights from the selected data. This is an analysis aid, "
        "not a safety certification._",
    ]

    return "\n".join(lines)



# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
st.sidebar.title("🔥 FlameLens")
st.sidebar.caption("NASA Space Apps 2026 · Flame in Freefall")

upload = st.sidebar.file_uploader("Load your own CSV", type="csv")
try:
    raw = load_csv(upload if upload is not None else DEFAULT_CSV)
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load data: {e}")
    st.stop()

st.sidebar.subheader("Risk score weighting")
w_spread = st.sidebar.slider("Weight on flame spread rate", 0.0, 1.0, 0.7, 0.05,
                             help="The rest goes to 'burns at low oxygen'.")
data = add_risk(raw, w_spread)

st.sidebar.subheader("Filters")
mats = sorted(data["material"].unique())
sel_mats = st.sidebar.multiselect("Materials", mats, default=mats)


def range_slider(label, col):
    s = data[col].dropna()
    if s.empty:  # variable not reported in this dataset
        st.sidebar.caption(f"{label}: not reported in the loaded data")
        return None
    lo, hi = float(s.min()), float(s.max())
    if lo == hi:
        return lo, hi
    return st.sidebar.slider(label, lo, hi, (lo, hi))


def in_range(col, rng):
    """Keep rows inside the range; rows with an unreported value are kept, not dropped."""
    return data[col].isna() if rng is None else (data[col].between(*rng) | data[col].isna())


o2_rng = range_slider("Oxygen (%)", "oxygen_pct")
p_rng = range_slider("Pressure (kPa)", "pressure_kpa")
f_rng = range_slider("Flow speed (cm/s)", "flow_cm_s")

view = data[
    data["material"].isin(sel_mats)
    & in_range("oxygen_pct", o2_rng)
    & in_range("pressure_kpa", p_rng)
    & in_range("flow_cm_s", f_rng)
]
measured = view.dropna(subset=["spread_rate_mm_s"])  # rows with a reported spread rate
MIN_FOR_RANKING = 20  # below this, a risk ranking is not scientifically meaningful
ranking = rank_materials(measured) if len(measured) >= MIN_FOR_RANKING else pd.DataFrame()

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("FlameLens")
st.markdown("**Fire safety insights from microgravity combustion data, ranked and explained by AI.**")

if raw["source"].astype(str).str.contains("PLACEHOLDER", case=False).any():
    st.warning("⚠️ This is **placeholder demo data**, not real NASA results. "
               "Replace `data/experiments.csv` with real NASA data before presenting.")

if view.empty:
    st.info("No experiments match the current filters.")
    st.stop()

if len(measured) < MIN_FOR_RANKING:
    st.warning(f"Only {len(measured)} of {len(view)} records have a reported spread rate, so the risk ranking is "
               f"switched off (needs at least {MIN_FOR_RANKING}). Observed outcomes are shown instead.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Experiments", len(view))
k2.metric("Materials", view["material"].nunique())
k3.metric("Fastest reported spread", f"{measured['spread_rate_mm_s'].max():.2f} mm/s" if not measured.empty else "n/a")
k4.metric("Highest-risk material", ranking.iloc[0]["material"] if not ranking.empty else "n/a (too few data)")

tab_rank, tab_explore, tab_ai, tab_chat, tab_about = st.tabs(
    ["🏆 Risk ranking", "📈 Explorer", "🧠 AI insights", "💬 Ask the data", "ℹ️ Method & sources"]
)

COLORS = {"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e74c3c"}

with tab_rank:
  if ranking.empty:
    st.info("Risk ranking is off for this dataset size. Observed experiment outcomes (as reported by NASA):")
    cols = [c for c in ["material", "configuration", "oxygen_pct", "flow_cm_s", "spread_rate_mm_s", "outcome", "record_id"] if c in view.columns]
    st.dataframe(view[cols], width="stretch", hide_index=True)
  else:
    fig = px.bar(ranking, x="mean_risk", y="material", orientation="h", color="risk_level",
                 color_discrete_map=COLORS, template="plotly_dark",
                 labels={"mean_risk": "Mean risk score (0-100)", "material": ""},
                 category_orders={"material": ranking["material"].tolist()})
    fig.update_layout(height=380, yaxis=dict(autorange="reversed"), legend_title_text="Risk level")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(ranking, width="stretch", hide_index=True)

with tab_explore:
    if measured.empty:
        st.info("No records with a reported spread rate to chart.")
    else:
        c1, c2 = st.columns(2)
        f1 = px.scatter(measured, x="oxygen_pct", y="spread_rate_mm_s", color="material", size="risk_score",
                        hover_data=["pressure_kpa", "flow_cm_s", "risk_score"], template="plotly_dark",
                        title="Flame spread vs oxygen", labels={"oxygen_pct": "Oxygen (%)", "spread_rate_mm_s": "Spread (mm/s)"})
        c1.plotly_chart(f1, width="stretch")
        f2 = px.scatter(measured, x="flow_cm_s", y="spread_rate_mm_s", color="material", template="plotly_dark",
                        title="Flame spread vs airflow", labels={"flow_cm_s": "Flow (cm/s)", "spread_rate_mm_s": "Spread (mm/s)"})
        c2.plotly_chart(f2, width="stretch")
        heat = measured.pivot_table(index="material", columns="oxygen_pct", values="spread_rate_mm_s", aggfunc="mean")
        f3 = px.imshow(heat, aspect="auto", color_continuous_scale="YlOrRd", template="plotly_dark",
                       title="Average spread rate: material × oxygen (%)",
                       labels={"color": "mm/s", "x": "Oxygen (%)", "y": ""})
        st.plotly_chart(f3, width="stretch")
    with st.expander("Raw data"):
        st.dataframe(view, width="stretch", hide_index=True)

with tab_ai:
    st.subheader("Plain-English insight for your current selection")
    if not ai_available():
        st.info("No `ANTHROPIC_API_KEY` found, so a rule-based summary is shown. Add a key for full AI insights.")
    if st.button("Generate insight", type="primary"):
        if ai_available():
            with st.spinner("Analysing selected experiments..."):
                try:
                    prompt = (build_context(view, ranking)
                              + "\n\nTask: Write 3 short fire-safety insights for mission planners based only on "
                                "this data: (1) the biggest risk, (2) how oxygen/airflow/pressure change it, "
                                "(3) one practical recommendation. Use bullet points.")
                    st.session_state["insight"] = call_claude([{"role": "user", "content": prompt}])
                except Exception as e:  # noqa: BLE001
                    st.session_state["insight"] = offline_summary(view, ranking) + f"\n\n_(AI call failed: {e})_"
        else:
            st.session_state["insight"] = offline_summary(view, ranking)
    st.markdown(st.session_state.get("insight", "Click **Generate insight** to analyse the current filters."))

with tab_chat:
    st.subheader("Ask the data")
    st.caption("Answers use only the experiments currently selected in the sidebar.")
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    for m in st.session_state["chat"]:
        st.chat_message(m["role"]).markdown(m["content"])
    q = st.chat_input("e.g. Which material is safest at 21% oxygen?")
    if q:
        st.session_state["chat"].append({"role": "user", "content": q})
        st.chat_message("user").markdown(q)
        if ai_available():
            history = st.session_state["chat"][-6:]
            msgs = [{"role": "user", "content": build_context(view, ranking)}, {"role": "assistant", "content": "Data received."}]
            msgs += history
            try:
                with st.spinner("Thinking..."):
                    ans = call_claude(msgs)
            except Exception as e:  # noqa: BLE001
                ans = f"AI call failed: {e}"
        else:
            ans = answer_question(view, q)
        st.session_state["chat"].append({"role": "assistant", "content": ans})
        st.chat_message("assistant").markdown(ans)

with tab_about:
    st.markdown(f"""
### Why this matters
Fire is one of the most dangerous events on a spacecraft: crews cannot leave, and flames behave differently
without gravity (rounder, slower-moving, and sometimes able to persist at lower oxygen). FlameLens turns scattered
experiment results into something mission planners can scan, compare and question.

### How the risk score works
`risk = 100 × [ w × normalised spread rate + (1 − w) × (1 − normalised oxygen) × (flame present) ]`
with **w = {w_spread:.2f}** (adjust in the sidebar). Faster spread is riskier, and a flame that still burns at lower
oxygen is riskier. It is a transparent **heuristic for comparison**, not a validated safety model.

### Data sources
""" + "\n".join(f"- {s}" for s in sorted(raw["source"].astype(str).unique()) if s) + """

### AI use
An LLM writes summaries and answers questions using only the filtered data table passed to it. Numbers come from
the dataset, and the model is instructed to say when something is not in the data.

### Limitations
Small datasets, simplified scoring, and no replacement for NASA safety standards or expert review.
""")
