import sqlite3

conn = sqlite3.connect("usuarios.db")

cursor = conn.cursor()
usuarios=[
    ("marcos","marcos"),
    ("jere","jere"),
    ("seba","seba"),
    ("lucas1","lucas1"),
    ("lucas","lucas"),
    ("abi","abi"),
    ("mat","mat"),
    ("profe","profe")
]
cursor.executemany(
    "INSERT INTO usuarios VALUES (?, ?)",
    usuarios
)

conn.commit()
conn.close()
print("usuarios cargados")