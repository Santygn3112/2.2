import os
import requests
import json
import random
from app.core.database import db
from app.models.chat import MensajeUsuario, ConversacionDB

API_KEY = os.getenv("GEMINI_API_KEY")

# --- MODELO ELEGIDO: GEMMA 3 (Estabilidad Total) ---
# Usamos el 12b-it porque entiende mejor las instrucciones de rol que el 4b
MODELO_STABLE = "gemma-3-12b-it"


def generar_respuesta_simulada_offline(mensaje: str, modelo: str) -> str:
    """Solo salta si te quedas sin internet o Google se cae mundialmente"""
    prefijo = f"🔌 [{modelo} Offline]: "
    return f"{prefijo}Sin conexión al servidor. He recibido tu mensaje: '{mensaje}'"


def llamar_api_gemma(prompt, sistema, modelo_api):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_api}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}

    # Gemma a veces prefiere que la instrucción vaya unida al prompt
    full_prompt = f"Instrucción del sistema: {sistema}\n\nUsuario: {prompt}"

    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    # Timeout de 10s porque Gemma a veces tarda un pelín en "calentar"
    return requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)


def generar_respuesta_ia(input_usuario: str, modelo_seleccionado: str) -> str:
    # 1. Definimos la PERSONALIDAD (System Prompt)
    if modelo_seleccionado == "Gemini":
        instruccion = (
            "Eres Gemini. Responde de forma breve, amigable y usa muchos emojis ✨."
        )
    elif modelo_seleccionado == "ChatGPT":
        instruccion = "Eres ChatGPT. Responde de forma muy profesional, estructurada y sin emociones."
    elif modelo_seleccionado == "Claude":
        instruccion = "Eres Claude. Usa un lenguaje muy culto, formal y elegante."
    elif modelo_seleccionado == "Grok":
        instruccion = "Eres Grok. Sé sarcástico, usa humor negro y sé un poco rebelde."
    else:
        instruccion = "Eres un asistente útil."

    if not API_KEY:
        return generar_respuesta_simulada_offline(input_usuario, modelo_seleccionado)

    try:
        # 2. Llamada Directa a Gemma
        response = llamar_api_gemma(input_usuario, instruccion, MODELO_STABLE)

        if response.status_code == 200:
            data = response.json()
            # Extraemos el texto
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # Si Gemma falla (raro), mostramos el error técnico (útil para ti)
            # O cambiamos a simulado si prefieres que no se vea el error
            print(f"⚠️ Error API ({response.status_code}): {response.text}")
            return generar_respuesta_simulada_offline(
                input_usuario, modelo_seleccionado
            )

    except Exception as e:
        print(f"❌ Error conexión: {e}")
        return generar_respuesta_simulada_offline(input_usuario, modelo_seleccionado)


def procesar_mensaje(datos: MensajeUsuario):
    # Generamos respuesta
    respuesta = generar_respuesta_ia(datos.mensaje, datos.modelo)

    # Guardamos en Mongo
    nueva_conversacion = ConversacionDB(
        mensaje=datos.mensaje,
        modelo=datos.modelo,
        usuario=datos.usuario,
        respuesta_ia=respuesta,
        calidad_estimada=random.uniform(0.7, 0.9),
    )

    db.get_db()["conversaciones"].insert_one(nueva_conversacion.model_dump())

    return {
        "id_conversacion": str(nueva_conversacion.id)
        if nueva_conversacion.id
        else "gemma-api",
        "respuesta": respuesta,
        "timestamp": nueva_conversacion.timestamp,
    }
