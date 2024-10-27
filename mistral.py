from mistralai import Mistral
import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')
USERS_DIR = "usuarios"
CONTEXT_FILE = "context.txt"

# Crear directorio de usuarios si no existe
if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

# Verificar credencial de Mistral
if not MISTRAL_API_KEY:
    print("❌ Error: Falta MISTRAL_API_KEY en .env")
    raise ValueError("MISTRAL_API_KEY es requerido")

# Verificar existencia del archivo de contexto
if not os.path.exists(CONTEXT_FILE):
    print("❌ Error: No se encuentra el archivo context.txt")
    raise FileNotFoundError("Se requiere el archivo context.txt")

# Leer el contexto inicial
try:
    with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
        INITIAL_CONTEXT = f.read().strip()
except Exception as e:
    print(f"❌ Error leyendo context.txt: {str(e)}")
    raise

# Inicializar cliente
mistral_client = Mistral(api_key=MISTRAL_API_KEY)


def load_chat_history(phone_number: str) -> list:
    """Carga el historial de chat de un usuario"""
    filename = os.path.join(USERS_DIR, f"{phone_number.replace('whatsapp:', '')}.json")
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error cargando historial: {str(e)}")
            return []
    return []


def initialize_chat_history() -> list:
    """Inicializa el historial de chat con el contexto inicial"""
    return [{
        "role": "system",
        "content": INITIAL_CONTEXT,
        "timestamp": datetime.now().isoformat()
    }]


def save_chat_history(phone_number: str, history: list) -> None:
    """Guarda el historial de chat de un usuario"""
    filename = os.path.join(USERS_DIR, f"{phone_number.replace('whatsapp:', '')}.json")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error guardando historial: {str(e)}")


def get_completion(prompt: str, phone_number: str) -> str:
    """
    Obtiene una respuesta de Mistral AI considerando el historial

    Args:
        prompt (str): El mensaje del usuario
        phone_number (str): Número de teléfono del usuario

    Returns:
        str: La respuesta generada por Mistral
    """
    try:
        # Cargar historial existente o inicializar nuevo con contexto
        history = load_chat_history(phone_number)
        if not history:
            history = initialize_chat_history()

        # Agregar nuevo mensaje del usuario
        history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })

        # Preparar mensajes para Mistral (últimos 10 mensajes para mantener contexto)
        messages = [{"role": msg["role"], "content": msg["content"]}
                   for msg in history[-10:]]

        # Obtener respuesta
        chat_response = mistral_client.chat.complete(
            model=MISTRAL_MODEL,
            messages=messages
        )

        response_content = chat_response.choices[0].message.content

        # Agregar respuesta al historial
        history.append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        })

        # Guardar historial actualizado
        save_chat_history(phone_number, history)

        return response_content
    except Exception as e:
        logging.error(f"Error al obtener respuesta de Mistral: {str(e)}")
        return "Lo siento, hubo un error al procesar tu mensaje."