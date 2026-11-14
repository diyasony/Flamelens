# FlameLens – AI Testing Results

**Project:** FlameLens – AI-Powered Fire Safety Insights from Microgravity Combustion Data  
**Challenge:** NASA Space Apps Challenge 2026 – Flame in Freefall  
**Testing Date:** 14 November 2026  
**Testing Mode:** Rule-Based Offline Fallback

## 1. AI Question Testing – Task 1

A total of 15 questions were tested using the application's rule-based question-answering system.

| No. | Test Question | Expected Result | Status |
|---|---|---|---|
| 1 | Which material has the highest average flame spread rate? | Explains that only cotton-fiberglass has numerical measurements and a reliable material comparison is not possible. | PASS |
| 2 | Which material has the lowest average flame spread rate? | Explains that the available data is insufficient for a reliable material ranking. | PASS |
| 3 | What is the highest flame spread rate recorded? | 2.6 mm/s – SAFFIRE-2-6. | PASS |
| 4 | What is the lowest flame spread rate recorded? | 1.3 mm/s – SAFFIRE-1-2. | PASS |
| 5 | What is the average flame spread rate? | 1.95 mm/s, calculated from 4 numerical measurements. | PASS |
| 6 | Which experiment recorded the highest oxygen concentration? | Approximately 22.1%, in multiple SAFFIRE-2 records. | PASS |
| 7 | Which experiment recorded the lowest oxygen concentration? | Approximately 21.5% – SAFFIRE-1-2. | PASS |
| 8 | Which material has the highest average spread under low oxygen conditions? | Below 22% oxygen, average spread is 1.55 mm/s, based on 2 measurements. | PASS |
| 9 | How does oxygen concentration affect flame spread? | Explains that the limited dataset cannot establish a reliable causal relationship. | PASS |
| 10 | Compare cotton-fiberglass and silicone. | Shows numerical measurements for cotton-fiberglass and reports no numerical spread rates for silicone. | PASS |
| 11 | Which experiment had the highest pressure? | Explains that pressure measurements are unavailable for all 11 records. | PASS |
| 12 | How does airflow affect flame spread? | Displays available airflow-group averages and warns that a causal relationship cannot be established. | PASS |
| 13 | How many experimental records are available? | 11 records. | PASS |
| 14 | What are the major observations from the dataset? | Summarizes the available measurements, missing data, and dataset limitations. | PASS |
| 15 | What happens when experimental data is missing? | Explains that missing values are excluded from calculations and are not treated as zero. | PASS |

**Result:** 15/15 question tests passed in rule-based offline mode.

## 2. AI Insights Testing – Task 2

The Generate Insight feature was tested.

The generated insights correctly displayed:
- Total experimental records: 11
- Records with numerical spread rates: 4
- Missing spread rates: 7
- Missing pressure measurements: 11
- Highest recorded spread rate: 2.6 mm/s
- Lowest recorded spread rate: 1.3 mm/s
- Average of numerical measurements: 1.95 mm/s

The application also displayed important limitations, including the small dataset size, missing measurements, and inability to establish reliable oxygen or airflow effects.

**Result: PASS**

## 3. Sidebar Filter Testing – Task 3

The material filter in the sidebar was tested by selecting only Cotton-fiberglass fabric (SIBAL).

The generated insights updated according to the selected material:
- Records displayed: 4
- Numerical spread measurements: 4
- Missing spread measurements: 0
- Average spread rate: 1.95 mm/s
- Highest spread rate: 2.6 mm/s
- Lowest spread rate: 1.3 mm/s

The filter was then restored to include all available materials.

**Result: PASS**

## 4. Dataset Limitations

- The dataset contains only 11 experimental records.
- Only 4 records contain numerical flame spread measurements.
- 7 spread-rate values are missing.
- Pressure measurements are unavailable for all 11 records.
- The available data is insufficient for reliable material risk ranking.
- Oxygen and airflow effects cannot be established conclusively.
- The below-22% oxygen cutoff used in one test is an analysis choice, not a predefined NASA threshold.

Missing measurements are not treated as zero.

## 5. Important Implementation Note

The application was tested using its rule-based offline fallback because an Anthropic API key was not configured.

Therefore, these results validate the deterministic question-answering and insight-generation logic. They do not validate live Claude API or LLM integration.

## 6. Conclusion

All 15 predefined question tests passed in offline rule-based mode. The AI Insights feature and sidebar material filtering also worked as expected.

FlameLens presents the available microgravity combustion observations while communicating data limitations and avoiding unsupported conclusions.