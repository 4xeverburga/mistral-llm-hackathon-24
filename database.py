# database_wsp.py
import os
from datetime import datetime
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Establece conexión con la base de datos PostgreSQL"""
    try:
        connection = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def ensure_user_exists(cursor, userid: str) -> None:
    """Verifica si el usuario existe, si no, lo crea"""
    check_query = "SELECT userid FROM users WHERE userid = %s"
    cursor.execute(check_query, (userid,))

    if cursor.fetchone() is None:
        # Si el usuario no existe, lo creamos
        insert_user_query = """
            INSERT INTO users (userid) 
            VALUES (%s)
        """
        cursor.execute(insert_user_query, (userid,))


def get_next_ticket_id(cursor):
    """Obtiene el siguiente ticket_id disponible en formato texto"""
    cursor.execute("SELECT MAX(ticket_id) FROM ticket")
    result = cursor.fetchone()[0]

    # Si no hay tickets, empezamos desde 1
    if result is None:
        return "000001"

    try:
        # Intentar convertir el último ticket_id a entero y sumar 1
        next_num = int(result) + 1
        return str(next_num).zfill(6)
    except (ValueError, TypeError):
        # Si hay algún error al convertir, empezamos desde 1
        return "000001"


def get_last_ticket_id(cursor, userid: str) -> str:
    """Obtiene el último ticket_id para un usuario específico"""
    query = """
        SELECT ticket_id 
        FROM ticket 
        WHERE userid = %s 
        ORDER BY ticket_id DESC 
        LIMIT 1
    """
    cursor.execute(query, (userid,))
    result = cursor.fetchone()
    return result[0] if result else None


def save_chat_to_db(phone_number: str, history: list, channel: str) -> None:
    """
    Guarda el chat en la tabla ticket de PostgreSQL, con actualización de campos adicionales
    """
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Preparar el userid
            userid = phone_number.replace('whatsapp:', '').replace('+', '')

            # Asegurar que el usuario existe
            ensure_user_exists(cursor, userid)

            # Obtener el último ticket_id del usuario
            last_ticket_id = get_last_ticket_id(cursor, userid)

            # Determinar valores para campos adicionales
            agentid = "1"  # Por defecto
            statustypedesc = "nuevo" if not last_ticket_id else "abierto"
            prioritytypedesc = "media" if channel == "whatsapp" else "alta"
            channeltype = channel
            message = json.dumps(history)
            recordcreationts = datetime.now()
            lastupdatets = datetime.now()

            if last_ticket_id:
                # Si existe un ticket, actualizarlo
                update_chat_to_db(phone_number, history, channel)
            else:
                # Si no existe, crear uno nuevo
                next_ticket_id = get_next_ticket_id(cursor)

                # Query de inserción
                insert_query = """
                    INSERT INTO ticket 
                    (ticket_id, userid, message, recordcreationts, lastupdatets, 
                     statustypedesc, channeltype, prioritytypedesc, agentid) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # Valores a insertar
                values = (
                    next_ticket_id, userid, message, recordcreationts, lastupdatets,
                    statustypedesc, channeltype, prioritytypedesc, agentid
                )

                # Ejecutar la inserción
                cursor.execute(insert_query, values)
                connection.commit()

            cursor.close()
            connection.close()

    except Exception as e:
        print(f"Error al guardar en la base de datos: {e}")


def update_chat_to_db(phone_number: str, history: list, channel: str) -> None:
    """
    Actualiza el chat existente en la tabla ticket de PostgreSQL con nuevos mensajes y campos adicionales
    """
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Preparar el userid
            userid = phone_number.replace('whatsapp:', '').replace('+', '')

            # Obtener el último ticket_id del usuario
            last_ticket_id = get_last_ticket_id(cursor, userid)

            if last_ticket_id:
                # Convertir el historial a JSON string
                message = json.dumps(history)

                # Actualizar valores adicionales
                lastupdatets = datetime.now()
                statustypedesc = "abierto"  # Cambiar el estado a 'abierto' al actualizar

                # Query de actualización
                update_query = """
                    UPDATE ticket 
                    SET message = %s, lastupdatets = %s, statustypedesc = %s, 
                        channeltype = %s, prioritytypedesc = %s
                    WHERE ticket_id = %s AND userid = %s
                """

                # Valores a actualizar
                values = (
                    message, lastupdatets, statustypedesc, channel,
                    "media" if channel == "whatsapp" else "alta",
                    last_ticket_id, userid
                )

                # Ejecutar la actualización
                cursor.execute(update_query, values)
                connection.commit()

            cursor.close()
            connection.close()

    except Exception as e:
        print(f"Error al actualizar en la base de datos: {e}")


def load_chat_from_db(phone_number: str) -> list:
    """
    Carga el historial de chat de un usuario desde la base de datos
    """
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Preparar el userid (eliminar 'whatsapp:' y '+')
            userid = phone_number.replace('whatsapp:', '').replace('+', '')

            # Query para obtener el último mensaje
            query = """
                SELECT message 
                FROM ticket 
                WHERE userid = %s 
                ORDER BY ticket_id DESC 
                LIMIT 1
            """

            cursor.execute(query, (userid,))
            result = cursor.fetchone()

            cursor.close()
            connection.close()

            if result and result[0]:
                # Convertir el JSON string a lista
                return json.loads(result[0])

            return []

    except Exception as e:
        print(f"Error al cargar chat de la base de datos: {e}")
        return []


def initialize_chat_history(phone_number: str) -> list:
    """
    Inicializa el historial del chat basado en el contexto del agente.

    Args:
        phone_number (str): Número de teléfono del agente

    Returns:
        list: Lista con el mensaje inicial del sistema incluyendo el contexto del agente
    """
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Preparar el agentid (eliminar 'whatsapp:' y '+' si existen)
            agentid = phone_number.replace('whatsapp:', '').replace('+', '')

            # Query para obtener el contexto del agente
            query = """
                SELECT context 
                FROM agente 
                WHERE agentid = %s 
                LIMIT 1
            """

            cursor.execute(query, (agentid,))
            result = cursor.fetchone()

            cursor.close()
            connection.close()

            if result and result[0]:
                return [{
                    "role": "system",
                    "content": result[0],
                    "timestamp": datetime.now().isoformat()
                }]

            # Si no se encuentra el agente, retornar lista vacía
            return []

    except Exception as e:
        print(f"Error al inicializar el historial del chat: {e}")
        return[]