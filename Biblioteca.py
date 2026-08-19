import os

import streamlit as st



# Configuración de la página

st.set_page_config(

    page_title="Biblioteca de Economía", page_icon="📚", layout="wide"

)



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

                # Contenedor con altura fija para evitar que se desalineen las líneas

                with st.container(height=520, border=True):

                    st.image(libro["portada"], use_container_width=True)

                    st.subheader(libro["titulo"])

                    st.write(f"**Autor:** {libro['autor']}")



                    # Botón interactivo y descarga real habilitada

                    if os.path.exists(libro["archivo"]):

                        with open(libro["archivo"], "rb") as archivo_pdf:

                            st.download_button(

                                label=f"📥 Descargar PDF",

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
