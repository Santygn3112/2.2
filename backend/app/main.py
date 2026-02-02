from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importante para Vue
from app.core.database import db
from app.routers import chat, auth  # <--- NUEVO: Importamos el router

app = FastAPI(title="IA 2.2 API")

# Configuración de CORS (Permite que Vue hable con FastAPI)
# Esto es vital porque Vue corre en puerto 5173 y FastAPI en 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción deberías poner solo la URL de Vue
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


# Registramos las rutas del chat
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])


@app.get("/")
def read_root():
    return {"status": "IA 2.2 Backend is running"}
