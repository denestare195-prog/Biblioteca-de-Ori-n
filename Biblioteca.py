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
        {"id": 1, "titulo": "Brics", "autor": "Dr. C. Roberto Muñoz González & Dr. C. Bonifácio Vissetaca", "portada": "", "drive_id": "1rO9SnsctKcYeXg5mps5XM5x4fJU7wM1W", "categoria": "Realidad Nacional"},
        {"id": 2, "titulo": "Capitalismo actual", "autor": "Alejandro Dabat, Jorge Hernández & Canek Vega", "portada": "", "drive_id": "1YcngD-_DMw0qCyKqFjMlNUezoHa6bDPK", "categoria": "Realidad Nacional"},
        {"id": 3, "titulo": "Desigualdad", "autor": "Anastasio Ovejero", "portada": "", "drive_id": "18KcO5reez_VhgWcwRqxU-CwZ09HIS-sd", "categoria": "Realidad Nacional"},
        {"id": 4, "titulo": "El caso del Perú", "autor": "José Matos Mar", "portada": "", "drive_id": "1fKWKrK7Vc4J39qbzYLNHMw6uiKWMyoLU", "categoria": "Realidad Nacional"},
        {"id": 5, "titulo": "Estado Nación e Identidad Nacional", "autor": "Sonia García Segura", "portada": "", "drive_id": "11Vi0hbf7MggyvM9dX4tquhAK5M5fJ4Iv", "categoria": "Realidad Nacional"},
        {"id": 6, "titulo": "Historia e Identidad del Perú", "autor": "Oswaldo Holguín Callo", "portada": "", "drive_id": "1h0gKEvkmeYjkfPs47_46ysffhEXh4PEj", "categoria": "Realidad Nacional"},
        {"id": 7, "titulo": "La nueva corrupción en el Perú", "autor": "Óscar Ugarteche Galarza", "portada": "", "drive_id": "1kRBaRGFcB0UtFu3aRiVL9EOAJmLScidQ", "categoria": "Realidad Nacional"},
        {"id": 8, "titulo": "Nuevo orden", "autor": "Juan José Palacios L.", "portada": "", "drive_id": "1qlOkimhC8zLXCZdRmYoOx6cnM-Ilueom", "categoria": "Realidad Nacional"},
        {"id": 9, "titulo": "Oligarquía en el Perú", "autor": "Dennis Gilbert", "portada": "", "drive_id": "1CA8_C63lZRcP2HoGdQFyVg552vJ2RKO3", "categoria": "Realidad Nacional"},
        {"id": 10, "titulo": "Realidad Peruana", "autor": "Abelardo Hurtado, Wadson Pinchi & Norman Coronel", "portada": "", "drive_id": "1Buf7l02S0cdnp2I84FilcUz7U7uV7Zmt", "categoria": "Realidad Nacional"},
        {"id": 11, "titulo": "Sociedad de la información", "autor": "José Antonio Moreiro González", "portada": "", "drive_id": "10FRdSCjI42zGR6CyqTRtFLz-aM4fI_Ed", "categoria": "Realidad Nacional"},
        {"id": 12, "titulo": "Sociedad del conocimiento", "autor": "Adriana Marrero", "portada": "", "drive_id": "1vssz4OIiQS5o2H9Cb5haRxBjLiwmuFsZ", "categoria": "Realidad Nacional"},
        # Categoría: Economía Política
        {"id": 13, "titulo": "El arte de la manipulación política", "autor": "Josep M. Colomer", "portada": "", "drive_id": "10cdSfPGQsvlMvTy6fKKmeUlYQosY8SX4", "categoria": "Economía Política"},
        {"id": 14, "titulo": "Democracia y participación", "autor": "Boaventura de Sousa Santos", "portada": "", "drive_id": "1KTSn63XwP7D3CoGDOCzLIC3vdgX6a6hC", "categoria": "Economía Política"},
        {"id": 15, "titulo": "Derecha e Izquierda: Razones y Significados de una Distinción", "autor": "Norberto Bobbio", "portada": "", "drive_id": "1k1eCfIu6a2Ar4v7OWYuKOFN6_oiadZvo", "categoria": "Economía Política"},
        {"id": 16, "titulo": "El Político y El Científico", "autor": "Max Weber", "portada": "", "drive_id": "1sCPyplbyr2Y_1DnKlwP-vkv18CUAK7v2", "categoria": "Economía Política"},
        {"id": 17, "titulo": "Ensayos de Mercadotecnia Política", "autor": "Pedro Barrientos Felipa", "portada": "", "drive_id": "1EBf8Iqtl8rnJyCwO2ORLASReAkEbJwbj", "categoria": "Economía Política"},
        {"id": 18, "titulo": "Gramsci", "autor": "Gramsci", "portada": "", "drive_id": "1oE82b6_vTquHjWQJIwd3m_7yHHKXDAxe", "categoria": "Economía Política"},
        {"id": 19, "titulo": "Historia y ciencias políticas", "autor": "Luis Alberto de la Garza", "portada": "", "drive_id": "10cA6A_ecG5IY2Oz8MGf_cFCVm4-pLW1w", "categoria": "Economía Política"},
        {"id": 20, "titulo": "La isla de los pingüinos", "autor": "Anatole France", "portada": "", "drive_id": "1M9ovCb1mOyv7QCb3V0X284t-mGU-9iQP", "categoria": "Economía Política"},
        {"id": 21, "titulo": "La política por dentro", "autor": "Rafael Roncagliolo & Carlos Meléndez", "portada": "", "drive_id": "134KIes4ZG1RhyAyEHcWCV1pWAcrdHOys", "categoria": "Economía Política"},
        {"id": 22, "titulo": "La Teoría de las Formas de Gobierno en la historia del pensamiento político", "autor": "Norberto Bobbio", "portada": "", "drive_id": "1qZtR1B0-q3HJvdVJfEQbXNj2B9O43IST", "categoria": "Economía Política"},
        {"id": 23, "titulo": "Manual de Campaña - Teoría y práctica de la persuasión electoral", "autor": "Mario Martínez Silva & Roberto Salcedo Aquino", "portada": "", "drive_id": "1z3PJhNd3MVyde85DGiJbFT2tt4ydWyFM", "categoria": "Economía Política"},
        {"id": 24, "titulo": "Manual de Ciencias Políticas", "autor": "Juan Manuel Abal Medina", "portada": "", "drive_id": "13Y_FCvhsuwhAqRc19Jk1rYAytZlpkofQ", "categoria": "Economía Política"},
        {"id": 25, "titulo": "Manual de Ciencia Política", "autor": "Miquel Caminal Badia", "portada": "", "drive_id": "1KaARp9Jns0Tc73HX0IV8kfte99XXDEAB", "categoria": "Economía Política"},
        {"id": 26, "titulo": "Manual de introducción a la ciencia política", "autor": "José Cazorla Pérez", "portada": "", "drive_id": "11fZJAjc26uUmIc7GKbLuoDhmTLvT4Lij", "categoria": "Economía Política"},
        {"id": 27, "titulo": "Política, Economía y Política Económica", "autor": "Leopoldo Fergusson", "portada": "", "drive_id": "19rndO0jN-Zzi-3qYKH2pUfuORHH9ZjlU", "categoria": "Economía Política"},
        {"id": 28, "titulo": "¿Qué es la democracia?", "autor": "Giovanni Sartori", "portada": "", "drive_id": "1QPBSE3d1wLVTIR8yjZ_Vsbr2PSf4GWPJ", "categoria": "Economía Política"},
        {"id": 29, "titulo": "Routledge Dictionary of Politics", "autor": "David Robertson", "portada": "", "drive_id": "1E8AYdQUq76DEIEjmCMAMAYDQjZJCc5WX", "categoria": "Economía Política"},
        # Categoría: Estadística   
        {"id": 30, "titulo": "Estadística para administración y economía", "autor": "Anderson, Sweeney, Williams", "portada": "", "drive_id": "1O_lMyCxWiXHCdzveMq-eoSiM-EtRANt6", "categoria": "Estadística"},
        {"id": 31, "titulo": "Ciencia de datos", "autor": "Joel Grus", "portada": "", "drive_id": "1Ymg-Y3naCRfMVohF567Vs6WDpVe_jV9U", "categoria": "Estadística"},
        {"id": 32, "titulo": "Estadística aplicada a administración y economía", "autor": "Leonard Kazmier & Alfredo Díaz Mata", "portada": "", "drive_id": "1AJtZ6VkaxTo4d33ant3qkVls7rqYkI1m", "categoria": "Estadística"},
        {"id": 33, "titulo": "Estadística aplicada a los negocios y la economía", "autor": "Douglas A. Lind, William G. Marchal & Samuel A. Wathen", "portada": "", "drive_id": "1o9B4sbe111_MwPyWz2QLWKPOPUSrekjL", "categoria": "Estadística"},
        {"id": 34, "titulo": "Estadística descriptiva aplicada en Python", "autor": "Marcelo Bernavé Chancusig López, Guido Euclides Yauli Chicaiza, Guadalupe de las Mercedes López Castillo, José Antonio Andrade Valencia & Jhon Eduardo López Velasco", "portada": "", "drive_id": "171ysh9W0c9adGUITjLROjGmDMDKvN3v5", "categoria": "Estadística"},
        {"id": 35, "titulo": "Estadística para administración y economía", "autor": "Paul Newbold, William L. Carlson & Betty M. Thorne", "portada": "", "drive_id": "16sSIRNsS86JvrTld980BDN2oxmcFmOzo", "categoria": "Estadística"},
        {"id": 36, "titulo": "Estadística para ingenieros y científicos", "autor": "William Navidi", "portada": "", "drive_id": "1FwUOkxIHUMWMRTtuHBFyVCrd-SPb4G-1", "categoria": "Estadística"},
        {"id": 37, "titulo": "Un primer vistazo a la probabilidad", "autor": "Hildebrand", "portada": "", "drive_id": "1rHlfIJPxFYJqFzI1zC2Ix0OBwZXWr0cW", "categoria": "Estadística"},
        {"id": 38, "titulo": "Estadística para administración", "autor": "Levin, Rubin, Banderas del Valle & Gómez", "portada": "", "drive_id": "1ulGQM7eJaWESgY3I2j_Xf2Yr6NOn0AnD", "categoria": "Estadística"},
        {"id": 39, "titulo": "Manual de estadística aplicada", "autor": "Jorge Córdova Egocheaga", "portada": "", "drive_id": "1Ju5g4NLSUBm300PNqXmTqf67gFXpULqc", "categoria": "Estadística"},
        {"id": 40, "titulo": "Estadística", "autor": "Mario F. Triola", "portada": "", "drive_id": "1MrGYiXerNsOQzhl5hnBnv9Uc0W2IVxPf", "categoria": "Estadística"},
        {"id": 41, "titulo": "Probabilidad e inferencia estadística", "autor": "Rufino Moya C. & Gregorio Saravia A.", "portada": "", "drive_id": "1YcGw3jK-vSqcg6Ksn5V4EF6ESJC8WOig", "categoria": "Estadística"},
        {"id": 42, "titulo": "Procesamiento de datos y análisis utilizando SPSS", "autor": "Maria Belén Castañeda, Alberto F. Cabrera, Yadira Navarro & Wietse de Vries", "portada": "", "drive_id": "1O7EbulQf4RzmzvIfcmdfq0nqbd9juHlc", "categoria": "Estadística"},
        {"id": 43, "titulo": "Estadística aplicada a los negocios y la economía (3.ª ed.)", "autor": "Allen L. Webster", "portada": "", "drive_id": "1gph4sFhogzhVPRfkz4E92cfye_yKFepe", "categoria": "Estadística"},
        # Categoría: Microeconomía
        {"id": 44, "titulo": "Análisis microeconómico", "autor": "Hal R. Varian", "portada": "", "drive_id": "177QlcTiEKZmWh_lUWb04RsVsO5Rn0l7s", "categoria": "Microeconomía"},
        {"id": 45, "titulo": "Microeconomía intermedia (8.ª edición)", "autor": "Hal R. Varian", "portada": "", "drive_id": "1tVkDiHMDsgmxbXObY_KdTsAiZpsgD4qR", "categoria": "Microeconomía"},
        {"id": 46, "titulo": "Microeconomía intermedia: Un enfoque actual", "autor": "Hal R. Varian", "portada": "", "drive_id": "1LiB9vzwSNoGLpCRDNBkqxG_som1jg1gP", "categoria": "Microeconomía"},
        {"id": 47, "titulo": "Microeconomía (8.ª edición)", "autor": "Robert S. Pindyck & Daniel L. Rubinfeld", "portada": "", "drive_id": "1PIa-dPTi2hRMYGmMGrjxRKtrPmTUQp2C", "categoria": "Microeconomía"},
        {"id": 48, "titulo": "Microeconomía para productores", "autor": "Cecilia Garavito Masalías", "portada": "", "drive_id": "12u8E94qey_ElXH7fLNB_WV6hJg-9YtYJ", "categoria": "Microeconomía"},
        {"id": 49, "titulo": "Microeconomía para Latinoamérica", "autor": "Michael Parkin", "portada": "", "drive_id": "12u8E94qey_ElXH7fLNB_WV6hJg-9YtYJ", "categoria": "Microeconomía"},
        {"id": 50, "titulo": "Microeconomía (7.ª edición)", "autor": "Robert S. Pindyck & Daniel L. Rubinfeld", "portada": "", "drive_id": "11ZwsCjMuvQQyZa3D8x0ykhnzNy1oO2Oc", "categoria": "Microeconomía"},
        {"id": 51, "titulo": "Microeconomía", "autor": "Dominick Salvatore", "portada": "", "drive_id": "1lEDvBY--T0l-upKUZgdJEm91xY0lz-Sk", "categoria": "Microeconomía"},
        {"id": 52, "titulo": "Teoría microeconómica: Principios básicos y ampliaciones (9.ª ed.)", "autor": "Walter Nicholson", "portada": "", "drive_id": "1A8hQVqmRsLOo542ewYORZN7m60wJCv7S", "categoria": "Microeconomía"},
        {"id": 53, "titulo": "Teoría microeconómica (11.ª edición)", "autor": "Walter Nicholson & Christopher Snyder", "portada": "", "drive_id": "1B3x8Kfs02EwPqS0t8F7JbYGrwSFQVrZc", "categoria": "Microeconomía"}
]
if "pendientes" not in st.session_state:
    st.session_state.pendientes = []

# El orden de esta lista es el orden en que se muestran las filas (como Netflix,
# no alfabético). Nuevas categorías se agregan al final automáticamente.
if "orden_categorias" not in st.session_state:
    st.session_state.orden_categorias = ["Realidad Nacional", "Economía Política","Estadística","Microeconomía"]


def registrar_categoria(categoria):
    if categoria and categoria not in st.session_state.orden_categorias:
        st.session_state.orden_categorias.append(categoria)


def siguiente_id():
    ids = [l["id"] for l in st.session_state.libros] + [p["id"] for p in st.session_state.pendientes]
    return max(ids, default=0) + 1


# =============================================================
# TÍTULO Y MENÚ
# =============================================================
st.title("📚✨ Biblioteca de Orión")

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
