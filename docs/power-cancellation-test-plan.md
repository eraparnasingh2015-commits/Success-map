# Test plan: "Will this project happen?" for utility-scale power

Committed before any model is fitted. The only things looked at so far are row counts by
technology, status and announcement year (needed to define the sample).

## Why this sector

The factory test (docs/cancellation-test-plan.md, phase 1 and 2) failed, and it had only 60
cancellations. Utility-scale power in the same Clean Investment Monitor file (CIM, Rhodium/MIT,
CC BY 4.0, release 2026_Q2.20260805.0) has about 9,300 solar, battery and wind projects and
several hundred cancellations, so a real signal would show up if it exists.

## Known limits, stated up front

- For power, CIM's "announcement date" is the first month the project shows up in EIA-860M.
  Projects reach EIA-860M late, after most interconnection-queue attrition. So this tests
  "will a project that already reached EIA's planned list get built", not "will a queue
  request get built". The second question is the bigger one and is not testable with this file.
- No announcement-time status is available (same problem as phase 1). Features are things
  known at announcement: technology, state, size, new vs expansion, year, local politics.
- `unique_id` contains EIA-style numbers that trend with time and differ by status. It is
  excluded from all features to avoid leakage.
- Competitors already sell power-project completion estimates (e.g. Enverus). This test is
  about whether a signal exists, not about whether there is room in the market.

## Sample

- Main: Technology in {Solar, Storage, Wind}, Subcategory in {Solar Photovoltaic, Batteries,
  Onshore Wind Turbine}, announcement year 2018-2023, status known
  (Operating, Under Construction, Retired = built; "Canceled prior to operation" = cancelled).
  Projects still "Announced" are excluded. 2024+ is excluded because outcomes are not yet settled.
- Sensitivity (reported, not part of pass mark): projects announced 2018-2022 that are still
  "Announced" counted as cancelled (stalled).

## Models and baselines

- Features: Subcategory, State, is_new, rep_party (categorical); log_capex, year,
  dem_senators (numeric).
- Models: logistic regression and gradient boosting, same settings as scripts/cancellation_test.py.
- Baselines: B1 technology rate, B2 size + new, B3 vintage rate, B4 state rate.
- Evaluation: repeated stratified 5-fold CV (10 repeats), plus a time check
  (train 2018-2021, test 2022-2023).

## Pass mark (all three needed)

1. Best model AUC >= 0.70
2. Beats the best baseline AUC by >= 0.05
3. Top-30% recall >= 70% (the riskiest 30% of projects contain at least 70% of cancellations)

If it fails, the "will this project happen" wedge is dropped for power too, at least with
public announcement-time data.
