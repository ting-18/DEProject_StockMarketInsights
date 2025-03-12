# Post-Pandemic Stock Market Recovery/Rebound (Project name)

e.g.1. Macro-Economic Impact Report:
Objective: Analyzes the impact of macroeconomic factors (interest rates, inflation, GDP growth) on a stock or sector.
e.g.2. Sector Performance Report:
Objective: Analyzes the performance of a specific sector, such as technology or healthcare, and its impact on individual stocks within that sector.
Example:
Sector: Technology
Sector Performance (Last Quarter):
Total Market Cap: $5 trillion
Average Return: +6%
Best Performing Stocks:

## Table of Content


## Overview
This is a data engineer project focus on stock market。 
The goal of this project is to ....


automate process
### Problem Description
This project aims to 

Some of the questions answered
- 疫情后股市恢复情况
- 时间是金钱，多长时间恢复？ 恢复最快的股票
- 目前股市情况
- 预测

- 大选对股市的影响？ 其他宏观因素（利率，失业率,疫情期间的政府补助，人类活动）
- 全球恢复情况（China, India）
- Why and possible effects


- 分析方法： 宏观分析 --》找最早恢复的那支/类股票-->具体分析原因

### Architecture and Technologies




The Technologies used:
- Cloud: GCP
- Container: Docker
- Infrastructure as code (IaC): Terraform
- Workflow orchestration: Airflow
- Storage / DataLake: GCS
- Data Warehouse: BigQuery
- Batch processing: Spark
- Data Modeling: dbt
- Dashboard: Google Data Studio

How does this end-to-end pipeline work?


### Data Sources
- Raw S&P 500 stocks data
  - Get historical data from Yahoo Finance API via yfinance package.
  - 
- Reference table () for stock company information.
- External data sources like COVID-cases, events, news that could impact stock price.

NASDAQ 100 and Dow Jones 30


### dbt project
A standard dbt project focuses on transforming and modeling raw data into analytics-ready tables, i.e. defining clear layers of transformations that clean, aggregate, and structure stock market data for analytics and reporting.
### Design the dbt Models
dbt follows a staging → intermediate → marts structure.
#### 1. Staging Layer (stg_*) - Cleans and standardizes raw data.
Load raw data into staging tables, ensuring clean and structured formats.
Remove duplicates, rename columns, and standardize data types.
| Table Name | Purpose |
|------------|----------|
| stg_stocks | Standardizes stock price data (Open, High, Low, Close, Volume).|




#### 2. Intermediate Layer (int_*) - Performs calculations and aggregations.
Create aggregated or derived calculations such as moving averages, stock returns, volatility, etc.
| Table Name | Purpose |
|------------|----------|
| int_stock_returns | Calculates daily, weekly, and monthly returns.|
| int_moving_averages | Computes 30-day and 90-day moving averages. |
| int_sector_performance | Aggregates stock performance by sector. |
| int_volatility | Measures stock volatility (standard deviation of returns). |
| int_news_impact | Computes sentiment scores for stock movements. |


#### 3. Marts Layer (dim_* and fact_*) - Provides final tables for dashboarding.
Fact tables: Contain numerical values for analytics.
Dimension tables: Contain descriptive information.
| Table Name | Purpose |
|------------|----------|
| fact_stock_prices |	Main table with price, volume, returns, and moving averages. |
| fact_trading_activity |	Aggregated trading volume and order flow. |
| fact_news_sentiment |	Sentiment trends over time for stocks. |
| dim_stock_metadata | Stock details (company name, sector, industry). |
| dim_dates	| Date dimension for time-based filtering. |
	




### Dashboard/Visualization




### Reproducing this repo(Try these in a VM after finished this project)
1. git clone
2. Environment setup
  - Set up Cloud Infrastructure \
    Local setup terraform, GCP account, projectID
    Excute
    ```
    #Git Bash shell
    cd 1_terraform-gcp/terraform
    terraform init
    terraform plan
    terraform apply
    terraform destroy 
    ```
    
- Credentials 
