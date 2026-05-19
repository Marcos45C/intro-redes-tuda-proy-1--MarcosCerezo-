
import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 65000


def ejecutar_comando(comando):
    partes = comando.split()

    if len(partes) == 0:
        return "Comando vacío"

    cmd = partes[0].lower()
    if cmd == "ls":
        archivos = os.listdir()

        if not archivos:
            return "Directorio vacío"

        return "\n".join(archivos)

    elif cmd == "pwd":
        return os.getcwd()

    elif cmd == "cat":

        if len(partes) < 2:
            return "ERROR: falta nombre de archivo"

        nombre_archivo = partes[1]

        try:
            with open(nombre_archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            return contenido

        except FileNotFoundError:
            return "ERROR: archivo no encontrado"

        except Exception as e:
            return f"ERROR: {e}"

    else:
        return "ERROR: comando no válido"


def atender_cliente(conn, addr):

    print(f"[NUEVA CONEXION] {addr}")

    bienvenida = (
        "Bienvenido al Shell Remoto\n"
        "Comandos disponibles:\n"
        "ls\n"
        "pwd\n"
        "cat archivo.txt\n"
        "exit\n"
    )

    conn.send(bienvenida.encode("utf-8"))

    while True:

        try:

            data = conn.recv(1024).decode("utf-8").strip()

            if not data:
                break

            print(f"[{addr}] comando: {data}")
            if data.lower() == "exit":

                conn.send("Conexion cerrada".encode("utf-8"))
                break

            respuesta = ejecutar_comando(data)

            conn.send(respuesta.encode("utf-8"))

        except Exception as e:

            print(f"[ERROR] {addr}: {e}")
            break

    conn.close()
    print(f"[DESCONECTADO] {addr}")


def iniciar_servidor():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))

    server.listen(5)

    print(f"[SERVER] Escuchando en {HOST}:{PORT}")

    while True:

        conn, addr = server.accept()

        thread = threading.Thread(
            target=atender_cliente,
            args=(conn, addr)
        )

        thread.start()

        print(f"[HILOS ACTIVOS] {threading.active_count() - 1}")


if __name__ == "__main__":
    iniciar_servidor()