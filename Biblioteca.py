import os
import re
import base64
import streamlit as st
import streamlit.components.v1 as components

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


def extraer_id_drive(texto):
    """Acepta un ID de Drive 'pelado' o una URL completa
    (.../file/d/ID/view..., .../open?id=ID, .../uc?id=ID) y devuelve solo el ID."""
    if not texto:
        return None
    texto = texto.strip()
    match = re.search(r"/d/([-\w]{20,})", texto)
    if match:
        return match.group(1)
    match = re.search(r"[?&]id=([-\w]{20,})", texto)
    if match:
        return match.group(1)
    if re.fullmatch(r"[-\w]{20,}", texto):
        return texto
    return None


def url_descarga_drive(drive_id):
    return f"https://drive.google.com/uc?export=download&id={drive_id}"


def url_portada_drive(drive_id):
    # Miniatura generada automáticamente por Drive a partir de la 1a página del PDF.
    # Requiere que el archivo esté compartido como "Cualquier persona con el enlace".
    return f"https://drive.google.com/thumbnail?id={drive_id}&sz=w400"


def obtener_imagen_src(libro):
    """Prioridad: portada local subida > miniatura automática de Drive > por defecto."""
    nombre_archivo = libro.get("portada")
    if nombre_archivo:
        ruta = os.path.join(COVERS_DIR, nombre_archivo)
        if os.path.exists(ruta):
            ext = ruta.split(".")[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            b64 = archivo_a_base64(ruta)
            if b64:
                return f"data:{mime};base64,{b64}"
    if libro.get("drive_id"):
        return url_portada_drive(libro["drive_id"])
    return PORTADA_DEFECTO


def obtener_pdf_href(libro):
    """Prioridad: enlace de Google Drive > archivo local embebido > None (no disponible)."""
    if libro.get("drive_id"):
        return url_descarga_drive(libro["drive_id"]), True  # (href, es_externo)

    nombre_archivo = libro.get("archivo")
    if nombre_archivo:
        ruta = os.path.join(BOOKS_DIR, nombre_archivo)
        if os.path.exists(ruta) and os.path.getsize(ruta) <= MAX_PDF_EMBED_MB * 1024 * 1024:
            b64 = archivo_a_base64(ruta)
            if b64:
                return f"data:application/pdf;base64,{b64}", False

    return None, False


def escapar(texto):
    """Escapa comillas para insertar de forma segura dentro de atributos HTML."""
    return (texto or "").replace('"', "&quot;").replace("'", "&#39;")


# =============================================================
# ESTILOS GENERALES (sin JS — esto sí puede ir por st.markdown)
# =============================================================
st.markdown(
    """
<style>
    #MainMenu, footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================
# CARRUSEL ESTILO NETFLIX
#
# IMPORTANTE: este bloque se renderiza con components.html() y NO con
# st.markdown(unsafe_allow_html=True). Motivo del bug original: cuando el
# HTML se inyecta vía innerHTML (que es lo que hace st.markdown por dentro),
# los navegadores IGNORAN cualquier <script> por seguridad — nunca se
# ejecutaba, por eso los botones de flecha aparecían pero no hacían nada al
# hacer clic. components.html() sí crea un <iframe> con un documento real,
# donde el <script> se ejecuta con normalidad.
# =============================================================
CARRUSEL_CSS = """
<style>
    body { margin: 0; background: transparent; font-family: "Source Sans Pro", sans-serif; }
    .fila-container { margin-bottom: 30px; }
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
        gap: 6px;
        width: 100%;
        box-sizing: border-box;
    }
    .carousel-track {
        display: flex;
        flex: 1 1 0%;
        min-width: 0;
        overflow-x: auto;
        scroll-behavior: smooth;
        gap: 14px;
        padding: 6px 4px 14px 4px;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    .carousel-track::-webkit-scrollbar { display: none; }
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
    .download-btn:hover { background-color: #f6121d; }
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
    .scroll-btn:hover { background: rgba(229,9,20,0.9); }
</style>
"""

CARRUSEL_JS = """
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
"""

# =============================================================
# ESTADO INICIAL
# =============================================================
if "libros" not in st.session_state:
    st.session_state.libros = [
        {"id": 1, "titulo": "Brics", "autor": "Dr. C. Roberto Muñoz González & Dr. C. Bonifácio Vissetaca", "portada": "", "brics.png": "1rO9SnsctKcYeXg5mps5XM5x4fJU7wM1W", "categoria": "Realidad Nacional"},
        {"id": 2, "titulo": "Capitalismo actual", "autor": "Alejandro Dabat, Jorge Hernández & Canek Vega", "portada": "", "drive_id": "1YcngD-_DMw0qCyKqFjMlNUezoHa6bDPK", "categoria": "Realidad Nacional"},
        {"id": 3, "titulo": "Desigualdad", "autor": "Anastasio Ovejero", "portada": "", "drive_id": "18KcO5reez_VhgWcwRqxU-CwZ09HIS-sd", "categoria": "Realidad Nacional"},
        {"id": 4, "titulo": "El caso del Perú", "autor": "José Matos Mar", "portada": "", "drive_id": "1fKWKrK7Vc4J39qbzYLNHMw6uiKWMyoLU", "categoria": "Realidad Nacional"},
        {"id": 5, "titulo": "Estado Nación e Identidad Nacional", "autor": "Sonia García Segura", "portada": "", "drive_id": "11Vi0hbf7MggyvM9dX4tquhAK5M5fJ4Iv", "categoria": "Realidad Nacional"},
        {"id": 6, "titulo": "Historia e Identidad del Perú", "autor": "Oswaldo Holguín Callo", "portada": "", "drive_id": "1h0gKEvkmeYjkfPs47_46ysffhEXh4PEj", "categoria": "Realidad Nacional"},
        {"id": 7, "titulo": "La nueva corrupción en el Perú", "autor": "Óscar Ugarteche Galarza", "portada": "", "drive_id": "1kRBaRGFcB0UtFu3aRiVL9EOAJmLScidQ", "categoria": "Realidad Nacional"},
        {"id": 8, "titulo": "Nuevo orden", "autor": "Juan José Palacios L.", "portada": "", "drive_id": "1qlOkimhC8zLXCZdRmYoOx6cnM-Ilueom", "categoria": "Realidad Nacional"},
        # Antes faltaban estos 4 — ya completados.
        {"id": 9, "titulo": "Oligarquía en el Perú", "autor": "Dennis Gilbert", "portada": "", "drive_id": "1CA8_C63lZRcP2HoGdQFyVg552vJ2RKO3", "categoria": "Realidad Nacional"},
        {"id": 10, "titulo": "Realidad Peruana", "autor": "Abelardo Hurtado, Wadson Pinchi & Norman Coronel", "portada": "", "drive_id": "1Buf7l02S0cdnp2I84FilcUz7U7uV7Zmt", "categoria": "Realidad Nacional"},
        {"id": 11, "titulo": "Sociedad de la información", "autor": "José Antonio Moreiro González", "portada": "", "drive_id": "10FRdSCjI42zGR6CyqTRtFLz-aM4fI_Ed", "categoria": "Realidad Nacional"},
        {"id": 12, "titulo": "Sociedad del conocimiento", "autor": "Adriana Marrero", "portada": "", "drive_id": "1vssz4OIiQS5o2H9Cb5haRxBjLiwmuFsZ", "categoria": "Realidad Nacional"},
    ]

if "pendientes" not in st.session_state:
    st.session_state.pendientes = []

# El orden de esta lista es el orden en que se muestran las filas (como Netflix,
# no alfabético). Nuevas categorías se agregan al final automáticamente.
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
# 1. VER BIBLIOTECA (carrusel tipo Netflix)
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
        # Mantenemos el orden curado en session_state, no alfabético
        categorias_presentes = [
            c for c in st.session_state.orden_categorias
            if any(l["categoria"] == c for l in libros_filtrados)
        ]

        filas_html = ""
        for idx, categoria in enumerate(categorias_presentes):
            libros_cat = [l for l in libros_filtrados if l["categoria"] == categoria]
            track_id = f"track_{idx}"

            cards_html = ""
            for libro in libros_cat:
                img_src = obtener_imagen_src(libro)
                pdf_href, es_externo = obtener_pdf_href(libro)
                titulo = escapar(libro["titulo"])
                autor = escapar(libro["autor"])

                if not pdf_href:
                    boton = '<span class="download-btn disabled">Archivo no disponible</span>'
                elif es_externo:
                    # Enlace de Google Drive: se abre en pestaña nueva (el atributo
                    # "download" no funciona en enlaces de otro dominio).
                    boton = (
                        f'<a class="download-btn" href="{pdf_href}" target="_blank" '
                        f'rel="noopener">📥 Descargar PDF</a>'
                    )
                else:
                    boton = (
                        f'<a class="download-btn" href="{pdf_href}" '
                        f'download="{escapar(libro.get("archivo", "libro.pdf"))}">📥 Descargar PDF</a>'
                    )

                # onerror: si la miniatura de Google Drive falla en cargar (ocurre a
                # veces por bloqueo de hotlinking), se reemplaza por la portada por
                # defecto en vez de mostrar un ícono de imagen rota.
                cards_html += f"""
                <div class="netflix-card">
                    <img src="{img_src}" alt="{titulo}"
                         onerror="this.onerror=null;this.src='{PORTADA_DEFECTO}';">
                    <div class="card-info">
                        <div class="card-title" title="{titulo}">{titulo}</div>
                        <div class="card-author" title="{autor}">Autor: {autor}</div>
                        {boton}
                    </div>
                </div>
                """

            filas_html += f"""
            <div class="fila-container">
                <div class="fila-titulo">📌 {categoria}</div>
                <div class="carousel-wrapper">
                    <button class="scroll-btn" onclick="scrollCarousel('left', '{track_id}')">&#10094;</button>
                    <div class="carousel-track" id="{track_id}">
                        {cards_html}
                    </div>
                    <button class="scroll-btn" onclick="scrollCarousel('right', '{track_id}')">&#10095;</button>
                </div>
            </div>
            """

        html_completo = CARRUSEL_CSS + filas_html + CARRUSEL_JS
        # Altura del iframe: ~330px por fila + margen. scrolling=True actúa como
        # red de seguridad si el cálculo se queda corto (evita que se corte contenido).
        altura_estimada = 40 + len(categorias_presentes) * 335
        components.html(html_completo, height=altura_estimada, scrolling=True)

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

        st.caption("Puedes subir el PDF directamente, o pegar un enlace de Google Drive "
                    "(el archivo debe estar compartido como 'Cualquier persona con el enlace').")
        enlace_drive = st.text_input("Enlace de Google Drive (opcional)")
        archivo_pdf = st.file_uploader("O sube el archivo PDF", type=["pdf"])
        archivo_portada = st.file_uploader(
            "Sube la portada (opcional, si no se usa la miniatura automática de Drive)",
            type=["png", "jpg", "jpeg"],
        )

        enviado = st.form_submit_button("Enviar al Panel de Autor")

        if enviado:
            categoria_final = (
                nueva_categoria.strip()
                if opcion_categoria == "➕ Nueva categoría..."
                else opcion_categoria
            )
            drive_id_detectado = extraer_id_drive(enlace_drive)
            tiene_archivo = archivo_pdf is not None or drive_id_detectado is not None

            if not titulo or not autor or not categoria_final or not tiene_archivo:
                st.warning(
                    "Completa título, autor, categoría, y adjunta un PDF o pega un enlace "
                    "de Google Drive válido."
                )
            elif enlace_drive and not drive_id_detectado:
                st.error("No pude reconocer ese enlace de Google Drive. Revisa que sea correcto.")
            else:
                st.session_state.pendientes.append(
                    {
                        "id": siguiente_id(),
                        "titulo": titulo.strip(),
                        "autor": autor.strip(),
                        "categoria": categoria_final,
                        "drive_id": drive_id_detectado,
                        "archivo_bytes": archivo_pdf.getvalue() if archivo_pdf else None,
                        "archivo_nombre": archivo_pdf.name if archivo_pdf else None,
                        "portada_bytes": archivo_portada.getvalue() if archivo_portada else None,
                        "portada_nombre": archivo_portada.name if archivo_portada else None,
                    }
                )
                st.success("¡Aporte enviado con éxito! Quedará pendiente de aprobación.")

# -------------------------------------------------------------
# 3. PANEL DE AUTOR
# -------------------------------------------------------------
elif menu == "Panel de Autor":
    st.header("Panel de Moderación")

    st.subheader("Aportes pendientes de revisión")
    if not st.session_state.pendientes:
        st.info("No hay aportes pendientes en este momento. ¡Todo al día!")
    else:
        for i, aporte in enumerate(list(st.session_state.pendientes)):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**Título:** {aporte['titulo']}")
                    st.write(f"**Autor:** {aporte['autor']}")
                with col2:
                    st.write(f"**Categoría:** {aporte['categoria']}")
                    origen = "Google Drive" if aporte.get("drive_id") else aporte.get("archivo_nombre", "—")
                    st.write(f"**Origen del PDF:** {origen}")
                with col3:
                    if st.button("✅ Aprobar", key=f"aprobar_{aporte['id']}"):
                        # Guardar el PDF en disco solo si vino como archivo subido
                        nombre_archivo = ""
                        if aporte.get("archivo_bytes"):
                            nombre_archivo = aporte["archivo_nombre"]
                            ruta_pdf = os.path.join(BOOKS_DIR, nombre_archivo)
                            with open(ruta_pdf, "wb") as f:
                                f.write(aporte["archivo_bytes"])

                        # Guardar la portada en disco (si se subió)
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
                                "archivo": nombre_archivo,
                                "drive_id": aporte.get("drive_id"),
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
                colA, colB, colC = st.columns([4, 3, 1])
                with colA:
                    estado = "✅" if (libro.get("drive_id") or libro.get("archivo")) else "⚠️ sin PDF"
                    st.write(f"- **{libro['titulo']}** | *{libro['autor']}* {estado}")
                with colB:
                    nuevo_enlace = st.text_input(
                        "Enlace/ID de Drive",
                        value=libro.get("drive_id") or "",
                        key=f"drive_{libro['id']}",
                        label_visibility="collapsed",
                        placeholder="Pegar enlace o ID de Google Drive",
                    )
                    if nuevo_enlace and nuevo_enlace != (libro.get("drive_id") or ""):
                        nuevo_id = extraer_id_drive(nuevo_enlace)
                        if nuevo_id:
                            libro["drive_id"] = nuevo_id
                            st.rerun()
                        else:
                            st.error("Enlace no reconocido")
                with colC:
                    if st.button("🗑️", key=f"del_{libro['id']}"):
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
