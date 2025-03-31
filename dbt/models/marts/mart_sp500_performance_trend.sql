{{
    config(
        materialized='table'       
    )
}}


SELECT ticker, trade_date, opening_price, closing_price, lowest_price, highest_price, volume
FROM {{ ref('stg_sp500_stockdata') }}
WHERE ticker = "^GSPC" 
ORDER BY trade_date DESC