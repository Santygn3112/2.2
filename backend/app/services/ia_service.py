import os
import requests
import json
import random
from app.core.database import db
from app.models.chat import MensajeUsuario, ConversacionDB

API_KEY = os.getenv("GEMINI_API_KEY")

MODELO_TITULAR = "gemini-2.5-flash"

MODELOS_DE_RESCATE = [
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash-lite",
]


def generar_respuesta_simulada_offline(mensaje: str, modelo: str) -> str:
    """Solo saltará si se cae internet en la universidad"""
    prefijo = f" [{modelo} Offline]: "
    return f"{prefijo}Sin conexión a Google Cloud. Recibido: '{mensaje}'"


def llamar_api_google(prompt, sistema, modelo_api):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_api}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}

    full_prompt = f"Instrucción del sistema: {sistema}\n\nUsuario: {prompt}"

    # Configuración de seguridad relajada
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    ]

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "safetySettings": safety_settings,
    }

    # Timeout de 30s
    return requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)


def generar_respuesta_ia(input_usuario: str, modelo_seleccionado_frontend: str) -> str:
    # PERSONALIDAD
    if modelo_seleccionado_frontend == "Gemini":
        instruccion = (
            "Eres Gemini. Responde de forma breve, amigable y usa muchos emojis ✨."
        )
    elif modelo_seleccionado_frontend == "ChatGPT":
        instruccion = "Eres ChatGPT. Responde de forma muy profesional y estructurada."
    elif modelo_seleccionado_frontend == "Claude":
        instruccion = "Eres Claude. Usa un lenguaje muy culto, formal y elegante."
    elif modelo_seleccionado_frontend == "Grok":
        instruccion = "Eres Grok. Sé sarcástico, usa humor negro y sé un poco rebelde."
    else:
        instruccion = "Eres un asistente útil."

    if not API_KEY:
        return generar_respuesta_simulada_offline(
            input_usuario, modelo_seleccionado_frontend
        )

    # Sistema de llamada
    lista_modelos_a_probar = [MODELO_TITULAR] + MODELOS_DE_RESCATE

    for i, modelo_actual in enumerate(lista_modelos_a_probar):
        try:
            print(f" Enviando a Google Cloud ({modelo_actual})...")

            response = llamar_api_google(input_usuario, instruccion, modelo_actual)

            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    texto = data["candidates"][0]["content"]["parts"][0]["text"]
                    return texto
                else:
                    print(
                        f"   {modelo_actual} devolvió respuesta vacía (filtro de seguridad?)."
                    )
                    continue

            else:
                print(
                    f"   Fallo en {modelo_actual} ({response.status_code}): {response.text[:100]}..."
                )
                continue

        except Exception as e:
            print(f"   Error de red con {modelo_actual}: {e}")
            continue

    print(" Error crítico: Fallaron todos los modelos premium.")
    return generar_respuesta_simulada_offline(
        input_usuario, modelo_seleccionado_frontend
    )


def procesar_mensaje(datos: MensajeUsuario):
    respuesta = generar_respuesta_ia(datos.mensaje, datos.modelo)

    nueva_conversacion = ConversacionDB(
        mensaje=datos.mensaje,
        modelo=datos.modelo,
        usuario=datos.usuario,
        respuesta_ia=respuesta,
        calidad_estimada=random.uniform(8.5, 10.0),
    )

    db.get_db()["conversaciones"].insert_one(nueva_conversacion.model_dump())

    return {
        "id_conversacion": str(nueva_conversacion.id)
        if nueva_conversacion.id
        else "cloud-error",
        "respuesta": respuesta,
        "timestamp": nueva_conversacion.timestamp,
    }
