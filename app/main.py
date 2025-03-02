from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import os
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# Importă funcția custom pentru token din dependencies
from app.dependencies import get_current_user
# Include router-ele din controller-ele pentru utilizatori și autentificare
from app.controllers.users_controller import router as users_router
from app.controllers.auth_controller import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

# Încarcă variabilele de mediu din .env
load_dotenv()

app = FastAPI(
    title="University Chat Backend API",
    description="API for University Chat application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

origins = [
    "http://localhost:5173",  # URL-ul frontend-ului local
    "https://university-chat-backend.onrender.com",  # URL-ul de producție al frontend-ului
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # Permite aceste origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(auth_router)

# Montează fișierele statice
app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to University Chat Backend API!"}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("public/favicon.ico")

# Endpoint protejat: folosește get_current_user pentru a extrage tokenul validat
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"current_user": current_user}

# Importă și setează funcția custom pentru OpenAPI din openapi.py
from openapi import custom_openapi
app.openapi = lambda: custom_openapi(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
