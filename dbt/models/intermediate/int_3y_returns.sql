{{
    config(
        materialized='table', 
        partition_by={
        "field": "ticker",
        "data_type": "string"     
        },
        cluster_by=["trade_date"]          
    )
}}

WITH threey_start_dates AS (
    SELECT 
        ticker,
        MIN(trade_date) AS start_date        
    FROM {{ ref('stg_sp500_stockdata') }}
    WHERE trade_date >= CURRENT_DATE - INTERVAL 3 YEAR  -- Current year data
    GROUP BY ticker  -- Current year data
),
threey_start_prices AS (
    SELECT 
        s.ticker,
        s.closing_price AS start_price    
    FROM threey_start_dates y
    LEFT JOIN {{ ref('stg_sp500_stockdata') }} s
    ON s.ticker = y.ticker AND s.trade_date = y.start_date
)



select 
    s.ticker,
    s.trade_date,    
    ROUND((s.closing_price - y.start_price) / y.start_price * 100, 2) as threey_return
from {{ ref('stg_sp500_stockdata') }} s
join threey_start_prices y on s.ticker = y.ticker
where s.trade_date between CURRENT_DATE - INTERVAL 3 YEAR and current_date

