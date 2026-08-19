import os
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Biblioteca de Economía", page_icon="📚", layout="wide"
)

# Estilos CSS avanzados para el scroll horizontal estilo Netflix
st.markdown("""
<style>
    .netflix-category {
        margin-bottom: 30px;
    }
    .netflix-title {
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .netflix-row {
        display: flex;
        overflow-x: auto;
        gap: 16px;
        padding-bottom: 10px;
        scrollbar-width: thin;
        scrollbar-color: #555 #1e1e1e;
    }
    .netflix-row::-webkit-scrollbar {
        height: 6px;
    }
    .netflix-row::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 3px;
    }
    .netflix-card {
        flex: 0 0 160px;
        background-color: #1e1e1e;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .netflix-card:hover {
        transform: scale(1.05);
    }
    .netflix-card img {
        width: 100%;
        height: 220px;
        object-fit: cover;
    }
    .card-info {
        padding: 10px;
    }
    .card-title {
        font-size: 14px;
        font-weight: bold;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }
    .card-author {
        font-size: 11px;
        color: #b0b0b0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar el estado de la sesión con los libros, autores, portadas y categorías
if "libros" not in st.session_state:
    st.session_state.libros = [
        {
            "id": 1,
            "titulo": "Brics",
            "autor": "Dr. C. Roberto Muñoz González & Dr. C. Bonifácio Vissetaca",
            "portada": "brics.png",
            "archivo": "Brics.pdf",
            "categoria": "Geopolítica y Globalización"
        },
        {
            "id": 2,
            "titulo": "Capitalismo actual",
            "autor": "Alejandro Dabat, Jorge Hernández & Canek Vega",
            "portada": "capitalismo.png",
            "archivo": "Capitalismo actual-Dabat.pdf",
            "categoria": "Geopolítica y Globalización"
        },
        {
            "id": 3,
            "titulo": "Desigualdad",
            "autor": "Anastasio Ovejero",
            "portada": "desigualdad.png",
            "archivo": "Desigualdad-Ovejero.pdf",
            "categoria": "Sociedad y Tecnología"
        },
        {
            "id": 4,
            "titulo": "El caso del Perú",
            "autor": "José Matos Mar",
            "portada": "casoperu.png",
            "archivo": "El caso del Perú.pdf",
            "categoria": "Realidad Nacional"
        },
        {
            "id": 5,
            "titulo": "Estado Nación e Identidad Nacional",
            "autor": "Sonia García Segura",
            "portada": "estadonacion.png",
            "archivo": "Estado Nación e Identidad Nacional.pdf",
            "categoria": "Realidad Nacional"
        },
        {
            "id": 6,
            "titulo": "Historia e Identidad del Perú",
            "autor": "Oswaldo Holguín Callo",
            "portada": "historia.png",
            "archivo": "Historia e Identidad del Perú.pdf",
            "categoria": "Realidad Nacional"
        },
        {
            "id": 7,
            "titulo": "La nueva corrupción en el Perú",
            "autor": "Óscar Ugarteche Galarza",
            "portada": "nuevacorrupcion.png",
            "archivo": "La nueva corrupción en el Perú.pdf",
            "categoria": "Realidad Nacional"
        },
        {
            "id": 8,
            "titulo": "Nuevo orden",
            "autor": "Juan José Palacios L.",
            "portada": "nuevoorden.png",
            "archivo": "Nuevo orden-Palacios.pdf",
            "categoria": "Geopolítica y Globalización"
        },
        {
            "id": 9,
            "titulo": "Oligarquía en el Perú",
            "autor": "Dennis Gilbert",
            "portada": "oligarquia.png",
            "archivo": "Oligarquía en el Perú.pdf",
            "categoria": "Realidad Nacional"
        },
        {
            "id": 10,
            "titulo": "Realidad Peruana",
            "autor": "Abelardo Hurtado, Wadson Pinchi & Norman Coronel",
            "portada": "realidad.png",
            "archivo": "Realidad Peruana.pdf",
            "categoria": "Realidad Nacional"
        },
        {
            "id": 11,
            "titulo": "Sociedad de la información",
            "autor": "José Antonio Moreiro González",
            "portada": "info.png",
            "archivo": "Sociedad de la información-Moreiro.pdf",
            "categoria": "Sociedad y Tecnología"
        },
        {
            "id": 12,
            "titulo": "Sociedad del conocimiento",
            "autor": "Adriana Marrero",
            "portada": "conocimiento.png",
            "archivo": "Sociedad del conocimiento-Marredo.pdf",
            "categoria": "Sociedad y Tecnología"
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
    st.write("Explora las categorías y desliza horizontalmente para ver todos los títulos.")

    # Barra de búsqueda global
    busqueda = st.text_input("🔍 Buscar por título o autor", "").lower()

    libros_filtrados = [
        l for l in st.session_state.libros
        if busqueda in l["titulo"].lower() or busqueda in l["autor"].lower()
    ]

    if not libros_filtrados:
        st.warning("No se encontraron libros que coincidan con la búsqueda.")
    else:
        categorias = sorted(list(set(l["categoria"] for l in libros_filtrados)))

        for categoria in categorias:
            libros_cat = [l for l in libros_filtrados if l["categoria"] == categoria]
            
            # Renderizado de la categoría y su contenedor horizontal
            st.markdown(f"""
            <div class="netflix-category">
                <div class="netflix-title">🔥 {categoria}</div>
                <div class="netflix-row">
            """, unsafe_allow_html=True)
            
            for libro in libros_cat:
                img_path = libro["portada"] if os.path.exists(libro["portada"]) else "https://picsum.photos/seed/default/150/200"
                st.markdown(f"""
                    <div class="netflix-card">
                        <img src="{img_path}" alt="{libro['titulo']}">
                        <div class="card-info">
                            <div class="card-title" title="{libro['titulo']}">{libro['titulo']}</div>
                            <div class="card-author" title="{libro['autor']}">Autor: {libro['autor']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div></div>", unsafe_allow_html=True)

            # Botones de descarga organizados debajo de cada sección para mantener la funcionalidad interactiva
            with st.expander(f"📥 Opciones de descarga para: {categoria}"):
                cols = st.columns(min(len(libros_cat), 3))
                for idx, libro in enumerate(libros_cat):
                    with cols[idx % 3]:
                        st.write(f"**{libro['titulo']}**")
                        if os.path.exists(libro["archivo"]):
                            with open(libro["archivo"], "rb") as archivo_pdf:
                                st.download_button(
                                    label=f"Descargar PDF",
                                    data=archivo_pdf,
                                    file_name=libro["archivo"],
                                    mime="application/pdf",
                                    key=f"download_{libro['id']}"
                                )
                        else:
                            st.error("⚠️ Archivo no encontrado.")

# -------------------------------------------------------------
# 2. SUGERIR APORTE
# -------------------------------------------------------------
elif menu == "Sugerir Aporte":
    st.header("Sube tu aporte para revisión")
    st.write("Comparte documentos o libros académicos con la comunidad.")

    with st.form("form_aporte", clear_on_submit=True):
        titulo = st.text_input("Título del libro o documento")
        autor = st.text_input("Autor")
        categoria_sug = st.selectbox("Categoría", ["Realidad Nacional", "Geopolítica y Globalización", "Sociedad y Tecnología"])
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
                    "categoria": categoria_sug
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
                    st.write(f"**Categoría:** {aporte['categoria']}")
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
