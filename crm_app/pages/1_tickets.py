# ticket_dashboard.py
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import pandas as pd

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

# Configuración de la página
st.set_page_config(page_title="CRM Ticket Manager", layout="wide")

# Cargar datos de tickets desde la base de datos
@st.cache_data
def load_tickets_data():
    query = """
        SELECT
            ticket_id AS "ID del Ticket",
            userid AS "Cliente",
            description AS "Asunto",
            statustypedesc AS "Estado",
            prioritytypedesc AS "Prioridad",
            recordcreationts AS "Fecha de Creación",
            lastupdatets AS "Fecha de Actualización",
            agentid AS "Asignado a",
            description AS "Descripción"
        FROM ticket
    """
    with get_db_connection() as conn:
        return pd.read_sql(query, conn)

# Cargar datos de tickets
tickets_df = load_tickets_data()

# Botón para actualizar la lista de tickets
if st.button("Actualizar lista de tickets"):
    st.cache_data.clear()  # Borra el caché para asegurarse de que recargue
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

# Mostrar el DataFrame completo sin límites
st.write("### Lista de Tickets Completa")
st.dataframe(filtered_df, use_container_width=True)

# Vista detallada de cada ticket
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
