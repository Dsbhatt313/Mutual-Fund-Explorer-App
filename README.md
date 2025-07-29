# Mutual-Fund-Explorer-App

## 🚀 Project Overview
Mutual Fund Explorer is an interactive web application built to help investors and analysts discover and research Indian mutual funds. The app lets users:

Search AMC and mutual fund schemes across categories (debt/short-term/dynamic/etc.)

View real-time and historical NAV data (fetched and stored from AMFI / MFAPI)

Plot NAV movement and compare it side by side with Nifty 50 benchmark

View detailed risk/performance metrics: Alpha, Beta, Sharpe, Sortino, Std. Deviation

Get a suggested action ("Buy/Hold/Sell") based on returns vs. benchmark

All metrics, data loaders, and visualizations are automated and updated regularly

## 🏗️ Features
Clean, responsive UI built with Bootstrap-like CSS and custom JavaScript

Fast search/filter for AMCs or scheme names

Charts for NAV & benchmark comparison (via Chart.js)

In-depth risk metrics (Alpha, Beta, etc.), calculated using pandas/numpy on stored historical NAV & Nifty50 prices

Easy Data Freshness Tracking for users & admins

## 🗂️ Project Structure
text
mutual-fund-explorer/
│
├── app.py                # Main Flask app, API routes & frontend rendering
├── templates/
│     ├── index.html
│     ├── schemes.html
│     └── scheme_details.html
├── static/
│     ├── styles.css      # App styling (colorful, modern, animated)
│     └── script.js       # App interactivity, chart rendering & page logic
│
├── load_data.py          # Loads static scheme master data into MySQL
├── load_nifty50.py       # Loads Nifty50 historical data into MySQL
├── backfill_historical.py# Fetches historic NAV data per scheme via MFAPI
├── data_updater.py       # Scheduled daily NAV, auto-update (from AMFI)
├── calculate_metrics.py  # Calculates advanced metrics for each scheme
│
├── cleaned_dataset.csv   # Mutual fund scheme master (basic snapshot)
├── Nifty-50-Historical-Data.csv # Historic Nifty 50 price data
│
├── requirements.txt      # (recommend to add) All dependencies
├── README.md             # This file!
💾 Database Schema
Uses MySQL with three main tables:

mutual_funds: Holds latest NAV, ISINs, names, AMC, etc.

historical_nav: Daily historic NAVs for all tracked schemes

nifty50_data: Nifty50 historical OHLCV prices

scheme_metrics: Precomputed risk/return stats (alpha, beta, sharpe, etc.)

You will need to create these tables before running the app (see below).

## ⚙️ Data Sources
AMFI (India) — latest NAVs

MFAPI — for historical NAVs

Nifty 50 CSV — manual or sourced from investing.com or NSE

## 🛠️ Setup Guide
Prerequisites
Python 3.8+

MySQL server running locally

pip install the following:
Flask mysql-connector-python pandas numpy APScheduler requests chart.js
(see requirements.txt)

Steps
Clone this repository

Provision MySQL database

sql
CREATE DATABASE mf_database;
# Create required tables as per your code (see .py scripts)
Load scheme master and Nifty50 data

bash
python load_data.py
python load_nifty50.py
Backfill historical NAVs (via MFAPI.in, automated sleep between calls)

bash
python backfill_historical.py
Calculate metrics

bash
python calculate_metrics.py
(Optional) Run daily updater to keep NAVs refreshed

The apscheduler job in app.py and data_updater.py does this on a scheduled basis

Run the Flask app

bash
python app.py
Open the browser:
Go to http://localhost:5000

## ✨ Usage
Start at the homepage:

Choose AMC → View schemes

Select a fund to view full details

Fund details show: ISIN codes, Scheme code, NAV snapshots, NAV chart, performance vs. Nifty50, risk metrics, and a suggested action (Buy/Sell/Hold)

Risk metrics legend is provided for interpretation

## 📁 Customization & Extending
Add/modify schemes: Use cleaned_dataset.csv and reload

Add new benchmarks: Adapt code to include new index CSVs & DB tables

Performance Metrics: Tune your risk-free rate, comparison window, etc. in calculate_metrics.py

Improve UI: static/styles.css and static/script.js are fully flexible

Production: Remove debug, consider deploying with gunicorn/uwsgi, and secure database credentials!

## 🧑💻 Contributing
PRs are welcome! Please open issues for bugs/suggested features.
To contribute, fork this repo, make improvements, and send a pull request.

## 📢 Credits & License
Mutual fund data sourced from AMFI and MFAPI.

Nifty 50 data is from official NSE sources or public CSVs (such as Investing.com or similar).

Built using Flask, pandas, Chart.js, and MySQL.

This project is provided under an open license for educational purposes and personal use only.
It is not intended for commercial distribution.

If you use or extend this project, please credit the above data sources.

You can simply copy and replace the old Credits & License section in your README with this one, or merge it as needed.
