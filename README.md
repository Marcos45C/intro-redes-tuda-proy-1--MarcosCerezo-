Se crearon dos maquinas virtuales, asignando la ip 192.168.50.10 como servidor y como cliente 192.168.50.11.

# Proyecto 1 - Shell remoto multihilo

## Descripcon
Este proyecto implementa un shell remoto limitado utilizando sockets TCP y multithreading en Python.
El servidor permite la conexión simultánea de múltiples clientes y soporta los comandos:
- ls
- pwd
- cat
- exit

## Comunicacion de socket
La comunicación se implemento utilizando sockets TCP.
El cliente envía comandos al servidor mediante send() y el servidor responde utilizando recv() y send().
Cada mensaje es codificado usando UTF-8.

## Manejo de hilos
El servidor utiliza la librería threading para manejar múltiples clientes simultaneamente.
Cada vez que un cliente se conecta, el servidor crea un nuevo hilo utilizando:
threading.Thread()
Cada hilo ejecuta la funcion encargada de atender al cliente
## Ejecucion
#Servidor
python3 proy-1-server.py

#Cliente
python3 proy-1-client.py

## Diagrama flujo
Cliente
   ↓
Socket TCP
   ↓
Servidor
   ↓
Thread
   ↓
Ejecución comando
   ↓
Respuesta
