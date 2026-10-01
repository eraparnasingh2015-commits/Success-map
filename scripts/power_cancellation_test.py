"""Run the pre-registered test in docs/power-cancellation-test-plan.md."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from cancellation_test import FACILITIES, recall_top30, rate_rule, report

SUBCATS = {"Solar Photovoltaic", "Batteries", "Onshore Wind Turbine"}
BUILT = {"Under Construction", "Operating", "Retired"}
CANCELLED = "Canceled prior to operation"
# is_new is dropped (plan amendment 1): CIM sets Project_Type to "Cancelled" for cancelled
# power projects, so it leaks the outcome.
CATEGORICAL = ["Subcategory", "State", "rep_party"]
NUMERIC = ["log_capex", "year", "dem_senators"]


def load(sample):
    df = pd.read_csv(FACILITIES, skiprows=5, low_memory=False)
    df = df[df.Technology.isin({"Solar", "Storage", "Wind"}) & df.Subcategory.isin(SUBCATS)].copy()
    df["year"] = pd.to_datetime(df.Announcement_Date, errors="coerce", format="mixed").dt.year
    if sample == "main":
        df = df[df.year.between(2018, 2023) & df.Current_Facility_Status.isin(BUILT | {CANCELLED})]
        df["y"] = df.Current_Facility_Status.eq(CANCELLED).astype(int)
    else:  # sensitivity: still-"Announced" projects from 2018-2022 count as stalled
        df = df[df.year.between(2018, 2022)]
        df["y"] = df.Current_Facility_Status.isin({CANCELLED, "Announced"}).astype(int)
    df["log_capex"] = np.log1p(df.Estimated_Total_Facility_CAPEX)
    df["rep_party"] = df["US Representative Party"].fillna("unknown")
    df["dem_senators"] = (df["US Senator 1: Party"].eq("Democratic").astype(int)
                          + df["US Senator 2: Party"].eq("Democratic").astype(int))
    return df.reset_index(drop=True)


def model(kind):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), CATEGORICAL),
        ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUMERIC),
    ])
    if kind == "logistic":
        est = LogisticRegression(C=0.5, max_iter=2000, class_weight="balanced")
    else:
        est = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                             class_weight="balanced", random_state=0)
        pre.set_params(sparse_threshold=0)
    return make_pipeline(pre, est)


def score_all(train, test):
    out = {"B1 technology": rate_rule(train, test, "Subcategory"),
           "B2 size": test.log_capex.fillna(train.log_capex.median()).to_numpy(),
           "B3 vintage": rate_rule(train, test, "year"),
           "B4 state": rate_rule(train, test, "State")}
    for kind in ("logistic", "boosted"):
        m = model(kind).fit(train[CATEGORICAL + NUMERIC], train.y)
        out[kind] = m.predict_proba(test[CATEGORICAL + NUMERIC])[:, 1]
    return out


def evaluate(df):
    scores = {}
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=0)
    for tr, te in cv.split(df, df.y):
        test = df.iloc[te]
        for name, s in score_all(df.iloc[tr], test).items():
            scores.setdefault(name, []).append((roc_auc_score(test.y, s),
                                                recall_top30(test.y.to_numpy(), s)))
    return {k: np.mean(v, axis=0) for k, v in scores.items()}


def time_check(df):
    train, test = df[df.year <= 2021], df[df.year >= 2022]
    res = {name: (roc_auc_score(test.y, s), recall_top30(test.y.to_numpy(), s))
           for name, s in score_all(train, test).items()}
    return res, int(test.y.sum()), len(test)


def main():
    for sample in ("main", "sensitivity"):
        df = load(sample)
        print(f"\n=== {sample} sample: {len(df)} projects, {df.y.sum()} cancelled ({df.y.mean():.1%}) ===")
        print("Cancellation rate by technology:",
              ", ".join(f"{k} {v:.1%}" for k, v in df.groupby("Subcategory").y.mean().items()))
        print("Cancellation rate by year:",
              ", ".join(f"{int(k)} {v:.1%}" for k, v in df.groupby("year").y.mean().items()))
        res = evaluate(df)
        report("Cross-validated (5-fold x 10)", res)
        tc, n_cancel, n = time_check(df)
        report(f"Time check: train 2018-21, test 2022+ ({n} projects, {n_cancel} cancelled)", tc)
        if sample == "main":
            best = max(("logistic", "boosted"), key=lambda k: res[k][0])
            auc, rec = res[best]
            base = max(v[0] for k, v in res.items() if k.startswith("B"))
            checks = [auc >= 0.70, auc - base >= 0.05, rec >= 0.70]
            print(f"\nPASS MARK ({best}): AUC>=0.70 {checks[0]} ({auc:.3f}), beats best baseline by "
                  f">=0.05 {checks[1]} ({auc - base:+.3f}), top-30% recall>=70% {checks[2]} "
                  f"({rec:.1%}) -> {'PASS' if all(checks) else 'FAIL'}")


if __name__ == "__main__":
    main()
