import pandas as pd
import mysql.connector

# Load dataset
df = pd.read_csv("cleaned_dataset.csv")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="kakabapa12",
    database="mf_database"
)
cursor = conn.cursor()

# Insert data into MySQL
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO mutual_funds (scheme_code, isin_growth, isin_div_reinvestment, scheme_name, net_asset_value, amc_name)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE net_asset_value = VALUES(net_asset_value);
    """, (row["Scheme Code"], row["ISIN Div Payout/ISIN Growth"], row["ISIN Div Reinvestment"], row["Scheme Name"], row["Net Asset Value"], row["AMC Name"]))

conn.commit()
cursor.close()
conn.close()