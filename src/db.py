from functools import lru_cache
from contextlib import contextmanager
from typing import List, Dict, Any
from sqlalchemy import create_engine, text, QueuePool
from sqlalchemy.orm import sessionmaker


@lru_cache(maxsize=None)
def create_db_engine(database_name: str = "postgres"):
    """Create a SQLAlchemy engine for a specific database."""
    engine = create_engine(
        f"postgresql+psycopg2://postgres:password123@localhost:5432/{database_name}",
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=False,
    )
    return engine


@contextmanager
def SqlSession(database_name: str = "postgres", commit: bool = True):
    engine = create_db_engine(database_name)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
        if commit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_all_symbols(database_name: str = "postgres") -> List[str]:
    """Lấy danh sách tất cả mã cổ phiếu từ bảng stocks_list."""
    with SqlSession(database_name) as session:
        result = session.execute(text("SELECT code FROM stocks_list ORDER BY code ASC"))
        return [row[0] for row in result]


def get_top_100_symbols(database_name: str = "postgres") -> List[str]:
    """Lấy danh sách 100 mã cổ phiếu có vốn điều lệ lớn nhất từ bảng dim_fundamental_top_100."""
    with SqlSession(database_name) as session:
        result = session.execute(text("SELECT symbol FROM dim_fundamental_top_100 ORDER BY von_dieu_le DESC"))
        return [row[0] for row in result]


def get_crawled_symbols(table_name: str = "raw_balance_sheet", database_name: str = "postgres") -> set:
    """Lấy tập hợp các mã đã cào xong trong bất kỳ bảng nào."""
    with SqlSession(database_name) as session:
        exists = session.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = :table_name
            );
        """), {"table_name": table_name}).scalar()
        if not exists:
            return set()

        result = session.execute(text(f"SELECT DISTINCT symbol FROM {table_name} WHERE symbol IS NOT NULL"))
        return {row[0] for row in result}


def write_to_db(
    records: List[Dict[str, Any]],
    table_name: str = "raw_balance_sheet",
    database_name: str = "postgres"
) -> int:
    """
    Ghi danh sách bản ghi BCTC (5 cột) vào PostgreSQL.
    """
    if not records:
        return 0

    with SqlSession(database_name, commit=True) as session:
        session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                symbol TEXT,
                year INTEGER,
                content TEXT,
                code TEXT,
                value NUMERIC
            );
        """))

        insert_query = text(f"""
            INSERT INTO {table_name} (symbol, year, content, code, value)
            VALUES (:symbol, :year, :content, :code, :value)
        """)
        session.execute(insert_query, records)

    return len(records)


def write_fundamental_to_db(
    records: List[Dict[str, Any]],
    table_name: str = "raw_fundamental",
    database_name: str = "postgres"
) -> int:
    """
    Ghi thông tin cơ bản cổ phiếu (fundamental) vào PostgreSQL.
    """
    if not records:
        return 0

    with SqlSession(database_name, commit=True) as session:
        session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                symbol TEXT PRIMARY KEY,
                san_giao_dich TEXT,
                nganh_nghe TEXT,
                ngay_giao_dich_dau_tien TEXT,
                gia_dong_cua_ngay_dau_tien NUMERIC,
                khoi_luong_ngay_dau_tien NUMERIC,
                von_dieu_le NUMERIC,
                so_luong_co_phieu_niem_yet NUMERIC,
                so_luong_co_phieu_luu_hanh NUMERIC,
                co_phieu_quy NUMERIC,
                co_phieu_pho_thong NUMERIC,
                co_phieu_uu_dai NUMERIC
            );
        """))

        insert_query = text(f"""
            INSERT INTO {table_name} (
                symbol, san_giao_dich, nganh_nghe, ngay_giao_dich_dau_tien, gia_dong_cua_ngay_dau_tien,
                khoi_luong_ngay_dau_tien, von_dieu_le, so_luong_co_phieu_niem_yet, so_luong_co_phieu_luu_hanh,
                co_phieu_quy, co_phieu_pho_thong, co_phieu_uu_dai
            )
            VALUES (
                :symbol, :san_giao_dich, :nganh_nghe, :ngay_giao_dich_dau_tien, :gia_dong_cua_ngay_dau_tien,
                :khoi_luong_ngay_dau_tien, :von_dieu_le, :so_luong_co_phieu_niem_yet, :so_luong_co_phieu_luu_hanh,
                :co_phieu_quy, :co_phieu_pho_thong, :co_phieu_uu_dai
            )
            ON CONFLICT (symbol) DO UPDATE SET
                san_giao_dich = EXCLUDED.san_giao_dich,
                nganh_nghe = EXCLUDED.nganh_nghe,
                ngay_giao_dich_dau_tien = EXCLUDED.ngay_giao_dich_dau_tien,
                gia_dong_cua_ngay_dau_tien = EXCLUDED.gia_dong_cua_ngay_dau_tien,
                khoi_luong_ngay_dau_tien = EXCLUDED.khoi_luong_ngay_dau_tien,
                von_dieu_le = EXCLUDED.von_dieu_le,
                so_luong_co_phieu_niem_yet = EXCLUDED.so_luong_co_phieu_niem_yet,
                so_luong_co_phieu_luu_hanh = EXCLUDED.so_luong_co_phieu_luu_hanh,
                co_phieu_quy = EXCLUDED.co_phieu_quy,
                co_phieu_pho_thong = EXCLUDED.co_phieu_pho_thong,
                co_phieu_uu_dai = EXCLUDED.co_phieu_uu_dai;
        """)
        session.execute(insert_query, records)

    return len(records)
