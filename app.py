import streamlit as st

from src.estilos import aplicar_estilos

st.set_page_config(
    page_title="Dashboard GKAS",
    page_icon=":material/dashboard:",
    layout="wide",
)

paginas = {
    "General": [
        st.Page("inicio.py", title="Inicio", icon=":material/home:", default=True),
        st.Page("pages/01_resumen.py", title="Resumen", icon=":material/summarize:", url_path="resumen"),
    ],
    "Detalle": [
        st.Page("pages/02_estudiantes.py", title="Estudiantes", icon=":material/groups:", url_path="estudiantes"),
        st.Page("pages/04_cancelaciones.py", title="Cancelaciones", icon=":material/event_busy:", url_path="cancelaciones"),
        st.Page("pages/05_aulas.py", title="Aulas", icon=":material/meeting_room:", url_path="aulas"),
        st.Page("pages/06_notas.py", title="Notas", icon=":material/grading:", url_path="notas"),
        st.Page("pages/07_reposiciones.py", title="Reposiciones", icon=":material/event_repeat:", url_path="reposiciones"),
        st.Page("pages/08_seguimiento.py", title="Seguimiento", icon=":material/trending_up:", url_path="seguimiento"),
    ],
}

pagina = st.navigation(paginas)
aplicar_estilos(pagina.title)
pagina.run()