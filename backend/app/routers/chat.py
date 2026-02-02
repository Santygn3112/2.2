from fastapi import APIRouter, HTTPException
from app.models.chat import MensajeUsuario
from app.services.ia_service import procesar_mensaje

# Creamos un grupo de rutas
router = APIRouter()


@router.post("/enviar", summary="Enviar mensaje a la IA")
def conversar(datos: MensajeUsuario):
    """
    Recibe el mensaje del usuario, lo guarda en MongoDB y devuelve la respuesta simulada.
    """
    try:
        # Llamamos a tu lógica de negocio (Service)
        respuesta = procesar_mensaje(datos)
        return respuesta
    except Exception as e:
        # Si algo falla (ej: MongoDB caído), devolvemos error 500
        print(f"Error en el chat: {e}")
        raise HTTPException(
            status_code=500, detail="Error interno del servidor procesando el mensaje"
        )
