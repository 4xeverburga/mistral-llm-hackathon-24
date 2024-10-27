import streamlit as st

# Configuración de la página
st.set_page_config(page_title="VirtualSellers CRM", page_icon="📋")

# Añadir imagen de cabecera
st.image("pages\logo.png", use_column_width=True)  # Cambia "imagen_bienvenida.jpg" por la ruta de tu imagen o URL

# Título estilizado y descripción
st.markdown("<h1 style='text-align: center; color: #0099CC;'>VirtualSellers</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555;'>Gestión de tus clientes a la palma de tu mano 👋</h3>", unsafe_allow_html=True)

# Texto introductorio y descripción
st.markdown("""
    <p style='text-align: center; font-size: 1.1em; color: #666;'>
        Bienvenido a <strong>VirtualSellers</strong>, tu asistente virtual inteligente que revoluciona la atención al cliente 
        mediante la integración con <strong>WhatsApp, correo electrónico e Instagram</strong>.
    </p>
""", unsafe_allow_html=True)

# Sidebar con opciones de navegación
st.sidebar.success("Selecciona una sección de la lista.")

# Cuerpo principal con detalles
st.markdown("""
    <div style="background-color: #E0F7FA; padding: 20px; border-radius: 10px; margin-top: 20px;">
        <p style="font-size: 1.1em; color: #333;">
            Con <strong>VirtualSellers</strong>, tus clientes nunca tendrán que esperar. Gracias a los agentes virtuales, 
            obtendrán respuestas rápidas y personalizadas las 24 horas del día, los 7 días de la semana, eliminando 
            tiempos de espera y simplificando la comunicación entre <strong>empresas y clientes</strong>.
        </p>
        <p style="font-size: 1.1em; color: #333;">
            VirtualSellers permite la personalización total de sus agentes para adaptarse a las necesidades específicas de cada negocio. 
            Con el poder de <strong>Mistral AI</strong>, tu CRM es capaz de:
        </p>
        <ul style="color: #555; font-size: 1.1em;">
            <li>Responder consultas comunes de manera eficiente</li>
            <li>Gestionar solicitudes de atención en múltiples canales</li>
            <li>Adaptarse a diferentes casos de uso y orientar los agentes según las necesidades del cliente</li>
        </ul>
        <p style="font-size: 1.1em; color: #333;">
            Así, creamos una red de agentes virtuales adaptable y eficiente, lista para potenciar la relación con tus clientes.
        </p>
    </div>
""", unsafe_allow_html=True)

# Pie de página opcional con llamada a la acción
st.markdown("""
    <div style="margin-top: 40px; text-align: center;">
        <p style="font-size: 1.2em; font-weight: bold; color: #0099CC;">
            ¡Empieza hoy a gestionar tus clientes de una forma innovadora y eficiente!
        </p>
    </div>
""", unsafe_allow_html=True)
