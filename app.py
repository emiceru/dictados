import streamlit as st
import sqlite3
from gtts import gTTS
from datetime import datetime
import os
import pytesseract
from PIL import Image
import openai
from dotenv import load_dotenv

# Configuración inicial
st.set_page_config(page_title="Dictados Ortográficos", layout="centered")

# Cargar API Key\load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Crear carpetas necesarias
os.makedirs("dictados", exist_ok=True)
os.makedirs("correcciones", exist_ok=True)

# Base de datos
conn = sqlite3.connect('dictados.db')
c = conn.cursor()

# Crear tablas
c.execute('''CREATE TABLE IF NOT EXISTS reglas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT,
                descripcion TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS dictados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regla_id INTEGER,
                texto TEXT,
                fecha TEXT,
                FOREIGN KEY(regla_id) REFERENCES reglas(id))''')

conn.commit()

st.title("📚 Dictados Ortográficos")

# Navegación
opcion = st.sidebar.selectbox("Selecciona una opción", ["Inicio", "Añadir regla", "Añadir dictado", "Corregir dictado"])

if opcion == "Inicio":
    st.header("📖 Dictados disponibles")
    dictados = c.execute("SELECT d.id, r.titulo, d.texto, d.fecha FROM dictados d JOIN reglas r ON d.regla_id = r.id").fetchall()
    for dictado in dictados:
        st.subheader(f"{dictado[1]} ({dictado[3]})")
        st.write(dictado[2])

elif opcion == "Añadir regla":
    st.header("🖊️ Nueva Regla Ortográfica")
    titulo_regla = st.text_input("Título")
    descripcion_regla = st.text_area("Descripción")
    if st.button("Añadir"):
        c.execute("INSERT INTO reglas (titulo, descripcion) VALUES (?, ?)", (titulo_regla, descripcion_regla))
        conn.commit()
        st.success("Regla añadida correctamente")

elif opcion == "Añadir dictado":
    st.header("📝 Nuevo Dictado")
    reglas = c.execute("SELECT * FROM reglas").fetchall()
    regla_id_seleccionada = st.selectbox("Selecciona la regla", [f"{r[0]} - {r[1]}" for r in reglas])
    texto_dictado = st.text_area("Texto del dictado")

    if st.button("Añadir dictado"):
        regla_id = int(regla_id_seleccionada.split(" - ")[0])
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        c.execute("INSERT INTO dictados (regla_id, texto, fecha) VALUES (?, ?, ?)", (regla_id, texto_dictado, fecha_actual))
        conn.commit()

        tts = gTTS(texto_dictado, lang='es')
        audio_file = f"dictados/dictado_{fecha_actual}.mp3"
        tts.save(audio_file)
        st.audio(audio_file)
        st.success("Dictado añadido y audio generado")

elif opcion == "Corregir dictado":
    st.header("🖼️ Corrección de Dictado por Foto")
    dictados = c.execute("SELECT id, texto FROM dictados").fetchall()
    dictado_id = st.selectbox("Selecciona el dictado", [f"{d[0]}" for d in dictados])
    foto = st.file_uploader("Subir foto", type=["jpg", "jpeg", "png"])

    if foto and dictado_id:
        imagen = Image.open(foto)
        texto_alumno = pytesseract.image_to_string(imagen, lang='spa')
        dictado_texto = c.execute("SELECT texto FROM dictados WHERE id=?", (dictado_id,)).fetchone()[0]

        prompt_correccion = f"""
        Corrige este dictado:
        Original: {dictado_texto}
        Alumno: {texto_extraido}
        Enumera y explica errores.
        """

        correccion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_correccion}]
        )['choices'][0]['message']['content']

        st.write("### 📌 Corrección")
        st.write(correccion)

        reporte = f"correccion_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        with open(reporte, 'w', encoding='utf-8') as f:
            f.write(correccion)

        with open(reporte, 'rb') as f:
            st.download_button("Descargar corrección", f, file_name=reporte)
