from fastapi import FastAPI, Request
from database import SessionLocal, Signal
import datetime

app = FastAPI()

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
        print(f"DEBUG: Received Data -> {data}")
    except Exception:
        print("Error: Received non-JSON data")
        return {"status": "error", "message": "Invalid JSON"}

    # 1. Extract fields
    ticker = data.get("ticker")
    price = data.get("price")
    list_name = data.get("list")
    # Mapping 'long' or 'short' from your TV alert
    action = data.get("action", "").lower() 

    if not ticker or action not in ["buy", "sell"]:
        print(f"Ignored: Invalid action '{action}' or missing ticker.")
        return {"status": "ignored"}

    db = SessionLocal()
    try:
        # 2. Simply save the signal as a new event
        new_entry = Signal(
            ticker=ticker,
            action=action, # This will now store 'buy' or 'sell'
            price=float(price) if price else 0.0,
            list_name=list_name,
            status="active" # We can just label them all as active events
        )
        
        db.add(new_entry)
        db.commit()
        
        print(f"Recorded {action.upper()} for {ticker} at ${price}")
        return {"status": "success"}

    except Exception as e:
        db.rollback()
        print(f"DB Error: {e}")
        return {"status": "error"}
    finally:
        db.close()