# FlameLens: Data research report (verified 14 Nov 2026)

## 1. What I could and could not verify
- **Verified by reading the source myself:** NASA Glenn's Saffire results paper (Ferkul et al., 47th ICES, 2017), Table I.
  https://ntrs.nasa.gov/api/citations/20170008805/downloads/20170008805.pdf
  It reports, per sample: material, flow speed (cm/s), oxygen (%), burn outcome and microgravity spread rate (mm/s).
- **Corroborated:** the PSI-98 (Saffire-I) page lists the same Saffire-I conditions (SIBAL fabric, 20 cm/s, 21.5 to 21.7% O2, concurrent and opposed).
  https://psi.nasa.gov/physci/repo/data/investigations/PSI-98
- **NOT verified:** the PSI data files themselves. psi.nasa.gov renders its file lists with JavaScript, and my tools cannot run it, so I did not download or open any PSI data table. Nothing in experiments.csv comes from a PSI file or from anyone's GitHub repo.

## 2. Candidate sources
| Source | What it holds | Fit to the 7-column schema | Status |
|---|---|---|---|
| Ferkul et al. 2017 Table I (Saffire-I and -II) | 11 samples with material, O2, flow, outcome; 4 with a numeric spread rate | Good: 4 of 5 variables reported | Extracted |
| PSI-98 Saffire-I (https://psi.nasa.gov/physci/repo/data/investigations/PSI-98) | Telemetry (thermocouples, radiometers, O2/CO2, pressure, anemometers) and sample table | Pressure exists as a sensor channel, but a spread rate is not a column | Page read; files not opened |
| PSI-25 BASS (https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) | Opposed/concurrent flame spread on solids, with a publications list | Study varies O2 and flow; whether per-test spread rates are tabulated is unverified | Page read via search; files not opened |
| NTRS: Olson, Ruff, Miller, SAE 2008-01-2005, "Microgravity Flame Spread in Exploration Atmospheres..." (cited in NTRS 20170001636) | Pressure, O2 and velocity effects on opposed and concurrent spread | Likely to give the missing pressure axis | Not accessed; best next target |
| PSI-69 FLEX | Droplet combustion; the variable is a burning-rate constant (mm²/s), not spread rate | Different physics; do not force into spread_rate_mm_s | Third-party description only, not verified |

Third-party note: a public Space Apps repo (YoussefHegazy74/flame-in-freefall) states that BASS/BASS-II publish test matrices and video rather than processed spread-rate tables, and that SAFFIRE-III/SAME data are engineering telemetry. That is consistent with what I found, but I have not verified it against PSI. Treat it as a pointer only.

## 3. Primary dataset recommendation
**Saffire-I/II results (Ferkul et al., Table I).** It is the only source I could verify that reports spread rate with flow and oxygen conditions and a stated source location. Why the others are weaker: BASS/BASS-II and FLEX could not be verified to contain per-test spread-rate numbers, and Saffire PSI telemetry needs analysis, not transcription.

## 4. Extraction rules applied
- oxygen_pct = the start-of-test value of the reported range (for example "21.7 to 21.5" gives 21.7); rows reported as "~22.1" keep 22.1 and the notes say "approximate". The paper says these values are derived from measured CO2 and referenced to the ISS initial reading.
- pressure_kpa left empty: this source does not report it. Never filled with 0.
- spread_rate_mm_s left empty where the source reports none (silicone, Nomex, thick PMMA). The thick PMMA regression rate (0.01 to 0.04 mm/s) is a different quantity and was kept only in the notes.
- 1-g Earth-gravity values in the same table appear only in the notes, labelled "1-g reference (NOT microgravity)".
- No unit conversions were needed (cm/s, mm/s and % are as reported), so UNIT_CONVERTED = 0 and DIGITIZED_ESTIMATE = 0.
- Not used: ignition power, because the same document gives 165 W on one slide and 182 W in Table I for Saffire-I.

## 5. Data quality report
| Measure | Count |
|---|---|
| Source documents extracted from | 1 |
| Experimental observations (rows) | 11 |
| DIRECTLY_REPORTED / UNIT_CONVERTED / DIGITIZED_ESTIMATE | 11 / 0 / 0 |
| Missing oxygen_pct | 0 |
| Missing pressure_kpa | 11 |
| Missing flow_cm_s | 0 |
| Missing spread_rate_mm_s | 7 (4 no-spread or non-burning; 3 not reported as a spread rate) |
| Missing source | 0 |
| Records with a numeric spread rate | 4 |

## 6. Scientific limitations
1. Only 4 numeric spread rates. That is too few for statistics or a risk ranking.
2. Two cotton-fiberglass tests at 20 cm/s differ in sample width (40.6 vs 5 cm) and O2 (21.7 vs ~22.1), so they are not clean repeats.
3. The Saffire duct is large and confined; published work reports Saffire spread rates well below those from the smaller BASS apparatus at similar O2 and flow. Do not mix BASS and Saffire numbers without noting that.
4. Pressure is not reported here. A source containing pressure is needed for the pressure axis.
5. Higher spread rate is not automatically higher risk. In this data silicone did not spread in microgravity but burned in 1-g, and Nomex did not ignite. Flammability limits and ignition matter as much as speed. The app therefore switches its risk ranking off below 20 measured records and shows observed outcomes instead.
6. The source is a conference slide deck, not the underlying data table.

## 7. Next research steps
1. Open PSI-25, PSI-26 and PSI-98 in a normal browser and list their downloadable files.
2. Read the PSI-25 publications list and Olson, Ruff and Miller SAE 2008-01-2005. Transcribe any tables of spread rate vs O2, pressure and flow, with table numbers. Use data_class UNIT_CONVERTED or DIGITIZED_ESTIMATE where applicable.
3. Re-run `python data/placeholder.py` after every addition.
