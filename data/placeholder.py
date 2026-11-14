#!/usr/bin/env python3
"""FlameLens data utility: validates data/experiments.csv. It NEVER creates observations.

Usage (from the repo root or the data folder):
    python data/placeholder.py                 # validate data/experiments.csv
    python data/placeholder.py path/to/file.csv

What it does
- If the CSV is missing, creates an EMPTY template (header row only) and stops.
- Checks the required columns, numeric fields, missing values, duplicates, source references,
  physically invalid values, record classification, and leftover synthetic/placeholder markers.
- Prints a report and saves it to validation_report.txt next to the CSV.
- Exit code 0 = no errors (warnings allowed), 1 = errors found, 2 = template created.
"""
import sys
from pathlib import Path

import pandas as pd

REQUIRED = ["material", "oxygen_pct", "pressure_kpa", "flow_cm_s", "spread_rate_mm_s", "source", "notes"]
OPTIONAL = ["record_id", "experiment", "configuration", "outcome", "data_class", "source_location", "original_units"]
NUMERIC = ["oxygen_pct", "pressure_kpa", "flow_cm_s", "spread_rate_mm_s"]
DATA_CLASSES = {"DIRECTLY_REPORTED", "UNIT_CONVERTED", "DIGITIZED_ESTIMATE"}
SYNTHETIC_MARKERS = ("placeholder", "synthetic", "dummy", "fake", "lorem", "made up", "example data")


def create_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=REQUIRED + OPTIONAL).to_csv(path, index=False)


def validate(path: Path):
    errors, warnings, info = [], [], []
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    n = len(df)
    info.append(f"File: {path}")
    info.append(f"Total records (rows): {n}")

    # 1. columns
    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return errors, warnings, info
    if list(df.columns[: len(REQUIRED)]) != REQUIRED:
        warnings.append(f"The first {len(REQUIRED)} columns are not in the expected order {REQUIRED}.")
    extra = [c for c in df.columns if c not in REQUIRED + OPTIONAL]
    if extra:
        info.append(f"Additional (unrecognised) columns kept as-is: {extra}")
    if n == 0:
        warnings.append("File has a header but no records.")
        return errors, warnings, info

    blank = lambda s: s.str.strip() == ""

    # 2. numeric fields: blank = missing (allowed); anything else must be a number
    num = {}
    for c in NUMERIC:
        s = df[c].str.strip()
        parsed = pd.to_numeric(s.where(s != ""), errors="coerce")
        bad = df.index[(s != "") & parsed.isna()]
        if len(bad):
            errors.append(f"{c}: non-numeric entries in rows {[int(i) + 2 for i in bad]} "
                          f"(use an empty cell for missing, not text such as 'n/a').")
        num[c] = parsed

    # 3. physical validity
    for c in NUMERIC:
        if num[c].isna().all():
            warnings.append(f"{c} is empty for ALL records (not reported by the source). Visuals and filters "
                            f"that depend on it will have nothing to show.")
        neg = df.index[num[c] < 0]
        if len(neg):
            errors.append(f"{c}: negative values in rows {[int(i) + 2 for i in neg]}.")
        zero = df.index[num[c] == 0]
        if len(zero):
            warnings.append(f"{c}: zero in rows {[int(i) + 2 for i in zero]}. Confirm zero was actually "
                            f"measured and is not a coded 'missing/no-spread'.")
    over = df.index[num["oxygen_pct"] > 100]
    if len(over):
        errors.append(f"oxygen_pct above 100 in rows {[int(i) + 2 for i in over]}.")

    # 4. source references
    src = df["source"].str.strip()
    no_src = df.index[src == ""]
    if len(no_src):
        errors.append(f"source missing in rows {[int(i) + 2 for i in no_src]} (every record must be traceable).")
    not_url = df.index[(src != "") & ~src.str.lower().str.startswith(("http://", "https://"))]
    if len(not_url):
        warnings.append(f"source is not a URL in rows {[int(i) + 2 for i in not_url]}.")

    # 5. synthetic / placeholder markers anywhere in text columns
    text = df[["material", "source", "notes"]].agg(" ".join, axis=1).str.lower()
    hit = df.index[text.apply(lambda t: any(m in t for m in SYNTHETIC_MARKERS))]
    if len(hit):
        errors.append(f"Possible synthetic/placeholder text in rows {[int(i) + 2 for i in hit]}. "
                      f"Do not submit these as NASA data.")
    if blank(df["material"]).any():
        errors.append("material is empty in some rows.")

    # 6. duplicates
    dup_full = df.index[df.duplicated(keep="first")]
    if len(dup_full):
        errors.append(f"Exact duplicate rows: {[int(i) + 2 for i in dup_full]}.")
    if "record_id" in df.columns:
        ids = df["record_id"].str.strip()
        d = df.index[(ids != "") & ids.duplicated(keep="first")]
        if len(d):
            errors.append(f"Duplicate record_id in rows {[int(i) + 2 for i in d]}.")
        if (ids == "").any():
            warnings.append("Some records have no record_id.")
    else:
        warnings.append("No record_id column: records are harder to trace back to the source.")

    # 7. classification
    if "data_class" in df.columns:
        cls = df["data_class"].str.strip()
        bad_cls = df.index[~cls.isin(DATA_CLASSES)]
        if len(bad_cls):
            errors.append(f"data_class must be one of {sorted(DATA_CLASSES)}; invalid in rows "
                          f"{[int(i) + 2 for i in bad_cls]}.")
        for k in sorted(DATA_CLASSES):
            info.append(f"  {k}: {(cls == k).sum()}")
        if (cls == "DIGITIZED_ESTIMATE").any():
            warnings.append("DIGITIZED_ESTIMATE records present: keep them visibly separate from reported values.")
    else:
        warnings.append("No data_class column (DIRECTLY_REPORTED / UNIT_CONVERTED / DIGITIZED_ESTIMATE).")

    # 8. summary counts
    info.append("Missing values:")
    for c in NUMERIC:
        info.append(f"  {c}: {int(num[c].isna().sum())} of {n}")
    info.append(f"  source: {int(blank(df['source']).sum())} of {n}")
    info.append(f"Distinct source documents referenced: {src[src != ''].nunique()}")
    info.append(f"Records with a numeric spread rate: {int(num['spread_rate_mm_s'].notna().sum())}")
    if "outcome" in df.columns:
        info.append("Outcomes: " + ", ".join(f"{k}={v}" for k, v in df["outcome"].value_counts().items()))
    return errors, warnings, info


def main(argv):
    default = Path(__file__).resolve().parent / "experiments.csv"
    path = Path(argv[1]) if len(argv) > 1 else default
    if not path.exists():
        create_template(path)
        print(f"{path} did not exist. Created an EMPTY template (header only). "
              f"Add real, sourced records, then re-run.")
        return 2
    errors, warnings, info = validate(path)
    lines = ["=== FlameLens data validation report ==="] + info + [""]
    lines += [f"ERRORS ({len(errors)})"] + [f"  - {e}" for e in errors]
    lines += [f"WARNINGS ({len(warnings)})"] + [f"  - {w}" for w in warnings]
    lines += ["", "RESULT: " + ("FAIL" if errors else "PASS (review warnings)")]
    report = "\n".join(lines)
    print(report)
    (path.parent / "validation_report.txt").write_text(report + "\n", encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
