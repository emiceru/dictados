import streamlit as st
import sqlite3
import pyttsx3
from datetime import datetime
import os
import bcrypt

# Inicialización
def init_db():
    conn = sqlite3.connect('dictados.db')
    c = conn.cursor()
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
    return conn, c

conn, c = init_db()

# Sesión
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None

# Funciones Auth
def registrar_usuario(username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    fecha_registro = datetime.now().strftime('%Y-%m-%d')
    try:
        c.execute("INSERT INTO usuarios (username, password, fecha_registro) VALUES (?, ?, ?)", (username, hashed_pw, fecha_registro))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verificar_usuario(username, password):
    c.execute("SELECT password FROM usuarios WHERE username=?", (username,))
    user = c.fetchone()
    if user:
        return bcrypt.checkpw(password.encode(), user[0])
    return False

# UI Login
if st.session_state['usuario'] is None:
    st.header("🔐 Autenticación")
    accion = st.selectbox("Acción", ["Iniciar sesión", "Registrar usuario"])
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Enviar"):
        if accion == "Registrar usuario":
            if registrar_usuario(username, password):
                st.success("Registrado con éxito")
            else:
                st.error("Usuario existente")
        elif accion == "Iniciar sesión":
            if verificar_usuario(username, password):
                st.session_state['usuario'] = username
                st.success(f"Bienvenido {username}")
                st.experimental_rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    usuario = st.session_state['usuario']
    st.sidebar.write(f"👤 {usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state['usuario'] = None
        st.experimental_rerun()

    st.title("📚 Dictados Ortográficos")

    if usuario == "admin":
        menu = ["Inicio", "Añadir regla", "Añadir dictado"]
    else:
        menu = ["Inicio"]

    opcion = st.sidebar.selectbox("Menú", menu)

    if opcion == "Inicio":
        if st.button("▶️ Nuevo dictado aleatorio"):
            dictado = c.execute("SELECT texto FROM dictados ORDER BY RANDOM() LIMIT 1").fetchone()
            engine = pyttsx3.init()
            audio_file = "dictado_actual.mp3"
            engine.save_to_file(dictado[0], audio_file)
            engine.runAndWait()
            st.audio(audio_file)

        reglas = c.execute("SELECT * FROM reglas").fetchall()
        for regla in reglas:
            st.subheader(regla[1])
            st.write(regla[2])
            if st.button(f"▶️ Dictado regla {regla[0]}"):
                dictado = c.execute("SELECT texto FROM dictados WHERE regla_id=? ORDER BY RANDOM() LIMIT 1", (regla[0],)).fetchone()
                engine = pyttsx3.init()
                audio_file = f"dictados/dictado_{regla[0]}.mp3"
                engine.save_to_file(dictado[0], audio_file)
                engine.runAndWait()
                st.audio(audio_file)

    elif opcion == "Añadir regla":
        titulo = st.text_input("Título")
        descripcion = st.text_area("Descripción")
        if st.button("Añadir regla"):
            c.execute("INSERT INTO reglas (titulo, descripcion) VALUES (?, ?)", (titulo, descripcion))
            conn.commit()
            st.success("Regla añadida")

    elif opcion == "Añadir dictado":
        reglas = c.execute("SELECT id, titulo FROM reglas").fetchall()
        regla_id = st.selectbox("Regla", [f"{r[0]} - {r[1]}" for r in reglas])
        texto = st.text_area("Texto")
        if st.button("Añadir"):
            regla_num = int(regla_id.split(" - ")[0])
            fecha = datetime.now().strftime('%Y-%m-%d')
            c.execute("INSERT INTO dictados (regla_id, texto, fecha) VALUES (?, ?, ?)", (regla_id_num, texto, fecha_actual))
            conn.commit()
            st.success("Dictado añadido")

    if st.sidebar.button("Ver progreso"):
        st.info("Aquí irán las estadísticas del usuario.")
