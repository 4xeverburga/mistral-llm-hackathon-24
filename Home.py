import streamlit as st

st.set_page_config(page_title="CRM Básico", page_icon="📋")

st.write("# Bienvenido al CRM Básico 👋")
st.sidebar.success("Selecciona una sección de la lista.")
st.markdown("""
Este CRM básico permite gestionar la información de clientes, añadir nuevos contactos, manejar tickets y ver reportes.
""")
