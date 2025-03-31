{{
    config(
        materialized='table'       
    )
}}


WITH latest_date AS (
    SELECT trade_date 
    FROM {{ ref('stg_sp500_stockdata') }}
    ORDER BY trade_date DESC 
    LIMIT 1
),
start_dates AS (
    SELECT 
        ticker,
        MIN(trade_date) AS start_date        
    FROM {{ ref('stg_sp500_stockdata') }}
    WHERE trade_date >= (SELECT trade_date FROM latest_date) - INTERVAL 7 DAY  
    GROUP BY ticker  
),
start_prices AS (
    SELECT 
        s.ticker,
        s.closing_price AS start_price    
    FROM start_dates y
    LEFT JOIN {{ ref('stg_sp500_stockdata') }} s
    ON s.ticker = y.ticker AND s.trade_date = y.start_date
)


select 
    s.ticker,
    s.trade_date,    
    ROUND((s.closing_price - y.start_price) / y.start_price * 100, 2) as seven_days_return
from {{ ref('stg_sp500_stockdata') }} s
join start_prices y on s.ticker = y.ticker
where s.trade_date between (SELECT trade_date FROM latest_date) - INTERVAL 7 DAY and (SELECT trade_date FROM latest_date)



-- Only get latest 30 day return
-- WITH latest AS (
--     SELECT trade_date, closing_price 
--     FROM {{ ref('stg_sp500_stockdata') }}
--     ORDER BY trade_date DESC 
--     LIMIT 1
-- ),
-- past AS (
--     SELECT closing_price 
--     FROM {{ ref('stg_sp500_stockdata') }} 
--     WHERE date = (SELECT MAX(trade_date) FROM {{ ref('stg_sp500_stockdata') }} WHERE trade_date <= (SELECT trade_date FROM latest) - INTERVAL 30 DAY)
-- )
-- SELECT 
--     (latest.price - past.price) / past.price AS price_return_30d
-- FROM latest, past;