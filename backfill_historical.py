import requests
from datetime import datetime, timedelta
import mysql.connector
import time

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="kakabapa12",
        database="mf_database"
    )

def get_historical_nav_from_api(scheme_code):
    """Fetch historical NAV from MFAPI.in"""
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data for scheme {scheme_code}: {e}")
        return None

def backfill_scheme_history(scheme_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        data = get_historical_nav_from_api(scheme_code)
        if not data or 'data' not in data:
            print(f"No data found for scheme {scheme_code}")
            return
        
        for entry in data['data']:
            try:
                nav_date = datetime.strptime(entry['date'], '%d-%m-%Y').date()
                nav_value = float(entry['nav'])
                
                cursor.execute("""
                    INSERT INTO historical_nav 
                    (scheme_code, nav_date, nav_value)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nav_value = VALUES(nav_value)
                """, (scheme_code, nav_date, nav_value))
                
            except Exception as e:
                print(f"Error processing entry for {scheme_code}: {e}")
                continue
        
        conn.commit()
        print(f"Added {len(data['data'])} records for scheme {scheme_code}")
        
    finally:
        cursor.close()
        conn.close()

def backfill_historical():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all scheme codes from your database
        cursor.execute("SELECT DISTINCT scheme_code FROM mutual_funds")
        scheme_codes = [row['scheme_code'] for row in cursor.fetchall()]
        
        for scheme_code in scheme_codes:
            print(f"\nProcessing scheme {scheme_code}...")
            backfill_scheme_history(scheme_code)
            time.sleep(1)  # Be polite to the API
            
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Starting historical data backfill...")
    backfill_historical()
    print("\nBackfill completed")