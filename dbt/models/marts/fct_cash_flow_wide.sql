{% set get_items_query %}
    SELECT item_code, item_name, order_num
    FROM {{ ref('dim_cash_flow_schema') }}
    ORDER BY order_num ASC
{% endset %}

{% set items = run_query(get_items_query) %}

WITH staged AS (
    SELECT * FROM {{ ref('stg_cash_flow') }}
)

SELECT
    symbol,
    company_name,
    exchange,
    year,
    content
    {% for item in items %}
    , MAX(CASE WHEN item_code = '{{ item.item_code }}' THEN value END) AS "{{ item.item_code }} - {{ item.item_name }}"
    {% endfor %}
FROM staged
GROUP BY 
    symbol,
    company_name,
    exchange,
    year,
    content
ORDER BY 
    symbol, 
    year DESC
