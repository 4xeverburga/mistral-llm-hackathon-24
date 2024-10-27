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

            # Obtener el siguiente ticket_id
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