# Stock Market Insights

## Table of Content
- [Overview](#overview)
- [Architecture and Technologies](#architecture-and-technologies)
- [ETL Data Pipeline](#etl-data-pipeline)
 - [Extract and load data](#extract-and-load-data)
 - [Data Transformation](#data-transformation)
 - [Dashboard/Visualization](#dashboard-visualization)
- [Reproducing this repo](#reproducing-this-repo)




## Overview
- This data engineering project focused on batch processing data to provide investors with stock market insights.
### project goal
- The project monitors S&P 500 stocks performance (like Apple, Amazon, Google, Nvidia, Microsoft) over time to help investors make informed investment decisions. \
	✅ Collect daily stock prices of all the S&P 500 stocks for the last 10 years.\
	✅ Compute price change/returns for the last 7 days, 30 days, and 1 year, and sector-wise performance.\
	✅ Visualize key factors such as price trends, sector performance, and top gainers and losers via the Google Looker Studio dashboard.\
	✅ Update data and a Google Looker Studio dashboard daily using batch processing.

### Problem description 
- Some of the questions answered:
"How's the S&P 500 performance for the last 10 years?"
"Which sector performed best for the last 30 days?"
"Which stocks had the highest return for the last 7 days, the last 30 days and the last 1 year?"
"Which stocks had the lowest return for the last 7 days, the last 30 days and the last 1 year?"
"What are the Top-Performing & Worst-Performing Stocks?"
"How's the historical trends of the top gainer"

## Architecture and Technologies
### Architecture
- ![architecture_image](images/  .png)

### The Technologies used:
- Cloud: Google Cloud Platform(GCP)
- Container: Docker, Docker Compose
- Infrastructure as code (IaC): Terraform
- Workflow orchestration: Airflow
- Storage / DataLake: Google Cloud Storage(GCS)
- Data Warehouse: BigQuery
- Batch processing: Python
- Transformation/Data Modeling: dbt
- Dashboard/ Data Visualization: Google Looker Studio

How does this end-to-end pipeline work?



## ETL Data Pipeline
### Extract and Load Data
- Data sources:
  - Raw S&P 500 stocks data: Get historical data from Yahoo Finance API via yfinance package.
  - Reference table (sp500_stocks_info.csv) for stock company information.
- DAG graph:
  ![img](images/DAG_graph.png)

- After ETL Pipeline, Data in BigQuery:
  ![img](images/bq_table1.png)
  ![img](images/bq_table2.png)

### Data Transformation
#### Data modeling: 


Schema Design for Stock Analysis
Fact Table: Stock Price Fact
Holds historical price data, serving as the core table.

Column	Type	Description
StockID	INT (FK)	Links to Stock Dimension
DateID	INT (FK)	Links to Date Dimension
OpenPrice	FLOAT	Opening price of the stock
ClosePrice	FLOAT	Closing price of the stock
HighPrice	FLOAT	Highest price of the day
LowPrice	FLOAT	Lowest price of the day
Volume	INT	Total shares traded
AdjClose	FLOAT	Adjusted closing price for splits, dividends
Dimension Tables
Stock Dimension
Stores company and stock information.

Column	Type	Description
StockID	INT (PK)	Unique identifier
Ticker	VARCHAR	Stock symbol (e.g., AAPL)
CompanyName	VARCHAR	Company name
Sector	VARCHAR	Sector (e.g., Tech, Finance)
Industry	VARCHAR	Industry classification
Date Dimension
Stores time-based attributes for trend analysis.

Column	Type	Description
DateID	INT (PK)	Unique identifier
Date	DATE	Actual date
Year	INT	Year
Quarter	INT	Quarter (1-4)
Month	INT	Month (1-12)
Weekday	INT	Day of the week (0-6)
Market Events Dimension (Optional)
Captures external events affecting stock prices.

Column	Type	Description
EventID	INT (PK)	Unique identifier
DateID	INT (FK)	Links to Date Dimension
EventType	VARCHAR	Type of event (e.g., Fed Rate Hike, Earnings Report)
Impact	VARCHAR	Market impact (Positive, Negative, Neutral)




Structure Aggregated Fact Tables:
Table: MonthlyStockPerformance (Aggregated Table)
Column	Type	Description
StockID	INT (FK)	Links to Stock Dimension
Year	INT	Year of return calculation
Month	INT	Month of return calculation
MonthlyReturn	FLOAT	% return based on price change











What insights you want to extract (e.g., stock performance, volatility, trends, sector-wise comparison).
Data modeling design: Star Schema.
Base fact table: 
granularity: daily

Using star schema for stock analytics:

Fact Table: Stock Prices (StockID, Date, Open, Close, High, Low, Volume, AdjustedClose)
Dimension Tables:
Stock Dimension (StockID, Ticker, Name, Sector, Industry)
Date Dimension (DateID, Year, Quarter, Month, Day, Weekday)
Market Events (EventID, Date, Description, Impact)
This allows efficient querying for historical trends, sector-wise performance, and volatility analysis.


Stock Trend Analysis: Find moving averages, RSI, Bollinger Bands.
Sector-wise Performance: Compare sector gains/losses.
Volatility Modeling: Calculate beta, standard deviation.
Anomaly Detection: Identify stock price manipulation.
News Sentiment Analysis: Extract insights from financial news.




A stock market data model typically includes:

Entity	Description
Stocks	Represents individual stocks (e.g., AAPL, TSLA).
Companies	Issuers of stocks, including sector & financials.
Prices	Tracks stock prices over time (open, close, high, low).
Trades	Buy/sell transactions with timestamp, volume, and price.
Market Indexes	Tracks broader market performance (e.g., S&P 500).
Corporate Actions	Events like dividends, stock splits, mergers.
Macroeconomic Data	Interest rates, inflation, and GDP impacting markets.
News & Sentiment	Market-moving news and sentiment analysis.

Stock (StockID, Ticker, CompanyID, Sector, Industry)
Company (CompanyID, Name, Sector, MarketCap)
StockPrice (StockID, Date, Open, Close, High, Low, Volume)
Trade (TradeID, StockID, Timestamp, Price, Volume, TraderID)











#### dbt project: dbt-SQL-Transformation
A standard dbt project focuses on transforming and modeling raw data into analytics-ready tables, i.e. defining clear layers of transformations that clean, aggregate, and structure stock market data for analytics and reporting.
##### Design the dbt Models
dbt project Structure: dbt follows a staging → intermediate → marts structure.
```
stock_analysis/
│── models/
│   │── staging/
│   │   ├── stg_stock_prices.sql
│   │   ├── stg_companies.sql
│   │   ├── stg_dates.sql
│   │── intermediate/
│   │   ├── int_stock_returns.sql
│   │   ├── int_volatility.sql
│   │── marts/
│   │   ├── stock_performance.sql
│   │   ├── sector_analysis.sql
│── dbt_project.yml
│── packages.yml
│── seeds/
│   ├── sp500_stocks_info
│── snapshots/
│── tests/
│── macros/

```
staging/ → Cleans and standardizes raw data (1:1 with source tables).
intermediate/ → Derived tables for calculations (e.g., returns, volatility).
marts/ → Final analytics tables for reporting.
seeds/ → Static reference data (e.g., stocks info).
tests/ → Data quality tests (e.g., null checks, uniqueness). Ensure data quality with tests.





Stock Price Fact (Daily Data) → Base transactional fact.
Stock Performance Fact (Monthly Returns) → Aggregated fact table (not just a derived table but a summarized fact).
Sector Analysis Fact → Another fact table at the sector level.
Dimension Tables → Companies, Dates, Sectors.


### Design dbt Models
#### 1. Staging Layer (stg_*) - Cleans and standardizes raw data.
- Load raw data into staging tables, ensuring clean and structured formats.
- Normalization: \
	This layer removes duplicates, renames columns, fill in missing values, and standardizes data types to ensure the data format matches your target schema. Ensures one row per stock per day.

| Table Name | Purpose |
|------------|----------|
| stg_stocks | Standardizes stock price data (Open, High, Low, Close, Volume).|




#### 2. Intermediate Layer (int_*) - Transformations: Performs calculations and aggregations.
Create aggregated or derived calculations such as moving averages, stock returns, volatility, etc.
Derived Tables: used to feed into final reporting tables.

e.g. 
Fact Table: monthly_returns stores precomputed results for performance analysis.
Granularity: Monthly-level summary.
Optimization: Improves dashboard performance.


| Table Name | Purpose |
|------------|----------|
| int_stock_returns | Calculates daily, weekly, and monthly returns.|
| int_moving_averages | Computes 30-day and 90-day moving averages. |
| int_sector_performance | Aggregates stock performance by sector. |
| int_volatility | Measures stock volatility (standard deviation of returns). |
| int_news_impact | Computes sentiment scores for stock movements. |

Table: stock_performance_fact (Granularity: Monthly)

Tracks historical stock performance over time.
Easy to calculate daily returns, volatility, moving averages, etc.
Supports slicing by date, company, sector, or exchange.



people calculate different types of metrics depending on the goal (trading, investing, risk management)
- Price Change Metrics: Daily return, cumulative return.
- Trend Indicators: \
	- Moving Averages (Simple Moving Average-SMA, Exponential Moving Average-EMA) – smooth out price to detect trends.   Popular Moving Averages: 5-day MA – very short-term. 20-day MA – about 1 month of trading. 50-day MA – medium-term trend. 200-day MA – long-term trend.\
Moving Averages helps identify the overall trend (uptrend, downtrend).\
Moving Averages smooths noisy data to see clearer trends.\
	- Moving Average Crossovers – identify trend reversals.  Traders use MA crossovers (like when 50-day MA crosses above 200-day MA) as buy/sell signals.
	- Relative Strength Index (RSI) – measures if a stock is overbought or oversold.
	- MACD (Moving Average Convergence Divergence) – shows momentum and trend direction.


- Volatility & Risk: \
  Volatility (Standard Deviation of Returns) – measures price fluctuation.
Average True Range (ATR) – measures market volatility.
Sharpe Ratio – return vs. risk.
Beta – how much the stock moves compared to the market.
- Volume Analysis:
Average Volume – helps confirm trends.
Volume Spikes – can indicate big moves or interest.



- __Daily return__ measures how much the stock price changes from one day to the next, expressed as a percentage. It's commonly calculated using the closing prices. \
Daily Return = (Today’s Close − Yesterday’s Close)/Yesterday’s Close × 100% \
It tells you how much the stock increased or decreased in one day. \
Daily Return shows profit/loss over time.
- __Cumulative Return__ – total return over a period.
  The formula for cumulative return at time 𝑡 is: \
  Cumulative Return<sub>t</sub> = (1+ Return<sub>1</sub>) x (1+ Return<sub>2</sub>) x ... x (1+ Return<sub>t</sub>) -1  \
This formula helps in tracking the total return over time, considering the effect of compounding. \
	Q: Multiplication instead of simple addition ensures proper compounding. bcz daily return is based on yesterday's price.
- __Volatility__ measures how much the stock price fluctuates over time. \
e.g. daily volatility, a common approach is calculating the standard deviation of daily returns over a period (like 30 days).  Formula (simplified): Volatility = Standard Deviation of Daily Returns\
If volatility = 1.5%, it means the stock typically moves ±1.5% per day from its average return.\
Volatility helps assess risk—higher volatility = higher risk (but potentially higher reward).
- __Moving Average (MA)__ is a very common indicator in stock analysis, used to smooth out short-term price fluctuations and identify trends over time.







#### 3. Marts Layer (dim_* and fact_*) - Analytics: Provides final tables for dashboarding. 
Goal: Create Fact & Dimension tables for business insights.
Star Schema → Fact Tables & Dimension Tables.
	Fact tables: Contain numerical values for analytics. (aggregated fact table)
	Dimension tables: Contain descriptive information.
| Table Name | Purpose |
|------------|----------|
| fact_stock_prices |	Main table with price, volume, returns, and moving averages. |
| fact_trading_activity |	Aggregated trading volume and order flow. |
| fact_news_sentiment |	Sentiment trends over time for stocks. |
| dim_stock_metadata | Stock details (company name, sector, industry). |
| dim_dates	| Date dimension for time-based filtering. |
	


In fact table, you might store precomputed MAs (like 20-day MA, 50-day MA) as extra columns, or calculate them on the fly with SQL window functions or in Python/Pandas.


Sector-Wise Analysis (Fact-Dimension Modeling)
📌 Goal: Analyze performance at the sector level. 📌 Data Modeling Concept: Star Schema → Fact + Dimension Table.

Example: Sector Fact Table
Star Schema:

Fact Table: sector_performance (aggregated returns per sector).
Dimension Tables:
stg_companies (maps stocks to sectors).
stg_dates (time-based attributes).













### Dashboard/Visualization

![img](images/Dashboard.png)
or  https://lookerstudio.google.com/reporting/94fbb36f-a6a8-406d-aa0a-4b3a19084a29 

1. Overall Market Trends 
Line Chart: Tracks the S&P 500 index trends over 10 years.
2. Sector-wise Performance
Bar Chart: Shows percentage gains/losses per sector for the last 30 days.
3. Top Gainer Stock Price Trend
Line Chart: Tracks 30-day-top-gainer stock price trends for 10 years.
4. Top gainers/losers
Bar Chart: Shows Top gainers and losers for the last 7 days, 30 days, and 1 year.



## Reproducing this repo
1. git clone 
2. Environment setup
  - Set up Terraform, GCP account and SDK \
    Local install and setup terraform: \
    GCP account setup: Apply a GCP account, try free trial, new project and copy project ID. \
    Download and install SDK (Google Cloud CLI). and run commands below to authorizing gcloud CLI access Google Cloud.\
       ```
       #Git Bash shell
       gcloud init
       gcloud auth application-default login   #After this, $GOOGLE_APPLICATION_CREDENTIALS was set to google cloud account default credential.json. Which is different from Service Account credential.
       ``` 
    Set Service Account for this project: GCP console >menu>IAM & Admin> Service Accounts -> Create service account ---> once created, click three dots at the right>Manage Keys>json> save the downloaded serviceaccount_credential.json file.
    
  - Set up Cloud Infrastructure(Bucket and dataset) via terraform
    Edit terraform/variables.tf and run commands below.
    ```
    #Git Bash shell      
    cd 1_terraform-gcp/terraform
    terraform init
    terraform plan
    terraform apply
    terraform destroy 
    ```
3. EL pipeline via airflow  

- Environment setup 
  ```
  #Git Bash shell  
  mv $HOME/Downloads/<YOUR SERVICE ACCOUNT KEY>.json ~/.google/credentials/google_credentials.json
  ```
  Edit docker-compose.yaml: GCP_PROJECT_ID

- Build and run custom airflow container
    ```
    #Git Bash shell      
    cd airflow
    docker-compose build    (it takes 10 mins for the first time)
    docker-compose up airflow-init
    docker-compose up -d

    docker-compose down   
    ```
- Check or manually run Dag/pipeline in Browser: localhost:8080    airflow/airflow \
  Two DAGs: stocksdata_gcs_bq_dag - Extrat stock data for 10 years. \
  		_dag - Scheduled daily, and extract today's stock data at the end of a day.
  

4. dbt Transformation
   ```
   dbt 
   ```




## Further work
(all the tickers whose stock price is under 200 dollars )
stock recommendation model
