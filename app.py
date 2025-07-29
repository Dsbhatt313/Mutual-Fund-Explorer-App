from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from calculate_metrics import calculate_and_store_metrics

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="kakabapa12",
        database="mf_database"
    )

# Routes
@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT MAX(last_updated) as last_update FROM mutual_funds")
    last_update = cursor.fetchone()['last_update']
    last_update_str = last_update.strftime('%d %b %Y, %I:%M %p') if last_update else "Never"
    cursor.close()
    conn.close()
    return render_template("index.html", last_updated=last_update_str)

@app.route("/schemes/<amc>")
def schemes(amc):
    return render_template("schemes.html", amc=amc)

@app.route("/scheme-details/<scheme>")
def scheme_details(scheme):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT scheme_code, isin_growth, isin_div_reinvestment, 
               scheme_name, net_asset_value, amc_name 
        FROM mutual_funds 
        WHERE scheme_name = %s
    """, (scheme,))
    
    details = cursor.fetchone()

    cursor.execute("SELECT * FROM scheme_metrics WHERE scheme_code = %s", (details['scheme_code'],))
    metrics = cursor.fetchone() or {}
    
    if details:
        cursor.execute("""
            SELECT MAX(last_updated) as last_update FROM mutual_funds 
            WHERE scheme_code = %s
        """, (details['scheme_code'],))
        last_update = cursor.fetchone()['last_update']
        details['last_updated'] = last_update.strftime('%d %b %Y, %I:%M %p') if last_update else "Unknown"
    
    cursor.close()
    conn.close()
    return render_template("scheme_details.html", details=details, metrics=metrics)

# API Endpoints
@app.route("/get_amc")
def get_amc():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT amc_name FROM mutual_funds")
    amcs = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({"data": amcs})

@app.route("/get_schemes/<amc>")
def get_schemes(amc):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scheme_name FROM mutual_funds WHERE amc_name = %s", (amc,))
    schemes = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({"data": schemes})

@app.route("/get_nifty50_history")
def get_nifty50_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT date, close 
            FROM nifty50_data 
            ORDER BY date DESC 
            LIMIT 30
        """)
        
        history = cursor.fetchall()
        formatted_history = [{
            'date': row['date'].strftime('%Y-%m-%d'),
            'close': float(row['close'])
        } for row in history]
        
        return jsonify(formatted_history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/get_historical_nav/<scheme_code>")
def get_historical_nav(scheme_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get scheme history
        cursor.execute("""
            SELECT nav_date, nav_value 
            FROM historical_nav 
            WHERE scheme_code = %s 
            ORDER BY nav_date DESC 
            LIMIT 30
        """, (scheme_code,))
        
        scheme_history = cursor.fetchall()
        dates = [row['nav_date'] for row in scheme_history]
        
        # Get matching Nifty 50 data for the same dates
        placeholders = ','.join(['%s'] * len(dates))
        cursor.execute(f"""
            SELECT date, close 
            FROM nifty50_data 
            WHERE date IN ({placeholders})
            ORDER BY date DESC
        """, dates)
        
        nifty_history = cursor.fetchall()
        
        # Format the response
        result = {
            'scheme': [{
                'date': row['nav_date'].strftime('%Y-%m-%d'),
                'nav': float(row['nav_value'])
            } for row in scheme_history],
            'nifty50': [{
                'date': row['date'].strftime('%Y-%m-%d'),
                'close': float(row['close'])
            } for row in nifty_history]
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Scheduled Updates
scheduler = BackgroundScheduler()

def scheduled_update():
    from data_updater import update_database
    update_database()
    calculate_and_store_metrics()

scheduler.add_job(
    func=scheduled_update,
    trigger='cron',
    hour=6,
    minute=0
)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)
