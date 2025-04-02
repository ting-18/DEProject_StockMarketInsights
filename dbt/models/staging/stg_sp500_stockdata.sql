{{
    config(
        materialized='view',
        partition_by={
        "field": "trade_date ",
        "data_type": "date",
        "granularity": "day"       
        },
        cluster_by=["ticker"]  
    )
}}

with stockdata as 
(
  select *,
    row_number() over(partition by ticker, Date) as rn
  from {{ source('staging','sp500_stocks_table') }}
  where ticker is not null 
)
select
    -- stock symbol:use Jinja to ensure compatibility across different databases:
    {{ dbt.safe_cast('ticker', api.Column.translate_type('string')) }} as ticker,

    -- timestamps
    cast(Date as DATE) as trade_date,  

    -- price info
    -- {{ dbt.safe_cast("passenger_count", api.Column.translate_type("integer")) }} as passenger_count,
    cast(volume as integer) as volume,
    cast(open as numeric) as opening_price,
    cast(close as numeric) as closing_price,
    cast(high as numeric) as highest_price,
    cast(low as numeric) as lowest_price,
from stockdata
where rn = 1


-- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'
-- {% if var('is_test_run', default=true) %}

--   limit 100

-- {% endif %}