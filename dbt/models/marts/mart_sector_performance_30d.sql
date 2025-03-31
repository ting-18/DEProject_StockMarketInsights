{{
    config(
        materialized='table'       
    )
}}


WITH latest_date AS (
    SELECT trade_date 
    FROM {{ ref('int_30d_returns') }}
    ORDER BY trade_date DESC 
    LIMIT 1
),
last_30d_price_returns AS (
    SELECT 
        ticker,
        thirty_days_return        
    FROM {{ ref('int_30d_returns') }}
    WHERE trade_date = (SELECT trade_date FROM latest_date)
)


SELECT info.sector, AVG(r.thirty_days_return) AS sector_return
FROM last_30d_price_returns r
LEFT JOIN {{ ref('sp500_stocks_info') }} info
ON r.ticker = info.ticker
GROUP BY info.sector
ORDER BY sector_return DESC





