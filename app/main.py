from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.controllers.users_controller import router as users_router
from app.controllers.auth_controller import router as auth_router
from app.dependencies import get_current_user  # importă funcția custom

app = FastAPI(
    title="University Chat Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Include router-ele definite în controller-e
app.include_router(users_router)
app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to University Chat Backend API!"}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("public/favicon.ico")

# Endpoint protejat - folosește tokenul JWT extras de get_current_user
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"current_user": current_user}
