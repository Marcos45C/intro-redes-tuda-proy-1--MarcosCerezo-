
import socket
import threading
import os

from datetime import datetime

HOST = '0.0.0.0'
PORT = 65000

usuarios={
    "marcos":"marcos","jere":"jere","seba":"seba","lucas1":"lucas1","lucas":"lucas","abi":"abi","mat":"mat","profe":"profe",
}
MAXCLIENTES = 1

clientes_conectados = {}


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

def consola_admin():

    while True:

        comando = input("admin> ").strip()

        partes = comando.split()

        if len(partes) == 0:
            continue

        cmd = partes[0].lower()

        if cmd == "who":

            if not clientes_conectados:
                print("No hay usuarios conectados")

            else:

                print("\nUsuarios conectados:")

                for usuario in clientes_conectados:
                    print("-", usuario)


        elif cmd == "contar":
            print(
                f"Clientes conectados: {len(clientes_conectados)}/{MAXCLIENTES}"
                )

        elif cmd == "kick":

            if len(partes) < 2:
                print("Uso: kick usuario")
                continue

            usuario = partes[1]

            if usuario not in clientes_conectados:
                print("Usuario no conectado")
                continue

            try:

                conn = clientes_conectados[usuario]

                conn.send(
                    "[SERVIDOR] Has sido expulsado".encode("utf-8")
                )

                conn.close()

                print(f"{usuario} expulsado")

            except Exception as e:

                print(e)

###para expulsar
def expulsar_usuario(nombre):

    if nombre not in clientes_conectados:
        return "Usuario no conectado"

    try:

        cliente = clientes_conectados[nombre]

        cliente.send(
            "[SERVIDOR] Has sido expulsado".encode("utf-8")
        )

        cliente.close()

        del clientes_conectados[nombre]

        return f"Usuario {nombre} expulsado"

    except Exception as e:

        return f"ERROR: {e}"

def ejecutar_comando(comando):

    partes = comando.split()

    if len(partes) == 0:
        return "Comando vacío"

    cmd = partes[0].lower()

    if cmd == "help":

        return (
            "\n COMANDOS DISPONIBLES \n"
            "---------------------\n"
            "help  -> muestra esta ayuda\n"
            "pwd      -> directorio actual\n"
            "ls       -> listar contenido\n"
            "ls ruta   -> listar ruta específica\n"
            "ls -l       -> listado detallado\n"
            "ls -lh      -> listado detallado legible\n"
            "mkdir nombre    -> crear directorio\n"
            "cat archivo       -> mostrar contenido\n"
            "exit  -> salir\n"
            "kick -> ejem marcos\n"
            "who -> quienes estan en la red"
        )

    #
    elif cmd == "kick":
        if len(partes) < 2:
            return "Uso: kick usuario"
        return expulsar_usuario(partes[1])


    elif cmd == "who":
        if not clientes_conectados:
            return "No hay usuarios conectados"
        return "\n".join(clientes_conectados.keys())

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



# Cliente


def atender_cliente(conn, addr):

    #evita errores
    usuario = None

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

        #cuando ingresa un nuevo uusario lo guardo
        #cliente conectado
        clientes_conectados[usuario] = conn


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
        if usuario in clientes_conectados:
            del clientes_conectados[usuario]
        conn.close()

        print(f"[DESCONECTADO] {addr}")


#servidor

def iniciar_servidor():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.bind((HOST, PORT))

    server.listen(5)

    print(f"[SERVER] Escuchando en {HOST}:{PORT}")

    admin_thread = threading.Thread(
        target=consola_admin,
        daemon=True
    )

    admin_thread.start()

    while True:
        conn, addr = server.accept()
        # CONTROL DE LIMITE
        if len(clientes_conectados) >= MAXCLIENTES:
                #caso que fue rechazado
            print(
                f"[RECHAZADO] {addr} - servidor lleno"
            )
            conn.send(
                    "Servidor lleno. Intente más tarde.".encode("utf-8")
                )
            conn.close()
            continue

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