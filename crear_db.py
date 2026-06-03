import sqlite3

conn = sqlite3.connect("usuarios.db")

cursor = conn.cursor()

cursor.execute(
"""
""")

conn.commit()
conn.close()

print("Base creada")