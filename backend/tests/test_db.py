# test_db.py
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/realtoros",
)

def main():
    print(f"Using DATABASE_URL: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    try:
        with engine.connect() as conn:
            # Verify basic connectivity
            result = conn.execute(text("SELECT 1"))
            print("SELECT 1 ->", result.scalar())

            # Show server version
            version = conn.execute(text("SHOW server_version")).scalar()
            print("Postgres server_version:", version)

            # List tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print("Tables:", tables if tables else "(no tables found)")

        print("Connection OK.")
        sys.exit(0)
    except SQLAlchemyError as e:
        print("Connection FAILED.")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()