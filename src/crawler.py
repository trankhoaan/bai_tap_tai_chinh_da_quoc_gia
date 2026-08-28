import os
import requests
import asyncio
import random
from typing import List, Dict, Any, Optional, Callable

try:
    from src.db import (
        get_all_symbols,
        get_top_100_symbols,
        get_crawled_symbols,
        write_to_db,
        write_fundamental_to_db,
    )
    from src.parser import parse_balance_sheet, parse_cash_flow, parse_income_statement, parse_fundamental
except ImportError:
    from db import (
        get_all_symbols,
        get_top_100_symbols,
        get_crawled_symbols,
        write_to_db,
        write_fundamental_to_db,
    )
    from parser import parse_balance_sheet, parse_cash_flow, parse_income_statement, parse_fundamental

# Định nghĩa các mẫu URL
URL_BALANCE_SHEET = "https://apiweb.cafef.vn/api/v2/BCTC/GetReportCDKT?symbol={symbol}&pageIndex={page_index}&pageSize={page_size}&reportType=ALL&TypeTime=NAM"
URL_CASH_FLOW = "https://apiweb.cafef.vn/api/v1/BCTC/GetReportLCTT?symbol={symbol}&pageIndex={page_index}&pageSize={page_size}&reportType=ALL&TypeTime=NAM"
URL_INCOME_STATEMENT = "https://apiweb.cafef.vn/api/v1/BCTC/GetReportDetail?symbol={symbol}&pageIndex={page_index}&pageSize={page_size}&reportType=KQKD&TypeTime=NAM"
URL_FUNDAMENTAL = "https://cafef.vn/du-lieu/ajax/pagenew/companyinfor.ashx?symbol={symbol}"


def _get_session() -> requests.Session:
    """
    Khởi tạo Session requests.
    """
    s = requests.Session()
    user_agent = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    s.headers.update({
        "User-Agent": user_agent,
        "Referer": "https://cafef.vn/",
        "Accept": "application/json, text/plain, */*"
    })
    return s


def fetch_data(session: requests.Session, url: str) -> Optional[Dict[Any, Any]]:
    """
    Gọi GET request đến bất kỳ URL nào của CafeF.
    """
    try:
        response = session.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Lỗi khi gọi API: {url} -> {e}")
        return None


async def crawl_ticker(
    session: requests.Session,
    symbol: str,
    url_template: str,
    parser: Callable[[Dict[str, Any]], Any],
    writer: Callable[[List[Dict[str, Any]]], int],
    page_size: int = 4
) -> int:
    """
    Hàm cào đa năng cho 1 mã cổ phiếu:
    - Nếu url_template có '{page_index}': tự động phân trang lặp while True
    - Nếu url_template không có '{page_index}': cào 1 request duy nhất rồi dừng
    """
    total_saved = 0
    page_index = 1
    is_paginated = "{page_index}" in url_template

    while True:
        url = url_template.format(symbol=symbol, page_index=page_index, page_size=page_size)
        data = fetch_data(session, url)
        await asyncio.sleep(random.uniform(0.1, 0.3))

        if not data:
            break

        records = parser(data)
        if not records:
            if is_paginated:
                print(f"[{symbol}] Hết dữ liệu ở trang {page_index}.")
            break

        # Chuẩn hóa nếu parser trả về 1 dict đơn lẻ
        if isinstance(records, dict):
            records = [records]

        saved_count = writer(records)
        total_saved += saved_count
        print(f"[{symbol}] Đã lưu {saved_count} bản ghi vào DB.")

        if not is_paginated:
            break

        page_index += 1

    return total_saved


async def crawl_all_pipeline(
    url_template: str = URL_BALANCE_SHEET,
    parser: Callable[[Dict[str, Any]], Any] = parse_balance_sheet,
    writer: Callable[[List[Dict[str, Any]]], int] = write_to_db,
    table_name: str = "raw_balance_sheet",
    symbols: Optional[List[str]] = None
) -> int:
    """
    Hàm tổng chạy pipeline đa năng cho bất kỳ nguồn URL, parser và writer nào.
    Nếu truyền symbols thì cào theo danh sách đó, ngược lại cào toàn bộ stocks_list.
    """
    if symbols is None:
        symbols = get_all_symbols()

    crawled = get_crawled_symbols(table_name=table_name)
    symbols_to_crawl = [s for s in symbols if s not in crawled]

    print(f"[{table_name}] Đã có sẵn {len(crawled)} mã. Bắt đầu cào {len(symbols_to_crawl)} / {len(symbols)} mã...")

    total_records = 0
    with _get_session() as session:
        for symbol in symbols_to_crawl:
            saved = await crawl_ticker(
                session=session,
                symbol=symbol,
                url_template=url_template,
                parser=parser,
                writer=writer
            )
            total_records += saved

    print(f"=== Hoàn tất pipeline! Đã ghi tổng cộng {total_records} bản ghi vào '{table_name}' ===")
    return total_records


if __name__ == "__main__":
    # Mặc định cào BCTC
    asyncio.run(crawl_all_pipeline())
