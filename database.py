import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////home/debs/code/trading-signal-newsletter/signals.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Signal Table
class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    # Strip the tzinfo to prevent SQLAlchemy 2.0 aware/naive mixing errors on insert
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(pytz.timezone('US/Eastern')).replace(tzinfo=None))
    ticker = Column(String)
    action = Column(String) # 'buy' or 'sell'
    price = Column(Float)
    list_name = Column(String)
    interval = Column(String) # 'daily' or 'weekly'

# Create the table
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()