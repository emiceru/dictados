import streamlit as st
import sqlite3
import pyttsx3
import pytesseract
from PIL import Image
from datetime import datetime
import openai
from dotenv import load_dotenv
import os
import bcrypt
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Dictados Ortográficos", layout="centered")

# Cargar API Key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Crear carpetas necesarias
os.makedirs("dictados", exist_ok=True)
os.makedirs("correcciones", exist_ok=True)

# Base de datos
conn = sqlite3.connect('dictados.db')
c = conn.cursor()

# Crear tablas necesarias
c.executescript('''
CREATE TABLE IF NOT EXISTS reglas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    descripcion TEXT);

CREATE TABLE IF NOT EXISTS dictados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regla_id INTEGER,
    texto TEXT,
    fecha TEXT,
    FOREIGN KEY(regla_id) REFERENCES reglas(id));

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    fecha_registro TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    dictado_id INTEGER,
    fecha TEXT,
    errores INTEGER,
    aciertos INTEGER,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY(dictado_id) REFERENCES dictados(id));
''')

conn.commit()

# Autenticación
st.sidebar.header("🔐 Autenticación")
accion = st.sidebar.selectbox("Acción", ["Iniciar sesión", "Registrar usuario"])
username = st.sidebar.text_input("Usuario")
password = st.sidebar.text_input("Contraseña", type="password")

if accion == "Registrar usuario":
    if st.sidebar.button("Registrar"):
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        fecha_registro = datetime.now().strftime('%Y-%m-%d')
        try:
            c.execute("INSERT INTO usuarios (username, password, fecha_registro) VALUES (?, ?, ?)",
                      (username, hashed_pw, fecha_registro))
            conn.commit()
            st.sidebar.success("Usuario registrado correctamente")
        except sqlite3.IntegrityError:
            st.sidebar.error("El usuario ya existe.")

elif accion == "Iniciar sesión":
    if st.sidebar.button("Entrar"):
        c.execute("SELECT password FROM usuarios WHERE username=?", (username,))
        usuario = c.fetchone()
        if usuario and bcrypt.checkpw(password.encode(), usuario[0]):
            st.sidebar.success("Sesión iniciada correctamente")
            st.session_state['usuario'] = username
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")

# Mostrar contenido solo si está autenticado
if 'usuario' in st.session_state:
    st.title(f"📚 Dictados Ortográficos - Bienvenido {st.session_state['usuario']}")

    opcion = st.sidebar.selectbox("Selecciona una opción", ["Inicio", "Añadir regla", "Añadir dictado", "Corregir dictado", "Mi progreso"])

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
        regla_id = st.selectbox("Regla", [f"{r[0]} - {r[1]}" for r in reglas])
        texto_dictado = st.text_area("Texto del dictado")
        if st.button("Añadir dictado"):
            regla_id_num = int(regla_id.split(" - ")[0])
            fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            c.execute("INSERT INTO dictados (regla_id, texto, fecha) VALUES (?, ?, ?)", (regla_id_num, texto_dictado, fecha_actual))
            conn.commit()

            engine = pyttsx3.init()
            audio_file = f"dictados/dictado_{fecha_actual}.mp3"
            engine.save_to_file(texto_dictado, audio_file)
            engine.runAndWait()

            st.audio(audio_file)
            st.success("Dictado añadido y audio generado")

    elif opcion == "Corregir dictado":
        st.header("🖼️ Corrección de Dictado por Foto")
        dictado_id = st.selectbox("Selecciona dictado", [d[0] for d in c.execute("SELECT id FROM dictados")])
        foto = st.file_uploader("Subir foto", type=["jpg", "jpeg", "png"])

        if foto:
            imagen = Image.open(foto)
            texto_alumno = pytesseract.image_to_string(imagen, lang='spa')
            dictado_texto = c.execute("SELECT texto FROM dictados WHERE id=?", (dictado_id,)).fetchone()[0]

            prompt_correccion = f"""Corrige el siguiente dictado:\n\nDictado original: {dictado_texto}\n\nDictado alumno: {texto_alumno}\n\nExplica claramente cada error."""

            respuesta = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                     messages=[{"role": "user", "content": prompt_correccion}])
            correccion = respuesta['choices'][0]['message']['content']

            st.write("📌 Corrección")
            st.write(correccion)
else:
    st.info("🔒 Debes iniciar sesión para usar la aplicación.")
