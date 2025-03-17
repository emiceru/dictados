import bcrypt
import sqlite3
from datetime import datetime

def registrar_usuario(username, password):
    conn = sqlite3.connect('dictados.db')
    c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    fecha = datetime.now().strftime('%Y-%m-%d')

    try:
        c.execute("INSERT INTO usuarios (username, password, fecha_registro) VALUES (?, ?, ?)",
                  (username, hashed_pw, fecha))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_usuario(username, password):
    conn = sqlite3.connect('dictados.db')
    c = conn.cursor()
    c.execute("SELECT password FROM usuarios WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False
