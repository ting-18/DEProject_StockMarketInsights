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


### Datasource
Narrow down S&P 500, NASDAQ 100 and Dow Jones 30

Get historical Stock Market data from a Python library- yfinance.

### Data modeling

### Data Transformation

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
