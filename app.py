import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
from collections import Counter

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Entre dudas y decisiones",
    page_icon="∫",
    layout="wide"
)

DATA_PATH = Path("respuestas_evento_mujer_matematica.csv")

# ============================================================
# PREGUNTAS COMPLETAS
# ============================================================

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

COLUMNAS = [
    "timestamp", "nombre", "anonima", "rol", "institucion",
    *PREGUNTAS.keys(),
    "consentimiento"
]

# ============================================================
# FUNCIONES
# ============================================================

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
    return texto

def contar_palabras(series, top_n=20):
    texto = " ".join(series)
    palabras = [p for p in texto.split() if len(p) > 3]
    return pd.DataFrame(Counter(palabras).most_common(top_n), columns=["palabra", "frecuencia"])

# ============================================================
# ESTILO (OCRES)
# ============================================================

st.markdown("""
<style>
.main-title {
    font-size: 2.3rem;
    font-weight: 700;
    color: #3d3329;
}
.subtitle {
    color: #6b5b4a;
    margin-bottom: 1.5rem;
}
.box {
    background-color: #f5efe4;
    padding: 1rem;
    border-left: 5px solid #a87332;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# MENÚ
# ============================================================

st.sidebar.title("Menú")
pagina = st.sidebar.radio("Sección", ["Formulario", "Dashboard", "Exportar"])

# ============================================================
# FORMULARIO
# ============================================================

if pagina == "Formulario":

    st.markdown('<div class="main-title">Entre dudas y decisiones: ser mujer matemática</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Experiencias que orientan trayectorias</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="box">
    La participación puede ser anónima. Si compartes una experiencia adversa,
    acompáñala con un aprendizaje o estrategia que pueda orientar a otras estudiantes.
    </div>
    """, unsafe_allow_html=True)

    with st.form("formulario", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            anonima = st.checkbox("Participación anónima")
            nombre = st.text_input("Nombre", disabled=anonima)
            rol = st.selectbox("Rol", ["Profesora", "Egresada", "Profesora y egresada"])

        with col2:
            institucion = st.text_input("Institución (opcional)")

        st.divider()
        st.subheader("Preguntas guía")

        respuestas = {}
        for k, pregunta in PREGUNTAS.items():
            respuestas[k] = st.text_area(pregunta)

        consentimiento = st.checkbox("Autorizo el uso del testimonio")

        enviar = st.form_submit_button("Enviar")

        if enviar:
            if not consentimiento:
                st.error("Debes aceptar el consentimiento")
            else:
                guardar_respuesta({
                    "timestamp": datetime.now(),
                    "nombre": "Anónimo" if anonima else nombre,
                    "anonima": anonima,
                    "rol": rol,
                    "institucion": institucion,
                    **respuestas,
                    "consentimiento": consentimiento
                })
                st.success("Respuesta guardada")

# ============================================================
# DASHBOARD (CORREGIDO)
# ============================================================

elif pagina == "Dashboard":

    st.markdown('<div class="main-title">Dashboard</div>', unsafe_allow_html=True)

    df = cargar_datos()

    if df.empty:
        st.info("Sin respuestas aún")
    else:
        st.metric("Total de respuestas", len(df))

        # 🔴 AQUÍ ESTABA EL ERROR → YA CORREGIDO
        texto_series = df[list(PREGUNTAS.keys())] \
            .fillna("") \
            .astype(str) \
            .apply(lambda fila: " ".join(fila), axis=1)

        palabras_df = contar_palabras(texto_series)

        st.subheader("Palabras frecuentes")
        st.bar_chart(palabras_df.set_index("palabra"))

        st.subheader("Respuestas")
        st.dataframe(df)

# ============================================================
# EXPORTAR
# ============================================================

elif pagina == "Exportar":

    st.markdown('<div class="main-title">Exportar datos</div>', unsafe_allow_html=True)

    df = cargar_datos()

    if df.empty:
        st.info("No hay datos")
    else:
        csv = df.to_csv(index=False, encoding="utf-8-sig")

        st.download_button(
            "Descargar CSV",
            data=csv,
            file_name="respuestas_evento.csv",
            mime="text/csv"
        )
