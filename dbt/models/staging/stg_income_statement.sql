WITH raw_fact AS (
    SELECT * FROM {{ source('postgres', 'raw_income_statement') }}
    WHERE year >= 2016
),

top_100_companies AS (
    SELECT * FROM {{ ref('dim_fundamental_top_100') }}
),

dim_schema AS (
    SELECT * FROM {{ ref('dim_income_statement_schema') }}
)

SELECT
    f.symbol,
    top100.ten_cong_ty AS company_name,
    top100.san_giao_dich AS exchange,
    f.year,
    f.content,
    s.section_code,
    s.section_name,
    TRIM(f.code) AS item_code,
    s.item_name,
    s.level,
    s.order_num,
    CASE 
        WHEN f.value = -1 THEN 0 
        ELSE f.value 
    END AS value
FROM raw_fact f
INNER JOIN top_100_companies top100 ON f.symbol = top100.symbol
LEFT JOIN dim_schema s ON TRIM(f.code) = s.item_code
ORDER BY f.symbol, f.year DESC, s.order_num
