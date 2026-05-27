import socket
#es para que no sea vea la clave je
from getpass import getpass

HOST = '10.7.224.12'   
PORT = 65000




def iniciar_cliente():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

        client.connect((HOST, PORT))

        print("[CONECTADO AL SERVIDOR]\n")
        
        #pantalla de login del cli
        usuario = input("Usuario: ")
        client.send(usuario.encode("utf-8"))

        password = input("Contraseña: ")
        client.send(password.encode("utf-8"))

        login = client.recv(1024).decode("utf-8")

        if login != "LOGIN_OK":
            print("Usuario o contraseña incorrectos")
            return

        print("login exitoso")
        ####
        
        #entrada
        bienvenida = client.recv(1024).decode("utf-8")

        print(bienvenida)

        while True:
            comando = input("shell> ")

            client.send(comando.encode("utf-8"))
            respuesta = client.recv(1024).decode("utf-8")

            print("\n" + respuesta + "\n")
            if comando.lower() == "exit":
                break

    except ConnectionRefusedError:

        print("No se pudo conectar al servidor")

    except Exception as e:

        print(f"ERROR: {e}")

    finally:

        client.close()
        print("[CONEXION CERRADA]")

if __name__ == "__main__":
    iniciar_cliente()