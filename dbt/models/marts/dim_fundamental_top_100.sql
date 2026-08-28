{{ config(
    materialized='table'
) }}

WITH fundamental AS (
    SELECT * FROM {{ ref('stg_fundamental') }}
)

SELECT
    symbol,
    ten_cong_ty,
    san_giao_dich,
    nganh_nghe,
    ngay_giao_dich_dau_tien,
    gia_dong_cua_ngay_dau_tien,
    khoi_luong_ngay_dau_tien,
    von_dieu_le,
    so_luong_co_phieu_niem_yet,
    so_luong_co_phieu_luu_hanh,
    co_phieu_quy,
    co_phieu_pho_thong,
    co_phieu_uu_dai
FROM fundamental
WHERE von_dieu_le IS NOT NULL
ORDER BY von_dieu_le DESC
LIMIT 100
