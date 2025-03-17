import streamlit as st
import sqlite3
from auth import registrar_usuario, verificar_usuario
from gamificacion import mostrar_panel
from datetime import datetime

st.set_page_config(page_title="Dictados Gamificados")

# Función login
def login_ui():
    st.sidebar.header("🔐 Autenticación")
    accion = st.sidebar.selectbox("Acción", ["Iniciar sesión", "Registrar usuario"])
    user = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if accion == "Registro":
        if st.sidebar.button("Registrar"):
            if registrar_usuario(user, password):
                st.sidebar.success("Registro exitoso.")
            else:
                st.sidebar.error("El usuario ya existe.")
        return None

    elif accion == "Login":
        if st.sidebar.button("Entrar"):
            if verificar_usuario(user, password):
                st.sidebar.success(f"¡Bienvenido/a, {user}!")
                return user
            else:
                st.sidebar.error("Credenciales incorrectas.")
        return None

usuario_actual = login_ui()

if usuario_actual := usuario_actual:
    menu = st.sidebar.selectbox("Menú", ["Inicio", "Añadir regla", "Añadir dictado", "Corregir dictado", "Mi progreso"])

    conn = sqlite3.connect('dictados.db')
    c = conn.cursor()

    if menu == "Inicio":
        st.header("Dictados disponibles")
        dictados = c.execute("SELECT texto FROM dictados ORDER BY fecha DESC LIMIT 10").fetchall()
        for dictado in dictados:
            st.write(dictado[0])

    elif menu == "Añadir regla":
        st.header("Añadir regla")
        titulo = st.text_input("Título")
        desc = st.text_area("Descripción")
        if st.button("Añadir regla"):
            c.execute("INSERT INTO reglas (titulo, descripcion) VALUES (?, ?)", (titulo, desc))
            conn.commit()
            st.success("Regla añadida.")

    elif menu == "Añadir dictado":
        st.header("Añadir dictado")
        reglas = c.execute("SELECT * FROM reglas").fetchall()
        regla = st.selectbox("Regla", [f"{r[0]}-{r[1]}" for r in reglas])
        texto = st.text_area("Texto dictado")
        if st.button("Añadir dictado"):
            regla_id = int(regla.split(" - ")[0])
            c.execute("INSERT INTO dictados (regla_id, texto, fecha) VALUES (?, ?, ?)", (regla_id, texto, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            st.success("Dictado añadido.")

    elif menu == "Corregir dictado":
        st.header("Sube tu dictado para corregir")
        dictado_id = st.selectbox("Selecciona dictado", [f"{d[0]}" for d in c.execute("SELECT id FROM dictados")])
        errores = st.number_input("Número de errores", min_value=0)
        aciertos = st.number_input("Número de aciertos", min_value=0)
        if st.button("Guardar resultado"):
            usuario_id = c.execute("SELECT id FROM usuarios WHERE username=?", (user,)).fetchone()[0]
            c.execute("INSERT INTO resultados (usuario_id, dictado_id, fecha, errores, aciertos) VALUES (?, ?, ?, ?, ?)",
                      (usuario_id, dictado_id, datetime.now().strftime('%Y-%m-%d'), errores, aciertos))
            conn.commit()
            st.success("Resultados guardados.")

    elif menu == "Mi progreso":
        mostrar_panel(usuario=user)

    conn.close()
else:
    st.info("Por favor, inicia sesión.")
