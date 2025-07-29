import pandas as pd
import mysql.connector
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="kakabapa12",
        database="mf_database"
    )

def create_nifty50_table():
    """Create the nifty50_data table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nifty50_data (
            date DATE PRIMARY KEY,
            close DECIMAL(10, 2),
            open DECIMAL(10, 2),
            high DECIMAL(10, 2),
            low DECIMAL(10, 2),
            volume BIGINT
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def clean_and_convert_data(df):
    """Clean and convert data types for the specific CSV format"""
    # Rename columns to match our database schema
    df = df.rename(columns={
        'Date': 'date',
        'Price': 'close',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Vol.': 'volume'
    })
    
    # Convert date column (handle different date formats)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Clean and convert numeric columns
    numeric_cols = ['close', 'open', 'high', 'low']
    for col in numeric_cols:
        # Remove commas and convert to float
        if df[col].dtype == object:
            df[col] = df[col].str.replace(',', '').astype(float)
    
    # Clean volume column (handle 'K' for thousands and 'M' for millions)
    if 'volume' in df.columns:
        df['volume'] = df['volume'].replace('-', '0')  # Handle missing values
        df['volume'] = df['volume'].astype(str).str.replace(',', '')
        
        # Convert K (thousands) and M (millions) to actual numbers
        multiplier = df['volume'].str.extract(r'([KM])', expand=False)
        numbers = pd.to_numeric(df['volume'].str.replace(r'[KM]', ''), errors='coerce')
        
        df['volume'] = numbers * multiplier.map({'K': 1e3, 'M': 1e6}).fillna(1)
        df['volume'] = df['volume'].fillna(0).astype(int)
    
    # Drop rows with missing essential data
    df = df.dropna(subset=['date', 'close'])
    
    return df

def load_nifty50_data(csv_path):
    """Load and process Nifty50 data from CSV to MySQL"""
    # Read CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Clean and convert data
    df = clean_and_convert_data(df)
    
    if df.empty:
        print("No valid data found after cleaning")
        return
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert data
    success_count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO nifty50_data (date, close, open, high, low, volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    close = VALUES(close),
                    open = VALUES(open),
                    high = VALUES(high),
                    low = VALUES(low),
                    volume = VALUES(volume)
            """, (
                row['date'].to_pydatetime().date(),
                row['close'],
                row.get('open', None),
                row.get('high', None),
                row.get('low', None),
                row.get('volume', None)
            ))
            success_count += 1
        except Exception as e:
            print(f"Error inserting data for {row['date']}: {e}")
    
    conn.commit()
    print(f"Successfully loaded {success_count} out of {len(df)} records")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # Path to your Nifty50 CSV file
    CSV_PATH = "Nifty 50 Historical Data.csv"
    
    print("Creating nifty50_data table if it doesn't exist...")
    create_nifty50_table()
    
    print(f"Loading data from {CSV_PATH}...")
    load_nifty50_data(CSV_PATH)
    print("Data loading completed.")