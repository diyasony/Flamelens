"""Creates a SYNTHETIC placeholder dataset so the app runs before you have real data.
Replace data/experiments.csv with real NASA data before submitting."""
import numpy as np, pandas as pd
rng = np.random.default_rng(7)
mats = {"Material A (thin fabric)": 1.0, "Material B (acrylic sheet)": 0.55,
        "Material C (cellulose paper)": 0.8, "Material D (coated fabric)": 0.3}
rows = []
for m, k in mats.items():
    for o2 in [15, 17, 19, 21, 23, 25]:
        for flow in [5, 20, 40]:
            for p in [60, 101]:
                base = max(0.0, (o2 - 15.5)) * 0.35 * k
                s = base * (1 + 0.004*flow) * (1.15 if p == 101 else 1.0)
                s = max(0.0, s + rng.normal(0, 0.08)) if base > 0 else 0.0
                rows.append([m, o2, p, flow, round(s, 3), "PLACEHOLDER - synthetic, replace with NASA data", ""])
df = pd.DataFrame(rows, columns=["material","oxygen_pct","pressure_kpa","flow_cm_s","spread_rate_mm_s","source","notes"])
df.to_csv("data/experiments.csv", index=False)
print(len(df), "rows written")
