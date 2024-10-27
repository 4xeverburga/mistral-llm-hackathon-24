import streamlit as st

# Configuración de la aplicación
st.set_page_config(page_title="CRM Básico", layout="wide")

# Título del CRM
st.title("CRM Básico")

# Barra de navegación lateral
menu = st.sidebar.selectbox("Menú", ["Inicio", "Clientes", "Añadir Cliente", "Reportes"])

# Sección de inicio
if menu == "Inicio":
    st.header("Bienvenido al CRM")
    st.write("Este es un sistema de CRM básico donde puedes gestionar la información de tus clientes.")

# Sección para visualizar clientes
elif menu == "Clientes":
    st.header("Clientes")
    st.write("Aquí puedes ver una lista de tus clientes. (Pendiente de implementación)")

# Sección para añadir nuevos clientes
elif menu == "Añadir Cliente":
    st.header("Añadir Nuevo Cliente")
    with st.form("form_cliente"):
        nombre = st.text_input("Nombre del Cliente")
        empresa = st.text_input("Empresa")
        email = st.text_input("Email")
        telefono = st.text_input("Teléfono")
        st.form_submit_button("Guardar")

# Sección de reportes
elif menu == "Reportes":
    st.header("Reportes")
    st.write("Genera reportes y analiza datos de los clientes. (Pendiente de implementación)")

