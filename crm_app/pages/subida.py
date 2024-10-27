import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Datos JSON proporcionados
ticket_data = {
    "ticket_id": "942230232",
    "status_type_desc": "Abierto",
    "description": "Consulta inicial",
    "nps_flg": 'false',
    "channel_type": "WhatsApp",
    "priority_type_desc": "Media",
    "user": {
        "userid": "1230232",
        "email": 'null',
        "phone_number": "942230232",
        "name": "942230232"
    },
    "agent": {
        "agent_id": "agente1",
    },
    "nps_score": 6,
    "ticket_tag_array": [],
    "timestamps": {
        "record_creation_ts": "2024-10-27 03:01:21",
        "last_update_ts": "2024-10-27 03:11:30",
        "last_response_agent_ts": '2024-10-27 03:02:30',
        "last_response_user_ts": "2024-10-27 03:10:45",
        "last_response_asesor_ts": "2024-10-27 03:11:30",
    },
    "messages": [
        {
            "message_id": 2,
            "timestamp": "2024-10-27 03:01:24",
            "role": "user",
            "content": "hola amigo"
        },
        {
            "message_id": 4,
            "timestamp": "2024-10-27 03:01:26",
            "role": "assistant",
            "content": "\u00a1Hola! \u00bfEn qu\u00e9 puedo ayudarte hoy?"
        },
        {
            "message_id": 4,
            "timestamp": "2024-10-27 03:02:25",
            "role": "user",
            "content": "que vendes?"
        },
        {
            "message_id": 6,
            "timestamp": "2024-10-27 03:02:26",
            "role": "assistant",
            "content": "Parece que hay un error en tu pregunta. \u00bfPodr\u00edas repetirla?"
        },
        {
            "message_id": 6,
            "timestamp": "2024-10-27 03:02:29",
            "role": "user",
            "content": "oe"
        },
        {
            "message_id": 8,
            "timestamp": "2024-10-27 03:02:30",
            "role": "assistant",
            "content": "Hello! How can I assist you today? Let's have a friendly and engaging conversation. \ud83d\ude0a How are you doing?"
        },
        {
            "message_id": 7,
            "timestamp": "2024-10-27 03:10:19",
            "role": "admin",
            "content": "hola amigo"
        },
        {
            "message_id": 9,
            "timestamp": "2024-10-27 03:10:45",
            "role": "user",
            "content": "no puedes ayudarme? me robaron mi producto carajo, la caja vino abierta, vas a devolverme el dinero o que xuxa?"
        },
        {
            "message_id": 9,
            "timestamp": "2024-10-27 03:11:30",
            "role": "admin",
            "content": "intentaremos solucionar tu problema amigo, no te preocupes. pero lamento informarte \ud83d\ude2d que no podemos realizar devoluciones, espero puedas comprender pero intentaremos mantener la mejor experiencia para ti <3"
        }
    ]
}

# Convertir listas a JSON
ticket_data['ticket_tag_array'] = json.dumps(ticket_data['ticket_tag_array'])
ticket_data['messages'] = json.dumps(ticket_data['messages'])

# Conexión a PostgreSQL usando datos de .env
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# Crear el usuario en la tabla "users" si no existe
with connection:
    with connection.cursor() as cursor:
        # Comprobar si el usuario existe
        userid = ticket_data["user"]["userid"]
        cursor.execute("SELECT 1 FROM users WHERE userid = %s", (userid,))
        user_exists = cursor.fetchone()

        # Insertar el usuario si no existe
        if not user_exists:
            insert_user_query = """
                INSERT INTO users (userid, email, phone_number, name)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_user_query, (
                userid,
                ticket_data["user"]["email"],
                ticket_data["user"]["phone_number"],
                ticket_data["user"]["name"]
            ))
            connection.commit()
            print(f"Usuario {userid} insertado en la tabla users.")

# Crear un cursor y ejecutar el INSERT para el ticket
with connection:
    with connection.cursor() as cursor:
        insert_query = """
            INSERT INTO ticket (
                ticket_id,
                statustypedesc,
                description,
                nps_flg,
                channeltype,
                prioritytypedesc,
                userid,
                agentid,
                nps_score,
                tickettagarray,
                recordcreationts,
                lastupdatets,
                lastresponseagentts,
                lastresponseuserts,
                lastresponseasesorts,
                message
            ) VALUES (
                %(ticket_id)s,
                %(status_type_desc)s,
                %(description)s,
                %(nps_flg)s,
                %(channel_type)s,
                %(priority_type_desc)s,
                %(userid)s,
                %(agent_id)s,
                %(nps_score)s,
                %(ticket_tag_array)s,
                %(record_creation_ts)s,
                %(last_update_ts)s,
                %(last_response_agent_ts)s,
                %(last_response_user_ts)s,
                %(last_response_asesor_ts)s,
                %(messages)s
            );
        """
        
        # Crear un diccionario con los valores necesarios
        values = {
            "ticket_id": ticket_data["ticket_id"],
            "status_type_desc": ticket_data["status_type_desc"],
            "description": ticket_data["description"],
            "nps_flg": ticket_data["nps_flg"],
            "channel_type": ticket_data["channel_type"],
            "priority_type_desc": ticket_data["priority_type_desc"],
            "userid": ticket_data["user"]["userid"],
            "agent_id": ticket_data["agent"]["agent_id"],
            "nps_score": ticket_data["nps_score"],
            "ticket_tag_array": ticket_data["ticket_tag_array"],
            "record_creation_ts": ticket_data["timestamps"]["record_creation_ts"],
            "last_update_ts": ticket_data["timestamps"]["last_update_ts"],
            "last_response_agent_ts": ticket_data["timestamps"]["last_response_agent_ts"],
            "last_response_user_ts": ticket_data["timestamps"]["last_response_user_ts"],
            "last_response_asesor_ts": ticket_data["timestamps"]["last_response_asesor_ts"],
            "messages": ticket_data["messages"]
        }

        # Ejecutar el INSERT del ticket
        cursor.execute(insert_query, values)
        connection.commit()
        print("Datos del ticket insertados exitosamente.")
