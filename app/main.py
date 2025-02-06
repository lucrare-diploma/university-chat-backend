from fastapi import FastAPI
import os
import uvicorn
import psycopg2
from dotenv import load_dotenv

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
            port=6543,  # Supabase folosește 6543 pentru baza de date, nu pentru FastAPI!
            dbname=DBNAME
        )
        return connection
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

# Ruta principală pentru verificare
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

# Ruta principală pentru HEAD (fix pentru Render)
@app.head("/")
def root_head():
    return {"message": "HEAD request received"}

# Rulează serverul Uvicorn cu portul corect
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Preia portul setat de Render
    print(f"🚀 Running on port {port}...")  # Debugging pentru a verifica portul
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
