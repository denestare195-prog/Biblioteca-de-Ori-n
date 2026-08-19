import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Biblioteca de Economía", page_icon="📚", layout="wide"
)

# Inicializar el estado de la sesión para persistir datos
if "libros" not in st.session_state:
    st.session_state.libros = [
        {
            "id": 1,
            "titulo": "Economía 4.0",
            "autor": "Nes",
            "portada": "https://picsum.photos/seed/econ1/150/200",
            "archivo": "economia_4.pdf",
        },
        {
            "id": 2,
            "titulo": "Microeconomía Avanzada",
            "autor": "Nes",
            "portada": "https://picsum.photos/seed/econ2/150/200",
            "archivo": "micro_avanzada.pdf",
        },
        {
            "id": 3,
            "titulo": "Realidad Nacional",
            "autor": "Nes",
            "portada": "https://picsum.photos/seed/econ3/150/200",
            "archivo": "realidad_nacional.pdf",
        },
        {
            "id": 4,
            "titulo": "Macroeconomía Global",
            "autor": "Nes",
            "portada": "https://picsum.photos/seed/econ4/150/200",
            "archivo": "macro_global.pdf",
        },
    ]

if "pendientes" not in st.session_state:
    st.session_state.pendientes = []

# Título principal
st.title("📚 Biblioteca Interactiva de Economía")

# Menú lateral
menu = st.sidebar.selectbox(
    "Menú de Navegación", ["Ver Biblioteca", "Sugerir Aporte", "Panel de Autor"]
)

# -------------------------------------------------------------
# 1. VER BIBLIOTECA
# -------------------------------------------------------------
if menu == "Ver Biblioteca":
    st.header("Estante de Libros")
    st.write("Haz clic en un libro para ver sus detalles o descargarlo.")

    # Barra de búsqueda simple
    busqueda = st.text_input("🔍 Buscar por título o autor", "").lower()

    libros_filtrados = [
        l for l in st.session_state.libros
        if busqueda in l["titulo"].lower() or busqueda in l["autor"].lower()
    ]

    if not libros_filtrados:
        st.warning("No se encontraron libros que coincidan con la búsqueda.")
    else:
        # Creamos una cuadrícula de 3 columnas
        cols = st.columns(3)

        for i, libro in enumerate(libros_filtrados):
            with cols[i % 3]:
                st.image(libro["portada"], use_container_width=True)
                st.subheader(libro["titulo"])
                st.write(f"**Autor:** {libro['autor']}")

                # Botón interactivo
                if st.button("Ver Detalles", key=f"btn_{libro['id']}"):
                    st.success(f"Seleccionaste: {libro['titulo']}")
                    st.markdown(f"📥 Proximamente {libro['archivo']}(#)")
                
                st.divider()

# -------------------------------------------------------------
# 2. SUGERIR APORTE
# -------------------------------------------------------------
elif menu == "Sugerir Aporte":
    st.header("Sube tu aporte para revisión")
    st.write("Comparte documentos o libros académicos con la comunidad.")

    with st.form("form_aporte", clear_on_submit=True):
        titulo = st.text_input("Título del libro o documento")
        autor = st.text_input("Autor")
        archivo_subido = st.file_uploader("Sube el archivo PDF", type=["pdf"])
        
        enviado = st.form_submit_button("Enviar al Panel de Autor")

        if enviado:
            if titulo and autor and archivo_subido:
                nuevo_aporte = {
                    "id": len(st.session_state.libros) + len(st.session_state.pendientes) + 1,
                    "titulo": titulo,
                    "autor": autor,
                    "portada": "https://picsum.photos/seed/default/150/200",
                    "archivo": archivo_subido.name,
                }
                st.session_state.pendientes.append(nuevo_aporte)
                st.success("¡Aporte enviado con éxito! Quedará pendiente de aprobación.")
            else:
                st.warning("Por favor completa todos los campos y adjunta el archivo PDF.")

# -------------------------------------------------------------
# 3. PANEL DE AUTOR
# -------------------------------------------------------------
elif menu == "Panel de Autor":
    st.header("Panel de Moderación")
    st.write("Aportes pendientes de revisión:")

    if not st.session_state.pendientes:
        st.info("No hay aportes pendientes en este momento. ¡Todo al día!")
    else:
        for i, aporte in enumerate(st.session_state.pendientes):
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**Título:** {aporte['titulo']}")
                    st.write(f"**Autor:** {aporte['autor']}")
                with col2:
                    st.write(f"**Archivo:** {aporte['archivo']}")
                with col3:
                    if st.button("Aprobar", key=f"aprobar_{i}"):
                        st.session_state.libros.append(aporte)
                        st.session_state.pendientes.pop(i)
                        st.success(f"¡Aprobado: {aporte['titulo']}!")
                        st.rerun()
                    if st.button("Rechazar", key=f"rechazar_{i}"):
                        st.session_state.pendientes.pop(i)
                        st.warning(f"Aporte rechazado.")
                        st.rerun()
                st.divider()