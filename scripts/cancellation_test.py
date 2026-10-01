"""Run the pre-registered cancellation test in docs/cancellation-test-plan.md."""
import pathlib

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = pathlib.Path(__file__).resolve().parent.parent
FACILITIES = ROOT / "data/raw/cim/CleanInvestmentMonitor_Download/manufacturing_energy_and_industry_facility_metadata.csv"
INDUSTRIAL = {"Carbon Management", "Cement", "Clean Fuels", "Hydrogen", "Iron & Steel", "SAF", "Pulp & Paper"}
BUILT = {"Under Construction", "Operating", "Retired"}
CATEGORICAL = ["Technology", "is_new", "State", "rep_party"]
NUMERIC = ["log_capex", "year", "dem_senators"]


def load(sample):
    df = pd.read_csv(FACILITIES, skiprows=5, low_memory=False)
    keep = df.Segment.eq("Manufacturing")
    if sample == "secondary":
        keep |= df.Segment.eq("Energy and Industry") & df.Technology.isin(INDUSTRIAL)
    df = df[keep].copy()
    df["year"] = pd.to_datetime(df.Announcement_Date, errors="coerce", format="mixed").dt.year
    df = df[df.year.between(2018, 2024)]
    df = df[df.Current_Facility_Status.isin(BUILT | {"Canceled prior to operation"})]
    df["y"] = df.Current_Facility_Status.eq("Canceled prior to operation").astype(int)
    df["is_new"] = df.Project_Type.eq("New").map({True: "new", False: "not_new"})
    df["log_capex"] = np.log1p(df.Estimated_Total_Facility_CAPEX)
    df["rep_party"] = df["US Representative Party"].fillna("unknown")
    df["dem_senators"] = (df["US Senator 1: Party"].eq("Democratic").astype(int)
                          + df["US Senator 2: Party"].eq("Democratic").astype(int))
    return df.reset_index(drop=True)


def model(kind, numeric):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), CATEGORICAL),
        ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric),
    ])
    if kind == "logistic":
        est = LogisticRegression(C=0.5, max_iter=2000, class_weight="balanced")
    else:
        est = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                             class_weight="balanced", random_state=0)
        pre.set_params(sparse_threshold=0)
    return make_pipeline(pre, est)


def rate_rule(train, test, col):
    rates = train.groupby(col).y.mean()
    return test[col].map(rates).fillna(train.y.mean()).to_numpy()


def baselines(train, test):
    size = test.log_capex.fillna(train.log_capex.median()) + 2 * test.is_new.eq("new")
    return {"B1 technology": rate_rule(train, test, "Technology"),
            "B2 size+new": size.to_numpy(),
            "B3 vintage": rate_rule(train, test, "year")}


def recall_top30(y, score):
    cutoff = np.quantile(score, 0.70)
    top = score >= cutoff
    return (top & (y == 1)).sum() / max((y == 1).sum(), 1)


def evaluate(df, numeric):
    scores = {}
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=0)
    for tr, te in cv.split(df, df.y):
        train, test = df.iloc[tr], df.iloc[te]
        results = baselines(train, test)
        for kind in ("logistic", "boosted"):
            m = model(kind, numeric).fit(train[CATEGORICAL + numeric], train.y)
            results[kind] = m.predict_proba(test[CATEGORICAL + numeric])[:, 1]
        for name, s in results.items():
            scores.setdefault(name, []).append((roc_auc_score(test.y, s), recall_top30(test.y.to_numpy(), s)))
    return {k: np.mean(v, axis=0) for k, v in scores.items()}


def time_check(df, numeric):
    train, test = df[df.year <= 2022], df[df.year >= 2023]
    out = {}
    results = baselines(train, test)
    for kind in ("logistic", "boosted"):
        m = model(kind, numeric).fit(train[CATEGORICAL + numeric], train.y)
        results[kind] = m.predict_proba(test[CATEGORICAL + numeric])[:, 1]
    for name, s in results.items():
        out[name] = (roc_auc_score(test.y, s), recall_top30(test.y.to_numpy(), s))
    return out, int(test.y.sum()), len(test)


def report(title, res):
    print(f"\n{title}")
    print(f"  {'method':16} {'AUC':>6} {'top-30% recall':>15}")
    for name, (auc, rec) in sorted(res.items(), key=lambda kv: -kv[1][0]):
        print(f"  {name:16} {auc:6.3f} {rec:15.1%}")


def main():
    for sample in ("main", "secondary"):
        df = load(sample)
        print(f"\n=== {sample} sample: {len(df)} projects, {df.y.sum()} cancelled ({df.y.mean():.1%}) ===")
        main_res = evaluate(df, NUMERIC)
        report("Cross-validated (with capex)", main_res)
        report("Cross-validated (without capex)", evaluate(df, ["year", "dem_senators"]))
        tc, n_cancel, n = time_check(df, NUMERIC)
        report(f"Time check: train 2018-22, test 2023-24 ({n} projects, {n_cancel} cancelled)", tc)
        if sample == "main":
            best_model = max(("logistic", "boosted"), key=lambda k: main_res[k][0])
            auc, rec = main_res[best_model]
            best_base = max(v[0] for k, v in main_res.items() if k.startswith("B"))
            checks = [auc >= 0.70, auc - best_base >= 0.05, rec >= 0.70]
            print(f"\nPASS MARK ({best_model}): AUC>=0.70 {checks[0]}, beats best baseline by >=0.05 "
                  f"{checks[1]} ({auc - best_base:+.3f}), top-30% recall>=70% {checks[2]} -> "
                  f"{'PASS' if all(checks) else 'FAIL'}")


if __name__ == "__main__":
    main()
