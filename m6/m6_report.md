# M6: cảm biến ảo PWP có ràng buộc vật lý, chuyển giao mù granite ↔ sa thạch

Kế hoạch đăng ký trước: `m6_plan.md` (commit `da513b2`). Sai khác so với kế hoạch: `m6_deviations.md`. Dữ liệu: Zenodo 10.5281/zenodo.19470865 (Li và cộng sự, CC BY 4.0), nguồn THIRD_PARTY_SENSOR. T1 = mái dốc granite, T2 = mái dốc sa thạch.

## Kết quả (RMSE gộp của ΔPWP, kPa)

| Chiều | M6 | B0 (giữ nguyên) | B1 (tuyến tính theo VWC) | B2 (GBR) | M6 thắng? |
|---|---|---|---|---|---|
| A: fit T1 → dự đoán T2 | **0,536** | 0,628 | 0,541 | 0,596 | có |
| B: fit T2 → dự đoán T1 | 0,621 | **0,353** | 0,561 | 0,935* | không |

**Gate: PARTIAL** (M6 chỉ thắng ở chiều A). \*Lần chạy cloud cho 0,938; xem D1 trong `m6_deviations.md`. Gate không đổi. RMSE từng cảm biến: `results/m6_*_per_sensor.csv`.

## Tham số M6 (dh/dt = a·Sⁿ − h/τ)

| Fit trên | a (kPa/phút) | n | τ (phút) |
|---|---|---|---|
| T1 granite | 0,0214 | 20,0 (chạm cận trên) | 10,67 |
| T2 sa thạch | 0,0767 | 13,26 | 10,78 |

## Kết luận

τ ≈ 11 phút chuyển được giữa hai loại đá: fit độc lập trên mỗi thí nghiệm đều cho τ ≈ 10,7–10,8 phút. Việc PWP dương có hình thành hay không thì không chuyển được. Ở granite, PWP tuyệt đối của 4#/5# vẫn âm suốt cửa sổ đánh giá dù VWC đã lên mức bão hòa (hình 3). Mô hình fit trên sa thạch vì vậy dự đoán ΔPWP dương ở các cảm biến này, và thua B0 ở chiều B. Ở chiều A, không mô hình nào bắt được bước nhảy PWP đột ngột của sa thạch 2# (khoảng phút 29) và 3# (khoảng phút 73) (hình 1).

## Giới hạn

- Chỉ có 2 thí nghiệm, mỗi thí nghiệm 5 cảm biến. Không có thống kê lặp lại.
- Giả định t = 0 là lúc bắt đầu mưa (50 mm/h từ đầu bản ghi).
- Giả định cột VWC thứ k và cột PWP thứ k đo cùng một vị trí (cảm biến k#).
- Không dự đoán thời điểm phá hoại, không suy ra tham số cơ học đất, không áp dụng cho hiện trường.
- Dữ liệu là THIRD_PARTY_SENSOR, đo trong thí nghiệm mô hình mái dốc trong phòng.

Hình: `results/m6_fig1_T2_pred.png`, `results/m6_fig2_T1_pred.png`, `results/m6_fig3_vwc_pwp.png`. Chạy lại: `python m6/run_m6.py data_external/guangdong m6/results`, sau đó `python m6/plot_m6.py data_external/guangdong m6/results`.
