import sqlite3
import bcrypt

usuarios = [
    ("marcos", "marcos"),
    ("jere", "jere"),
    ("seba", "seba"),
    ("lucas1", "lucas1"),
    ("lucas", "lucas"),
    ("abi", "abi"),
    ("mat", "mat"),
    ("profe", "profe")
]

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")

for usuario, password in usuarios:

    hash_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute(
        """
        INSERT OR REPLACE INTO usuarios
        VALUES (?,?)
        """,
        (usuario, hash_password)
    )

conn.commit()
conn.close()

print("Usuarios cargados")