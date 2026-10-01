# Data

## `raw/cim/` — Clean Investment Monitor (US)

- **Source:** Clean Investment Monitor, Rhodium Group & MIT CEEPR — https://www.cleaninvestmentmonitor.org
- **Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (per the site's Terms & Conditions).
- **Version:** `2026_Q2.20260805.0`, downloaded 2026-10-01 via `scripts/fetch_cim.py`.
- **Key file:** `manufacturing_energy_and_industry_facility_metadata.csv` — one row per facility.
  The first 5 lines are a title block; read with `skiprows=5`. Field definitions are in `README.txt`.

Refresh with `python3 scripts/fetch_cim.py`.
