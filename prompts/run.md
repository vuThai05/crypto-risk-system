## 1) Kiểm tra `.env` (đã có project Supabase)

Trong `.env` cần đúng các biến chính:

- `POSTGRES_SERVER=db.<project-ref>.supabase.co`
- `POSTGRES_PORT=5432` (khuyên dùng direct connection)
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=<db-password>`
- `POSTGRES_DB=postgres` (thường là `postgres` trên Supabase)
- `COINGECKO_MAX_REQUESTS_PER_MINUTE=25`
- `AUTO_CREATE_TABLES=false`  ← quan trọng sau khi sửa `init_db`

## 2) Cài dependencies (nếu chưa)

```powershell
cd c:\Users\AD\crypto-risk-system
python -m pip install -e ".[dev]"
```

(hoặc dùng `uv sync` nếu bạn dùng uv)

## 3) Tạo schema lần đầu trên Supabase

Vì giờ startup không auto `create_all`, bạn chạy thủ công:

```powershell
python scripts/init_db.py
```

Kỳ vọng: in ra `OK: tables created (if not already present).`

## 4) Áp RLS policy (nếu bạn muốn bật read policy ngay)

```powershell
python apply_rls.py
```

Script này sẽ bật RLS và tạo policy SELECT cho các bảng analytics.

## 5) Chạy API (terminal 1)

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6) Chạy worker riêng (terminal 2)

```powershell
python scripts/run_worker.py
```

Worker sẽ:
- seed `coins` nếu DB trống,
- chạy market ingestion + risk pipeline mỗi 15 phút,
- OHLCV mỗi 12 giờ,
- backfill mỗi 7 ngày.

## 7) Trigger tay để có dữ liệu ngay (không chờ lịch)

Mở terminal 3 hoặc Postman:

```powershell
curl -X POST http://localhost:8000/api/v1/trigger-ingestion
```

## 8) Kiểm tra kết quả API

- Market aggregate:
  - `GET http://localhost:8000/api/v1/market-risk`
- Top risky:
  - `GET http://localhost:8000/api/v1/top-risky-assets`
- Coin risk:
  - `GET http://localhost:8000/api/v1/coins/{coin_id}/risk`

## 9) Kiểm tra trực tiếp trên Supabase SQL Editor (tuỳ chọn)

Chạy nhanh:

```sql
select count(*) from coins;
select count(*) from market_snapshots;
select count(*) from feature_metrics;
select count(*) from risk_metrics;
select count(*) from market_aggregates;
```

---

### Lưu ý quan trọng sau bản sửa
- `AUTO_CREATE_TABLES=false` nghĩa là app/worker **không tự tạo bảng khi start**.
- Nếu deploy môi trường mới, luôn chạy trước:
  1) `scripts/init_db.py` (hoặc migration),  
  2) `apply_rls.py` (nếu dùng RLS).  

Nếu bạn muốn, mình có thể đưa luôn checklist “troubleshooting nhanh” (lỗi connect Supabase, lỗi thiếu bảng, lỗi RLS).