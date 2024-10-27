from mistralai import Mistral
import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime
import locale

from database import save_chat_to_db, load_chat_from_db, initialize_chat_history

# Diccionario de traducciones para los días y meses
DAYS_TRANSLATION = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

MONTHS_TRANSLATION = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre'
}

load_dotenv()

MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')

# Verificar credencial de Mistral
if not MISTRAL_API_KEY:
    print("❌ Error: Falta MISTRAL_API_KEY en .env")
    raise ValueError("MISTRAL_API_KEY es requerido")

def get_formatted_datetime():
    """Retorna la fecha y hora actual en formato personalizado en español"""
    now = datetime.now()

    # Obtener el día de la semana en inglés y traducirlo
    weekday_eng = now.strftime("%A")
    weekday = DAYS_TRANSLATION.get(weekday_eng, weekday_eng)

    # Obtener el mes en inglés y traducirlo
    month_eng = now.strftime("%B")
    month = MONTHS_TRANSLATION.get(month_eng, month_eng)

    # Formatear el resto de la fecha
    day = now.strftime("%d")
    year = now.strftime("%Y")
    time = now.strftime("%H:%M")  # Usando formato 24 horas

    return f"{weekday} {day} de {month} del {year}, {time}"

def process_text_with_date(text: str) -> str:
    """Reemplaza {fecha_actual} con la fecha actual en cualquier texto"""
    return text.replace('{fecha_actual}', get_formatted_datetime())

# Inicializar cliente
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

def get_completion(prompt: str, phone_number: str) -> str:
    try:
        # Cargar historial existente o inicializar nuevo con contexto
        history = load_chat_from_db(phone_number)
        if not history:
            history = initialize_chat_history("1")

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

        # Procesar la respuesta para reemplazar {fecha_actual}
        response_content = process_text_with_date(chat_response.choices[0].message.content)

        # Agregar respuesta al historial
        history.append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        })

        # Guardar historial actualizado solo en base de datos
        save_chat_to_db(phone_number, history)

        return response_content
    except Exception as e:
        logging.error(f"Error al obtener respuesta de Mistral: {str(e)}")
        return "Lo siento, hubo un error al procesar tu mensaje."