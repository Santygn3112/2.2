from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db
from app.routers import chat, auth

app = FastAPI(title="IA 2.2 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_db_client():
    db.connect()


@app.on_event("shutdown")
def shutdown_db_client():
    db.close()


app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])


@app.get("/")
def read_root():
    return {"status": "IA 2.2 Backend is running"}
