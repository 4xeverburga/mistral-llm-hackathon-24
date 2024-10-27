# admin_app.py
import streamlit as st
import os
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

# Load ticket IDs from session state
st.title("Panel de Administración - Conversaciones de Tickets")

# Ticket list from session data
ticket_ids = st.session_state.tickets_data["ID del Ticket"]
selected_ticket = st.selectbox("Seleccionar un Ticket", ticket_ids)

if selected_ticket:
    chat_file_path = os.path.join(tickets_dir, f"chat_data_{selected_ticket}.txt")
    st.write(f"### Conversación para el Ticket: {selected_ticket}")

    # Load and display chat history for the selected ticket
    if os.path.exists(chat_file_path):
        with open(chat_file_path, "r") as f:
            chat_history = f.readlines()

        for line in chat_history:
            if "Usuario:" in line:
                role, message = "user", line.split("Usuario:", 1)[1].strip()
            elif "Bot:" in line:
                role, message = "assistant", line.split("Bot:", 1)[1].strip()
            elif "Admin:" in line:
                role, message = "admin", line.split("Admin:", 1)[1].strip()
            else:
                continue
            with st.chat_message(role):
                st.write(message.strip())

    # Input for admin response
    st.write("### Responder como Admin")
    admin_response = st.chat_input("Escribe tu respuesta...")

    if admin_response:
        with st.chat_message("admin"):
            message_placeholder = st.empty()
            full_response = ""

            for chunk in stream_str(admin_response):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        # Save admin message to chat file
        with open(chat_file_path, "a") as f:
            f.write(f"{datetime.now()} | Admin: {admin_response}\n")
