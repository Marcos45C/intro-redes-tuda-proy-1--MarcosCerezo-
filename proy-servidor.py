
import socket
import threading
import os

from datetime import datetime

HOST = '0.0.0.0'
PORT = 65000

usuarios={
    "marcos":"marcos","jere":"jere","seba":"seba","lucas1":"lucas1","lucas":"lucas","abi":"abi","mat":"mat","profe":"profe",
}

## auxiliares para ver el peso
def tamano(size):
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unidad}"
        size /= 1024

    return f"{size:.1f} TB"
def ls_l(ruta="."):
    salida = []

    for nombre in os.listdir(ruta):

        path = os.path.join(ruta, nombre)

        try:
            stat = os.stat(path)

            fecha = datetime.fromtimestamp(
                stat.st_mtime
            ).strftime("%d/%m/%Y %H:%M")

            salida.append(
                f"{nombre:30} {stat.st_size:10} bytes   {fecha}"
            )

        except Exception:
            pass

    return "\n".join(salida)

def ls_lh(ruta="."):
    salida = []

    for nombre in os.listdir(ruta):

        path = os.path.join(ruta, nombre)

        try:
            stat = os.stat(path)

            fecha = datetime.fromtimestamp(
                stat.st_mtime
            ).strftime("%d/%m/%Y %H:%M")

            salida.append(
                f"{nombre:30} {tamano(stat.st_size):10}   {fecha}"
            )

        except Exception:
            pass

    return "\n".join(salida)

###


def ejecutar_comando(comando):

    partes = comando.split()

    if len(partes) == 0:
        return "Comando vacío"

    cmd = partes[0].lower()

    if cmd == "help":

        return (
            "\n COMANDOS DISPONIBLES \n"
            "---------------------\n"
            "help                 -> muestra esta ayuda\n"
            "pwd                  -> directorio actual\n"
            "ls                   -> listar contenido\n"
            "ls ruta              -> listar ruta específica\n"
            "ls -l                -> listado detallado\n"
            "ls -lh               -> listado detallado legible\n"
            "mkdir nombre         -> crear directorio\n"
            "cat archivo          -> mostrar contenido\n"
            "exit                 -> salir\n"
        )

    # 
    elif cmd == "pwd":

        return os.getcwd()

    # MKDIR
    elif cmd == "mkdir":

        if len(partes) < 2:
            return "ERROR: falta nombre del directorio"

        try:

            os.mkdir(partes[1])

            return f"Directorio '{partes[1]}' creado correctamente"

        except FileExistsError:

            return "ERROR: el directorio ya existe"

        except Exception as e:

            return f"ERROR: {e}"

    # 
    elif cmd == "ls":

        try:

            if len(partes) == 1:

                archivos = os.listdir()

                if not archivos:
                    return "Directorio vacío"

                return "\n".join(archivos)

            elif partes[1] == "-l":

                return ls_l()

            elif partes[1] == "-lh":

                return ls_lh()

            else:

                ruta = partes[1]

                archivos = os.listdir(ruta)

                if not archivos:
                    return "Directorio vacío"

                return "\n".join(archivos)

        except FileNotFoundError:

            return "Ruta inexistente"

        except Exception as e:

            return f"ERROR: {e}"

    # 
    elif cmd == "cat":

        if len(partes) < 2:
            return "ERROR: falta nombre del archivo"

        archivo = partes[1]

        try:

            with open(archivo, "r", encoding="utf-8") as f:

                contenido = f.read()

            if contenido == "":
                return "[Archivo vacío]"

            return contenido

        except FileNotFoundError:

            return "ERROR: archivo no encontrado"

        except Exception as e:

            return f"ERROR: {e}"

    return "ERROR: comando no válido. Escriba 'help'"


# ==========================
# CLIENTE
# ==========================

def atender_cliente(conn, addr):

    print(f"[NUEVA CONEXION] {addr}")

    try:

        # LOGIN

        usuario = conn.recv(1024).decode("utf-8").strip()

        password = conn.recv(1024).decode("utf-8").strip()

        if usuario not in usuarios:

            conn.send("LOGIN_ERROR".encode("utf-8"))

            conn.close()

            print(f"[LOGIN FALLIDO] {addr}")

            return

        if usuarios[usuario] != password:

            conn.send("LOGIN_ERROR".encode("utf-8"))

            conn.close()

            print(f"[LOGIN FALLIDO] {addr}")

            return

        conn.send("LOGIN_OK".encode("utf-8"))

        print(f"[LOGIN OK] {usuario} - {addr}")

        bienvenida = (
            f"\nBienvenido {usuario}\n"
            "Shell Remoto TUDA\n"
            "Escriba 'help' para ver comandos\n"
        )

        conn.send(bienvenida.encode("utf-8"))

        while True:

            data = conn.recv(1024).decode("utf-8").strip()

            if not data:
                break

            print(f"[{usuario}] {data}")

            if data.lower() == "exit":

                conn.send(
                    "Conexión cerrada".encode("utf-8")
                )

                break

            respuesta = ejecutar_comando(data)

            conn.send(
                respuesta.encode("utf-8")
            )

    except Exception as e:

        print(f"[ERROR] {addr}: {e}")

    finally:

        conn.close()

        print(f"[DESCONECTADO] {addr}")


# ==========================
# SERVIDOR
# ==========================

def iniciar_servidor():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

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

        print(
            f"[HILOS ACTIVOS] {threading.active_count() - 1}"
        )


if __name__ == "__main__":
    iniciar_servidor()