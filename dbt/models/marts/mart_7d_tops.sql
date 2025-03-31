{{
    config(
        materialized='table'       
    )
}}


WITH latest_date AS (
    SELECT trade_date 
    FROM {{ ref('int_7d_returns') }}
    ORDER BY trade_date DESC 
    LIMIT 1
),
last_7d_top_gianers AS (
    SELECT 
        ticker,
        seven_days_return        
    FROM {{ ref('int_7d_returns') }}
    WHERE trade_date = (SELECT trade_date FROM latest_date)  
    ORDER BY seven_days_return DESC LIMIT 4 
),
last_7d_top_losers AS (
    SELECT 
        ticker,
        seven_days_return        
    FROM {{ ref('int_7d_returns') }}
    WHERE trade_date = (SELECT trade_date FROM latest_date)  
    ORDER BY seven_days_return LIMIT 4
),
last_7d_tops AS (
    SELECT ticker, seven_days_return
    FROM last_7d_top_gianers 
    UNION DISTINCT
    SELECT ticker, seven_days_return
    FROM last_7d_top_losers     
)


SELECT t.ticker, t.seven_days_return, info.sector
FROM last_7d_tops t
LEFT JOIN {{ ref('sp500_stocks_info') }}  info
ON t.ticker = info.ticker
ORDER BY seven_days_return DESC