# ticket_dashboard.py
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="CRM Ticket Manager", layout="wide")

# Ensure ticket data is initialized in session state
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

# Convert session data to DataFrame for display
tickets_df = pd.DataFrame(st.session_state.tickets_data)

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

        # Option to update status and assignee
        new_status = st.selectbox(f"Actualizar Estado de Ticket #{row['ID del Ticket']}", ["Abierto", "En progreso", "Cerrado"], index=["Abierto", "En progreso", "Cerrado"].index(row["Estado"]))
        new_assignee = st.selectbox(f"Reasignar Ticket #{row['ID del Ticket']}", tickets_df["Asignado a"].unique(), index=tickets_df["Asignado a"].unique().tolist().index(row["Asignado a"]))

        if st.button(f"Guardar Cambios para Ticket #{row['ID del Ticket']}", key=f"save_{row['ID del Ticket']}"):
            # Update session state data
            ticket_index = tickets_df[tickets_df["ID del Ticket"] == row["ID del Ticket"]].index[0]
            st.session_state.tickets_data["Estado"][ticket_index] = new_status
            st.session_state.tickets_data["Asignado a"][ticket_index] = new_assignee
            st.session_state.tickets_data["Fecha de Actualización"][ticket_index] = pd.Timestamp.now().strftime("%Y-%m-%d")
            st.success(f"Estado y asignación de Ticket #{row['ID del Ticket']} actualizado.")
            st.experimental_rerun()  # Refresh to show updated data
