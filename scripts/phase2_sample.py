"""Draw the phase-2 sample: all cancelled projects plus year-matched built projects."""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cancellation_test import load  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data/phase2"


def main():
    df = load("main")
    cancelled = df[df.y == 1]
    built = df[df.y == 0]
    picks = []
    for year, n in cancelled.year.value_counts().items():
        pool = built[built.year == year]
        picks.append(pool.sample(min(n, len(pool)), random_state=42))
    sample = pd.concat([cancelled.assign(group="cancelled")] + [p.assign(group="built") for p in picks])
    cols = ["unique_id", "Company", "Technology", "Subcategory", "Project_Type", "State",
            "Announcement_Date", "Estimated_Total_Facility_CAPEX", "Address"]
    OUT.mkdir(parents=True, exist_ok=True)
    sample[cols + ["group"]].to_csv(OUT / "sample_with_outcome.csv", index=False)
    sample[cols].sample(frac=1, random_state=7).to_csv(OUT / "sample.csv", index=False)
    print(sample.group.value_counts().to_string())
    print(sample.groupby(["year", "group"]).size().unstack().to_string())


if __name__ == "__main__":
    main()
