# Phase 2 test plan: do hand-collected warning signs predict cancellation?

Written and committed **before** collecting any project facts. Follows the narrow fail in phase 1
(`docs/cancellation-test-plan.md`).

## Sample
From the phase-1 main sample (US clean-tech manufacturing, announced 2018–2024, outcome known):
- **all 60 cancelled projects**, and
- **60 built projects** (under construction, operating or retired), drawn at random (seed 42),
  matched to the cancelled projects by announcement year so vintage can't drive the result.

The sample is produced by `scripts/phase2_sample.py` → `data/phase2/sample.csv`.

## Warning signs to record (as of the announcement, or within 90 days after it)
| Field | Values | Rule |
|---|---|---|
| `site_secured` | yes / no / unknown | Land bought or leased, or an existing site/building named. Expansions at an existing plant count as yes. A shortlist of possible sites counts as no. |
| `state_incentives` | yes / no / unknown | A state or local incentive package (grants, tax abatements, land) announced. |
| `federal_support` | yes / no / unknown | A named DOE loan, DOE grant, or 48C tax-credit award tied to this project. General reliance on IRA production credits does **not** count. |
| `customer_named` | yes / no / unknown | A named buyer, supply agreement, or offtake contract; or the plant is owned by (or a joint venture with) its main customer, e.g. an automaker's battery plant. |
| `company_stage` | established / startup | Established = public company or subsidiary of one, or private with clear revenue at scale. Startup = pre-revenue or early-revenue venture-backed. |
| `foreign_parent_china` | yes / no | Owner or a JV partner headquartered in China. |

## Avoiding hindsight
- Only facts dated **up to 90 days after the announcement date** count. Each recorded fact keeps its source and date.
- `unknown` is used when nothing dated within the window says either way; it is **not** filled in from later knowledge.
- **Known limitation:** the person coding (Claude) knows each project's outcome, so coding is not blind.
  To limit this, rules are fixed above and every value cites a dated source that can be audited.
  A blind re-check of a random 20% by someone who doesn't know the outcomes is recommended before relying on results.

## Models and comparison (same 120 projects, repeated stratified 5-fold CV, 10 repeats)
- **M0 metadata only:** the phase-1 inputs (technology, new/expansion, log capex, year, state, politics).
- **M1 warning signs only:** the six fields above.
- **M2 combined:** M0 + M1.
- Model type: logistic regression (small sample; trees would overfit). `unknown` is its own category.

## Pass mark (decided in advance)
The wedge is worth pursuing only if **M2**:
1. reaches cross-validated AUC **≥ 0.80**, **and**
2. beats **M0** on the same projects by **≥ 0.05** AUC.

Top-30% recall isn't used here: with a 50/50 sample its maximum is 60%, so the phase-1 threshold doesn't apply.

## Interpretation
- **Pass:** hand-collected signs add real predictive value → worth checking buyers and how to collect these signs at scale.
- **Fail:** cancellations in this data aren't predictable enough from announcement-time facts → stop this wedge.
