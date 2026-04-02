from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import pytz

# Database setup
DATABASE_URL = "sqlite:///./signals.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Signal Table
class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    # The new date/time column
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(pytz.timezone('US/Eastern')))
    ticker = Column(String)
    action = Column(String) # 'buy' or 'sell'
    price = Column(Float)
    list_name = Column(String)

# Create the table
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()