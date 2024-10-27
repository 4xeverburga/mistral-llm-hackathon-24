from twilio.rest import Client
import logging
from colorama import Fore, Style
import os
from dotenv import load_dotenv
import time

load_dotenv()

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
MAX_MESSAGE_LENGTH = 1500  # Reducido para mayor seguridad

if not ACCOUNT_SID or not AUTH_TOKEN:
    print("❌ Error: Falta ACCOUNT_SID o AUTH_TOKEN en .env")
    raise ValueError("Se requieren credenciales de Twilio")

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def log_with_color(message: str, level: str, color: str):
    record = logging.LogRecord(
        name="", level=logging.INFO,
        pathname="", lineno=0,
        msg=message, args=(), exc_info=None
    )
    record.levelname = level
    record.color = color
    logging.getLogger().handle(record)


async def process_incoming_message(form_data):
    try:
        incoming_msg = form_data.get('Body', '')
        from_number = form_data.get('From', '')

        if is_valid_message(from_number, incoming_msg):
            log_with_color(f"📱 Mensaje de {from_number}: {incoming_msg}", "INFO", Fore.BLUE)
            return incoming_msg, from_number

        return None, None

    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {str(e)}")
        return None, None


def split_message(message: str) -> list:
    """Divide un mensaje largo en partes más pequeñas de forma inteligente"""
    if len(message) <= MAX_MESSAGE_LENGTH:
        return [message]

    parts = []
    paragraphs = message.split('\n')
    current_part = ""

    for paragraph in paragraphs:
        # Si el párrafo por sí solo es más largo que el límite
        if len(paragraph) > MAX_MESSAGE_LENGTH:
            words = paragraph.split()
            for word in words:
                if len(current_part) + len(word) + 1 <= MAX_MESSAGE_LENGTH:
                    current_part += " " + word if current_part else word
                else:
                    parts.append(current_part)
                    current_part = word
        # Si el párrafo cabe en la parte actual
        elif len(current_part) + len(paragraph) + 1 <= MAX_MESSAGE_LENGTH:
            current_part += "\n" + paragraph if current_part else paragraph
        else:
            parts.append(current_part)
            current_part = paragraph

    if current_part:
        parts.append(current_part)

    return parts


def send_message(to_number: str, message: str) -> None:
    """Envía un mensaje de WhatsApp, dividiendo si es necesario y esperando entre envíos"""
    try:
        message_parts = split_message(message)
        total_parts = len(message_parts)

        for i, part in enumerate(message_parts, 1):
            # Agregar numeración solo si hay múltiples partes
            if total_parts > 1:
                formatted_part = f"(Parte {i} de {total_parts})\n{part}"
            else:
                formatted_part = part

            client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=formatted_part,
                to=to_number
            )

            log_with_color(f"🤖 Respuesta {i}/{total_parts}:\n{formatted_part}", "INFO", Fore.BLUE)

            # Esperar un segundo entre mensajes si hay más de uno
            if i < total_parts:
                time.sleep(1)

    except Exception as e:
        logging.error(f"❌ Error enviando mensaje: {str(e)}")
        raise e


def is_valid_message(from_number: str, body: str) -> bool:
    if not body or not from_number:
        return False
    if from_number == TWILIO_WHATSAPP_NUMBER:
        return False
    return True