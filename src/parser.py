from typing import List, Dict, Any, Optional


def parse_balance_sheet(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse 1 response lẻ từ API CafeF sử dụng .get() có fallback mặc định,
    trích xuất 5 trường: symbol, year, content, code, value.
    """
    records = []
    value_obj = raw_data.get("value") or {}
    sections = value_obj.get("data") or []

    for section in sections:
        # Duyệt qua từng năm/kỳ
        for period in section.get("data", []):
            symbol = period.get("symbol", "")
            year = period.get("year")
            content = period.get("content") or "Đã kiểm toán"

            # Duyệt qua các dòng chỉ tiêu (code, value)
            for row in period.get("data", []):
                records.append({
                    "symbol": symbol,
                    "year": year,
                    "content": content,
                    "code": row.get("code", ""),
                    "value": row.get("value")
                })

    return records


def parse_cash_flow(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse dữ liệu Lưu chuyển tiền tệ (LCTT) từ API CafeF sang 5 trường:
    symbol, year, content, code, value.
    """
    return parse_balance_sheet(raw_data)


def parse_income_statement(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse dữ liệu Kết quả kinh doanh (KQKD) từ API CafeF sang 5 trường:
    symbol, year, content, code, value.
    Hỗ trợ cả định dạng period trực tiếp hoặc qua section.
    """
    records = []
    value_obj = raw_data.get("value") or {}
    items = value_obj.get("data") or []

    for item in items:
        if "year" in item and "symbol" in item:
            symbol = item.get("symbol", "")
            year = item.get("year")
            content = item.get("content") or "Đã kiểm toán"
            for row in item.get("data", []):
                records.append({
                    "symbol": symbol,
                    "year": year,
                    "content": content,
                    "code": str(row.get("code", "")).strip(),
                    "value": row.get("value")
                })
        else:
            for period in item.get("data", []):
                symbol = period.get("symbol", "")
                year = period.get("year")
                content = period.get("content") or "Đã kiểm toán"
                for row in period.get("data", []):
                    records.append({
                        "symbol": symbol,
                        "year": year,
                        "content": content,
                        "code": str(row.get("code", "")).strip(),
                        "value": row.get("value")
                    })

    return records


def parse_fundamental(raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse 1 response thông tin cơ bản (Fundamental) từ API CafeF sang tên tiếng Việt đầy đủ.
    """
    data = raw_data.get("Data") or {}
    if not data:
        return None

    return {
        "symbol": data.get("Symbol", ""),
        "san_giao_dich": data.get("San", ""),
        "nganh_nghe": data.get("Nganh", ""),
        "ngay_giao_dich_dau_tien": data.get("NgayGDDauTien"),
        "gia_dong_cua_ngay_dau_tien": data.get("GiaDongCuaNGDDT"),
        "khoi_luong_ngay_dau_tien": data.get("VolumeStartDate"),
        "von_dieu_le": data.get("VDL"),
        "so_luong_co_phieu_niem_yet": data.get("KLCPNY"),
        "so_luong_co_phieu_luu_hanh": data.get("KLCPLH"),
        "co_phieu_quy": data.get("CPQuy"),
        "co_phieu_pho_thong": data.get("CPPhoThong"),
        "co_phieu_uu_dai": data.get("CPUuDai")
    }
