
import socket
import threading
#Permite interactuar con el sistema operativo.
import os
#Se usa para mostrar fechas legibles cpn ls 
from datetime import datetime

import sqlite3
import bcrypt

HOST = '0.0.0.0'
PORT = 65000


MAXCLIENTES = 5

#para comandos who , expulsion y contar clientes activos
clientes_conectados = {}

def validar_usuario(usuario, password):

    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM usuarios WHERE username=?",
        (usuario,)
    )

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return False

    hash_guardado = resultado[0]

    return bcrypt.checkpw(
        password.encode(),
        hash_guardado.encode()
    )

## auxiliares para ver el peso, paso de 1048576 a 1.0 MB, lo uso en ls -lh
def tamano(size):
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unidad}"
        size /= 1024

    return f"{size:.1f} TB"
    
#muestro aca nombre, tamaño, fecha modificación
def ls_l(ruta="."):
    salida = []

    for nombre in os.listdir(ruta):

        path = os.path.join(ruta, nombre)

        try:
            #para obtener info del archivo os.stat
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

#aca corro un hilo independiente para que el servidor haga comandos 
def consola_admin():

    while True:
        try:

            comando = input("admin> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[CERRANDO CONSOLA ADMIN]")
            break
        
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
            "##SERVIDOR## has sido echao".encode("utf-8")
        )
        cliente.close()

        del clientes_conectados[nombre]

        return f"Usuario {nombre} expulsado"

    except Exception as e:

        return f"ERROR: {e}"

def ejecutar_comando(comando,directorio_actual):

    partes = comando.split()

    if len(partes) == 0:
        return "Comando vacío",directorio_actual

    cmd = partes[0].lower()

    if cmd == "help":

        return (
            "\n COMANDOS DISPONIBLES \n"
            "---------------------\n"
            "help  = muestra esta ayuda\n"
            "pwd  =directorio actual\n"
            "ls  = listar contenido\n"
            "ls ruta  = listar ruta específica\n"
            "ls -l   =listado detallado\n"
            "ls -lh   =listado detallado legible\n"
            "mkdir nombre  =crear directorio\n"
            "cat archivo =mostrar contenido\n"
            "exit  =salir\n"
            "kick = ejem marcos\n"
            "who = quienes estan en la red"
            "cd carpeta => cambiar directorio\n"
        ),directorio_actual

    #
    elif cmd == "kick":
        if len(partes) < 2:
            return "Uso: kick usuario",directorio_actual
        return expulsar_usuario(partes[1]),directorio_actual


    #elif cmd == "who":
     #   if not clientes_conectados:
      #      return "No hay usuarios conectados"
       # return "\n".join(clientes_conectados.keys())
    elif cmd == "who":
        if not clientes_conectados:
            return "No hay usuarios conectados", directorio_actual

        return "\n".join(clientes_conectados.keys()), directorio_actual
    #
        # CD
    elif cmd == "cd":

        if len(partes) < 2:
            return "ERROR: falta directorio", directorio_actual

        nueva_ruta = os.path.join(
            directorio_actual,
            partes[1]
        )

        nueva_ruta = os.path.abspath(nueva_ruta)

        if not os.path.isdir(nueva_ruta):
            return "ERROR: directorio inexistente", directorio_actual

        directorio_actual = nueva_ruta

        return f"Directorio cambiado a:\n{directorio_actual}", directorio_actual
    
    elif cmd == "pwd":

        #return os.getcwd()
        #ya no queres el directorio global, solo del cliente
        return directorio_actual, directorio_actual

    # MKDIR
    elif cmd == "mkdir":

        if len(partes) < 2:
            return "ERROR: falta nombre del directorio",directorio_actual

        try:
            #os.mkdir(partes[1])
            ruta = os.path.join(
                directorio_actual,
                partes[1]
                )
            os.mkdir(ruta)

            return f"Directorio '{partes[1]}' creado correctamente", directorio_actual

        except FileExistsError:

            return "ERROR: el directorio ya existe", directorio_actual

        except Exception as e:

            return f"ERROR: {e}",directorio_actual

    # 
    elif cmd == "ls":

        try:

            if len(partes) == 1:

                archivos = os.listdir(directorio_actual)

                if not archivos:
                    return "Directorio vacío",directorio_actual

                return "\n".join(archivos), directorio_actual

            elif partes[1] == "-l":
                #return ls_l()
                return ls_l(directorio_actual), directorio_actual
            elif partes[1] == "-lh":
                #return ls_lh()
                return ls_lh(directorio_actual), directorio_actual
            else:

                #ruta = partes[1]
                ruta = os.path.join(
                directorio_actual,
                partes[1]
                )
                archivos = os.listdir(ruta)

                if not archivos:
                    return "Directorio vacío",directorio_actual

                return "\n".join(archivos),directorio_actual

        except FileNotFoundError:

            return "Ruta inexistente",directorio_actual

        except Exception as e:

            return f"ERROR: {e}",directorio_actual

    # 
    elif cmd == "cat":

        if len(partes) < 2:
            return "ERROR: falta nombre del archivo",directorio_actual

        archivo = partes[1]

        try:

            #with open(archivo, "r", encoding="utf-8") as f:

            #este dcambio se hizo para que ahora ahora el cat busca en la carpeta donde esta el cliente y no en el server
            ruta = os.path.join(
            directorio_actual,
            archivo
                )

            with open(ruta, "r", encoding="utf-8") as f:




                contenido = f.read()

            if contenido == "":
                return "[Archivo vacío]",directorio_actual

            return contenido,directorio_actual

        except FileNotFoundError:

            return "ERROR: archivo no encontrado",directorio_actual

        except Exception as e:

            return f"ERROR: {e}",directorio_actual

    return "ERROR: comando no válido. Escriba 'help'", directorio_actual



# Cliente
def atender_cliente(conn, addr):

    #ahora cada  hilo tiene su propia copia de esta variable
    directorio_actual = os.getcwd()
    #evita errores
    usuario = None

    print(f"[NUEVA CONEXION] {addr}")

    #para que no se caigo todo si se va un cliente 
    try:

        #   

        usuario = conn.recv(1024).decode("utf-8").strip()

        password = conn.recv(1024).decode("utf-8").strip()
        #print(usuario ,"separado",password)

        #verifico el usuario dentro del diccionario 
        if not validar_usuario(usuario, password):
            conn.send("LOGIN_ERROR".encode("utf-8"))
            conn.close()
            #print(f"LOGIN FALLIDO# {addr}")
            return
        #si esta mal al contraseña o es diferente al usuario
        #if usuarios[usuario] != password:
            #conn.send("LOGIN_ERROR".encode("utf-8"))
            #conn.close()
            #print(f"[LOGIN_FALLIDO] {addr}")
            #return
        


        #si paso todo ok
        conn.send("LOGIN_OK".encode("utf-8"))

        #cuando ingresa un nuevo uusario lo guardo en el diccionario extra
        #cliente conectado
        lock_clientes = threading.Lock() ##aca agregue la exclusion mutua 
        with lock_clientes:
            clientes_conectados[usuario] = conn ####


        print(f"[LOGIN OK] {usuario} - {addr}")

        bienvenida = (
            f"\n Bienvenido {usuario}\n"
            "shell Remoto TUDA\n"
            "escriba 'help' para ver comandos\n"
        )

        conn.send(bienvenida.encode("utf-8"))

        while True:

            data = conn.recv(1024).decode("utf-8").strip()

            #cliente se desconecta
            if not data:
                break

            #muestro al usuario lo que mando y su nombre 
            print(f"[{usuario}] {data}")

            #si sale el usuario
            if data.lower() == "exit":
                conn.send(
                    "Conexión cerrada".encode("utf-8")
                )
                break

                #aca llamo a la funcion ejercutar_comando y hace lo que le pidieron, ls,pwd etc
            #respuesta = ejecutar_comando(data)

            #cambio para que ahora reciba comando y el directorio
            respuesta, directorio_actual = ejecutar_comando(
                data,
                directorio_actual
            )
            #envia al cliente la respuesta
            conn.send(
                respuesta.encode("utf-8")
            )
            #aca captura errores , cliente desconectado ,red caida
    except Exception as e:

        print(f"[ERROR] {addr}: {e}")

    finally:
        if usuario in clientes_conectados:
            with lock_clientes:
                del clientes_conectados[usuario] #####
        conn.close()

        print(f"[DESCONECTADO] {addr}")


#servidor

def iniciar_servidor():
    #creo los sockets TCP
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    #asocio el socket al puerto
    server.bind((HOST, PORT))
    #me pongo a escuchar
    server.listen(MAXCLIENTES)

    print(f"[SERVER] Escuchando en {HOST}:{PORT}")

    #hilo del admin para echar
    #ademas me permite escribir mientras esta funcionando el servidor
    admin_thread = threading.Thread(
        target=consola_admin,
        daemon=True
        #marca que el hilo es secundario y se cierra automaticamente 
    )

    admin_thread.start()
    try:
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
                #creo hilos por clientes 
            thread = threading.Thread(
                    target=atender_cliente,
                    args=(conn, addr)
                )

            thread.start()

            #muestro la cantidad de hilos activos
            print(
                    f"[HILOS ACTIVOS] {threading.active_count() - 1}"
                )
    except KeyboardInterrupt:

        print("\n[APAGANDO SERVIDOR]")

    finally:
        server.close()
    

if __name__ == "__main__":
    iniciar_servidor()