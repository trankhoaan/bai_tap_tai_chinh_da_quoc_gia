# Hệ Thống Thu Thập & Phân Tích Dữ Liệu Báo Cáo Tài Chính (Top 100 Doanh Nghiệp)

Dự án tự động hóa thu thập, xử lý và chuẩn hóa dữ liệu Báo cáo Tài chính của **Top 100 doanh nghiệp có vốn điều lệ lớn nhất Việt Nam** từ nguồn CafeF, lưu trữ trong cơ sở dữ liệu **PostgreSQL** và chuyển đổi dữ liệu phân tích dạng Wide bằng **dbt (data build tool)**.

---

## 🏗️ Kiến Trúc Hệ Thống (ELT Pipeline)

1. **Extract & Load (EL)**:
   - Thu thập thông tin cơ bản (**Fundamental**) của toàn bộ cổ phiếu niêm yết (HOSE, HNX, UPCOM).
   - Lọc ra danh sách **Top 100 công ty** có Vốn điều lệ lớn nhất (`dim_fundamental_top_100`).
   - Cào dữ liệu lịch sử các năm (2016 – 2025) cho 3 bộ báo cáo tài chính:
     - **Bảng Cân đối kế toán (Balance Sheet)**
     - **Báo cáo Lưu chuyển tiền tệ (Cash Flow Statement)** (Phương pháp gián tiếp)
     - **Báo cáo Kết quả kinh doanh (Income Statement)**
   - Lưu trữ thô vào PostgreSQL (`raw_fundamental`, `raw_balance_sheet`, `raw_cash_flow`, `raw_income_statement`).

2. **Transform (T - dbt)**:
   - Tầng **Staging**: Chuẩn hóa, lọc bỏ các năm lỗi/rác (`HDKD_2 = 0` hoặc placeholder), ép kiểu dữ liệu và liên kết với Dimension Top 100.
   - Tầng **Marts**: Sử dụng Dynamic Jinja Macro để tự động pivot toàn bộ các chỉ tiêu tài chính thành bảng dạng Wide:
     - `dim_fundamental_top_100`: 100 công ty × 13 thuộc tính.
     - `fct_balance_sheet_wide`: 133 chỉ tiêu Cân đối kế toán.
     - `fct_cash_flow_wide`: 42 chỉ tiêu Lưu chuyển tiền tệ.
     - `fct_income_statement_wide`: 24 chỉ tiêu Kết quả kinh doanh.

3. **Export**:
   - Xuất dữ liệu đã chuẩn hóa ra file Excel tổng hợp đa sheet (`bao_cao_tai_chinh_top_100.xlsx`) để phục vụ nghiên cứu và mô hình hóa tài chính.

---

## 📁 Cấu Trúc Dự Án

```
├── dbt/
│   ├── dbt_project.yml        # Cấu hình project dbt
│   ├── profiles.yml           # Kết nối PostgreSQL
│   ├── models/
│   │   ├── staging/           # Staging models (stg_balance_sheet, stg_cash_flow, stg_income_statement, stg_fundamental)
│   │   └── marts/             # Marts wide tables (fct_*_wide, dim_fundamental_top_100)
│   └── seeds/                 # Từ điển Schema phân cấp các chỉ tiêu tài chính
├── src/
│   ├── crawler.py             # Engine cào dữ liệu bất đồng bộ
│   ├── db.py                  # Quản lý kết nối & truy vấn PostgreSQL
│   ├── parser.py              # Parser chuẩn hóa JSON từ API CafeF
│   └── export_excel.py        # Xuất dữ liệu sang Excel đa sheet
├── docker-compose.yml         # Container PostgreSQL
├── pyproject.toml             # Quản lý thư viện Python (uv)
└── main.py                    # Entrypoint thực thi pipeline
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### 1. Khởi động PostgreSQL
```bash
docker compose up -d
```

### 2. Cài đặt môi trường Python (dùng uv)
```bash
uv sync
```

### 3. Nạp Seed Schema & Khởi tạo Marts trong dbt
```bash
uv run dbt seed --project-dir dbt --profiles-dir dbt
uv run dbt run --project-dir dbt --profiles-dir dbt
```

### 4. Chạy Crawler thu thập dữ liệu
```bash
uv run python main.py
```

### 5. Xuất báo cáo ra Excel
```bash
uv run python src/export_excel.py
```
File Excel kết quả sẽ được tạo tại `bao_cao_tai_chinh_top_100.xlsx`.
