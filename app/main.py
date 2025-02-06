from fastapi import FastAPI
import psycopg2
from dotenv import load_dotenv
import os

# Încarcă variabilele de mediu
load_dotenv()

# Configurare FastAPI
app = FastAPI()

# Obține variabilele de mediu
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Funcție pentru conectare la Supabase
def get_connection():
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        return connection
    except Exception as e:
        return None

# Ruta principală
@app.get("/")
def root():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"message": "Welcome to University Chat API!", "time": result}
    return {"error": "Database connection failed"}
