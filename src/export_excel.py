import os
import pandas as pd
from typing import Optional, List
from sqlalchemy import text

try:
    from src.db import create_db_engine
except ImportError:
    from db import create_db_engine


def export_all_reports_to_excel(
    output_path: str = "bao_cao_tai_chinh_top_100.xlsx",
    database_name: str = "postgres"
) -> str:
    """
    Xuất toàn bộ dữ liệu Top 100 công ty sang file Excel với 4 Sheet riêng biệt:
    1. Top_100_Cong_Ty (dim_fundamental_top_100)
    2. Can_Doi_Ke_Toan (fct_balance_sheet_wide)
    3. Luu_Chuyen_Tien_Te (fct_cash_flow_wide)
    4. Ket_Qua_Kinh_Doanh (fct_income_statement_wide)
    """
    engine = create_db_engine(database_name)

    with engine.connect() as conn:
        print("1. Đang đọc bảng dim_fundamental_top_100...")
        df_fund = pd.read_sql(text("SELECT * FROM dim_fundamental_top_100 ORDER BY von_dieu_le DESC"), conn)

        print("2. Đang đọc bảng fct_balance_sheet_wide...")
        df_bs = pd.read_sql(text("SELECT * FROM fct_balance_sheet_wide ORDER BY symbol ASC, year DESC"), conn)

        print("3. Đang đọc bảng fct_cash_flow_wide...")
        df_cf = pd.read_sql(text("SELECT * FROM fct_cash_flow_wide ORDER BY symbol ASC, year DESC"), conn)

        print("4. Đang đọc bảng fct_income_statement_wide...")
        df_is = pd.read_sql(text("SELECT * FROM fct_income_statement_wide ORDER BY symbol ASC, year DESC"), conn)

    print(f"Đang ghi vào file Excel: {output_path} với 4 Sheet...")
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_fund.to_excel(writer, sheet_name="Top_100_Cong_Ty", index=False)
        df_bs.to_excel(writer, sheet_name="Can_Doi_Ke_Toan", index=False)
        df_cf.to_excel(writer, sheet_name="Luu_Chuyen_Tien_Te", index=False)
        df_is.to_excel(writer, sheet_name="Ket_Qua_Kinh_Doanh", index=False)

    full_path = os.path.abspath(output_path)
    print(f"=> Xuất file Excel thành công! Lưu tại: {full_path}")
    return full_path


if __name__ == "__main__":
    export_all_reports_to_excel("bao_cao_tai_chinh_top_100.xlsx")
