# user_chat.py
import streamlit as st
import os
import json
from datetime import datetime
from mistralai import Mistral
import time

# Page configuration
st.set_page_config(page_title="LLMHackathon", page_icon="🤖", layout="wide")

# Initialize session state variables if they are not already defined
if 'MISTRAL_API_KEY' not in st.session_state:
    st.session_state['MISTRAL_API_KEY'] = st.secrets.get("MISTRAL_API_KEY", "")

if 'MISTRAL_MODEL' not in st.session_state:
    st.session_state['MISTRAL_MODEL'] = st.secrets.get("MISTRAL_MODEL", "mistral-large-latest")

if 'CODEGPT_API_KEY' not in st.session_state:
    st.session_state['CODEGPT_API_KEY'] = st.secrets.get("CODEGPT_API_KEY", "")

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

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Helper to simulate streaming output with delay
def stream_str(s, speed=250):
    for c in s:
        yield c
        time.sleep(1 / speed)

# Mistral API function
def get_mistral_completion(prompt: str):
    client = Mistral(api_key=st.session_state['MISTRAL_API_KEY'])
    chat_response = client.chat.complete(
        model=st.session_state['MISTRAL_MODEL'],
        messages=[{"role": "user", "content": prompt}]
    )
    return chat_response.choices[0].message.content

# Load or create ticket file
def load_or_create_ticket(ticket_id, user_data, description, priority, channel_type):
    ticket_file_path = os.path.join(tickets_dir, f"ticket_{ticket_id}.txt")
    if not os.path.exists(ticket_file_path):
        ticket_data = {
            "ticket_id": ticket_id,
            "status_type_desc": "Abierto",
            "description": description,
            "nps_flg": False,
            "channel_type": channel_type,
            "priority_type_desc": priority,
            "user": user_data,
            "agent": {"agent_id": None, "context": "No asignado"},
            "nps_score": None,
            "ticket_tag_array": [],
            "timestamps": {
                "record_creation_ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_update_ts": None,
                "last_response_agent_ts": None,
                "last_response_user_ts": None
            },
            "messages": []
        }
        with open(ticket_file_path, "w") as file:
            json.dump(ticket_data, file, indent=4)
    return ticket_file_path

# Directory to store ticket files
tickets_dir = "tickets"
if not os.path.exists(tickets_dir):
    os.makedirs(tickets_dir)

# Collect user contact information
st.sidebar.title("Información de Contacto")
contact_method = st.sidebar.selectbox("Método de Contacto", ["WhatsApp", "Gmail"], key="contact_method_selectbox")
contact_info = st.sidebar.text_input("Contacto", placeholder="Número o Email", key="contact_info_input")

# Generate or switch ticket ID based on contact info
chat_file_path = None  # Initialize chat_file_path as None
if contact_info:
    ticket_id = f"{contact_method}_{contact_info}"
    st.session_state['ticket_id'] = ticket_id
    chat_file_path = load_or_create_ticket(ticket_id, user_data={
        "user_id": ticket_id,
        "email": contact_info if "@" in contact_info else None,
        "phone_number": contact_info if "@" not in contact_info else None,
        "name": contact_info
    }, description="Consulta inicial", priority="Media", channel_type=contact_method)
else:
    st.warning("Ingresa tu información de contacto para comenzar.")

# Load chat history
def load_chat_history():
    st.session_state['messages'] = []
    if chat_file_path and os.path.exists(chat_file_path):  # Ensure chat_file_path is valid
        with open(chat_file_path, "r") as file:
            ticket_data = json.load(file)
            st.session_state['messages'] = ticket_data["messages"]

# Save messages to ticket file
def save_message(role, content):
    if not chat_file_path:  # Ensure chat_file_path is defined
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = {"message_id": len(st.session_state['messages']) + 1, "timestamp": timestamp, "role": role, "content": content}
    st.session_state['messages'].append(message)  # Add message immediately to session

    # Update ticket file with the new message
    with open(chat_file_path, "r") as file:
        ticket_data = json.load(file)
    ticket_data["messages"].append(message)
    ticket_data["timestamps"]["last_update_ts"] = timestamp
    ticket_data["timestamps"][f"last_response_{role}_ts"] = timestamp

    with open(chat_file_path, "w") as file:
        json.dump(ticket_data, file, indent=4)

# Main Interface
st.title("LLMHackathon")

# Reset chat button
if st.button("Reset Chat"):
    reset_chat()

# Load chat history
if chat_file_path:
    load_chat_history()

# Display chat messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.write(message['content'])

# User input for new messages
user_prompt = st.chat_input("Di algo")
if user_prompt:
    # Immediately display user message and save it
    st.session_state['messages'].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)
    save_message("user", user_prompt)

    # Get and display bot response
    response = get_mistral_completion(user_prompt)
    st.session_state['messages'].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
    save_message("assistant", response)
