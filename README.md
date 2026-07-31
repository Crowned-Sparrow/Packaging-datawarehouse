# VS Packaging — Data Warehouse & Predictive Maintenance

Hệ thống quản lý sản xuất bao bì (đơn hàng, khách hàng, nguyên vật liệu, vận hành máy corrugating) kết hợp với pipeline ETL và mô hình Machine Learning dự đoán rủi ro hỏng máy (predictive maintenance) dựa trên Survival Analysis.

## Mục lục

- [Kiến trúc tổng thể](#kiến-trúc-tổng-thể)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Database](#database)
- [Backend API](#backend-api)
- [Frontend](#frontend)
- [ETL Pipeline](#etl-pipeline)
- [ML Pipeline — Dự đoán rủi ro hỏng máy](#ml-pipeline--dự-đoán-rủi-ro-hỏng-máy)
- [Cài đặt & chạy thử](#cài-đặt--chạy-thử)
- [Giới hạn hiện tại](#giới-hạn-hiện-tại)
- [Roadmap](#roadmap)

## Kiến trúc tổng thể

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Frontend   │ ───▶ │  FastAPI     │ ───▶ │   PostgreSQL     │
│  (React+Vite)│      │  (backend)   │      │  public/         │
└─────────────┘      └──────────────┘      │  corrugating/    │
                                             │  ml/             │
                                             └────────┬─────────┘
                                                       │
                                    ┌──────────────────┴──────────────────┐
                                    │              ETL (Polars)            │
                                    │  extract → transform → load          │
                                    └──────────────────┬────────────────────┘
                                                       │
                                    ┌──────────────────┴──────────────────┐
                                    │        ML Pipeline (lifelines)        │
                                    │  build episodes → train Cox PH model  │
                                    └────────────────────────────────────────┘
```

Ba schema Postgres tách theo nghiệp vụ:
- **`public`** — dữ liệu lõi dùng chung: đơn hàng, khách hàng, nhân viên, nhà cung cấp, nguyên vật liệu.
- **`corrugating`** — dữ liệu riêng cho công đoạn corrugating (sóng): máy, log sản xuất, log sự cố.
- **`ml`** — bảng đặc trưng (feature store) phục vụ training, tách biệt khỏi dữ liệu vận hành gốc.

## Cấu trúc thư mục

```
backend/
  app/            # FastAPI app: models (SQLAlchemy), schemas (Pydantic), core (DB, security)
  routers/        # API endpoints, chia theo domain + subrouter cho corrugating
  SQL/            # Raw SQL: tables, functions, triggers, constraints — theo từng schema
  etl/            # Extract/Transform/Load bằng Polars, orchestration qua Airflow
  ml/             # Feature engineering, training (Cox PH), serving (predictor)
  sql_executor.py # Helper khởi tạo DB từ các file .sql theo thứ tự
frontend/
  src/
    pages/        # Các trang: Login, Order/Customer/Employee list & add, Profile
    components/   # Sidebar, ProtectedRoute
    context/      # AuthContext (JWT lưu localStorage)
    api/          # axios client + interceptor xử lý 401
data_samples/     # Dữ liệu mẫu dùng để test import & pipeline (KHÔNG phải dữ liệu production)
```

## Database

### Schema `public`
| Bảng | Vai trò |
|---|---|
| `dim_customers`, `dim_employees`, `dim_suppliers`, `dim_materials` | Dimension table |
| `fact_orders` | Đơn hàng, có trigger tự cập nhật `order_status` theo vòng đời (pending → in_progress → delivered/cancelled) |
| `fact_supply_details` | Chi tiết nhập nguyên vật liệu từ nhà cung cấp |

### Schema `corrugating`
| Bảng | Vai trò |
|---|---|
| `dim_machines` | Máy corrugating, có `machine_status` tự cập nhật qua trigger dựa trên log sản xuất/sự cố |
| `dim_machine_breakdowns` | Danh mục mã lỗi (breakdown code) |
| `fact_production_logs` | Log sản xuất theo `pds` (Production Data Sheet code) — liên kết `fact_orders.pds` |
| `fact_machine_breakdown_logs` | Log sự cố máy |
| `fact_products`, `fact_production_supply_usages` | Sản phẩm và tiêu hao vật tư theo lô sản xuất |

### Schema `ml`
| Bảng | Vai trò |
|---|---|
| `machine_survival_episodes` | Feature store — mỗi dòng là một "episode" (khoảng thời gian giữa 2 lần hỏng liên tiếp của 1 máy), dùng trực tiếp để train Cox PH model |

**Khởi tạo database:** dùng `backend/sql_executor.py` (`SQLExecutor.init_database()`), chạy tuần tự `tables → constraints → functions → triggers` cho từng schema trong 1 transaction — lỗi bất kỳ đâu sẽ rollback toàn bộ, tránh init dở dang.

## Backend API

FastAPI, xác thực JWT (`python-jose` + `bcrypt`), SQLAlchemy ORM. Router chính:

- `/api/auth` — login, trả JWT access token.
- `/api/employees`, `/api/customers`, `/api/orders`, `/api/materials`, `/api/supplies` — CRUD nghiệp vụ chung.
- `/corrugating/machines`, `/corrugating/logs`, `/corrugating/breakdowns` — nghiệp vụ riêng công đoạn corrugating.

Toàn bộ endpoint (trừ `/api/auth/login`) yêu cầu `Bearer token`, xác thực qua `get_current_employee` dependency.

## Frontend

React 19 + Vite + React Router 7. Layout dashboard có sidebar cố định, các trang list có filter debounce 400ms trước khi gọi API. Auth state lưu trong `localStorage`, tự động logout khi API trả 401 (qua axios interceptor).

## ETL Pipeline

`backend/etl/` — dùng **Polars** (không phải pandas) cho hiệu năng xử lý dữ liệu lớn hơn.

```
extract (PostgresReader / APIReader)
      │
      ▼
transform (clean_production_logs, clean_breakdown_logs, build_training_dataset)
      │
      ▼
load (ParquetWriter cho local, PostgresWriter cho ghi lại DB)
```

Pipeline chính: `backend/etl/pipelines/daily_batch.py` — trích xuất log sản xuất + sự cố, làm sạch, tổng hợp thành feature theo ngày/máy, ghi ra Parquet (và tuỳ chọn ghi ngược vào `ml` schema qua biến môi trường `ETL_LOAD_TO_POSTGRES`). Có thể lên lịch chạy hàng ngày qua Airflow DAG tại `backend/etl/orchestration/airflow_dags/etl_daily_breakdown_risk.py`.

## ML Pipeline — Dự đoán rủi ro hỏng máy

**Bài toán:** dự đoán khi nào một máy corrugating có khả năng hỏng tiếp theo, dựa trên lịch sử vận hành — đây là bài toán **time-to-event**, nên dùng **Survival Analysis (Cox Proportional Hazards)** thay vì classification thông thường, vì nó xử lý đúng dữ liệu "censored" (máy chưa hỏng tính đến thời điểm quan sát).

### Luồng xử lý

```
1. build_survival_episodes.py
   Cắt lịch sử mỗi máy thành các "episode" — khoảng thời gian giữa 2 lần hỏng
   liên tiếp. Episode cuối cùng của mỗi máy là "censored" (event_observed=0).

2. build_static_features.py + build_rolling_features.py
   Với mỗi episode, tính đặc trưng TẠI THỜI ĐIỂM episode bắt đầu (tránh data
   leakage từ tương lai):
     - Static: flute_type, machine_age_days, lifetime_total_runs,
       lifetime_breakdown_count, days_since_last_breakdown
     - Rolling (7/30/90 ngày): runs, utilization, waste_ratio,
       breakdown_count, downtime_minutes

3. build_and_load_episodes.py
   Ghi toàn bộ episode + feature vào ml.machine_survival_episodes.

4. train_cox_static.py (qua run_training.py)
   Train CoxPHFitter (lifelines), kiểm tra Proportional Hazards assumption,
   đánh giá bằng 5-fold cross-validation (concordance index).

5. predictor.py
   Serving: load model đã train, dự đoán median_days_to_breakdown và
   relative_risk_score cho một máy cụ thể.
```

### Kết quả hiện tại (trên `data_samples/`)

```
episode_count: 101, event_count: 97
Concordance (in-sample): 0.63
Concordance (5-fold CV): 0.580 ± 0.055
Không feature nào đạt p < 0.05
Log-likelihood ratio test: p ≈ 0.063 (ranh giới ngưỡng ý nghĩa 0.05)
Proportional Hazards assumption: OK
```

**Diễn giải:** model hiện tại **chưa đạt mức đáng tin cậy để dùng cho quyết định vận hành thật**. C-index ~0.58 chỉ nhỉnh hơn đoán ngẫu nhiên (0.5), và không feature nào có ý nghĩa thống kê rõ ràng. Đây là hệ quả trực tiếp của giới hạn dữ liệu mẫu (xem phần dưới), không phải lỗi thiết kế pipeline — pipeline đã được kiểm chứng chạy đúng logic (survival cutting, tránh leakage, đánh giá bằng CV, kiểm tra PH assumption).

## Cài đặt & chạy thử

```bash
# Backend
cd backend
pip install -r requirements.txt --break-system-packages   # nếu có requirements.txt
cp app/core/login.env.example app/core/login.env          # điền PG_USER, PG_PASSWORD, ...
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Khởi tạo database (từ thư mục gốc repo)
python -c "
from backend.sql_executor import SQLExecutor, get_engine
SQLExecutor(get_engine()).init_database()
"

# Chạy ETL build feature cho ML
python -m backend.ml.pipelines.build_and_load_episodes --mode replace

# Train model
python -m backend.ml.pipelines.run_training
```

## Giới hạn hiện tại

Ghi lại minh bạch để tránh hiểu nhầm khi đọc kết quả hoặc mở rộng dự án:

1. **`data_samples/` là dữ liệu mẫu, không phải dữ liệu vận hành thật.** Cột `recovery_time` trong `breakdownlog.csv` được **random sinh dựa trên khung giờ ca làm việc** (công ty gốc không lưu thời điểm sửa xong), nên mọi feature tính từ `recovery_time` (`lifetime_avg_downtime_minutes`, `downtime_minutes_*`, `days_since_last_breakdown`) **đã bị loại khỏi tập train** vì không phản ánh dữ liệu thật.
2. **Số lượng máy trong dữ liệu mẫu quá ít** (~4-6 máy) so với số episode (101) — mỗi máy đóng góp nhiều episode liên tiếp, các quan sát không hoàn toàn độc lập (vi phạm nhẹ giả định của Cox model). Khuyến nghị dùng `cluster_col="machine_id"` khi có dữ liệu lớn hơn.
3. **Một vài router/module còn thiếu sót đã biết**, ví dụ `backend/routers/corrugating/products.py` thiếu khởi tạo `router = APIRouter()` — cần sửa trước khi include vào `main.py` nếu module này được bật.
4. **Chưa có test tự động** (unit test cho ETL transform, integration test cho API) — nên bổ sung trước khi coi đây là hệ thống production-ready.
5. **FK giữa `fact_machine_breakdown_logs.pds` và `fact_orders.pds`** cần rà soát khi import dữ liệu mẫu, vì một số `pds` trong breakdown log không tồn tại trong `orders.csv` mẫu.

## Roadmap

- [ ] Thu thập `recovery_time` thật từ vận hành, bật lại downtime-based features.
- [ ] Mở rộng số lượng máy quan sát để Cox model tổng quát hoá tốt hơn.
- [ ] Thêm `cluster_col="machine_id"` cho robust standard error.
- [ ] Viết unit test cho `backend/etl/transform/` và `backend/ml/features/`.
- [ ] Hoàn thiện `corrugating/products.py` router và bật vào `main.py`.
- [ ] Dashboard hiển thị `relative_risk_score` theo máy trên frontend.