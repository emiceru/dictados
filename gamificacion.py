import sqlite3
import streamlit as st
import pandas as pd

def mostrar_panel(usuario):
    conn = sqlite3.connect('dictados.db')
    df = pd.read_sql("""
        SELECT fecha, errores, aciertos FROM resultados r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE u.username=? ORDER BY fecha DESC
    """, conn, params=(usuario,))
    conn.close()

    st.header(f"🏆 Panel de {usuario}")

    if not df.empty:
        st.subheader("📈 Últimos Resultados")
        st.table(df.head(10))

        col1, col2, col3 = st.columns(3)
        col1.metric("Dictados realizados", len(df))
        col2.metric("Aciertos totales", df['aciertos'].sum())
        col3.metric("Errores totales", df['errores'].sum())

        acierto_global = (df['aciertos'].sum() / (df['aciertos'].sum() + df['errores'].sum())) * 100
        st.metric("Tasa global de acierto", f"{acierto_global:.2f}%")

    else:
        st.write("Realiza dictados para ver tu progreso aquí.")
