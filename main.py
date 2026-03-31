from fastapi import FastAPI, Request, HTTPException
from database import SessionLocal, Signal
import datetime

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "TradingView Bridge is Online", "timestamp": datetime.datetime.now()}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    # 1. Capture the JSON data safely
    try:
        data = await request.json()
        print(f"DEBUG: Received Data -> {data}")
    except Exception:
        print("Error: Could not parse JSON payload")
        return {"status": "error", "message": "Invalid JSON"}

    # 2. Extract basic fields
    ticker = data.get("ticker")
    price = data.get("price")
    list_name = data.get("list") # Maps to 'list' in your TV JSON
    
    # 3. Handle the Plot Logic (Translating signals to 'buy' or 'sell')
    buy_val = data.get("buy_signal")
    sell_val = data.get("sell_signal")

    action = None
    if buy_val and str(buy_val).lower() != "n/a":
        action = "buy"
    elif sell_val and str(sell_val).lower() != "n/a":
        action = "sell"

    # Validation: If we don't have a ticker or a detected action, stop here
    if not ticker or not action:
        print(f"Ignoring Signal: Ticker={ticker}, Action detected={action}")
        return {"status": "ignored", "reason": "Missing ticker or active signal plot"}

    db = SessionLocal()
    try:
        # 4. Strategy Logic: Tracking Open/Closed states
        # If we receive a 'sell', find the previous 'open' trade for this stock and close it
        if action == "sell":
            existing_open_trade = db.query(Signal).filter(
                Signal.ticker == ticker, 
                Signal.status == "open"
            ).first()
            
            if existing_open_trade:
                existing_open_trade.status = "closed"
                print(f"Closed existing 'open' position for {ticker}")

        # 5. Save the incoming signal to the database
        new_entry = Signal(
            ticker=ticker,
            action=action,
            price=float(price) if price else 0.0,
            list_name=list_name,
            # If it's a buy, it's 'open'. If it's a sell, the record itself is 'closed'
            status="open" if action == "buy" else "closed"
        )
        
        db.add(new_entry)
        db.commit()
        
        print(f"Signal Processed: {action.upper()} {ticker} from {list_name} at ${price}")
        return {"status": "success", "processed_ticker": ticker, "action": action}

    except Exception as e:
        db.rollback()
        print(f"Database Error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()