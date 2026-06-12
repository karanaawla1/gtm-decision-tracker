from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()  # .env file padho

DATABASE_URL = os.getenv("DATABASE_URL")

# PostgreSQL se connection banao
engine = create_engine(DATABASE_URL)

# Har request ke liye ek session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Saare models yahan se inherit karenge
Base = declarative_base()

# Yeh function har API call ko DB session deta hai
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()