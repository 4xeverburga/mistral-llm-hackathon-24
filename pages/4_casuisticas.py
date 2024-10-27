# admin_app.py
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import time
from datetime import datetime
from mistralai import Mistral  # Asegúrate de tener la API de Mistral configurada

# Configuración de la conexión a PostgreSQL usando Streamlit secrets
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"]
    )

# Función para simular el "streaming" de texto
def stream_str(s, speed=250):
    for c in s:
        yield c
        time.sleep(1 / speed)

# Configuración de la página
st.set_page_config(page_title="Panel de Administración - Chat CRM", page_icon="👤")
st.title("Panel de Administración - Conversaciones de Tickets")

# Obtener lista de IDs de tickets
@st.cache_data
def get_ticket_ids():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_id FROM ticket")
            tickets = cur.fetchall()
    return [ticket[0] for ticket in tickets]

# Función para cargar datos del ticket seleccionado
def load_ticket_data(ticket_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM ticket WHERE ticket_id = %s", (ticket_id,))
            ticket = cur.fetchone()
            if ticket and ticket['message']:
                ticket['message'] = json.loads(ticket['message'])
            return ticket

# Función para generar una pauta utilizando Mistral
def generar_pauta(conversacion_texto):
    client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
    prompt = f"Genera una pauta de solución para el siguiente caso:\n\n{conversacion_texto}"
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Cargar pautas desde la base de datos
@st.cache_data
def load_pautas():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM pautas")
            return cur.fetchall()

# Botón para actualizar la lista de tickets y pautas
if st.button("Actualizar lista de tickets y pautas"):
    st.cache_data.clear()  # Borra el caché para recargar los datos
    ticket_ids = get_ticket_ids()
    pautas = load_pautas()  # Recarga las pautas desde la base de datos
else:
    ticket_ids = get_ticket_ids()  # Cargar los tickets al inicio
    pautas = load_pautas()  # Cargar las pautas al inicio

# Selección del ticket
selected_ticket = st.selectbox("Seleccionar un Ticket", ticket_ids)

# Visualización del ticket seleccionado
if selected_ticket:
    ticket_data = load_ticket_data(selected_ticket)

    st.write(f"### Conversación para el Ticket: {selected_ticket}")
    st.write("**Estado:**", ticket_data["statustypedesc"])
    st.write("**Prioridad:**", ticket_data["prioritytypedesc"])
    st.write("**Descripción:**", ticket_data["description"])
    st.write("**Cliente:**", ticket_data["userid"])
    st.write("**Fecha de Creación:**", ticket_data["recordcreationts"])
    st.write("**Última Actualización:**", ticket_data["lastupdatets"])

    st.markdown("#### Historial de Mensajes")
    user_admin_messages = [
        message for message in ticket_data["message"] if message["role"] in ["user", "admin"]
    ]
    for message in user_admin_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    st.write("### Responder como Admin")
    admin_response = st.chat_input("Escribe tu respuesta...")

    if admin_response:
        with st.chat_message("admin"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in stream_str(admin_response):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        admin_message = {
            "message_id": len(ticket_data["message"]) + 1,
            "timestamp": timestamp,
            "role": "admin",
            "content": admin_response
        }
        ticket_data["message"].append(admin_message)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ticket
                    SET message = %s, lastupdatets = %s
                    WHERE ticket_id = %s
                """, (json.dumps(ticket_data["message"]), timestamp, selected_ticket))
                conn.commit()
        st.success("Respuesta enviada.")

    if st.button("Generar Pauta de Conocimiento"):
        conversacion_texto = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in user_admin_messages]
        )
        pauta_generada = generar_pauta(conversacion_texto)

        st.write("**Pauta Generada**:")
        st.write(pauta_generada)

        if st.button("Aprobar y Guardar Pauta"):
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO pautas (pauta, ticket_id, timestamp)
                        VALUES (%s, %s, %s)
                    """, (pauta_generada, selected_ticket, timestamp))
                    conn.commit()
            st.success("Pauta guardada exitosamente en la base de conocimiento.")

# Visualización de Pautas Guardadas
st.subheader("Pautas de Conocimiento Guardadas")

if pautas:
    for pauta_data in pautas:
        st.markdown(f"""
        <div style="background-color: #E3F2FD; padding: 15px; margin: 10px 0; border-radius: 8px;">
            <p><strong>Ticket ID:</strong> {pauta_data['ticket_id']}</p>
            <p><strong>Pauta ID:</strong> {pauta_data['pautaid']}</p>
            <p><strong>Pauta:</strong></p>
            <p style="color: #1E88E5;">{pauta_data['pauta']}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.write("No hay pautas guardadas.")
