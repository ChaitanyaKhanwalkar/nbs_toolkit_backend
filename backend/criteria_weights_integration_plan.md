# Criteria Weights Integration Plan

Use the **ensemble weights** from the final AHP + Fuzzy-AHP workbook.

## Rounding rule

- Store in code/database: **6 decimals**.
- Show in reports/presentation: **3 decimals**.
- Avoid storing 2 decimals because small criteria like C6 can be distorted and per-use-case sums may drift from 1.0.

## Active criteria

C5 is intentionally absent/inactive. Active criteria are C1, C2, C3, C4, C6, C7, C8.

### discharge_inland
| Code | Criterion | Type | Stored weight | Report display |
|---|---|---|---:|---:|
| C1 | treatment_fit | benefit | 0.258313 | 0.258 |
| C2 | standard_fit | benefit | 0.258313 | 0.258 |
| C3 | site_fit | benefit | 0.099705 | 0.100 |
| C4 | source_fit | benefit | 0.113906 | 0.114 |
| C6 | hydrologic_fit | benefit | 0.056103 | 0.056 |
| C7 | footprint | cost | 0.099755 | 0.100 |
| C8 | om | cost | 0.113906 | 0.114 |

### drinking
| Code | Criterion | Type | Stored weight | Report display |
|---|---|---|---:|---:|
| C1 | treatment_fit | benefit | 0.266800 | 0.267 |
| C2 | standard_fit | benefit | 0.266800 | 0.267 |
| C3 | site_fit | benefit | 0.106500 | 0.106 |
| C4 | source_fit | benefit | 0.121700 | 0.122 |
| C6 | hydrologic_fit | benefit | 0.058250 | 0.058 |
| C7 | footprint | cost | 0.058250 | 0.058 |
| C8 | om | cost | 0.121700 | 0.122 |

### irrigation
| Code | Criterion | Type | Stored weight | Report display |
|---|---|---|---:|---:|
| C1 | treatment_fit | benefit | 0.228136 | 0.228 |
| C2 | standard_fit | benefit | 0.228136 | 0.228 |
| C3 | site_fit | benefit | 0.095330 | 0.095 |
| C4 | source_fit | benefit | 0.117709 | 0.118 |
| C6 | hydrologic_fit | benefit | 0.057781 | 0.058 |
| C7 | footprint_land | cost | 0.117709 | 0.118 |
| C8 | om_energy_difficulty | cost | 0.155200 | 0.155 |

These irrigation values are the final working weights used in this report after
the 2026-06-30 crisp + fuzzy AHP O&M re-blend. They are not labelled
expert-validated unless explicit approval documentation is added to the repo.


## Backend integration

1. Add/populate `criteria_weights`.
2. Ensure `EngineDataRepository.list_criteria_weights(use_case)` returns:
   - `criterion_code`
   - `criterion_name`
   - `benefit_or_cost`
   - `weight`
3. Confirm train TOPSIS uses these weights.
4. Add tests confirming each use case has 7 criteria and sums to 1.0.
5. Add scenario tests for:
   - domestic sewage discharge
   - irrigation reuse
   - drinking strict case
   - industrial acidic high-order Mandleshwar safety case

## Uvicorn command

```powershell
$root = "C:\Users\Ecosoul Enviro\OneDrive\Desktop\NBSGCT"
Set-Location $root

Push-Location "$root\backend"
& "$root\backend.venv_canonical\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Pop-Location
```
