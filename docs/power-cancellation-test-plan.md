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

## Amendment 1 (made after the first run, recorded honestly)

The first run scored AUC 0.99, which was a leak, not a signal. For cancelled power projects CIM
overwrites `Project_Type` with "Cancelled", so `is_new` encoded the outcome (324 of 328 cancelled
projects were "not new"). `is_new` is removed from the features and baseline B2 becomes size
only. Everything else is unchanged. The factory test was checked and does not have this leak
(cancelled factories keep "New"/"Expansion").

## Result (after amendment 1)

Main sample: 5,521 projects, 328 cancelled (5.9%). Full output: docs/power-cancellation-test-results.txt

| Check | Pass mark | Result |
|---|---|---|
| Best model AUC (boosted, cross-validated) | >= 0.70 | 0.798, pass |
| Beats best baseline (state rate 0.717) | by >= 0.05 | +0.081, pass |
| Top-30% recall | >= 70% | 76.6%, pass |

**Formally PASS, but the time check undercuts it.** Trained on 2018-21 and tested on 2022-23
(the way a product would actually be used), size alone scores AUC 0.740 and beats both
models (logistic 0.683, boosted 0.619). The sensitivity sample shows the same pattern
(size 0.825 vs models 0.80). So the cross-validated edge comes from mixing years (state and
local-politics patterns that change over time), and it does not carry forward.

Plain reading: in public data, "bigger projects and battery projects cancel more often" is
most of what can be said ahead of time, and that is a rule of thumb, not a product. A
model that cannot beat project size on future projects is not something a buyer would pay
for. Combined with the factory result and existing paid players (e.g. Enverus), the wedge
stays dropped unless private, announcement-time data (interconnection-queue position,
permits, offtake contracts) becomes available.
