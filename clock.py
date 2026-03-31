import time
import datetime
import pytz
from pandas_market_calendars import get_calendar
from scheduler import send_newsletter

def wait_until_2h_before_close():
    nyse = get_calendar('NYSE')
    
    while True:
        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        schedule = nyse.schedule(start_date=now, end_date=now)
        
        if not schedule.empty:
            market_close = schedule.iloc[0]['market_close'].to_pydatetime()
            target_time = market_close - datetime.timedelta(hours=2)
            
            # If we are within 1 minute of the target time, send it!
            if abs((now - target_time).total_seconds()) < 60:
                print("Target time reached. Sending newsletter...")
                send_newsletter()
                time.sleep(120) # Don't send twice in the same minute
        
        time.sleep(30) # Check the clock every 30 seconds

if __name__ == "__main__":
    print("Clock is running... waiting for 2:00 PM EST.")
    wait_until_2h_before_close()