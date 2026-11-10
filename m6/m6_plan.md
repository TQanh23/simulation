# M6 plan (pre-registration): physics-aware virtual PWP sensor, blind transfer granite ↔ sandstone

Written 2026-11-10 before any M6 model was fit on the sandstone (T2) data. Only exploratory look at T2 so far: VWC/PWP/displacement tables printed every 5 min to define the windows below. Deviations go to `m6_deviations.md`, not into this file.

Data: Zenodo 10.5281/zenodo.19470865 (Li et al., CC BY 4.0), provenance THIRD_PARTY_SENSOR. T1 granite 2025-10-03, T2 sandstone 2025-12-18, rain 50 mm/h from record start (assumed t=0 = rain start). Files: Gr_medifilt_vwcdata10hz.csv, Gr_meanfilt_pwpdata_0.1hz.csv, Sandstone_data_vwc_mean(1hz).csv, Ss_meanfilt_pwpdata_0.1hz.csv (columns reordered to PWP-1..5: file order is 1,3,2,4,5 per Suction_1218avg.m). VWC column k and PWP column k = co-located sensor k# (assumption, per Fig. 7 layout). All series resampled to 10 s means.

## Question
Does a parsimonious physics-structured model, fit on one slope, predict the PWP response of the other slope's sensors better than data-driven baselines that see the same inputs?

## Inputs available to every model (causal)
Measured VWC θ(t) of the same sensor, u0 = mean PWP over the first 2 min, θr = mean VWC over the first 2 min, time since rain start t. Target: Δu(t) = u(t) − u0.

## Model M6 (physics)
S(t) = clip((θ(t) − θr) / (max_{s≤t} θ(s) − θr), 0, 1) when max_{s≤t}θ − θr ≥ 3 points, else 0 (no wetting yet).
Perched water storage: dh/dt = a·S^n − h/τ, h ≥ 0 (Euler, 10 s). Δu = h.
Three parameters (a, n, τ) shared by all sensors, fit by least squares on the training slope (bounds a∈[0,1] kPa/min, n∈[1,20], τ∈[1,1000] min).

## Baselines (same inputs, same training data)
B0 persistence: Δu = 0.
B1 Anh Nhật-style linear regression on VWC: Δu = b0 + b1·(θ − θr).
B2 gradient boosting (sklearn GBR, random_state 17, defaults) on [θ − θr, S, t].

## Windows
T1 granite: 0–280 min (failure at ~282 min).
T2 sandstone: per sensor, from 0 until the first of: 90 min, VWC falls >5 points below its running max, VWC < 5 % (sensor disturbed by sliding).

## Evaluation
Direction A: fit on T1 (all 5 sensors), predict T2. Direction B: fit on T2, predict T1. Metric: RMSE of Δu pooled over all sensor-samples in the target window; also per sensor.

## Pass rule (fixed now)
PASS if M6 pooled RMSE < min(B0, B1, B2) pooled RMSE in BOTH directions.
PARTIAL if it wins in exactly one direction.
FAIL otherwise. Any outcome is reported. No refitting or changing the model form after seeing results; any change is a new step (M6.1).

## Not claimed
No failure-time prediction, no soil-mechanics parameters, no field validity. Two experiments only.
