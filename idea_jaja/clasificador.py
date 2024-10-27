# admin_app.py
import streamlit as st
import os
import json
from datetime import datetime
from mistralai import Mistral  # Asegúrate de tener la API de Mistral configurada

# Directorio para almacenar los tickets
tickets_dir = "tickets"
if not os.path.exists(tickets_dir):
    os.makedirs(tickets_dir)

# Configuración de la página
st.set_page_config(page_title="Panel de Administración - Chat CRM", page_icon="👤")

# Título del panel
st.title("Panel de Administración - Análisis de Sentimiento en Conversaciones de Tickets")

# Lista de tickets disponibles
ticket_files = [f for f in os.listdir(tickets_dir) if f.endswith(".txt")]
ticket_ids = [f.replace("ticket_", "").replace(".txt", "") for f in ticket_files]
selected_ticket = st.selectbox("Seleccionar un Ticket", ticket_ids)

# Función para realizar el análisis de sentimiento utilizando Mistral
def analizar_sentimientos(conversacion_texto):
    client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
    prompt = f"Analiza el sentimiento de la siguiente conversación. Genera etiquetas descriptivas sobre el estado emocional del cliente:\n\n{conversacion_texto}"
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    # Supongamos que la respuesta contiene etiquetas separadas por comas
    etiquetas = response.choices[0].message.content.strip().split(", ")
    return etiquetas

# Visualización del ticket seleccionado
if selected_ticket:
    # Cargar datos del ticket
    chat_file_path = os.path.join(tickets_dir, f"ticket_{selected_ticket}.txt")
    with open(chat_file_path, "r") as file:
        ticket_data = json.load(file)

    st.write(f"### Conversación para el Ticket: {selected_ticket}")
    st.write("**Estado:**", ticket_data["status_type_desc"])
    st.write("**Prioridad:**", ticket_data["priority_type_desc"])
    st.write("**Descripción:**", ticket_data["description"])
    st.write("**Cliente:**", ticket_data["user"]["name"])
    st.write("**Fecha de Creación:**", ticket_data["timestamps"]["record_creation_ts"])
    st.write("**Última Actualización:**", ticket_data["timestamps"]["last_update_ts"])

    # Visualizar el historial de mensajes solo de usuario y chatbot
    st.markdown("#### Historial de Mensajes (Usuario y Chatbot)")
    user_bot_messages = [
        message for message in ticket_data["messages"] if message["role"] in ["user", "assistant"]
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
        
        # Actualizar el campo ticket_tag_array
        ticket_data["ticket_tag_array"] = etiquetas_sentimiento
        st.write("**Etiquetas de Sentimiento Generadas**:")
        st.write(", ".join(etiquetas_sentimiento))
        
        # Guardar las etiquetas actualizadas en el ticket
        with open(chat_file_path, "w") as file:
            json.dump(ticket_data, file, indent=4)
        
        st.success("Análisis de sentimiento completado y etiquetas guardadas en el ticket.")

# Visualización de Etiquetas de Sentimiento Guardadas
st.subheader("Etiquetas de Sentimiento para el Ticket Seleccionado")
if selected_ticket and "ticket_tag_array" in ticket_data:
    if ticket_data["ticket_tag_array"]:
        st.write("**Etiquetas Generadas**:", ", ".join(ticket_data["ticket_tag_array"]))
    else:
        st.write("No hay etiquetas generadas para este ticket.")
