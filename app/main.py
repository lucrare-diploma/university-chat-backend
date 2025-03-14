from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import os
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.controllers.user_controller import router as user_router
from app.controllers.auth_controller import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from dependencies.dependencies import get_current_user
from openapi import custom_openapi
from schemas.generic_response import GenericResponse

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
    "https://lucrare-diploma.github.io",  # URL-ul de producție al frontend-ului
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # Permite aceste origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(auth_router)

app.openapi = lambda: custom_openapi(app)

# Montează fișierele statice
app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/")
def read_root():
    return GenericResponse(success=True, code=200, response="Welcome to University Chat Backend API!")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("public/favicon.ico")

# Endpoint protejat: folosește get_current_user pentru a extrage tokenul validat
@app.get("/current_user")
def protected_route(current_user: dict = Depends(get_current_user)):
    return GenericResponse(success=True, code=200, response={"current_user": current_user})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
