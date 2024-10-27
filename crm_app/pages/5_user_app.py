# user_chat.py
import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
import time

# Page configuration - this must be the first Streamlit command
st.set_page_config(page_title="LLMHackathon", page_icon="🤖", layout="wide")

# Directory to store ticket chat files
tickets_dir = "tickets"
if not os.path.exists(tickets_dir):
    os.makedirs(tickets_dir)

# Helper to simulate streaming output with delay
def stream_str(s, speed=250):
    for c in s:
        yield c
        time.sleep(1 / speed)

# Function to get response from Mistral AI
def get_mistral_completion(prompt: str):
    client = Mistral(api_key=st.session_state['MISTRAL_API_KEY'])
    chat_response = client.chat.complete(
        model=st.session_state['MISTRAL_MODEL'],
        messages=[{"role": "user", "content": prompt}]
    )
    return chat_response.choices[0].message.content

# Initialize session state variables
if 'tickets_data' not in st.session_state:
    st.session_state.tickets_data = {
        "ID del Ticket": [],
        "Cliente": [],
        "Asunto": [],
        "Estado": [],
        "Prioridad": [],
        "Fecha de Creación": [],
        "Fecha de Actualización": [],
        "Asignado a": [],
        "Descripción": []
    }

if 'CODEGPT_API_KEY' not in st.session_state:
    st.session_state['CODEGPT_API_KEY'] = st.secrets.get("CODEGPT_API_KEY", "")

if 'MISTRAL_API_KEY' not in st.session_state:
    st.session_state['MISTRAL_API_KEY'] = st.secrets.get("MISTRAL_API_KEY", "")

if 'MISTRAL_MODEL' not in st.session_state:
    st.session_state['MISTRAL_MODEL'] = st.secrets.get("MISTRAL_MODEL", "mistral-large-latest")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Collect user contact information
st.sidebar.title("Información de Contacto")
contact_method = st.sidebar.selectbox("Método de Contacto", ["WhatsApp", "Gmail"], key="contact_method_selectbox")
contact_info = st.sidebar.text_input("Contacto", placeholder="Número o Email", key="contact_info_input")

# Generate or switch ticket ID based on contact info
if contact_info:
    ticket_id = f"{contact_method}_{contact_info}"
    st.session_state['ticket_id'] = ticket_id
    chat_file_path = os.path.join(tickets_dir, f"chat_data_{ticket_id}.txt")

    # Add ticket data if it's a new ticket
    if ticket_id not in st.session_state.tickets_data["ID del Ticket"]:
        st.session_state.tickets_data["ID del Ticket"].append(ticket_id)
        st.session_state.tickets_data["Cliente"].append(contact_info)
        st.session_state.tickets_data["Asunto"].append(f"Consulta vía {contact_method}")
        st.session_state.tickets_data["Estado"].append("Abierto")
        st.session_state.tickets_data["Prioridad"].append("Media")
        st.session_state.tickets_data["Fecha de Creación"].append(datetime.now().strftime("%Y-%m-%d"))
        st.session_state.tickets_data["Fecha de Actualización"].append(datetime.now().strftime("%Y-%m-%d"))
        st.session_state.tickets_data["Asignado a"].append("No asignado")
        st.session_state.tickets_data["Descripción"].append(f"Contacto iniciado a través de {contact_method}")
else:
    st.warning("Ingresa tu información de contacto para comenzar.")

# Function to reset chat history
def reset_chat():
    st.session_state['messages'] = []

# Load chat history from the ticket-specific file
def load_chat_history():
    st.session_state['messages'] = []
    if contact_info and os.path.exists(chat_file_path):
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
            st.session_state['messages'].append({"role": role, "content": message})

# Main Interface
st.title("LLMHackathon")

# Reset chat button
if st.button("Reset Chat"):
    reset_chat()

# Load chat history to see any new messages, including from admin
load_chat_history()

# Display the chat messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.write(message['content'])

# User input for new messages
user_prompt = st.chat_input("Di algo")
if user_prompt:
    st.session_state['messages'].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # Save user message to the chat file
    with open(chat_file_path, "a") as f:
        f.write(f"{datetime.now()} | Usuario: {user_prompt}\n")

    # Get bot response and stream output
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Bot response streaming
        response = get_mistral_completion(user_prompt)
        for chunk in stream_str(response):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
        st.session_state['messages'].append({"role": "assistant", "content": full_response})

        # Save bot response to chat file
        with open(chat_file_path, "a") as f:
            f.write(f"{datetime.now()} | Bot: {full_response}\n")
