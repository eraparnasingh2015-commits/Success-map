# Test plan: can announcement-time data predict which clean-tech factories get cancelled?

Written and committed **before** running any model, so the pass mark cannot be tuned to the result.

## Question
Using only information available when a US clean-tech factory is announced, can we rank which
projects are later cancelled better than simple rules can?

## Data
Clean Investment Monitor 2026_Q2 (`data/raw/cim/`), facility file.

- **Main sample:** `Segment == Manufacturing`.
- **Secondary sample:** main sample plus industrial projects from the Energy and Industry segment
  (Carbon Management, Cement, Clean Fuels, Hydrogen, Iron & Steel, SAF, Pulp & Paper).
  Utility-scale solar, storage, wind and nuclear are excluded: those are power projects that Enverus already scores.
- **Announcement years:** 2018–2024. Later announcements have had too little time to be cancelled.

## Outcome
- `1` = Canceled prior to operation.
- `0` = Under Construction, Operating or Retired (the project got built or started building).
- Projects still `Announced` are **excluded**: their outcome is unknown.

## Inputs (known at announcement)
Technology, project type (new vs expansion/restart/retrofit), log estimated capex, announcement year,
state, party of the district's House representative, number of the state's senators who are Democrats.

Known weaknesses, accepted for this first pass:
- Estimated capex can be revised after announcement (possible leakage; also run without it).
- Political fields reflect the 119th Congress, not the one at announcement time.

Not used: company name, address, coordinates, subcategory (too sparse), anything about status.

## Models
1. Logistic regression (one-hot categories, scaled numbers).
2. Gradient-boosted trees.

## Baselines (the model must beat the best of these)
- **B1 technology rule:** score = cancellation rate of the project's technology in training data.
- **B2 size-and-newness rule:** score = log capex, plus a bonus for new builds.
- **B3 vintage rule:** score = cancellation rate of the project's announcement year in training data.

## Evaluation
- **Main:** repeated stratified 5-fold cross-validation (10 repeats). Metric: ROC AUC, and
  *recall in the top 30%*: the share of cancelled projects that land in the 30% the model rates riskiest.
- **Time check:** train on announcements 2018–2022, test on 2023–2024.

## Pass mark (decided in advance)
The signal is worth pursuing only if, on the **main sample**, the better model:
1. reaches cross-validated AUC **≥ 0.70**, **and**
2. beats the best baseline's AUC by **≥ 0.05**, **and**
3. puts **≥ 70%** of cancelled projects in its riskiest 30% (cross-validated).

The time check is reported but not part of the pass mark: its test set has too few cancellations
(about 26) for a reliable score.

## Interpretation rules
- **Fail:** this metadata alone holds little signal. That doesn't kill the idea: the warning signs most
  likely to matter (site, permits, customer contracts, finances) aren't in the data yet.
- **Pass:** worth the effort of adding those warning signs by hand for a sample of projects.
- Either way, the sample is small (about 60 cancellations), so results are indicative only.

## Result (first run, 2026-10-01)
Full output: `docs/cancellation-test-results.txt` (from `python3 scripts/cancellation_test.py`).

**FAIL on the pre-registered pass mark**, narrowly. Main sample, boosted trees:
AUC 0.763 (passes ≥ 0.70), beats the best baseline by +0.061 (passes ≥ 0.05),
but top-30% recall is 64.2% (fails ≥ 70%).

Notes:
- Most of the signal comes from project size and new-vs-expansion (baseline B2 alone: AUC 0.70).
- Without capex (possible leakage) the margin over B2 shrinks to +0.021.
- The secondary sample (adds industrial projects) scores higher (AUC about 0.79) but was not the pass-mark sample.
- The B3 vintage "100%" recall in the time check is an artefact: test years never appear in training,
  so every project gets the same score and ties all count as "top 30%". Ignore it.
