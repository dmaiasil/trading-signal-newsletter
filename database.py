from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Database setup
DATABASE_URL = "sqlite:///./signals.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String)
    action = Column(String)  # 'buy' or 'sell'
    price = Column(Float)
    list_name = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="open")

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database ready.")