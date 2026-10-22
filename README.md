# Dữ liệu chuyến đi – Đồ án tối ưu đường đi gom đơn hàng trong kho

## 1. Giới thiệu thư mục

| File | Mô tả |
|---|---|
| `trips_ml_v1.csv` | Dữ liệu chuẩn hóa từ `sample_trips.csv` (tuần 1), sẵn sàng cho ML |
| `validate_trips_csv.py` | Script kiểm tra tính hợp lệ của CSV (chạy trước khi training) |

## 2. Quy ước dữ liệu
- `is_simulated`: `1` = dữ liệu mô phỏng/thu thử, `0` = dữ liệu thực tế. Hiện tại toàn bộ 54 chuyến đều là `1`.
- `data_source`: danh mục chuẩn = `{osrm_api, openstreetmap, simulated, manual}`. Hiện tại toàn bộ là `osrm_api`.
- Đơn vị: khoảng cách = km, thờigian = phút, tốc độ = km/h.
- `actual_travel_time` = thờigian đi thực tế (cột gốc: `actual_duration_min`).
- `departure_time_full` = ngày + giờ xuất phát (`YYYY-MM-DD HH:MM:SS`).

## 3. Cách sử dụng
```bash
# Kiểm tra CSV trước khi đưa vào mô hình
python validate_trips_csv.py trips_ml_v1.csv
```

- Baseline (Quỳnh Phiếu): dùng cột `actual_travel_time` + `departure_time_full` (đã có sẵn để tương thích `baseline.py`).
- Khi bổ sung tuyến mới từ hàm OSRM của Hải My: cập nhật CSV → chạy lại validate → tăng version (v2).

## 4. Lịch sử phiên bản

| Version | Ngày | Ngườithực hiện | Thay đổi |
|---|---|---|---|
| v1 | 21/10/2026 | Thảo Vy | Chuẩn hóa cột cờ, đổi tên cột khớp baseline, 54 chuyến / 2 tuyến |

---

# BÁO CÁO THỐNG KÊ DỮ LIỆU CHUYẾN ĐI – TUẦN 2

| Thông tin | Chi tiết |
|---|---|
| **Ngườithực hiện** | Thảo Vy |
| **Ngày lập** | 21/10/2026 |
| **Dữ liệu phân tích** | `sample_trips.csv` (bộ dữ liệu thu thập tuần 1) |
| **Đối chiếu** | `baseline.py` của Quỳnh Phiếu (mô hình baseline theo trung bình tuyến) |

## 4.1. Tổng quan bộ dữ liệu

- **Tổng số chuyến:** 54 chuyến
- **Số tuyến đường:** 2 tuyến (R01, R02)
- **Thờigian thu thập:** 01/09/2026 → 30/09/2026
- **Nguồn dữ liệu:** OSRM (OpenStreetMap) ước lượng quãng đường; thờigian di chuyển thực tế ghi nhận theo mẫu thu thập tuần 1
- **Tính đầy đủ:** Không có giá trị thiếu ở tất cả các cột số và phân loại; cột `notes` chỉ ghi khi có sự kiện bất thường (37/54 chuyến để trống là bình thường)
- **Outlier:** Không phát hiện outlier theo phương pháp IQR trên `actual_duration_min` (ngưỡng cho phép: −3.6 đến 44.7 phút) → **dữ liệu sạch, không cần loại dòng nào**

> **Lưu ý:** Dãy `trip_id` bị khuyết 10 mã (T1002, T1017, T1018, T1021, T1029, T1032, T1040, T1041, T1045, T1048). Đây là các chuyến chưa thu thập được trong tuần 1, không phải lỗi nhập liệu.

## 4.2. Thống kê theo tuyến đường

| Tuyến | Số chuyến | Khoảng cách TB (km) | TG thực tế TB (phút) | TG OSRM TB (phút) | Tốc độ TB (km/h) | Hệ số trễ TB (thực/OSRM) |
|---|---|---|---|---|---|---|
| **R01** – Chợ Bến Thành → Landmark 81 | 27 | 12.51 | 23.77 | 12.60 | 34.54 | **1.89x** |
| **R02** – Sân bay TSN → ĐH Bách Khoa | 27 | 6.44 | 18.66 | 9.60 | 23.39 | **1.94x** |

**Nhận xét:** OSRM ước lượng thờigian di chuyển **thấp hơn thực tế khoảng 1.9 lần** trên cả hai tuyến. Đây chính là khoảng trống mà mô hình ML của nhóm cần bù — nếu mô hình ML đạt MAE nhỏ hơn MAE của OSRM thì mô hình có giá trị ứng dụng thực tế.

## 4.3. Thống kê theo khung giờ (time_slot)

| Khung giờ | Số chuyến | TG thực tế TB (phút) | Tốc độ TB (km/h) | Hệ số trễ TB |
|---|---|---|---|---|
| **1** – Sáng (6h–9h) | 13 | 25.35 | 23.89 | 2.23x |
| **2** – Trưa (9h–16h) | 11 | 15.36 | 35.28 | 1.40x |
| **3** – Giờ cao điểm (16h–19h) | 14 | **29.74** | **17.80** | **2.74x** |
| **4** – Tối (19h–23h) | 16 | 14.42 | 38.51 | 1.30x |

**Nhận xét:**
- Khung **giờ cao điểm chiều (slot 3)** là thờigian di chuyển tệ nhất: trung bình gần 30 phút, tốc độ chỉ 17.8 km/h, chậm gấp **2.74 lần** so với ước lượng OSRM.
- Khung **tối (slot 4)** thông thoáng nhất: tốc độ trung bình 38.5 km/h, nhanh hơn cả khung trưa.
- → Biến `time_slot` (hoặc `hour_of_day`) sẽ là **đặc trưng quan trọng nhất** cho mô hình dự báo.

## 4.4. Đối chiếu OSRM với thực tế (baseline tham chiếu)

| Chỉ số | Giá trị |
|---|---|
| **MAE của OSRM** (toàn bộ dữ liệu) | **10.11 phút** |
| MAE trên R01 | 11.17 phút |
| MAE trên R02 | 9.06 phút |
| Tỷ lệ dự báo OSRM sai số ≤ 10 phút | **50.0%** |

**Kết luận:** OSRM — dù là công cụ định tuyến chuẩn — vẫn sai lệch trung bình hơn 10 phút và chỉ đúng trong ngưỡng 10 phút ở một nửa số chuyến, vì OSRM không tính đến tình trạng giao thông theo giờ. Đây là cơ sở khoa học cho mục tiêu của mô hình ML:

> 🎯 **Mục tiêu mô hình ML:** MAE < 10 phút và tỷ lệ sai số ≤ 10 phút > 70% (vượt baseline OSRM).

## 4.5. Phân tích ghi chú bất thường (cột `notes`)

17/54 chuyến có ghi chú sự kiện:

| Ghi chú | Số chuyến | Ảnh hưởng |
|---|---|---|
| Mưa lớn, đi chậm | 4 | Làm tăng thờigian thực tế |
| Dừng đèn đỏ lâu | 4 | Làm tăng thờigian thực tế |
| Đường vắng, đi nhanh | 4 | Làm giảm thờigian thực tế |
| Kẹt xe nặng tại ngã tư | 3 | Làm tăng thờigian thực tế |
| Chở khách thêm 3 phút | 2 | Làm tăng thờigian thực tế |

→ Đề xuất tuần sau: mã hóa cột này thành đặc trưng phụ **`has_anomaly`** (0/1) để mô hình học được ảnh hưởng của sự kiện bất thường.

## 4.7. Kết luận & đề xuất
1. Đã chuẩn hóa: `is_simulated` → 0/1; `data_source` → danh mục chuẩn `osrm_api`; thêm cột `actual_travel_time` và `departure_time_full` để **tương thích với `baseline.py`**.
2. Baseline OSRM có MAE = 10.11 phút → mô hình ML cần vượt mốc này để chứng minh giá trị.
3. Đề xuất thu thập tuần 3: bổ sung số chuyến cho các trip_id còn khuyết và thêm tuyến từ hàm OSRM để tăng độ phủ dữ liệu.
