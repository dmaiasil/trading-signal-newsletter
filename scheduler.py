import os
import datetime
import resend
import pytz
from dotenv import load_dotenv
from database import SessionLocal, Signal

# Load environment variables
load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

def send_signal_alert(ticker, action, price, list_name, interval):
    print(f"--- Sending Alert for {ticker} to {TARGET_EMAIL} ---")
    
    subject = f"New Trading Signal: {action.upper()} {ticker}"
    action_color = "#2ecc71" if action.lower() == "buy" else "#e74c3c"
    
    html_content = (
        f"<h1 style='font-family: sans-serif;'>New Trading Signal</h1>"
        f"<p style='font-size: 16px;'>"
        f"List: <strong>{list_name}</strong><br>"
        f"Interval: <strong>{interval.capitalize()}</strong><br>"
        f"Action: <span style='color:{action_color}; font-weight: bold;'>{action.upper()}</span><br>"
        f"Ticker: <strong>{ticker}</strong><br>"
        f"Price: ${price:.2f}"
        f"</p>"
        f"<br><hr><p style='font-size: 11px; color: #bdc3c7;'>Sent automatically via M3 Radar, a DMS software.</p>"
    )

    try:
        resend.Emails.send({
            "from": "Trading Signals <onboarding@resend.dev>",
            "to": [TARGET_EMAIL],
            "subject": subject,
            "html": html_content,
        })
        print(f"SUCCESS: Alert dispatched for {ticker}.")
    except Exception as e:
        print(f"ERROR: {e}")

def send_newsletter():
    print(f"--- Starting Newsletter Process for {TARGET_EMAIL} ---")
    db = SessionLocal()
    
    try:
        # 1. Get Data (Using US/Eastern to match your local database timestamps)
        tz = pytz.timezone('US/Eastern')
        today_start = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Query only today's signals
        signals_today = db.query(Signal).filter(Signal.timestamp >= today_start).all()

        # 2. Build HTML
        subject = f"[Trading Signals Report: {datetime.date.today().strftime('%b %d, %Y')}]"
        html_content = "<h1 style='font-family: sans-serif;'>Daily Signal Summary</h1>"
        
        # Define your active list names here
        target_lists = ["Tier 1"] 
        
        for list_name in target_lists:
            list_signals = [s for s in signals_today if s.list_name == list_name]
            
            html_content += f"<h2 style='border-bottom: 1px solid #eee;'>{list_name}</h2>"
            
            if not list_signals:
                html_content += "<p style='color: gray;'>No new signals for this list today.</p>"
            else:
                html_content += "<ul style='list-style: none; padding: 0;'>"
                for s in list_signals:
                    action_color = "#2ecc71" if s.action.lower() == "buy" else "#e74c3c"
                    html_content += (
                        f"<li style='margin-bottom: 10px; font-size: 16px;'>"
                        f"<span style='color:{action_color}; font-weight: bold;'>{s.action.upper()}</span> "
                        f"<strong>{s.ticker}</strong> ({s.interval.capitalize() if s.interval else 'Daily'}) @ ${s.price:.2f} "
                        f"<span style='color: #95a5a6; font-size: 12px;'>({s.timestamp.strftime('%I:%M %p')})</span>"
                        f"</li>"
                    )
                html_content += "</ul>"

        # Catch-all for any other lists
        other_signals = [s for s in signals_today if s.list_name not in target_lists]
        if other_signals:
            html_content += "<h3>Other Lists</h3><ul>"
            for s in other_signals:
                html_content += f"<li><b>{s.action.upper()}</b> {s.ticker} ({s.interval.capitalize() if s.interval else 'Daily'}) @ ${s.price:.2f}</li>"
            html_content += "</ul>"

        html_content += "<br><hr><p style='font-size: 11px; color: #bdc3c7;'>Sent automatically via Trading Bridge Dashboard.</p>"

        # 3. Send Email
        print(f"Found {len(signals_today)} signals. Sending to Resend...")
        
        resend.Emails.send({
            "from": "Trading Signals <onboarding@resend.dev>",
            "to": [TARGET_EMAIL],
            "subject": subject,
            "html": html_content,
        })
        
        print("SUCCESS: Newsletter dispatched.")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()
        print("--- Process Finished ---")

if __name__ == "__main__":
    send_newsletter()