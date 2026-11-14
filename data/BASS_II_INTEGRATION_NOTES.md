# BASS-II oxygen integration notes

## What changed
Merged `OXYGEN_SEGMENT_DATA.csv` into `BASS_II_OBSERVATIONS.csv` using the exact composite key:
- `parent_test_no` = `test_id`
- `segment_no`
- `flow_cm_s` = `listed_flow_cm_s`

The merge was one-to-one for all 39 existing observation rows.

## Values inserted
- M8 / segment 1 / 10 cm/s: 18.99 vol%, ±0.05 vol%, figure-derived estimate.
- M8 / segment 2 / 6 cm/s: 18.72 vol%, ±0.05 vol%, figure-derived estimate.
- M8 / segment 3 / 5 cm/s: 18.39 vol%, ±0.05 vol%, figure-derived estimate.
- M9 / segment 1 / 14 cm/s: 17.78 vol%, ±0.10 vol%, **LOW confidence** estimate.

The M8 calculation uses the linear oxygen-profile assumption described in NASA Section 5.4 and segment boundaries digitised from Figure 5.2. The M9 estimate uses a rounded operator narrative from Table A.4 and an assumed 108–1008 s segment window; it is not confirmed by a figure.

## Added columns
- `o2_segment_uncertainty_pct`
- `o2_segment_confidence`
- `o2_segment_source`
- `o2_segment_start_s`
- `o2_segment_end_s`
- `o2_segment_value_class`
- `o2_missing_information`

Existing `o2_initial_pct` and `o2_final_pct` values were retained. Unrecoverable segment means remain blank and are classified `NOT_RECOVERABLE`.

## Important pairing limitation
The oxygen source file has 43 flow-segment rows, but the existing paired observation file has 39 rows. Four oxygen source rows (M6 and M12) have no matching observation because Table 5.1 reports "Not tracked" rather than one spread-rate value per listed flow. These were not inserted as paired observations.

## Files deliberately not changed
- `experiments.csv` (Saffire)
- `app.py`
- `BASS_II_RAW.csv`
- `placeholder.py`

## Validation
See `DATA_QUALITY_REPORT.txt` for counts, missing-value checks, duplicate checks and limitations.
