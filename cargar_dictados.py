import sqlite3
from datetime import datetime

# Conecta a la base de datos existente
conn = sqlite3.connect('dictados.db')
c = conn.cursor()

# Define reglas y dictados a insertar
reglas_dictados = [
    {
        "titulo": "Acentuación básica (Palabras agudas)",
        "descripcion": "Las palabras agudas llevan tilde cuando terminan en vocal, n o s.",
        "dictado": """En la ciudad, Sofía tomó café con limón mientras revisó la canción que sonó en la estación. Su corazón latió con emoción. Andrés también escuchó esa canción y decidió que viajará en avión. Después cenará arroz con salmón en algún balcón cercano al malecón. El capitán saludó desde el camión azul, mientras el ladrón corrió velozmente hacia el callejón. Martín contó cómo ganó la competición de natación. La información salió en televisión. Hoy saldrá el campeón de ajedrez, quien demostró pasión y atención. El volcán lanzó ceniza, y Ramón observó el espectáculo natural con admiración."""
    },
    {
        "titulo": "Uso correcto de B y V",
        "descripcion": "La b se usa generalmente antes de consonantes (bl, br) y después de m. La v aparece tras n o en palabras terminadas en ivo, iva.",
        "dictado": """Bruno vive en una bonita vivienda cerca del bosque. Cada día observa cómo las aves vuelan sobre el valle. Su hermano, Vicente, es activo y trabaja con bravura en la construcción de un nuevo puente. Ambos aman navegar en barco durante el verano. En noviembre visitarán Barcelona para celebrar el aniversario de su abuelo Alberto. Durante el viaje, llevarán libros y varios objetos valiosos. En la biblioteca encontrarán información sobre la biodiversidad del Amazonas. Vicente subrayó varias palabras importantes en el libro que le regaló la profesora Beatriz."""
    },
    {
        "titulo": "Uso de la H inicial",
        "descripcion": "La h se utiliza en palabras que comienzan por los diptongos hia, hie, hue, hui, y en todas las formas del verbo haber.",
        "dictado": """Hoy Héctor ha hecho una hermosa casa junto al huerto. Había muchas hierbas alrededor, pero ahora ha logrado limpiar el lugar. La hija de Helena siempre ha tenido habilidad para hacer helados caseros. En invierno, el hielo cubre las hojas de los árboles, y Humberto disfruta mucho viendo el horizonte nevado desde la ventana. Hugo, su hermano mayor, ha comprado huevos para hornear un delicioso pastel. Habrá invitados en la fiesta de cumpleaños que harán el sábado. Los niños esperan con ilusión porque habrá juegos y muchos regalos. Todos han prometido hacer hermosas decoraciones."""
    }
]

# Insertar automáticamente reglas y dictados
for regla in reglas_dictados:
    # Insertar regla
    c.execute("INSERT INTO reglas (titulo, descripcion) VALUES (?, ?)",
              (regla['titulo'], regla['descripcion']))
    regla_id = c.lastrowid

    # Insertar dictado
    c.execute("INSERT INTO dictados (regla_id, texto, fecha) VALUES (?, ?, ?)",
              (regla_id, regla['dictado'], datetime.now().strftime('%Y-%m-%d')))

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("✅ Reglas y dictados insertados correctamente.")
