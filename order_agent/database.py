import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain_community.utilities.sql_database import SQLDatabase

def get_engine_for_chinook_db():
    """Read local sql file, populate in-memory database, and create engine."""
    try:
        with open('customer_orders.sql', 'r') as file:
            sql_script = file.read()
    except FileNotFoundError:
        print("Error: customer_orders.sql not found. Please ensure the file exists in the same directory.")
        return None

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    engine = create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    return engine

# Get the database engine
engine = get_engine_for_chinook_db()

# Initialize SQLDatabase if engine was created successfully
db = SQLDatabase(engine) if engine else None