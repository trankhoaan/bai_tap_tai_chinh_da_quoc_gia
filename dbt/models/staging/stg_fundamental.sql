WITH raw_fund AS (
    SELECT * FROM {{ source('postgres', 'raw_fundamental') }}
),

stocks AS (
    SELECT * FROM {{ source('postgres', 'stocks_list') }}
)

SELECT
    f.symbol,
    s.fullname_vi AS ten_cong_ty,
    f.san_giao_dich,
    f.nganh_nghe,
    f.ngay_giao_dich_dau_tien,
    f.gia_dong_cua_ngay_dau_tien,
    f.khoi_luong_ngay_dau_tien,
    f.von_dieu_le,
    f.so_luong_co_phieu_niem_yet,
    f.so_luong_co_phieu_luu_hanh,
    f.co_phieu_quy,
    f.co_phieu_pho_thong,
    f.co_phieu_uu_dai
FROM raw_fund f
LEFT JOIN stocks s ON f.symbol = s.code
