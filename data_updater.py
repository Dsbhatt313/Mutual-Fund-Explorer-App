import requests
import re
from datetime import datetime
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="kakabapa12",
        database="mf_database"
    )

def fetch_amfi_data():
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching AMFI data: {e}")
        return None

def parse_amfi_data(raw_data):
    schemes = []
    current_amc = None
    
    for line in raw_data.split('\n'):
        amc_match = re.match(r'Mutual Fund Name:\s*(.+)', line)
        if amc_match:
            current_amc = amc_match.group(1).strip()
            continue
        
        if not line or ';' not in line or current_amc is None:
            continue
        
        parts = line.split(';')
        if len(parts) >= 6:
            scheme = {
                'scheme_code': parts[0].strip(),
                'scheme_name': parts[1].strip(),
                'isin_growth': parts[2].strip() if parts[2].strip() else None,
                'isin_div_reinvestment': parts[3].strip() if parts[3].strip() else None,
                'net_asset_value': float(parts[4].strip()),
                'amc_name': current_amc,
                'date': parts[5].strip() if len(parts) > 5 else datetime.now().strftime('%d-%b-%Y')
            }
            schemes.append(scheme)
    return schemes

def update_database():
    print(f"\nStarting data update at {datetime.now()}")
    
    raw_data = fetch_amfi_data()
    if not raw_data:
        return False
    
    schemes = parse_amfi_data(raw_data)
    if not schemes:
        print("No valid scheme data found")
        return False
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we already updated today
        cursor.execute("SELECT DATE(MAX(last_updated)) FROM mutual_funds LIMIT 1")
        last_update_date = cursor.fetchone()[0]
        
        current_date = datetime.now().date()
        if last_update_date and last_update_date == current_date:
            print("Data already updated today")
            return True
            
        # Update data
        cursor.execute("TRUNCATE TABLE mutual_funds")
        
        for scheme in schemes:
            # Current NAV
            cursor.execute("""
                INSERT INTO mutual_funds 
                (scheme_code, isin_growth, isin_div_reinvestment, 
                 scheme_name, net_asset_value, amc_name, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                scheme['scheme_code'],
                scheme['isin_growth'],
                scheme['isin_div_reinvestment'],
                scheme['scheme_name'],
                scheme['net_asset_value'],
                scheme['amc_name'],
                datetime.strptime(scheme['date'], '%d-%b-%Y') if scheme.get('date') else datetime.now()
            ))
            
            # Historical NAV
            cursor.execute("""
                INSERT INTO historical_nav 
                (scheme_code, nav_date, nav_value)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE nav_value = VALUES(nav_value)
            """, (
                scheme['scheme_code'],
                datetime.strptime(scheme['date'], '%d-%b-%Y').date() if scheme.get('date') else datetime.now().date(),
                scheme['net_asset_value']
            ))
        
        conn.commit()
        print(f"Successfully updated {len(schemes)} schemes")
        return True
        
    except Exception as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_database()