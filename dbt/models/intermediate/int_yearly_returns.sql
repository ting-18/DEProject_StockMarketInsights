{{
    config(
        materialized='table'      
    )
}}


WITH yearly_prices AS (
    -- Get first and last available price for each ticker and year
    SELECT 
        ticker,
        DATE_TRUNC(trade_date, year) AS year_start,
        FIRST_VALUE(closing_price) OVER (
            PARTITION BY ticker, DATE_TRUNC(trade_date, year) 
            ORDER BY trade_date
        ) AS start_price,
        LAST_VALUE(closing_price) OVER (
            PARTITION BY ticker, DATE_TRUNC(trade_date, year) 
            ORDER BY trade_date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS end_price
    FROM {{ ref('stg_sp500_stockdata') }}
)

SELECT DISTINCT     
    ticker, 
    EXTRACT(YEAR FROM year_start) AS year,
    start_price,
    end_price,
    (end_price - start_price) / start_price * 100 AS yearly_return    
FROM yearly_prices
ORDER BY ticker, year


