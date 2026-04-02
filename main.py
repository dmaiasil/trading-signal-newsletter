from fastapi import FastAPI, Request
from database import SessionLocal, Signal
import datetime

app = FastAPI()

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    ticker = data.get("ticker")
    price = data.get("price")
    list_name = data.get("list")
    action = data.get("action", "").lower()

    if not ticker or action not in ["buy", "sell"]:
        return {"status": "ignored"}

    db = SessionLocal()
    try:
        # We no longer need to look for 'open' trades or update status
        new_entry = Signal(
            ticker=ticker,
            action=action,
            price=float(price) if price else 0.0,
            list_name=list_name
            # Timestamp is handled automatically by database.py
        )
        
        db.add(new_entry)
        db.commit()
        print(f"Logged {action.upper()} for {ticker} at {new_entry.timestamp}")
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()