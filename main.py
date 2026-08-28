import asyncio
from src.crawler import crawl_all_pipeline, URL_INCOME_STATEMENT
from src.parser import parse_income_statement
from src.db import write_to_db, get_top_100_symbols

if __name__ == "__main__":
    # 1. Lấy danh sách 100 công ty có vốn điều lệ lớn nhất từ bảng dim_fundamental_top_100
    top_100 = get_top_100_symbols()
    print(f"Bắt đầu pipeline cào Kết quả kinh doanh cho {len(top_100)} công ty...")

    # 2. Chạy pipeline cào và lưu vào bảng raw_income_statement
    asyncio.run(crawl_all_pipeline(
        url_template=URL_INCOME_STATEMENT,
        parser=parse_income_statement,
        writer=lambda records: write_to_db(records, table_name="raw_income_statement"),
        table_name="raw_income_statement",
        symbols=top_100
    ))
