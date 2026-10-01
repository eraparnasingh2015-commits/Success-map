# Test plan: "proving your case to a more powerful party"

Written and committed **before** the research, so the scoring can't be tuned to the findings.

## The theme
Individuals or small firms lose disputes with a larger party (insurer, landlord, platform, agency, airline)
because they can't assemble the right evidence in the right form in time. Hypothesis: a tool that helps them
build and file the case would capture real value.

## Segments tested
1. Health-insurance claim denials (US)
2. Home-insurance claims (US)
3. Rental security deposits (US)
4. Gig-platform deactivations (US)
5. Disability benefit claims, SSDI (US)
6. Air-passenger compensation (EU261) and refunds
7. Medical-bill errors and disputes (US)
8. Online-marketplace seller suspensions (Amazon)

## Scoring (each 0–2; total out of 12)
| Criterion | 2 | 1 | 0 |
|---|---|---|---|
| **A. Appeal gap** | Few people challenge (<20%) **and** challenges often win (≥40%) | One of the two holds | Neither, or no data |
| **B. Money at stake per case** | ≥ $1,000 typical | $100–1,000 | < $100 |
| **C. Proof people pay** | Paid intermediaries exist and charge meaningful fees (contingency %, flat fees) | Some paid help, small | Only free help |
| **D. Evidence decides the outcome** | Documented: better evidence/representation clearly changes win rates | Plausible but undocumented | Outcome mostly discretionary/arbitrary |
| **E. Room for a new tool** | No dominant DIY tool for the claimant | Some tools, none dominant | Crowded |
| **F. Legal/regulatory barrier** | Low (claimant can self-file; tools allowed) | Some limits | Strong limits (e.g. rules on who may charge or give advice) |

## Decision rule (decided in advance)
- A segment is a **candidate** if it scores **≥ 9/12 with A ≥ 1 and E ≥ 1**.
- The theme passes if **at least 2 segments** are candidates. Then the next step is buyer interviews in the top segment.
- If none qualify, stop the theme.

Facts come from web search summaries and are cited; figures are approximate.

## Result (2026-10-01)

| Segment | A gap | B $ | C pays | D evidence | E room | F barrier | Total | Candidate? |
|---|---|---|---|---|---|---|---|---|
| 1 Health-insurance denials | 2 | 2 | 1 | 1 | 0 | 2 | 8 | No (E=0: Counterforce free, Claimable ~$40, others) |
| 2 Home-insurance claims | 2* | 2 | 2 | 2 | 2 | 0 | **10** | **Yes** |
| 3 Rental deposits | 1 | 1 | 0 | 1 | 1 | 2 | 6 | No |
| 4 Gig deactivations | 0 | 2 | 0 | 0 | 2 | 1 | 5 | No |
| 5 SSDI claims | 2 | 2 | 2 | 2 | 1 | 1 | **10** | **Yes** |
| 6 EU air compensation | 2 | 1 | 2 | 2 | 0 | 2 | 9 | No (E=0: AirHelp, Flightright etc.) |
| 7 Medical-bill disputes | 1 | 2 | 2 | 2 | 0 | 2 | 9 | No (E=0: Goodbill, Resolve, CareRoute etc.) |
| 8 Amazon seller suspensions | 1 | 2 | 2 | 1 | 0 | 2 | 8 | No (E=0: consultants + AI POA tools) |

\* Home-insurance appeal-rate figure ("fewer than 1 in 500 appeal") comes from a vendor page and may mix
health and property data; success-rate range 57–80% is also vendor-sourced. Treat A as provisional.

**Theme PASSES** (2 candidates ≥ 9 with A ≥ 1 and E ≥ 1): home-insurance claims and SSDI.

Key evidence:
- Home insurance: public adjusters charge 10–20% and a 2010 Florida study found policyholders using them got
  substantially higher payouts; claimant-side DIY tools are scarce (ClaimWizard serves adjusters, not homeowners).
  **But** in 46 states only licensed public adjusters or attorneys may advise or negotiate a claim for a fee, and
  20 states make unlicensed adjusting a crime. A product must be self-help documentation, not advice or negotiation,
  or be sold to licensed adjusters.
- SSDI: ~60% of denied applicants never appeal; hearing-level approval ~50%; represented claimants win ~2–3x as often;
  representatives work on contingency (25%, capped at $9,200). Competition is mainly contingency lawyers, who cost the
  claimant nothing upfront, which makes a paid consumer tool hard to sell.

Next step per plan: buyer interviews in the top segment.
