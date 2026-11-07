import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Locate the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Explicitly load .env from the project root
load_dotenv(PROJECT_ROOT / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL not found. Check whether the project-root .env file "
        "exists and contains DATABASE_URL."
    )

engine = create_engine(database_url)

with engine.connect() as connection:
    result = connection.execute(
        text("SELECT current_database(), current_user")
    )

    print("Database connection successful!")
    print(result.fetchone())