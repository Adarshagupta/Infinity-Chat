import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import time

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_db_connection():
    try:
        engine = create_engine(DATABASE_URL, connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        })
        for attempt in range(3):
            try:
                with engine.connect() as connection:
                    result = connection.execute(text("SELECT 1"))
                    print(result.fetchone())
                print("Database connection successful")
                return
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(5)
        print("All connection attempts failed")
    except Exception as e:
        print(f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    test_db_connection()
