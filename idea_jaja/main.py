# admin_app.py
import streamlit as st
import os
import json
import time
from datetime import datetime
from mistralai import Mistral  # Asegúrate de tener la librería configurada

# Directorio para almacenar los tickets y pautas
tickets_dir = "tickets"
pautas_dir = "pautas"
if not os.path.exists(tickets_dir):
    os.makedirs(tickets_dir)
if not os.path.exists(pautas_dir):
    os.makedirs(pautas_dir)

# Función para simular el "streaming" de texto
def stream_str(s, speed=250):
    for c in s:
        yield c
        time.sleep(1 / speed)

# Configuración de la página
st.set_page_config(page_title="Panel de Administración - Chat CRM", page_icon="👤")

# Título del panel
st.title("Panel de Administración - Conversaciones de Tickets")

# Lista de tickets disponibles
ticket_files = [f for f in os.listdir(tickets_dir) if f.endswith(".txt")]
ticket_ids = [f.replace("ticket_", "").replace(".txt", "") for f in ticket_files]
selected_ticket = st.selectbox("Seleccionar un Ticket", ticket_ids)

# Función para generar una pauta utilizando Mistral
def generar_pauta(conversacion_texto):
    client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
    prompt = f"Genera una pauta de solución para el siguiente caso:\n\n{conversacion_texto}"
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

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

    # Visualizar el historial de mensajes solo de usuario y admin
    st.markdown("#### Historial de Mensajes")
    user_admin_messages = [
        message for message in ticket_data["messages"] if message["role"] in ["user", "admin"]
    ]
    for message in user_admin_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Entrada para la respuesta del administrador
    st.write("### Responder como Admin")
    admin_response = st.chat_input("Escribe tu respuesta...")

    if admin_response:
        # Mostrar y transmitir la respuesta del administrador
        with st.chat_message("admin"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in stream_str(admin_response):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        # Agregar respuesta del administrador a los mensajes del ticket
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        admin_message = {
            "message_id": len(ticket_data["messages"]) + 1,
            "timestamp": timestamp,
            "role": "admin",
            "content": admin_response
        }
        ticket_data["messages"].append(admin_message)

        # Actualizar los timestamps
        ticket_data["timestamps"]["last_update_ts"] = timestamp
        ticket_data["timestamps"]["last_response_asesor_ts"] = timestamp

        # Guardar datos actualizados del ticket
        with open(chat_file_path, "w") as file:
            json.dump(ticket_data, file, indent=4)
        
        st.success("Respuesta enviada.")

    # Generación de Pauta de Conocimiento con IA
    if st.button("Generar Pauta de Conocimiento"):
        conversacion_texto = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in user_admin_messages]
        )
        pauta_generada = generar_pauta(conversacion_texto)

        st.write("**Pauta Generada**:")
        st.write(pauta_generada)
        
        # Validación de la pauta
        if st.button("Aprobar y Guardar Pauta"):
            pauta_data = {
                "ticket_id": selected_ticket,
                "conversacion": conversacion_texto,
                "pauta": pauta_generada,
                "timestamp": timestamp
            }
            pauta_file_path = os.path.join(pautas_dir, f"pauta_{selected_ticket}.txt")
            with open(pauta_file_path, "w") as f:
                json.dump(pauta_data, f, indent=4)
            st.success("Pauta guardada exitosamente en la base de conocimiento.")

# Visualización de Pautas Guardadas
st.subheader("Pautas de Conocimiento Guardadas")
pauta_files = [f for f in os.listdir(pautas_dir) if f.endswith(".txt")]

if pauta_files:
    for pauta_file in pauta_files:
        with open(os.path.join(pautas_dir, pauta_file), "r") as f:
            pauta_data = json.load(f)
            st.write(f"**Pauta para Ticket {pauta_data['ticket_id']}**")
            st.write("**Conversación**:")
            st.write(pauta_data["conversacion"])
            st.write("**Pauta Generada**:")
            st.write(pauta_data["pauta"])
else:
    st.write("No hay pautas guardadas.")
