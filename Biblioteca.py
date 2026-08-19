import os
import base64
import textwrap
import streamlit as st

# =============================================================
# CONFIGURACIÓN GENERAL
# =============================================================
st.set_page_config(
    page_title="Biblioteca de Economía", page_icon="📚", layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COVERS_DIR = os.path.join(BASE_DIR, "assets", "covers")
BOOKS_DIR = os.path.join(BASE_DIR, "assets", "books")
os.makedirs(COVERS_DIR, exist_ok=True)
os.makedirs(BOOKS_DIR, exist_ok=True)

PORTADA_DEFECTO = "https://placehold.co/220x320/181818/e50914?text=Sin+Portada"
MAX_PDF_EMBED_MB = 25  # límite de seguridad para incrustar PDF como data-uri


# =============================================================
# FUNCIONES AUXILIARES
# =============================================================
def archivo_a_base64(ruta):
    """Lee un archivo y lo devuelve en base64. Vacío si no existe."""
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except (FileNotFoundError, IsADirectoryError):
        return ""


def obtener_imagen_src(nombre_archivo):
    """Devuelve el src (data-uri) de la portada o una imagen por defecto."""
    if not nombre_archivo:
        return PORTADA_DEFECTO
    ruta = os.path.join(COVERS_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return PORTADA_DEFECTO
    ext = ruta.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    b64 = archivo_a_base64(ruta)
    return f"data:{mime};base64,{b64}" if b64 else PORTADA_DEFECTO


def obtener_pdf_href(nombre_archivo):
    """Devuelve un data-uri para descargar el PDF, o '#' si no aplica."""
    if not nombre_archivo:
        return "#"
    ruta = os.path.join(BOOKS_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return "#"
    if os.path.getsize(ruta) > MAX_PDF_EMBED_MB * 1024 * 1024:
        return "#"
    b64 = archivo_a_base64(ruta)
    return f"data:application/pdf;base64,{b64}" if b64 else "#"


def escapar(texto):
    """Escapa comillas para insertar de forma segura dentro de atributos HTML."""
    return (texto or "").replace('"', "&quot;").replace("'", "&#39;")


# =============================================================
# ESTILOS Y JS (carrusel horizontal estilo Netflix)
# =============================================================
st.markdown(textwrap.dedent("""
<style>
    #MainMenu, footer {visibility: hidden;}

    .fila-container {
        margin-bottom: 34px;
    }
    .fila-titulo {
        font-size: 21px;
        font-weight: 700;
        color: #ffffff;
        margin: 4px 0 10px 2px;
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
        gap: 14px;
        padding: 6px 4px 14px 4px;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    .carousel-track::-webkit-scrollbar {
        display: none;
    }
    .netflix-card {
        flex: 0 0 165px;
        background-color: #181818;
        border-radius: 6px;
        overflow: hidden;
        box-shadow: 0 3px 8px rgba(0,0,0,0.5);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 1px solid #262626;
        display: flex;
        flex-direction: column;
    }
    .netflix-card:hover {
        transform: scale(1.06);
        box-shadow: 0 8px 20px rgba(0,0,0,0.65);
        border-color: #e50914;
        z-index: 5;
    }
    .netflix-card img {
        width: 100%;
        height: 235px;
        object-fit: cover;
        display: block;
        background: #222;
    }
    .card-info {
        padding: 8px 9px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .card-title {
        font-size: 12.5px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.25;
        min-height: 30px;
    }
    .card-author {
        font-size: 10.5px;
        color: #9a9a9a;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.2;
        min-height: 24px;
    }
    .download-btn {
        margin-top: auto;
        background-color: #e50914;
        color: white !important;
        text-align: center;
        padding: 5px 6px;
        border-radius: 3px;
        font-size: 10.5px;
        font-weight: 700;
        text-decoration: none;
        display: block;
        transition: background 0.2s;
    }
    .download-btn:hover {
        background-color: #f6121d;
    }
    .download-btn.disabled {
        background-color: #3a3a3a;
        color: #888 !important;
        cursor: not-allowed;
        pointer-events: none;
    }
    .scroll-btn {
        background: rgba(20,20,20,0.85);
        color: white;
        border: none;
        font-size: 22px;
        cursor: pointer;
        padding: 0;
        width: 34px;
        height: 60px;
        z-index: 10;
        border-radius: 4px;
        flex-shrink: 0;
        transition: background 0.2s;
    }
    .scroll-btn:hover {
        background: rgba(229,9,20,0.9);
    }
</style>

<script>
function scrollCarousel(direction, trackId) {
    const track = document.getElementById(trackId);
    if (!track) return;
    const scrollAmount = track.clientWidth * 0.8;
    if (direction === 'left') {
        if (track.scrollLeft <= 5) {
            track.scrollTo({ left: track.scrollWidth, behavior: 'smooth' });
        } else {
            track.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
    } else {
        if (track.scrollLeft + track.clientWidth >= track.scrollWidth - 5) {
            track.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
            track.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
    }
}
</script>
"""), unsafe_allow_html=True)

# =============================================================
# ESTADO INICIAL
# =============================================================
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

if "orden_categorias" not in st.session_state:
    st.session_state.orden_categorias = ["Realidad Nacional"]


def registrar_categoria(categoria):
    if categoria and categoria not in st.session_state.orden_categorias:
        st.session_state.orden_categorias.append(categoria)


def siguiente_id():
    ids = [l["id"] for l in st.session_state.libros] + [p["id"] for p in st.session_state.pendientes]
    return max(ids, default=0) + 1


# =============================================================
# TÍTULO Y MENÚ
# =============================================================
st.title("📚 Biblioteca Interactiva de Economía")

menu = st.sidebar.selectbox(
    "Menú de Navegación", ["Ver Biblioteca", "Sugerir Aporte", "Panel de Autor"]
)

# -------------------------------------------------------------
# 1. VER BIBLIOTECA
# -------------------------------------------------------------
if menu == "Ver Biblioteca":
    busqueda = st.text_input("🔍 Buscar por título o autor", "").strip().lower()

    libros_filtrados = [
        l for l in st.session_state.libros
        if busqueda in l["titulo"].lower() or busqueda in l["autor"].lower()
    ]

    if not libros_filtrados:
        st.warning("No se encontraron libros que coincidan con la búsqueda.")
    else:
        categorias_presentes = [
            c for c in st.session_state.orden_categorias
            if any(l["categoria"] == c for l in libros_filtrados)
        ]

        for idx, categoria in enumerate(categorias_presentes):
            libros_cat = [l for l in libros_filtrados if l["categoria"] == categoria]
            track_id = f"track_{idx}"

            cards_html = ""
            for libro in libros_cat:
                img_src = obtener_imagen_src(libro.get("portada", ""))
                pdf_href = obtener_pdf_href(libro.get("archivo", ""))
                titulo = escapar(libro["titulo"])
                autor = escapar(libro["autor"])

                if pdf_href == "#":
                    boton = '<span class="download-btn disabled">Archivo no disponible</span>'
                else:
                    boton = (
                        f'<a class="download-btn" href="{pdf_href}" '
                        f'download="{escapar(libro.get("archivo", "libro.pdf"))}">📥 Descargar PDF</a>'
                    )

                cards_html += f"""
                <div class="netflix-card">
                    <img src="{img_src}" alt="{titulo}">
                    <div class="card-info">
                        <div class="card-title" title="{titulo}">{titulo}</div>
                        <div class="card-author" title="{autor}">Autor: {autor}</div>
                        {boton}
                    </div>
                </div>
                """

            st.markdown(textwrap.dedent(f"""
                <div class="fila-container">
                    <div class="fila-titulo">📌 {categoria}</div>
                    <div class="carousel-wrapper">
                        <button class="scroll-btn" onclick="scrollCarousel('left', '{track_id}')">❮</button>
                        <div class="carousel-track" id="{track_id}">
                            {cards_html}
                        </div>
                        <button class="scroll-btn" onclick="scrollCarousel('right', '{track_id}')">❯</button>
                    </div>
                </div>
                """), unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. SUGERIR APORTE
# -------------------------------------------------------------
elif menu == "Sugerir Aporte":
    st.header("Sube tu aporte para revisión")
    st.write("Comparte documentos o libros académicos con la comunidad.")

    categorias_existentes = st.session_state.orden_categorias

    with st.form("form_aporte", clear_on_submit=True):
        titulo = st.text_input("Título del libro o documento")
        autor = st.text_input("Autor")

        opcion_categoria = st.selectbox(
            "Categoría (fila del catálogo)",
            categorias_existentes + ["➕ Nueva categoría..."],
        )
        nueva_categoria = ""
        if opcion_categoria == "➕ Nueva categoría...":
            nueva_categoria = st.text_input("Nombre de la nueva categoría")

        archivo_pdf = st.file_uploader("Sube el archivo PDF", type=["pdf"])
        archivo_portada = st.file_uploader(
            "Sube la portada (opcional)", type=["png", "jpg", "jpeg"]
        )

        enviado = st.form_submit_button("Enviar al Panel de Autor")

        if enviado:
            categoria_final = (
                nueva_categoria.strip()
                if opcion_categoria == "➕ Nueva categoría..."
                else opcion_categoria
            )
            if titulo and autor and archivo_pdf and categoria_final:
                st.session_state.pendientes.append(
                    {
                        "id": siguiente_id(),
                        "titulo": titulo.strip(),
                        "autor": autor.strip(),
                        "categoria": categoria_final,
                        "archivo_bytes": archivo_pdf.getvalue(),
                        "archivo_nombre": archivo_pdf.name,
                        "portada_bytes": archivo_portada.getvalue() if archivo_portada else None,
                        "portada_nombre": archivo_portada.name if archivo_portada else None,
                    }
                )
                st.success("¡Aporte enviado con éxito! Quedará pendiente de aprobación.")
            else:
                st.warning(
                    "Completa título, autor, categoría y adjunta el PDF antes de enviar."
                )

# -------------------------------------------------------------
# 3. PANEL DE AUTOR
# -------------------------------------------------------------
elif menu == "Panel de Autor":
    st.header("Panel de Moderación")

    st.subheader("Aportes pendientes de revisión")
    if not st.session_state.pendientes:
        st.info("No hay aportes pendientes en este momento. ¡Todo al día!")
    else:
        for aporte in list(st.session_state.pendientes):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**Título:** {aporte['titulo']}")
                    st.write(f"**Autor:** {aporte['autor']}")
                with col2:
                    st.write(f"**Categoría:** {aporte['categoria']}")
                    st.write(f"**Archivo:** {aporte['archivo_nombre']}")
                with col3:
                    if st.button("✅ Aprobar", key=f"aprobar_{aporte['id']}"):
                        ruta_pdf = os.path.join(BOOKS_DIR, aporte["archivo_nombre"])
                        with open(ruta_pdf, "wb") as f:
                            f.write(aporte["archivo_bytes"])

                        nombre_portada = ""
                        if aporte.get("portada_bytes"):
                            nombre_portada = aporte["portada_nombre"]
                            ruta_portada = os.path.join(COVERS_DIR, nombre_portada)
                            with open(ruta_portada, "wb") as f:
                                f.write(aporte["portada_bytes"])

                        registrar_categoria(aporte["categoria"])
                        st.session_state.libros.append(
                            {
                                "id": aporte["id"],
                                "titulo": aporte["titulo"],
                                "autor": aporte["autor"],
                                "portada": nombre_portada,
                                "archivo": aporte["archivo_nombre"],
                                "categoria": aporte["categoria"],
                            }
                        )
                        st.session_state.pendientes = [
                            p for p in st.session_state.pendientes if p["id"] != aporte["id"]
                        ]
                        st.success(f"¡Aprobado: {aporte['titulo']}!")
                        st.rerun()

                    if st.button("❌ Rechazar", key=f"rechazar_{aporte['id']}"):
                        st.session_state.pendientes = [
                            p for p in st.session_state.pendientes if p["id"] != aporte["id"]
                        ]
                        st.warning("Aporte rechazado.")
                        st.rerun()

    st.divider()
    st.subheader("Libros registrados actualmente")
    for categoria in st.session_state.orden_categorias:
        libros_cat = [l for l in st.session_state.libros if l["categoria"] == categoria]
        if not libros_cat:
            continue
        with st.expander(f"📌 {categoria} ({len(libros_cat)})"):
            for libro in libros_cat:
                colA, colB = st.columns([5, 1])
                with colA:
                    st.write(f"- **{libro['titulo']}** | *{libro['autor']}*")
                with colB:
                    if st.button("🗑️ Eliminar", key=f"del_{libro['id']}"):
                        st.session_state.libros = [
                            l for l in st.session_state.libros if l["id"] != libro["id"]
                        ]
                        st.rerun()

    st.divider()
    st.subheader("Gestionar categorías")
    st.caption("El orden de esta lista define el orden de las filas en 'Ver Biblioteca'.")
    for i, cat in enumerate(st.session_state.orden_categorias):
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.write(cat)
        if c2.button("⬆️", key=f"up_{i}") and i > 0:
            orden = st.session_state.orden_categorias
            orden[i - 1], orden[i] = orden[i], orden[i - 1]
            st.rerun()
        if c3.button("⬇️", key=f"down_{i}") and i < len(st.session_state.orden_categorias) - 1:
            orden = st.session_state.orden_categorias
            orden[i + 1], orden[i] = orden[i], orden[i + 1]
            st.rerun()
        en_uso = any(l["categoria"] == cat for l in st.session_state.libros)
        if c4.button("🗑️", key=f"delcat_{i}", disabled=en_uso):
            st.session_state.orden_categorias.pop(i)
            st.rerun()

    nueva_cat_admin = st.text_input("Agregar nueva categoría vacía (fila nueva)")
    if st.button("➕ Agregar categoría") and nueva_cat_admin.strip():
        registrar_categoria(nueva_cat_admin.strip())
        st.rerun()
