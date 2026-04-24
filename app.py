import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
from collections import Counter

st.set_page_config(page_title="Entre dudas y decisiones", page_icon="∫", layout="wide")

DATA_PATH = Path("respuestas_evento_mujer_matematica.csv")

PREGUNTAS = {
    "decision_clave": "¿Qué decisión marcó un antes y un después en tu trayectoria?",
    "como_decidiste": "¿Cómo tomaste esa decisión? ¿Qué factores consideraste?",
    "duda": "¿En qué momento dudaste de continuar en matemáticas y por qué?",
    "que_te_ayudo": "¿Qué te ayudó a seguir o a redefinir tu camino?",
    "obstaculo": "¿Qué obstáculo significativo enfrentaste en tu formación o ejercicio profesional?",
    "afrontamiento": "¿Cómo lo afrontaste o qué aprendiste de esa experiencia?",
    "error_formativo": "¿Hay alguna decisión que no haya resultado como esperabas? ¿Qué aprendiste de ello?",
    "trayectoria": "¿Tu camino profesional ha sido distinto a lo que imaginabas? ¿En qué sentido?",
    "criterio": "¿Qué criterio o principio utilizas hoy para tomar decisiones importantes?",
    "saber_estudiante": "¿Qué te hubiera gustado saber cuando eras estudiante?"
}

COLUMNAS = ["timestamp", "nombre", "anonima", "rol", "institucion", *PREGUNTAS.keys(), "consentimiento"]

STOPWORDS = set("""
a ante bajo con contra de desde durante en entre hacia hasta para por según sin sobre tras y o u e la las el los lo
un una unos unas al del que qué se me mi mis tu tus su sus es era fue fui fueron soy somos son ser estar estoy estaba
como cómo cuando cuándo donde dónde porque porqué pero mas más no sí si ya muy algo alguien todo toda todos todas esto
esta este estas estos ese esa eso esas esos ahí aqui aquí alli allí también tan tanto tanta tener tuve tuvo tenido he ha
han hay hacer hace hizo hice poder puedo pude puede pueden deber debe deben cada cual cuáles quien quién quienes quiénes
""".split())

def inicializar_csv():
    if not DATA_PATH.exists():
        pd.DataFrame(columns=COLUMNAS).to_csv(DATA_PATH, index=False, encoding="utf-8-sig")

def cargar_datos():
    inicializar_csv()
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")

def guardar_respuesta(respuesta):
    df = cargar_datos()
    df = pd.concat([df, pd.DataFrame([respuesta])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")

def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = re.sub(r"[^a-záéíóúüñ\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def contar_palabras(series_texto, top_n=20):
    texto_total = " ".join(limpiar_texto(x) for x in series_texto.dropna())
    palabras = [p for p in texto_total.split() if len(p) > 3 and p not in STOPWORDS]
    return pd.DataFrame(Counter(palabras).most_common(top_n), columns=["palabra", "frecuencia"])

def texto_completo_por_fila(row):
    partes = []
    for k, pregunta in PREGUNTAS.items():
        respuesta = row.get(k, "")
        if isinstance(respuesta, str) and respuesta.strip() and respuesta.strip().lower() != "nan":
            partes.append(f"**{pregunta}**\n\n{respuesta.strip()}")
    return "\n\n---\n\n".join(partes)

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.main-title { font-size: 2.35rem; font-weight: 750; margin-bottom: 0.2rem; color: #3d3329; }
.subtitle { font-size: 1.1rem; color: #6b5b4a; margin-bottom: 1.5rem; }
.note-box { background-color: #f5efe4; border-left: 5px solid #a87332; padding: 1rem 1.2rem; border-radius: 0.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Menú")
pagina = st.sidebar.radio("Selecciona una sección", ["Formulario", "Dashboard", "Exportar datos"])

if pagina == "Formulario":
    st.markdown('<div class="main-title">Entre dudas y decisiones: ser mujer matemática</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Formulario para profesoras y egresadas · Experiencias que orientan trayectorias</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="note-box">
    Este formulario recopila experiencias reales para enriquecer la dinámica de cierre del evento.
    La participación puede ser anónima. Si compartes una experiencia adversa, te pedimos acompañarla
    de un aprendizaje, estrategia de afrontamiento o reflexión que pueda orientar a otras estudiantes.
    </div>
    """, unsafe_allow_html=True)

    with st.form("formulario_experiencias", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            anonima = st.checkbox("Deseo que mi participación sea anónima")
            nombre = st.text_input("Nombre completo", disabled=anonima)
            rol = st.selectbox("Rol", ["Profesora", "Egresada", "Profesora y egresada", "Otra"])
        with col2:
            institucion = st.text_input("Institución o adscripción (opcional)")

        st.divider()
        st.subheader("Preguntas guía")
        st.caption("Puedes responder todas o solo aquellas en las que desees participar.")

        respuestas = {}
        for key, pregunta in PREGUNTAS.items():
            respuestas[key] = st.text_area(pregunta, height=90)

        consentimiento = st.checkbox("Autorizo el uso de este testimonio con fines académicos y de difusión del evento.")
        enviar = st.form_submit_button("Enviar participación")

        if enviar:
            if not consentimiento:
                st.error("Para enviar el formulario es necesario aceptar el consentimiento de uso.")
            elif not any(v.strip() for v in respuestas.values()):
                st.error("Por favor responde al menos una pregunta guía.")
            else:
                respuesta = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "nombre": "Anónimo" if anonima else nombre.strip(),
                    "anonima": "Sí" if anonima else "No",
                    "rol": rol,
                    "institucion": institucion.strip(),
                    **{k: v.strip() for k, v in respuestas.items()},
                    "consentimiento": "Sí" if consentimiento else "No"
                }
                guardar_respuesta(respuesta)
                st.success("Gracias. Tu experiencia fue registrada correctamente.")

elif pagina == "Dashboard":
    st.markdown('<div class="main-title">Dashboard de experiencias</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Resumen de participaciones recibidas</div>', unsafe_allow_html=True)
    df = cargar_datos()

    if df.empty:
        st.info("Aún no hay respuestas registradas.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de respuestas", len(df))
        col2.metric("Participaciones anónimas", int((df["anonima"] == "Sí").sum()))
        col3.metric("Con consentimiento", int((df["consentimiento"] == "Sí").sum()))
        st.divider()

        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.subheader("Respuestas por rol")
            rol_counts = df["rol"].fillna("Sin dato").value_counts().reset_index()
            rol_counts.columns = ["rol", "frecuencia"]
            st.bar_chart(rol_counts.set_index("rol"))
        with col_b:
            st.subheader("Palabras frecuentes")
            palabras_df = contar_palabras(df[list(PREGUNTAS.keys())].astype(str).agg(" ".join, axis=1), top_n=20)
            if palabras_df.empty:
                st.info("Aún no hay suficiente texto para generar frecuencias.")
            else:
                st.bar_chart(palabras_df.set_index("palabra"))

        st.divider()
        st.subheader("Explorar testimonios")
        filtro_rol = st.multiselect("Filtrar por rol", options=sorted(df["rol"].dropna().unique()), default=sorted(df["rol"].dropna().unique()))
        df_filtrado = df[df["rol"].isin(filtro_rol)] if filtro_rol else df

        busqueda = st.text_input("Buscar palabra o frase")
        if busqueda.strip():
            texto_filas = df_filtrado[list(PREGUNTAS.keys())].astype(str).agg(" ".join, axis=1)
            df_filtrado = df_filtrado[texto_filas.str.contains(busqueda, case=False, na=False)]

        for _, row in df_filtrado.iterrows():
            nombre_visible = row["nombre"] if isinstance(row["nombre"], str) and row["nombre"].strip() else "Sin nombre"
            with st.expander(f"{nombre_visible} · {row.get('rol', 'Sin rol')} · {row.get('timestamp', '')}"):
                st.write(f"**Institución:** {row.get('institucion', '')}")
                st.markdown(texto_completo_por_fila(row))

elif pagina == "Exportar datos":
    st.markdown('<div class="main-title">Exportar datos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Descarga las respuestas en formato CSV</div>', unsafe_allow_html=True)
    df = cargar_datos()

    if df.empty:
        st.info("Aún no hay respuestas para exportar.")
    else:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("Descargar CSV", data=csv, file_name="respuestas_evento_mujer_matematica.csv", mime="text/csv")
        st.caption("Nota: si el archivo contiene testimonios identificables, compártelo únicamente con fines académicos y de organización del evento.")
