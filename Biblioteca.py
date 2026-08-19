import os
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Biblioteca de Economía", page_icon="📚", layout="wide"
)

# Estilos CSS para convertir la sección en una banda de desplazamiento horizontal continua
st.markdown("""
<style>
    .horizontal-scroll-container {
        display: flex;
        overflow-x: auto;
        gap: 20px;
        padding-bottom: 20px;
        scroll-behavior: smooth;
        scrollbar-width: thin;
    }
    .horizontal-scroll-container::-webkit-scrollbar {
        height: 8px;
    }
    .horizontal-scroll-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    /* Forzar que las columnas internas de Streamlit se mantengan en línea horizontal */
    [data-testid="column"] {
        flex: 0 0 250px !important;
        min-width: 250px !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar el estado de la sesión con los libros y autores reales
if "libros" not in st.session_state:
    st.session_state.libros = [
        {
            "id": 1,
            "titulo": "Brics",
            "autor": "Dr. C. Roberto Muñoz González & Dr. C. Bonifácio Vissetaca",
            "portada": "brics.png",
            "archivo": "Brics.pdf",
        },
        {
            "id": 2,
            "titulo": "Capitalismo actual",
            "autor": "Alejandro Dabat, Jorge Hernández & Canek Vega",
            "portada": "capitalismo.png",
            "archivo": "Capitalismo actual-Dabat.pdf",
        },
        {
            "id": 3,
            "titulo": "Desigualdad",
            "autor": "Anastasio Ovejero",
            "portada": "desigualdad.png",
            "archivo": "Desigualdad-Ovejero.pdf",
        },
        {
            "id": 4,
            "titulo": "El caso del Perú",
            "autor": "José Matos Mar",
            "portada": "casoperu.png",
            "archivo": "El caso del Perú.pdf",
        },
        {
            "id": 5,
            "titulo": "Estado Nación e Identidad Nacional",
            "autor": "Sonia García Segura",
            "portada": "estadonacion.png",
            "archivo": "Estado Nación e Identidad Nacional.pdf",
        },
        {
            "id": 6,
            "titulo": "Historia e Identidad del Perú",
            "autor": "Oswaldo Holguín Callo",
            "portada": "historia.png",
            "archivo": "Historia e Identidad del Perú.pdf",
        },
        {
            "id": 7,
            "titulo": "La nueva corrupción en el Perú",
            "autor": "Óscar Ugarteche Galarza",
            "portada": "nuevacorrupcion.png",
            "archivo": "La nueva corrupción en el Perú.pdf",
        },
        {
            "id": 8,
            "titulo": "Nuevo orden",
            "autor": "Juan José Palacios L.",
            "portada": "nuevoorden.png",
            "archivo": "Nuevo orden-Palacios.pdf",
        },
        {
            "id": 9,
            "titulo": "Oligarquía en el Perú",
            "autor": "Dennis Gilbert",
            "portada": "oligarquia.png",
            "archivo": "Oligarquía en el Perú.pdf",
        },
        {
            "id": 10,
            "titulo": "Realidad Peruana",
            "autor": "Abelardo Hurtado, Wadson Pinchi & Norman Coronel",
            "portada": "realidad.png",
            "archivo": "Realidad Peruana.pdf",
        },
        {
            "id": 11,
            "titulo": "Sociedad de la información",
            "autor": "José Antonio Moreiro González",
            "portada": "info.png",
            "archivo": "Sociedad de la información-Moreiro.pdf",
        },
        {
            "id": 12,
            "titulo": "Sociedad del conocimiento",
            "autor": "Adriana Marrero",
            "portada": "conocimiento.png",
            "archivo": "Sociedad del conocimiento-Marredo.pdf",
        },
    ]

# Título principal
st.title("📚 Biblioteca Interactiva de Economía")

# Menú lateral (Únicamente la sección de la biblioteca para mantenerlo limpio)
menu = st.sidebar.selectbox(
    "Menú de Navegación", ["Ver Biblioteca", "Panel de Autor"]
)

# -------------------------------------------------------------
# 1. VER BIBLIOTECA
# -------------------------------------------------------------
if menu == "Ver Biblioteca":
    st.header("📌 Realidad Nacional")
    st.write("Desliza horizontalmente para explorar los libros y descargarlos directamente.")

    # Barra de búsqueda simple
    busqueda = st.text_input("🔍 Buscar por título o autor", "").lower()

    libros_filtrados = [
        l for l in st.session_state.libros
        if busqueda in l["titulo"].lower() or busqueda in l["autor"].lower()
    ]

    if not libros_filtrados:
        st.warning("No se encontraron libros que coincidan con la búsqueda.")
    else:
        # Abrimos el contenedor con la clase CSS que fuerza el scroll horizontal
        st.markdown('<div class="horizontal-scroll-container">', unsafe_allow_html=True)
        
        # Creamos las columnas en línea para todos los libros filtrados
        cols = st.columns(len(libros_filtrados))

        for i, libro in enumerate(libros_filtrados):
            with cols[i]:
                with st.container(height=520, border=True):
                    # Carga de la imagen local con soporte de respaldo si no existe el archivo físico
                    if os.path.exists(libro["portada"]):
                        st.image(libro["portada"], use_container_width=True)
                    else:
                        st.image("https://picsum.photos/seed/default/150/200", use_container_width=True)
                    
                    st.subheader(libro["titulo"])
                    st.write(f"**Autor:** {libro['autor']}")

                    # Botón de descarga nativo original
                    if os.path.exists(libro["archivo"]):
                        with open(libro["archivo"], "rb") as archivo_pdf:
                            st.download_button(
                                label="📥 Descargar PDF",
                                data=archivo_pdf,
                                file_name=libro["archivo"],
                                mime="application/pdf",
                                key=f"download_{libro['id']}"
                            )
                    else:
                        st.error("⚠️ Archivo no encontrado.")
                        
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. PANEL DE AUTOR
# -------------------------------------------------------------
elif menu == "Panel de Autor":
    st.header("Panel de Moderación")
    st.write("Libros actualmente registrados en la biblioteca:")
    for libro in st.session_state.libros:
        st.write(f"- **{libro['titulo']}** por *{libro['autor']}*")
