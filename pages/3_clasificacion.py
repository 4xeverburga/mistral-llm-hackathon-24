# admin_app.py
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from mistralai import Mistral  # Asegúrate de tener la API de Mistral configurada

# Cargar variables de entorno
load_dotenv()

# Configuración de la conexión a PostgreSQL usando variables de entorno
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"]
    )

# Configuración de la página
st.set_page_config(page_title="Panel de Administración - Chat CRM", page_icon="👤")
st.title("Panel de Administración - Análisis de Sentimiento en Conversaciones de Tickets")

# Obtener lista de IDs de tickets
@st.cache_data
def get_ticket_ids():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_id FROM ticket")
            tickets = cur.fetchall()
    return [ticket[0] for ticket in tickets]

# Cargar datos del ticket seleccionado
def load_ticket_data(ticket_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM ticket WHERE ticket_id = %s", (ticket_id,))
            ticket = cur.fetchone()
            if ticket and ticket['message']:
                ticket['message'] = json.loads(ticket['message'])  # Convertir el campo de mensajes a un array de diccionarios
            if ticket and ticket['tickettagarray']:
                ticket['tickettagarray'] = json.loads(ticket['tickettagarray'])  # Convertir las etiquetas a lista
            return ticket

# Función para realizar el análisis de sentimiento simplificado utilizando Mistral
def analizar_sentimientos(conversacion_texto):
    client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
    prompt = (
        "Analiza la siguiente conversación y clasifica el estado emocional del cliente "
        "con una de las siguientes etiquetas: 'Calmado', 'Agradecido', 'Neutro', 'Curioso', "
        "'Molesto', 'Estresado', o 'Frustrado'.\n\n"
        f"{conversacion_texto}"
    )
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    etiquetas = response.choices[0].message.content.strip().split(", ")
    
    # Si no se genera ninguna etiqueta, asigna 'Neutro' como predeterminado
    if not etiquetas or etiquetas == ['']:
        etiquetas = ["Neutro"]
        
    return etiquetas

# Botón para actualizar la lista de tickets
if st.button("Actualizar lista de tickets"):
    st.cache_data.clear()  # Borra el caché para recargar los datos
    ticket_ids = get_ticket_ids()
else:
    ticket_ids = get_ticket_ids()  # Cargar los tickets al inicio

# Selección del ticket
selected_ticket = st.selectbox("Seleccionar un Ticket", ticket_ids)

# Visualización del ticket seleccionado
if selected_ticket:
    # Cargar datos del ticket desde la base de datos
    ticket_data = load_ticket_data(selected_ticket)

    # Mostrar detalles del ticket
    st.write(f"### Conversación para el Ticket: {selected_ticket}")
    st.write("**Estado:**", ticket_data["statustypedesc"])
    st.write("**Prioridad:**", ticket_data["prioritytypedesc"])
    st.write("**Descripción:**", ticket_data["description"])
    st.write("**Cliente:**", ticket_data["userid"])
    st.write("**Fecha de Creación:**", ticket_data["recordcreationts"])
    st.write("**Última Actualización:**", ticket_data["lastupdatets"])

    # Visualizar historial de mensajes solo de usuario y chatbot
    st.markdown("#### Historial de Mensajes (Usuario y Chatbot)")
    user_bot_messages = [
        message for message in ticket_data["message"] if message["role"] in ["user", "assistant"]
    ]
    for message in user_bot_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Generación de etiquetas de análisis de sentimiento con IA
    if st.button("Analizar Sentimientos y Clasificar Conversación"):
        # Concatena los mensajes de usuario y chatbot en texto
        conversacion_texto = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in user_bot_messages]
        )
        etiquetas_sentimiento = analizar_sentimientos(conversacion_texto)
        
        # Mostrar etiquetas de sentimiento generadas
        st.write("**Etiquetas de Sentimiento Generadas**:")
        st.write(", ".join(etiquetas_sentimiento))

        # Guardar las etiquetas de sentimiento en la base de datos
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ticket
                    SET tickettagarray = %s
                    WHERE ticket_id = %s
                """, (json.dumps(etiquetas_sentimiento), selected_ticket))
                conn.commit()
        
        st.success("Análisis de sentimiento completado y etiquetas guardadas en el ticket.")

# Función para estilizar etiquetas de sentimiento con colores
def display_sentiment_tags(tags):
    colors = {
        "Calmado": "green",
        "Agradecido": "blue",
        "Neutro": "gray",
        "Curioso": "orange",
        "Molesto": "red",
        "Estresado": "purple",
        "Frustrado": "darkred"
    }
    
    # Genera el HTML para cada etiqueta con su color correspondiente
    styled_tags = [
        f"<span style='background-color: {colors.get(tag, 'black')}; "
        "color: white; padding: 0.2em 0.5em; margin-right: 0.5em; border-radius: 5px;'>"
        f"{tag}</span>"
        for tag in tags
    ]
    # Mostrar etiquetas en una línea de texto usando HTML
    st.markdown("".join(styled_tags), unsafe_allow_html=True)

# Visualización de Etiquetas de Sentimiento Guardadas
st.subheader("Etiquetas de Sentimiento para el Ticket Seleccionado")
if selected_ticket and "tickettagarray" in ticket_data:
    if ticket_data["tickettagarray"]:
        st.write("**Etiquetas Generadas**:")
        display_sentiment_tags(ticket_data["tickettagarray"])  # Mostrar las etiquetas con estilo
    else:
        st.write("No hay etiquetas generadas para este ticket.")
