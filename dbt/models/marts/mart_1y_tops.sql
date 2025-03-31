{{
    config(
        materialized='table'       
    )
}}


WITH latest_date AS (
    SELECT trade_date 
    FROM {{ ref('int_1y_returns') }}
    ORDER BY trade_date DESC 
    LIMIT 1
),
last_1y_top_gianers AS (
    SELECT 
        ticker,
        oney_return        
    FROM {{ ref('int_1y_returns') }}
    WHERE trade_date = (SELECT trade_date FROM latest_date)  
    ORDER BY oney_return DESC LIMIT 4 
),
last_1y_top_losers AS (
    SELECT 
        ticker,
        oney_return        
    FROM {{ ref('int_1y_returns') }}
    WHERE trade_date = (SELECT trade_date FROM latest_date)  
    ORDER BY oney_return LIMIT 4
),
last_1y_tops AS (
    SELECT ticker, oney_return
    FROM last_1y_top_gianers 
    UNION DISTINCT
    SELECT ticker, oney_return
    FROM last_1y_top_losers     
)


SELECT t.ticker, t.oney_return, info.sector
FROM last_1y_tops t
LEFT JOIN {{ ref('sp500_stocks_info') }}  info
ON t.ticker = info.ticker
ORDER BY oney_return DESC