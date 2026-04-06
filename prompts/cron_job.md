Nếu muốn **chạy 24/7 kể cả tắt máy cá nhân** và vẫn **miễn phí + hiệu quả**, lựa chọn tốt nhất hiện tại là:

## Khuyến nghị số 1: Oracle Cloud Always Free VM (miễn phí thật, không sleep)

### Vì sao nên chọn
- Chạy process nền liên tục (API + worker) như app của bạn.
- Không bị “sleep” như nhiều free web hosting.
- Đủ để chạy FastAPI + worker + gọi CoinGecko 25 req/min.

---

## Cấu hình nhanh (30–45 phút)

### 1) Tạo VM Always Free
- Đăng ký Oracle Cloud → tạo **Compute Instance** (Ubuntu ARM Ampere, Always Free).
- Mở inbound port:
  - `22` (SSH)
  - `8000` (nếu expose API trực tiếp)
  - hoặc chỉ `80/443` nếu dùng Nginx reverse proxy.

### 2) SSH vào máy
```bash
ssh ubuntu@<public-ip>
```

### 3) Cài runtime
```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install git python3 python3-venv python3-pip
```

### 4) Clone project + tạo venv
```bash
git clone <repo-url> crypto-risk-system
cd crypto-risk-system
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 5) Tạo `.env` production
- Copy từ `.env.example`, điền:
  - Supabase `POSTGRES_*`
  - `AUTO_CREATE_TABLES=false`
  - `COINGECKO_MAX_REQUESTS_PER_MINUTE=25`
  - các interval theo nhu cầu.

### 6) Init DB + RLS (chạy 1 lần)
```bash
python scripts/init_db.py
python apply_rls.py
```

### 7) Tạo 2 service systemd (API + worker)
- `crypto-api.service` chạy:
  - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `crypto-worker.service` chạy:
  - `python scripts/run_worker.py`

Sau đó:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now crypto-api crypto-worker
sudo systemctl status crypto-api
sudo systemctl status crypto-worker
```

### 8) Log realtime
```bash
journalctl -u crypto-api -f
journalctl -u crypto-worker -f
```

---

## Option “siêu nhanh nhưng không 24/7 thật”

- **Render/Railway/Koyeb free**: dễ deploy nhưng thường sleep hoặc giới hạn giờ chạy.
- **GitHub Actions cron**: miễn phí, tốt cho job định kỳ (15m/12h/7d), nhưng không phải process luôn sống.

---

## Kiến trúc tối ưu miễn phí cho case của bạn

- **Supabase**: database + RLS.
- **Oracle VM**: chạy API + worker 24/7 bằng systemd.
- (Tuỳ chọn) **Cloudflare Tunnel/Nginx + domain** cho HTTPS.

---

Nếu bạn muốn, mình có thể gửi luôn **template 2 file systemd** sẵn dùng (copy-paste) đúng với cấu trúc repo hiện tại của bạn.