# ticket_dashboard.py
import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="CRM Ticket Manager", layout="wide")

# Directory to store ticket files
tickets_dir = "tickets"
if not os.path.exists(tickets_dir):
    os.makedirs(tickets_dir)

# Load ticket data from all ticket files in the directory
def load_tickets_data():
    tickets_data = {
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

    for filename in os.listdir(tickets_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(tickets_dir, filename), "r") as file:
                ticket = json.load(file)
                tickets_data["ID del Ticket"].append(ticket["ticket_id"])
                tickets_data["Cliente"].append(ticket["user"]["name"])
                tickets_data["Asunto"].append(ticket["description"])
                tickets_data["Estado"].append(ticket["status_type_desc"])
                tickets_data["Prioridad"].append(ticket["priority_type_desc"])
                tickets_data["Fecha de Creación"].append(ticket["timestamps"]["record_creation_ts"])
                tickets_data["Fecha de Actualización"].append(ticket["timestamps"]["last_update_ts"])
                tickets_data["Asignado a"].append(ticket["agent"]["context"])
                tickets_data["Descripción"].append(ticket["description"])

    return pd.DataFrame(tickets_data)

# Display the ticket data in a DataFrame
tickets_df = load_tickets_data()

# Sidebar filters
st.sidebar.header("Filtrar Tickets")
estado_filter = st.sidebar.multiselect("Estado", options=tickets_df["Estado"].unique(), default=tickets_df["Estado"].unique())
prioridad_filter = st.sidebar.multiselect("Prioridad", options=tickets_df["Prioridad"].unique(), default=tickets_df["Prioridad"].unique())
asignado_filter = st.sidebar.multiselect("Asignado a", options=tickets_df["Asignado a"].unique(), default=tickets_df["Asignado a"].unique())

# Apply filters to DataFrame
filtered_df = tickets_df[
    (tickets_df["Estado"].isin(estado_filter)) &
    (tickets_df["Prioridad"].isin(prioridad_filter)) &
    (tickets_df["Asignado a"].isin(asignado_filter))
]

# Display filtered table
st.write("### Lista de Tickets")
st.dataframe(filtered_df)

# Detailed view for each ticket
st.markdown("### Detalles del Ticket")
for index, row in filtered_df.iterrows():
    with st.expander(f"Ticket #{row['ID del Ticket']} - {row['Asunto']}"):
        st.write("**Cliente:**", row["Cliente"])
        st.write("**Estado:**", row["Estado"])
        st.write("**Prioridad:**", row["Prioridad"])
        st.write("**Fecha de Creación:**", row["Fecha de Creación"])
        st.write("**Fecha de Actualización:**", row["Fecha de Actualización"])
        st.write("**Asignado a:**", row["Asignado a"])
        st.write("**Descripción:**", row["Descripción"])
