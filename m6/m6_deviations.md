# M6 deviations

## D1: B2 pooled RMSE, direction B, differs from the cloud run (2026-11-10)

- Expected (cloud run): B2 pooled RMSE, direction B (fit T2 → predict T1) = 0.938.
- Local run: 0.9348 (|Δ| ≈ 0.003, above the 1e-3 reproduction tolerance).
- All other values match to 3 decimals: direction A M6 0.536 / B0 0.628 / B1 0.541 / B2 0.596; direction B M6 0.621 / B0 0.353 / B1 0.561. Gate = PARTIAL in both runs.
- Likely cause: package versions (GradientBoostingRegressor splits are sensitive to tiny floating-point differences). Local environment in `m6_environment.json`; cloud versions not recorded, so this is not verified.
- Action: none. Model, code and data unchanged; local value is reported as is. The gate outcome does not depend on it (M6 loses direction B to B0 = 0.353 either way).
