# Quản Lý Tài Chính Cá Nhân

Phần mềm quản lý tài chính cá nhân với đầy đủ chức năng quản lý chi tiêu, quản lý hạn mức, phân loại chi tiêu và cảnh báo chi tiêu.

## Tính năng

- **Phân loại chi tiêu**: Danh mục thu/chi kèm icon, màu sắc; tự động tạo danh mục mặc định khi khởi động.
- **Quản lý chi tiêu (giao dịch)**: Thêm, sửa, xóa, lọc theo loại (thu/chi), danh mục, khoảng ngày; phân trang.
- **Quản lý hạn mức**: Tạo hạn mức theo danh mục hoặc tổng thể, theo tháng hoặc theo năm, tùy chỉnh ngưỡng cảnh báo (mặc định 80%), thời gian hiệu lực.
- **Cảnh báo chi tiêu**: Tự động tạo cảnh báo khi chi tiêu đạt ngưỡng (`warning`) hoặc vượt hạn mức (`danger`); tự cập nhật khi giao dịch thêm/sửa/xóa; đánh dấu đã đọc.
- **Bảng điều khiển (dashboard)**: Tổng thu, tổng chi, số dư trong tháng; tình trạng sử dụng từng hạn mức; giao dịch và cảnh báo gần đây.

## Công nghệ

- FastAPI, SQLAlchemy 2.0, Pydantic v2
- PostgreSQL 16 (Docker Compose) — mặc định
- Uvicorn

## Cài đặt

### 1. Khởi động PostgreSQL

```bash
docker compose up -d
```

### 2. Cài dependencies

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Cấu hình (tùy chọn)

Tạo file `.env` nếu cần đổi cấu hình:

```
DATABASE_URL=postgresql+psycopg2://finance_user:finance_password@localhost:5432/finance_db
```

### 4. Chạy server

```bash
uvicorn app.main:app --reload
```

- Giao diện web: http://localhost:8000
- Tài liệu API (Swagger): http://localhost:8000/docs
- Kiểm tra sức khỏe: http://localhost:8000/health

Giao diện web (frontend) được FastAPI phục vụ trực tiếp từ `app/static/` — không cần build, gồm: Dashboard tổng quan, quản lý giao dịch (lọc, phân trang), quản lý hạn mức, quản lý danh mục và danh sách cảnh báo.

### 5. Seed dữ liệu demo

Tạo danh mục mặc định, hạn mức và giao dịch mẫu (kèm cảnh báo):

```bash
python scripts/seed_demo.py
```

> Danh mục mặc định tự động được tạo khi server khởi động lần đầu.

## API chính

| Phương thức | Endpoint | Mô tả |
|---|---|---|
| GET/POST | `/api/categories` | Danh sách / tạo danh mục |
| GET/PUT/DELETE | `/api/categories/{id}` | Chi tiết / sửa / xóa danh mục |
| GET/POST | `/api/transactions` | Danh sách (lọc + phân trang) / tạo giao dịch |
| GET/PUT/DELETE | `/api/transactions/{id}` | Chi tiết / sửa / xóa giao dịch |
| GET/POST | `/api/budgets` | Danh sách (kèm chi tiêu thực tế) / tạo hạn mức |
| GET/PUT/DELETE | `/api/budgets/{id}` | Chi tiết / sửa / xóa hạn mức |
| GET | `/api/alerts` | Danh sách cảnh báo (`?unread_only=true`) |
| POST | `/api/alerts/check` | Kiểm tra và cập nhật cảnh báo thủ công |
| PUT | `/api/alerts/{id}/read` | Đánh dấu một cảnh báo đã đọc |
| PUT | `/api/alerts/read-all` | Đánh dấu tất cả đã đọc |
| GET | `/api/alerts/unread-count` | Số cảnh báo chưa đọc |
| GET | `/api/dashboard/summary` | Tổng quan tháng hiện tại |

Ví dụ tạo giao dịch chi tiêu:

```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"expense","amount":500000,"category_id":1,"note":"Đi ăn","transaction_date":"2026-08-13"}'
```

## Cấu trúc dự án

```
app/
  main.py                 # FastAPI app, CORS, phục vụ static, khởi tạo bảng + seed danh mục
  config.py               # Cấu hình từ .env
  database.py             # Engine, Session
  models/                 # SQLAlchemy models (Category, Transaction, Budget, Alert)
  schemas/                # Pydantic schemas
  api/routes/             # Endpoints (categories, transactions, budgets, alerts, dashboard)
  services/               # Logic hạn mức, chi tiêu, sinh cảnh báo
  seed.py                 # Danh mục mặc định
  static/                 # Frontend (index.html, css, js)
scripts/seed_demo.py      # Dữ liệu demo
```
