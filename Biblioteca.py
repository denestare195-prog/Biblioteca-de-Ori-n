import os
import base64
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Biblioteca de Economía", page_icon="📚", layout="wide"
)

# Funciones auxiliares para codificar archivos a Base64 de forma segura
def archivo_a_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def obtener_imagen_src(ruta):
    if ruta and os.path.exists(ruta):
        ext = ruta.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        b64 = archivo_a_base64(ruta)
        if b64:
            return f"data:{mime};base64,{b64}"
    # Imagen de respaldo por defecto si la portada no se encuentra
    return "https://picsum.photos/seed/economia/200/300"

def obtener_pdf_link(ruta):
    if ruta and os.path.exists(ruta):
        b64 = archivo_a_base64(ruta)
        if b64:
            return f"data:application/pdf;base64,{b64}"
    return "#"

# Estilos CSS y JavaScript para el carrusel horizontal con flechas y bucle infinito
st.markdown("""
<style>
    .main-container {
        padding: 10px 0;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
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
        gap: 16px;
        padding: 10px 5px;
        scrollbar-width: none;
    }
    .carousel-track::-webkit-scrollbar {
        display: none;
    }
    .netflix-card {
        flex: 0 0 170px;
        background-color: #1e1e1e;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
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
        height: 230px;
        object-fit: cover;
    }
    .card-info {
        padding: 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
    }
    .card-title {
        font-size: 13px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 4px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .card-author {
        font-size: 10px;
        color: #b0b0b0;
        margin-bottom: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .download-btn {
        background-color: #e50914;
        color: white;
        text-align: center;
        padding: 5px 8px;
        border-radius: 4px;
        font-size: 11px;
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
        font-size: 22px;
        cursor: pointer;
        padding: 15px 8px;
        z-index: 10;
        border-radius: 4px;
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
        if (track.scrollLeft <= 5) {
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

# Estado inicial de la biblioteca (Preparado para agregar más temas o títulos fácilmente)
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

# Título principal
st.title("📚 Biblioteca Interactiva de Economía")

# Menú lateral simplificado (Sin sugerir aporte)
menu = st.sidebar.selectbox(
    "Menú de Navegación", ["Ver Biblioteca", "Panel de Autor"]
)

# -------------------------------------------------------------
# 1. VER BIBLIOTECA
# -------------------------------------------------------------
if menu == "Ver Biblioteca":
    st.header("Estante de Libros")
    
    # Barra de búsqueda global
    busqueda = st.text_input("🔍 Buscar por título o autor", "").lower()

    libros_filtrados = [
        l for l in st.session_state.libros
        if busqueda in l["titulo"].lower() or busqueda in l["autor"].lower()
    ]

    if not libros_filtrados:
        st.warning("No se encontraron libros que coincidan con la búsqueda.")
    else:
        # Extraer dinámicamente las categorías (Cintas de temas) existentes
        categorias = sorted(list(set(l["categoria"] for l in libros_filtrados)))

        for idx, categoria in enumerate(categorias):
            libros_cat = [l for l in libros_filtrados if l["categoria"] == categoria]
            track_id = f"track_{idx}"
            
            cards_html = ""
            for libro in libros_cat:
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
                    <div style="padding: 0 10px 10px 10px;">
                        <a class="download-btn" href="{pdf_link}" download="{libro['archivo']}">📥 Descargar PDF</a>
                    </div>
                </div>
                """

            # Renderizar carrusel en bucle horizontal para cada categoría
            st.markdown(f"""
            <div class="main-container">
                <div class="section-title">📌 {categoria}</div>
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
# 2. PANEL DE AUTOR (Administración interna)
# -------------------------------------------------------------
elif menu == "Panel de Autor":
    st.header("Panel de Moderación y Gestión")
    st.write("Aquí puedes ver los libros actuales registrados en la plataforma.")
    
    for libro in st.session_state.libros:
        st.write(f"- **{libro['titulo']}** ({libro['categoria']}) - *{libro['autor']}*")
