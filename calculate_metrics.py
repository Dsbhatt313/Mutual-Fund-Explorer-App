import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime

# Approximate daily risk-free rate (6% annual)
RISK_FREE_RATE = 0.06 / 252

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="kakabapa12",
        database="mf_database"
    )

def calculate_and_store_metrics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all Nifty 50 data once (for efficiency)
    cursor.execute("SELECT date, close FROM nifty50_data ORDER BY date ASC")
    nifty_rows = cursor.fetchall()
    nifty_df = pd.DataFrame(nifty_rows)
    nifty_df['date'] = pd.to_datetime(nifty_df['date'])
    nifty_df['close'] = nifty_df['close'].astype(float)
    nifty_df['return'] = nifty_df['close'].pct_change()
    nifty_df.dropna(inplace=True)

    # Get all scheme codes
    cursor.execute("SELECT DISTINCT scheme_code FROM mutual_funds")
    scheme_codes = [row['scheme_code'] for row in cursor.fetchall()]

    for scheme_code in scheme_codes:
        print(f"\nProcessing scheme: {scheme_code}")

        # Fetch NAV history
        cursor.execute("""
            SELECT nav_date, nav_value FROM historical_nav
            WHERE scheme_code = %s ORDER BY nav_date ASC
        """, (scheme_code,))
        nav_rows = cursor.fetchall()

        if len(nav_rows) < 20:
            print(f"  Skipped: Not enough NAV data")
            continue

        nav_df = pd.DataFrame(nav_rows)
        nav_df['nav_date'] = pd.to_datetime(nav_df['nav_date'])
        nav_df['nav_value'] = nav_df['nav_value'].astype(float)
        nav_df = nav_df[nav_df['nav_value'].notnull() & (nav_df['nav_value'] != 0)]

        nav_df['return'] = nav_df['nav_value'].pct_change()
        nav_df.dropna(inplace=True)

        # Merge NAV and Nifty data on date
        merged_df = pd.merge(
            nav_df[['nav_date', 'return']],
            nifty_df[['date', 'return']],
            left_on='nav_date',
            right_on='date',
            how='inner',
            suffixes=('_scheme', '_nifty')
        ).dropna()

        if len(merged_df) < 20:
            print(f"  Skipped: Not enough overlapping NAV & Nifty data ({len(merged_df)} rows)")
            continue

        # Extract aligned returns
        scheme_returns = merged_df['return_scheme'].reset_index(drop=True)
        market_returns = merged_df['return_nifty'].reset_index(drop=True)
        excess_returns = scheme_returns - RISK_FREE_RATE

        std_dev = np.std(scheme_returns) * np.sqrt(252)
        downside_std = np.std(scheme_returns[scheme_returns < 0]) * np.sqrt(252)

        try:
            beta = np.cov(scheme_returns, market_returns)[0][1] / np.var(market_returns)
        except Exception as e:
            print(f"  Skipped: Failed to calculate beta ({e})")
            continue

        sharpe = (excess_returns.mean() * 252) / std_dev if std_dev > 0 else None
        sortino = (excess_returns.mean() * 252) / downside_std if downside_std > 0 else None

        scheme_annual_return = scheme_returns.mean() * 252
        market_annual_return = market_returns.mean() * 252
        alpha = scheme_annual_return - (RISK_FREE_RATE * 252 + beta * (market_annual_return - RISK_FREE_RATE * 252))

        # Convert to native Python floats
        alpha = float(alpha) if alpha is not None else None
        beta = float(beta) if beta is not None else None
        sharpe = float(sharpe) if sharpe is not None else None
        sortino = float(sortino) if sortino is not None else None
        std_dev = float(std_dev) if std_dev is not None else None

        # Insert into DB
        cursor.execute("""
            INSERT INTO scheme_metrics 
                (scheme_code, alpha, beta, sharpe_ratio, sortino_ratio, std_dev)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                alpha=VALUES(alpha),
                beta=VALUES(beta),
                sharpe_ratio=VALUES(sharpe_ratio),
                sortino_ratio=VALUES(sortino_ratio),
                std_dev=VALUES(std_dev),
                calculated_on=CURRENT_TIMESTAMP
        """, (scheme_code, alpha, beta, sharpe, sortino, std_dev))
        conn.commit()

        print(f"  ✔ Metrics saved.")

    cursor.close()
    conn.close()
    print("\n✅ All available scheme metrics calculated and stored.")

if __name__ == "__main__":
    calculate_and_store_metrics()
