import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="MIMO | Monitor Operacional",
    page_icon="📡",
    layout="wide"
)

# Título de la aplicación
st.title("MIMO")
st.subheader("Monitor Integrado de Movimiento Operacional")

# Separador
st.divider()

# Indicadores principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Vehículo", "CA-742")

with col2:
    st.metric("Eventos registrados", "7")

with col3:
    st.metric("Tiempo en operación", "4 h 32 min")

with col4:
    st.metric("Nivel de vibración", "Alto")

st.divider()

# Sección de bienvenida
st.header("Panel de monitoreo")

st.write(
    "Bienvenido al sistema MIMO. "
    "Desde esta plataforma podrás visualizar "
    "los datos de movimiento, vibraciones e impactos "
    "registrados durante la operación del vehículo."

   
