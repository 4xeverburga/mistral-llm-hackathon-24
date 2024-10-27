from mistralai import Mistral
import os
import logging
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')

# Verificar credencial de Mistral
if not MISTRAL_API_KEY:
    print("❌ Error: Falta MISTRAL_API_KEY en .env")
    raise ValueError("MISTRAL_API_KEY es requerido")

# Inicializar cliente
mistral_client = Mistral(api_key=MISTRAL_API_KEY)


def get_completion(prompt: str) -> str:
    """
    Obtiene una respuesta de Mistral AI

    Args:
        prompt (str): El mensaje del usuario

    Returns:
        str: La respuesta generada por Mistral
    """
    try:
        chat_response = mistral_client.chat.complete(
            model=MISTRAL_MODEL,
            messages=[{
                "role": "user",
                "content": prompt,
            }]
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error al obtener respuesta de Mistral: {str(e)}")
        return "Lo siento, hubo un error al procesar tu mensaje."