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


def save_chat_to_db(phone_number: str, history: list) -> None:
    """
    Guarda el chat en la tabla ticket de PostgreSQL
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

            if last_ticket_id:
                # Si existe un ticket, actualizarlo
                update_chat_to_db(phone_number, history)
            else:
                # Si no existe, crear uno nuevo
                next_ticket_id = get_next_ticket_id(cursor)

                # Convertir el historial a JSON string
                message = json.dumps(history)

                # Query de inserción
                insert_query = """
                    INSERT INTO ticket 
                    (ticket_id, userid, message) 
                    VALUES (%s, %s, %s)
                """

                # Valores a insertar
                values = (next_ticket_id, userid, message)

                # Ejecutar la inserción
                cursor.execute(insert_query, values)
                connection.commit()

            cursor.close()
            connection.close()

    except Exception as e:
        print(f"Error al guardar en la base de datos: {e}")


def update_chat_to_db(phone_number: str, history: list) -> None:
    """
    Actualiza el chat existente en la tabla ticket de PostgreSQL
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

                # Query de actualización
                update_query = """
                    UPDATE ticket 
                    SET message = %s 
                    WHERE ticket_id = %s AND userid = %s
                """

                # Valores a actualizar
                values = (message, last_ticket_id, userid)

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