import os
import base64
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Biblioteca de Economía", page_icon="📚", layout="wide"
)

# Funciones auxiliares para convertir archivos locales a Base64 (para que carguen perfectamente en HTML)
def archivo_a_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def obtener_imagen_src(ruta):
    if os.path.exists(ruta):
        ext = ruta.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        b64 = archivo_a_base64(ruta)
        return f"data:{mime};base64,{b64}"
    return "https://picsum.photos/seed/default/150/200"

def obtener_pdf_link(ruta):
    if os.path.exists(ruta):
        b64 = archivo_a_base64(ruta)
        return f"data:application/pdf;base64,{b64}"
    return "#"

# Estilos CSS y JavaScript para el carrusel con flechas y diseño oscuro tipo Netflix
st.markdown("""
<style>
    .main-container {
        padding: 10px 0;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .carousel-wrapper {
        position: relative;
        display: flex;
        align-items: center;
    }
    .carousel-track {
        display: flex;
        overflow-x: auto;
        scroll-behavior: smooth;
        gap: 20px;
        padding: 10px 5px;
        scrollbar-width: none; /* Ocultar scrollbar en Firefox */
    }
    .carousel-track::-webkit-scrollbar {
        display: none; /* Ocultar scrollbar en Chrome/Safari */
    }
    .netflix-card {
        flex: 0 0 180px;
        background-color: #1e1e1e;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1px solid #333;
    }
    .netflix-card:hover {
        transform: scale(1.05);
        border-color: #555;
    }
    .netflix-card img {
        width: 100%;
        height: 240px;
        object-fit: cover;
    }
    .card-info {
        padding: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
    }
    .card-title {
        font-size: 14px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 6px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .card-author {
        font-size: 11px;
        color: #b0b0b0;
        margin-bottom: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .download-btn {
        background-color: #e50914;
        color: white;
        text-align: center;
        padding: 6px 10px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
        text-decoration: none;
        display: block;
        transition: background 0.2s;
    }
    .download-btn:hover {
        background-color: #f40612;
        color: white;
    }
    .scroll-btn {
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border: none;
        font-size: 24px;
        cursor: pointer;
        padding: 15px 10px;
        z-index: 10;
        border-radius: 5px;
        transition: background 0.2s;
        user-select: none;
    }
    .scroll-btn:hover {
        background-color: rgba(229, 9, 20, 0.9);
    }
</style>

<script>
function scrollCarousel(direction, trackId) {
    const track = document.getElementById(trackId);
    const scrollAmount = 400;
    if (direction === 'left') {
        if (track.scrollLeft <= 0) {
            track.scrollTo({ left: track.scrollWidth, behavior: 'smooth' }); // Bucle al final
        } else {
            track.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
    } else {
        if (track.scrollLeft + track.clientWidth >= track.scrollWidth - 5) {
            track.scrollTo({ left: 0, behavior: 'smooth' }); // Bucle al principio
        } else {
            track.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    }
}
</script>
""", unsafe_allow_html=True)

# Inicializar estado de sesión (Todos los libros asignados a Realidad Nacional por ahora)
if "libros" not in st.session_state:
    st.session_state.libros = [
        {"id": 1, "titulo": "Brics", "autor": "Dr. C. Roberto Muñoz González & Dr. C. Bonifácio Vissetaca", "portada": "brics.png", "archivo": "Brics.pdf", "categoria": "Realidad Nacional"},
        {"id": 2, "titulo": "Capitalismo actual", "autor": "Alejandro Dabat, Jorge Hernández & Canek Vega", "portada": "capitalismo.png", "archivo": "Capitalismo actual-Dabat.pdf", "categoria": "Realidad Nacional"},
        {"id": 3, "titulo": "Desigualdad", "autor": "Anastasio Ovejero", "portada": "desigualdad.png", "archivo": "Desigualdad-Ovejero.pdf", "categoria": "Realidad Nacional"},
        {"id": 4, "titulo": "El caso del Perú", "autor": "José Matos Mar", "portada": "casoperu.png", "archivo": "El caso del Perú.pdf", "categoria": "Realidad Nacional"},
        {"id": 5, "titulo": "Estado Nación e Identidad Nacional", "autor": "Sonia García Segura", "portada": "estadonacion.png", "archivo": "Estado Nación e Identidad Nacional.pdf", "categoria": "Realidad Nacional"},
        {"id": 6, "titulo": "Historia e Identidad del Perú", "autor": "Oswaldo Holguín Callo", "portada": "historia.png", "archivo": "Historia e Identidad del Perú.pdf", "categoria": "Realidad Nacional"},
        {"id": 7, "titulo": "La nueva corrupción en el Perú", "autor": "Óscar Ugarteche Galarza", "portada": "nuevacorrupcion.png", "archivo": "La nueva corrupción en el Perú.pdf", "categoria": "Realidad Nacional"},
        {"id": 8, "titulo": "Nuevo orden", "autor": "Juan José Palacios L.", "portada": "nuevoorden.png", "archivo": "Nuevo orden-Palacios.pdf", "categoria": "Realidad Nacional"},
        {"id": 9, "titulo": "Oligarquía en el Perú", "autor": "Dennis Gilbert", "portada": "oligarquia.png", "archivo": "Oligarquía en el Perú.pdf", "categoria": "Realidad Nacional"},
        {"id": 10, "titulo": "Realidad Peruana", "autor": "Abelardo Hurtado, Wadson Pinchi & Norman Coronel", "portada": "realidad.png", "archivo": "Realidad Peruana.pdf", "categoria": "Realidad Nacional"},
        {"id": 11, "titulo": "Sociedad de la información", "autor": "José Antonio Moreiro González", "portada": "info.png", "archivo": "Sociedad de la información-Moreiro.pdf", "categoria": "Realidad Nacional"},
        {"id": 12, "titulo": "Sociedad del conocimiento", "autor": "Adriana Marrero", "portada": "conocimiento.png", "archivo": "Sociedad del conocimiento-Marredo.pdf", "categoria": "Realidad Nacional"},
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
    st.header("Estante Principal")
    
    # Barra de búsqueda
    busqueda = st.text_input("🔍 Buscar por título o autor", "").lower()

    libros_filtrados = [
        l for l in st.session_state.libros
        if busqueda in l["titulo"].lower() or busqueda in l["autor"].lower()
    ]

    if not libros_filtrados:
        st.warning("No se encontraron libros que coincidan con la búsqueda.")
    else:
        # Renderizado único para la sección "Realidad Nacional"
        track_id = "track_realidad_nacional"
        
        cards_html = ""
        for libro in libros_filtrados:
            img_src = obtener_imagen_src(libro["portada"])
            pdf_link = obtener_pdf_link(libro["archivo"])
            cards_html += f"""
            <div class="netflix-card">
                <div>
                    <img src="{img_src}" alt="{libro['titulo']}">
                    <div class="card-info">
                        <div class="card-title" title="{libro['titulo']}">{libro['titulo']}</div>
                        <div class="card-author" title="{libro['autor']}">Autor: {libro['autor']}</div>
                    </div>
                </div>
                <div style="padding: 0 12px 12px 12px;">
                    <a class="download-btn" href="{pdf_link}" download="{libro['archivo']}">📥 Descargar PDF</a>
                </div>
            </div>
            """

        st.markdown(f"""
        <div class="main-container">
            <div class="section-title">🔥 Realidad Nacional</div>
            <div class="carousel-wrapper">
                <button class="scroll-btn" onclick="scrollCarousel('left', '{track_id}')">❮</button>
                <div class="carousel-track" id="{track_id}">
                    {cards_html}
                </div>
                <button class="scroll-btn" onclick="scrollCarousel('right', '{track_id}')">❯</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. SUGERIR APORTE
# -------------------------------------------------------------
elif menu == "Sugerir Aporte":
    st.header("Sube tu aporte para revisión")
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
                    "portada": "brics.png", # Imagen por defecto temporal
                    "archivo": archivo_subido.name,
                    "categoria": "Realidad Nacional"
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
