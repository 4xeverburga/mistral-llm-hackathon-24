# admin_app.py
import streamlit as st
import os
import json
from datetime import datetime
import time

# Directory to store ticket chat files
tickets_dir = "tickets"
if not os.path.exists(tickets_dir):
    os.makedirs(tickets_dir)

# Helper to simulate streaming text for admin response
def stream_str(s, speed=250):
    for c in s:
        yield c
        time.sleep(1 / speed)

# Page configuration
st.set_page_config(page_title="Chat CRM - Admin", page_icon="👤")

# Load all ticket IDs from available ticket files
st.title("Panel de Administración - Conversaciones de Tickets")

# List of ticket IDs from the tickets directory
ticket_files = [f for f in os.listdir(tickets_dir) if f.endswith(".txt")]
ticket_ids = [f.replace("ticket_", "").replace(".txt", "") for f in ticket_files]

selected_ticket = st.selectbox("Seleccionar un Ticket", ticket_ids)

if selected_ticket:
    # Load the selected ticket data
    chat_file_path = os.path.join(tickets_dir, f"ticket_{selected_ticket}.txt")
    with open(chat_file_path, "r") as file:
        ticket_data = json.load(file)

    st.write(f"### Conversación para el Ticket: {selected_ticket}")

    # Display ticket details
    st.write("**Estado:**", ticket_data["status_type_desc"])
    st.write("**Prioridad:**", ticket_data["priority_type_desc"])
    st.write("**Descripción:**", ticket_data["description"])
    st.write("**Cliente:**", ticket_data["user"]["name"])
    st.write("**Fecha de Creación:**", ticket_data["timestamps"]["record_creation_ts"])
    st.write("**Última Actualización:**", ticket_data["timestamps"]["last_update_ts"])

    # Display chat history for the selected ticket
    st.markdown("#### Historial de Mensajes")
    for message in ticket_data["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input for admin response
    st.write("### Responder como Admin")
    admin_response = st.chat_input("Escribe tu respuesta...")

    if admin_response:
        # Display and stream the admin's response
        with st.chat_message("admin"):
            message_placeholder = st.empty()
            full_response = ""

            for chunk in stream_str(admin_response):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        # Append admin's response to ticket messages
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        admin_message = {
            "message_id": len(ticket_data["messages"]) + 1,
            "timestamp": timestamp,
            "role": "admin",
            "content": admin_response
        }
        ticket_data["messages"].append(admin_message)

        # Update timestamps
        ticket_data["timestamps"]["last_update_ts"] = timestamp
        ticket_data["timestamps"]["last_response_asesor_ts"] = timestamp

        # Save updated ticket data back to the file
        with open(chat_file_path, "w") as file:
            json.dump(ticket_data, file, indent=4)
        
        st.success("Respuesta enviada.")
