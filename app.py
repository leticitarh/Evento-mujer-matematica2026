import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
from collections import Counter

# Configuración de página
st.set_page_config(page_title="Entre dudas y decisiones", page_icon="∫", layout="wide")

# Ruta del archivo
DATA_PATH = Path("respuestas_evento_mujer_matematica.csv")

# Preguntas
PREGUNTAS = {
    "decision_clave": "¿Qué decisión marcó un antes y un después en tu trayectoria?",
    "como_decidiste": "¿Cómo tomaste esa decisión?",
    "duda": "¿En qué momento dudaste de continuar?",
    "que_te_ayudo": "¿Qué te ayudó a seguir?",
    "obstaculo": "¿Qué obstáculo enfrentaste?",
    "afrontamiento": "¿Cómo lo afrontaste?",
}

# -----------------------------
# Funciones
# -----------------------------

def inicializar_csv():
    if not DATA_PATH.exists():
        columnas = ["timestamp", "nombre", "rol"] + list(PREGUNTAS.keys())
        pd.DataFrame(columns=columnas).to_csv(DATA_PATH, index=False)

def cargar_datos():
    inicializar_csv()
    return pd.read_csv(DATA_PATH)

def guardar_respuesta(data):
    df = cargar_datos()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

def contar_palabras(series):
    texto = " ".join(series)
    palabras = re.findall(r"\w+", texto.lower())
    return pd.DataFrame(Counter(palabras).most_common(20), columns=["palabra", "frecuencia"])

# -----------------------------
# Navegación
# -----------------------------

st.sidebar.title("Menú")
pagina = st.sidebar.radio("Sección", ["Formulario", "Dashboard", "Exportar"])

# -----------------------------
# FORMULARIO
# -----------------------------

if pagina == "Formulario":
    st.title("Entre dudas y decisiones: ser mujer matemática")
    st.subheader("Formulario para profesoras y egresadas")

    with st.form("form"):
        nombre = st.text_input("Nombre (opcional)")
        rol = st.selectbox("Rol", ["Profesora", "Egresada", "Otra"])

        respuestas = {}
        for key, pregunta in PREGUNTAS.items():
            respuestas[key] = st.text_area(pregunta)

        enviar = st.form_submit_button("Enviar")

        if enviar:
            data = {
                "timestamp": datetime.now(),
                "nombre": nombre,
                "rol": rol,
                **respuestas
            }
            guardar_respuesta(data)
            st.success("Tu respuesta fue guardada correctamente")

# -----------------------------
# DASHBOARD
# -----------------------------

elif pagina == "Dashboard":
    st.title("Dashboard de respuestas")

    df = cargar_datos()

    if df.empty:
        st.info("Aún no hay respuestas")
    else:
        st.metric("Total de respuestas", len(df))

        # Texto combinado (CORREGIDO)
        texto_series = df[list(PREGUNTAS.keys())] \
            .fillna("") \
            .astype(str) \
            .apply(lambda fila: " ".join(fila), axis=1)

        palabras_df = contar_palabras(texto_series)

        st.subheader("Palabras más frecuentes")
        st.bar_chart(palabras_df.set_index("palabra"))

        st.subheader("Respuestas completas")
        st.dataframe(df)

# -----------------------------
# EXPORTAR
# -----------------------------

elif pagina == "Exportar":
    st.title("Exportar datos")

    df = cargar_datos()

    if df.empty:
        st.info("No hay datos para descargar")
    else:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name="respuestas_evento.csv",
            mime="text/csv"
        )
