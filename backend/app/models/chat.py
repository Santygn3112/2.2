from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Lo que llega del Frontend
class MensajeUsuario(BaseModel):
    mensaje: str = Field(..., max_length=1000)
    modelo: str
    usuario: str = "Invitado"


# Lo que guardamos en Mongo
class ConversacionDB(MensajeUsuario):
    id: Optional[str] = None
    respuesta_ia: str
    timestamp: datetime = Field(default_factory=datetime.now)
    calidad_estimada: Optional[float] = None

    class Config:
        populate_by_name = True
