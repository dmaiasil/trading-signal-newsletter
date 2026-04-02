import os
import datetime
import resend
from dotenv import load_dotenv
from database import SessionLocal, Signal

# Load environment variables
load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

def send_newsletter():
    print(f"--- Starting Newsletter Process for {TARGET_EMAIL} ---")
    db = SessionLocal()
    
    try:
        # 1. Get Data
        today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        signals_today = db.query(Signal).filter(Signal.timestamp >= today_start).all()
        open_positions = db.query(Signal).filter(Signal.status == "open").all()

        # 2. Build HTML
        subject = f"Sinais M3: {datetime.date.today().strftime('%b %d, %Y')}"
        html_content = "<h1>Daily Trading Intelligence Report</h1>"
        
        # Section: Today's Signals Grouped by List
        html_content += "<h2>Today's Signals</h2>"
        
        target_lists = ["List A", "List B", "List C"]
        
        for list_name in target_lists:
            # Filter signals belonging to this specific list
            list_signals = [s for s in signals_today if s.list_name == list_name]
            
            html_content += f"<h3>{list_name}</h3>"
            if not list_signals:
                html_content += "<p>No new signals for this list today.</p>"
            else:
                html_content += "<ul>"
                for s in list_signals:
                    # Color coding for buy/sell actions
                    action_color = "green" if s.action.lower() == "buy" else "red"
                    html_content += (
                        f"<li><b style='color:{action_color};'>{s.action.upper()}</b> "
                        f"{s.ticker} @ ${s.price:.2f} "
                        f"(Time: {s.timestamp.strftime('%H:%M')} UTC)</li>"
                    )
                html_content += "</ul>"

        # Section: Signals from Unknown/Other lists (Catch-all)
        other_signals = [s for s in signals_today if s.list_name not in target_lists]
        if other_signals:
            html_content += "<h3>Other Signals</h3><ul>"
            for s in other_signals:
                html_content += f"<li><b>{s.action.upper()}</b> {s.ticker} @ ${s.price:.2f}</li>"
            html_content += "</ul>"

        # Section: Global Open Positions
        html_content += "<hr><h2>Current Open Positions</h2>"
        if not open_positions:
            html_content += "<p>No active positions currently in the portfolio.</p>"
        else:
            html_content += "<ul>"
            for p in open_positions:
                html_content += (
                    f"<li><b>{p.ticker}</b> (List: {p.list_name}) - "
                    f"Entered @ ${p.price:.2f} on {p.timestamp.strftime('%m/%d')}</li>"
                )
            html_content += "</ul>"

        html_content += "<p style='font-size: 12px; color: gray;'>Market closes in 2 hours.</p>"

        # 3. Send Email
        print("Sending to Resend API...")
        r = resend.Emails.send({
            "from": "Trading Bridge <onboarding@resend.dev>",
            "to": [TARGET_EMAIL],
            "subject": subject,
            "html": html_content,
        })
        
        if "id" in r:
            print(f"SUCCESS: Email ID {r['id']}")
        else:
            print(f"API request accepted without ID. Response: {r}")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()
        print("--- Process Finished ---")

if __name__ == "__main__":
    send_newsletter()