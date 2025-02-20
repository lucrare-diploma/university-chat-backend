import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Database connection parameters
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Create a connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=6543,
        database=DBNAME
    )
    print("✅ Connection pool created successfully.")
except Exception as e:
    print(f"❌ Error creating connection pool: {e}")

# Function to get a connection from the pool
def get_connection():
    try:
        conn = connection_pool.getconn()
        return conn
    except Exception as e:
        print(f"❌ Error getting connection: {e}")
        return None

# Function to release the connection back to the pool
def release_connection(conn):
    try:
        connection_pool.putconn(conn)
    except Exception as e:
        print(f"❌ Error releasing connection: {e}")
