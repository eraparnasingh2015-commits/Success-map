"""Run the pre-registered phase-2 test in docs/cancellation-test-plan-phase2.md."""
import pathlib
import sys

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cancellation_test import load  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIGNS = ["site_secured", "state_incentives", "federal_support", "customer_named",
         "company_stage", "foreign_parent_china"]
META_CAT = ["Technology", "is_new", "State", "rep_party"]
META_NUM = ["log_capex", "year", "dem_senators"]


def dataset():
    meta = load("main")
    sample = pd.read_csv(ROOT / "data/phase2/sample_with_outcome.csv")[["unique_id", "group"]]
    coding = pd.read_csv(ROOT / "data/phase2/coding.csv")
    df = sample.merge(meta, on="unique_id").merge(coding, on="unique_id")
    assert len(df) == 120, len(df)
    assert (df.y == df.group.eq("cancelled")).all()
    return df


def model(cat, num):
    parts = [("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), cat)]
    if num:
        parts.append(("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num))
    return make_pipeline(ColumnTransformer(parts),
                         LogisticRegression(C=0.5, max_iter=2000, class_weight="balanced"))


def cv_auc(df, cat, num):
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=0)
    aucs = []
    for tr, te in cv.split(df, df.y):
        m = model(cat, num).fit(df.iloc[tr][cat + num], df.y.iloc[tr])
        aucs.append(roc_auc_score(df.y.iloc[te], m.predict_proba(df.iloc[te][cat + num])[:, 1]))
    return np.mean(aucs), np.std(aucs)


def main():
    df = dataset()
    print(f"{len(df)} projects, {df.y.sum()} cancelled\n")

    print("Cancellation rate by warning sign (descriptive):")
    for col in SIGNS:
        t = df.groupby(col).y.agg(["mean", "size"])
        print(f"  {col}: " + ", ".join(f"{k} {r['mean']:.0%} (n={int(r['size'])})" for k, r in t.iterrows()))

    results = {
        "M0 metadata only": cv_auc(df, META_CAT, META_NUM),
        "M1 warning signs only": cv_auc(df, SIGNS, []),
        "M2 combined": cv_auc(df, META_CAT + SIGNS, META_NUM),
    }
    print("\nCross-validated AUC (5-fold x 10 repeats):")
    for name, (mean, sd) in results.items():
        print(f"  {name:24} {mean:.3f}  (sd {sd:.3f})")

    m0, m2 = results["M0 metadata only"][0], results["M2 combined"][0]
    checks = [m2 >= 0.80, m2 - m0 >= 0.05]
    print(f"\nPASS MARK: M2 AUC>=0.80 {checks[0]} ({m2:.3f}); M2 beats M0 by >=0.05 {checks[1]} "
          f"({m2 - m0:+.3f}) -> {'PASS' if all(checks) else 'FAIL'}")

    print("\nExploratory (not part of the pass mark):")
    for name, cols in [("company_stage only", ["company_stage"]),
                       ("signs without company_stage", [c for c in SIGNS if c != "company_stage"]),
                       ("metadata without State", None)]:
        if cols is None:
            mean, sd = cv_auc(df, ["Technology", "is_new", "rep_party"], META_NUM)
        else:
            mean, sd = cv_auc(df, cols, [])
        print(f"  {name:28} {mean:.3f}  (sd {sd:.3f})")


if __name__ == "__main__":
    main()
