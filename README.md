# Entre dudas y decisiones: ser mujer matemática

App en Streamlit para recopilar experiencias de profesoras y egresadas, con formulario, dashboard y exportación de datos.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicación en Streamlit Community Cloud

1. Crea un repositorio en GitHub.
2. Sube `app.py` y `requirements.txt`.
3. Entra a Streamlit Community Cloud.
4. Elige el repositorio y selecciona `app.py`.
5. Publica.

## Nota

La versión básica guarda las respuestas en un CSV dentro del entorno de la app. En Streamlit Community Cloud puede perderse si la app se reinicia. Para uso más robusto conviene conectar a Google Sheets, Supabase o una base de datos.
