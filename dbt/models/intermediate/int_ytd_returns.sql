{{
    config(
        materialized='table', 
        partition_by={
        "field": "trade_date",
        "data_type": "date",
        "granularity": "day"       
        },
        cluster_by=["ticker "]        
    )
}}

WITH ytd_start_dates AS (
    SELECT 
        ticker,
        MAX(trade_date) AS ytd_start_date        
    FROM {{ ref('stg_sp500_stockdata') }}
    WHERE trade_date < date_trunc(CURRENT_DATE, year)  -- Current year data
    GROUP BY ticker  -- Current year data
),
ydt_start_prices AS (
    SELECT 
        s.ticker,
        -- y.ytd_start_date,
        s.closing_price AS ytd_start_price    
    FROM ytd_start_dates y
    LEFT JOIN {{ ref('stg_sp500_stockdata') }} s
    ON s.ticker = y.ticker AND s.trade_date = y.ytd_start_date
)


select 
    s.ticker,
    s.trade_date,
    ROUND((s.closing_price - y.ytd_start_price) / y.ytd_start_price * 100, 2) as ytd_return
from {{ ref('stg_sp500_stockdata') }} s
join ydt_start_prices y on s.ticker = y.ticker
where s.trade_date between date_trunc(CURRENT_DATE, year) and current_date


