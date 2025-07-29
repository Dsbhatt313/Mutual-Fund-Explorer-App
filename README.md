# Mutual-Fund-Explorer-App

## 🚀 Project Overview
Mutual Fund Explorer is an interactive web application built to help investors and analysts discover and research Indian mutual funds. The app lets users:

1. Search AMC and mutual fund schemes across categories (debt/short-term/dynamic/etc.)

2. View real-time and historical NAV data (fetched and stored from AMFI / MFAPI)

3. Plot NAV movement and compare it side by side with Nifty 50 benchmark

4. View detailed risk/performance metrics: Alpha, Beta, Sharpe, Sortino, Std. Deviation

5. Get a suggested action ("Buy/Hold/Sell") based on returns vs. benchmark

6. All metrics, data loaders, and visualizations are automated and updated regularly

## 🏗️ Features
1. Clean, responsive UI built with Bootstrap-like CSS and custom JavaScript

2. Fast search/filter for AMCs or scheme names

3. Charts for NAV & benchmark comparison (via Chart.js)

4. In-depth risk metrics (Alpha, Beta, etc.), calculated using pandas/numpy on stored historical NAV & Nifty50 prices

5. Easy Data Freshness Tracking for users & admins

## 🗂️ Project Structure
**Core Application:**
- `app.py` - Main Flask app, API routes & frontend rendering
- `templates/` - HTML templates (index, schemes, scheme_details)
- `static/` - CSS styling and JavaScript interactivity

**Data Processing Scripts:**
- `load_data.py` - Loads static scheme master data into MySQL
- `load_nifty50.py` - Loads Nifty50 historical data into MySQL
- `backfill_historical.py` - Fetches historic NAV data per scheme via MFAPI
- `data_updater.py` - Scheduled daily NAV, auto-update (from AMFI)
- `calculate_metrics.py` - Calculates advanced metrics for each scheme

**Data Files:**
- `cleaned_dataset.csv` - Mutual fund scheme master (basic snapshot)
- `Nifty-50-Historical-Data.csv` - Historic Nifty 50 price data

## 💾 Database Schema
**Uses MySQL with three main tables:**

1. mutual_funds: Holds latest NAV, ISINs, names, AMC, etc.

2. historical_nav: Daily historic NAVs for all tracked schemes

3. nifty50_data: Nifty50 historical OHLCV prices

4. scheme_metrics: Precomputed risk/return stats (alpha, beta, sharpe, etc.)

5. You will need to create these tables before running the app (see below).

## ⚙️ Data Sources
1. AMFI (India) — latest NAVs

2. MFAPI — for historical NAVs

3. Nifty 50 CSV — manual or sourced from investing.com or NSE

## 🛠️ Setup Guide
### Prerequisites
1. Python 3.8+

2. MySQL server running locally

3. pip install the following:
    Flask mysql-connector-python pandas numpy APScheduler requests chart.js

### Steps
1. Clone this repository

2. Provision MySQL database

    sql
    CREATE DATABASE mf_database;
3. Load scheme master and Nifty50 data

    bash
    python load_data.py
    python load_nifty50.py
4. Backfill historical NAVs (via MFAPI.in, automated sleep between calls)

    bash
    python backfill_historical.py
5. Calculate metrics

    bash
    python calculate_metrics.py
6. (Optional) Run daily updater to keep NAVs refreshed

    The apscheduler job in app.py and data_updater.py does this on a scheduled basis

7. Run the Flask app

    bash
    python app.py
8. Open the browser:
    Go to http://localhost:5000

## ✨ Usage
1. Start at the homepage:

    Choose AMC → View schemes
    
    Select a fund to view full details

2. Fund details show: ISIN codes, Scheme code, NAV snapshots, NAV chart, performance vs. Nifty50, risk metrics, and a suggested action (Buy/Sell/Hold)

3. Risk metrics legend is provided for interpretation

## 📁 Customization & Extending
1. Add/modify schemes: Use cleaned_dataset.csv and reload

2. Add new benchmarks: Adapt code to include new index CSVs & DB tables

3. Performance Metrics: Tune your risk-free rate, comparison window, etc. in calculate_metrics.py

4. Improve UI: static/styles.css and static/script.js are fully flexible

5. Production: Remove debug, consider deploying with gunicorn/uwsgi, and secure database credentials!

## 🧑💻 Contributing
PRs are welcome! Please open issues for bugs/suggested features.
To contribute, fork this repo, make improvements, and send a pull request.

## 📢 Credits & License
1. Mutual fund data sourced from AMFI and MFAPI.

2. Nifty 50 data is from official NSE sources or public CSVs (such as Investing.com or similar).

3. Built using Flask, pandas, Chart.js, and MySQL.

4. This project is provided under an open license for educational purposes and personal use only.
   
5. It is not intended for commercial distribution.

6. If you use or extend this project, please credit the above data sources.

You can simply copy and replace the old Credits & License section in your README with this one, or merge it as needed.
