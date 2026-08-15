# AGENTS.md

Hướng dẫn ngữ cảnh dự án dành cho agent AI làm việc trong repo này.

## Tổng quan

**Quản Lý Tài Chính Cá Nhân** — ứng dụng web quản lý tài chính cá nhân: giao dịch (thu/chi), danh mục, hạn mức chi tiêu và cảnh báo khi chi tiêu vượt ngưỡng.

## Công nghệ

- Backend: Python, FastAPI, SQLAlchemy 2.0, Pydantic v2
- Database: PostgreSQL 16 (chạy qua Docker Compose)
- Frontend: HTML/CSS/JS thuần túy (vanilla), do FastAPI phục vụ trực tiếp từ `app/static/` — **không có build step**
- Server: Uvicorn

## Các lệnh thường dùng

```bash
# Khởi động PostgreSQL
docker compose up -d

# Cài dependencies (dùng virtualenv .venv)
pip install -r requirements.txt

# Chạy server dev (hot reload)
uvicorn app.main:app --reload

# Seed dữ liệu demo
python scripts/seed_demo.py
```

- Giao diện web: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Cấu trúc dự án

```
app/
  main.py                 # FastAPI app, CORS, static, khởi tạo bảng + seed danh mục mặc định
  config.py               # Settings (pydantic-settings, đọc từ .env)
  database.py             # Engine, SessionLocal, Base, get_db dependency
  models/                 # SQLAlchemy models: category, transaction, budget, alert, enums
  schemas/                # Pydantic schemas (v2)
  api/routes/             # Endpoints: categories, transactions, budgets, alerts, dashboard
  services/               # Logic nghiệp vụ: budget_service, alert_service
  seed.py                 # Danh mục mặc định
  static/                 # Frontend: index.html, css/style.css, js/api.js, js/app.js
scripts/seed_demo.py      # Dữ liệu demo
```

## Quy ước code

- Import luôn qua package gốc: `from app.models import Category`, `from app.services.budget_service import ...`.
- Route trả về schema Pydantic; logic nghiệp vụ (tính hạn mức, sinh cảnh báo) đặt trong `app/services/`.
- Transaction handling: logic cập nhật giao dịch/hạn mức phải đồng bộ với việc tạo cảnh báo.
- Frontend gọi API qua `app/static/js/api.js`, render trong `app/static/js/app.js`.
- Không thêm comment không cần thiết; giữ code ngắn gọn theo phong cách hiện có.
- Database schema tạo tự động qua `Base.metadata.create_all` lúc khởi động (không dùng Alembic migration trong runtime).

## Lưu ý quan trọng

- Không chạm vào cấu hình nhà cung cấp/model trong `opencode.json` trừ khi được yêu cầu.
- Tài liệu API đầy đủ trong `README.md`; cập nhật README khi thêm endpoint.
- `.env` (nếu có) để ghi đè cấu hình như `DATABASE_URL`.
