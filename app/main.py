from fastapi import FastAPI
from dotenv import load_dotenv
import os
import uvicorn
from app.controllers.users_controller import router as users_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Încarcă variabilele de mediu din .env
load_dotenv()

# Creează instanța FastAPI
app = FastAPI(
    title="University Chat Backend API",
    docs_url="/docs",        # Adresa Swagger UI
    redoc_url="/redoc",      # Adresa Redoc
    openapi_url="/openapi.json"  # Endpoint-ul OpenAPI
)


# Include router-ul definit în controllerul pentru utilizatori
app.include_router(users_router)
app.mount("/static", StaticFiles(directory="public"), name="static")

# Ruta principală (root)
@app.get("/")
def read_root():
    return {"message": "Welcome to University Chat Backend API!"}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("public/favicon.ico")

# Pornirea serverului folosind Uvicorn
if __name__ == "__main__":
    # Preia portul din variabila de mediu PORT; folosește 10000 ca valoare implicită
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
