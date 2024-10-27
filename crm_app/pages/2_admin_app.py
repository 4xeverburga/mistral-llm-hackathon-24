# admin_app.py
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import time

# Cargar variables de entorno
load_dotenv()

# Configuración de la conexión a PostgreSQL usando variables de entorno
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# Helper para simular texto en streaming para respuesta de admin
def stream_str(s, speed=250):
    for c in s:
        yield c
        time.sleep(1 / speed)

# Configuración de la página
st.set_page_config(page_title="Chat CRM - Admin", page_icon="👤")
st.title("Panel de Administración - Conversaciones de Tickets")

# Obtener IDs de tickets (usamos st.cache_data para evitar recargar constantemente)
@st.cache_data
def get_ticket_ids():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_id FROM ticket")
            tickets = cur.fetchall()
    return [str(ticket[0]) for ticket in tickets]

# Cargar datos del ticket seleccionado
@st.cache_data
def get_ticket_data(ticket_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM ticket WHERE ticket_id = %s", (ticket_id,))
            ticket = cur.fetchone()
            if ticket and ticket['message']:
                ticket['message'] = json.loads(ticket['message'])  # Convertir el campo de mensajes a un array de diccionarios
            return ticket

# Cargar la lista de tickets solo una vez
ticket_ids = get_ticket_ids()

# Añadir un botón para actualizar la lista de tickets
if st.button("Actualizar lista de tickets"):
    st.cache_data.clear()  # Borra el caché para asegurarse de que recargue
    ticket_ids = get_ticket_ids()

# Selección del ticket
selected_ticket = st.selectbox("Seleccionar un Ticket", ticket_ids)

# Cargar datos del ticket solo si hay un ticket seleccionado
if selected_ticket:
    # Cargar datos del ticket seleccionado
    ticket_data = get_ticket_data(selected_ticket)

    # Mostrar detalles del ticket
    st.write(f"### Conversación para el Ticket: {selected_ticket}")
    st.write("**Estado:**", ticket_data["statustypedesc"])
    st.write("**Prioridad:**", ticket_data["prioritytypedesc"])
    st.write("**Descripción:**", ticket_data["description"])
    st.write("**Cliente:**", ticket_data["userid"])
    st.write("**Fecha de Creación:**", ticket_data["recordcreationts"])
    st.write("**Última Actualización:**", ticket_data["lastupdatets"])

    # Historial de mensajes
    st.markdown("#### Historial de Mensajes")
    for message in ticket_data["message"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Entrada para respuesta de admin
    st.write("### Responder como Admin")
    admin_response = st.chat_input("Escribe tu respuesta...")

    if admin_response:
        # Mostrar y enviar la respuesta del admin
        with st.chat_message("admin"):
            message_placeholder = st.empty()
            full_response = ""

            for chunk in stream_str(admin_response):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        # Agregar respuesta del admin al historial de mensajes
        def add_admin_response(ticket_id, content):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_message = {
                "message_id": len(ticket_data["message"]) + 1,
                "timestamp": timestamp,
                "role": "admin",
                "content": content
            }
            ticket_data["message"].append(new_message)  # Agregar mensaje al array local

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE ticket
                        SET message = %s, lastupdatets = %s, lastresponseasesorts = %s
                        WHERE ticket_id = %s
                        """,
                        (json.dumps(ticket_data["message"]), timestamp, timestamp, ticket_id)
                    )
                    conn.commit()
            st.success("Respuesta enviada.")

        add_admin_response(selected_ticket, admin_response)
