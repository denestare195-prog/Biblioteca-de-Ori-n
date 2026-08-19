# 📚 Biblioteca Interactiva de Economía

App en Streamlit con catálogo estilo Netflix: cada categoría se muestra como
una fila con scroll horizontal (tarjetas con portada, autor y botón de
descarga), y se pueden agregar tantas filas/categorías como quieras.

## Qué se corrigió respecto al intento anterior
- **Orden de categorías fijo (no alfabético):** antes `sorted(set(...))`
  reordenaba las filas cada vez alfabéticamente; ahora hay una lista
  `orden_categorias` en `session_state` que define el orden real, como en
  Netflix, y se puede reordenar con flechas ⬆️⬇️ desde el Panel de Autor.
- **Archivos organizados:** portadas van en `assets/covers/` y PDFs en
  `assets/books/`, en vez de rutas sueltas en la raíz del proyecto (evita
  colisiones de nombres y hace el repo más limpio).
- **Sin errores si falta un archivo:** si una portada o PDF no existe, se
  muestra una portada por defecto o un botón "Archivo no disponible" en vez
  de romper la app.
- **Botón de descarga con límite de tamaño:** PDFs más pesados que 25 MB no
  se incrustan como base64 (evita que el navegador se cuelgue); ese límite es
  ajustable con `MAX_PDF_EMBED_MB` en `app.py`.
- **Escapado de HTML:** los títulos/autores se escapan antes de insertarse en
  el HTML del carrusel, evitando que comillas rompan el layout.
- **Flujo completo de aportes:** "Sugerir Aporte" ahora permite subir PDF +
  portada + elegir o crear categoría; "Panel de Autor" aprueba (guarda los
  archivos en disco y los agrega al catálogo) o rechaza.
- **Gestión de categorías:** agregar, reordenar o eliminar categorías (solo
  si no tienen libros asignados) desde el Panel de Autor.

## Estructura del proyecto
```
biblioteca/
├── app.py
├── requirements.txt
├── README.md
└── assets/
    ├── covers/   # portadas (.png / .jpg)
    └── books/    # PDFs de los libros
```

## Cómo correrlo localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo subirlo a GitHub y desplegarlo
1. Crea un repositorio nuevo en GitHub.
2. Sube esta carpeta completa (`app.py`, `requirements.txt`, `assets/`).
3. Coloca tus portadas en `assets/covers/` y tus PDFs en `assets/books/`
   con los mismos nombres que usaste en el diccionario `libros` dentro de
   `app.py` (o súbelos directamente desde "Sugerir Aporte" → "Panel de
   Autor" una vez la app esté corriendo).
4. Para desplegar gratis: ve a [share.streamlit.io](https://share.streamlit.io),
   conecta tu repo de GitHub y selecciona `app.py` como archivo principal.

## Notas
- Los datos (libros, pendientes, categorías) viven en `st.session_state`,
  así que **se reinician si reinicias la app** (excepto los archivos ya
  guardados en `assets/`, que si persisten en disco). Si necesitas que el
  catálogo persista entre reinicios sin depender de la sesión, el siguiente
  paso natural sería guardar la lista `libros` en un archivo JSON o una base
  de datos (SQLite) en vez de solo en memoria — puedo ayudarte a agregar eso
  si lo necesitas.
