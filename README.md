# Proyecto 1 - Shell Remoto Multihilo

Alumno: Marcos Cerezo

Materia: Introducción a las Redes

---

## Descripción

Este proyecto implementa un Shell Remoto Multihilo utilizando sockets TCP en Python.

Permite que múltiples clientes se conecten simultáneamente a un servidor y ejecuten comandos remotos mediante una consola interactiva.

Cada cliente es atendido mediante un hilo independiente, permitiendo conexiones concurrentes.

---

## Comunicación mediante sockets

La comunicación se implementa utilizando sockets TCP.

Servidor:

```python
socket(AF_INET, SOCK_STREAM)
```

Cliente:

```python
socket(AF_INET, SOCK_STREAM)
```

Proceso:

1. El servidor crea un socket.
2. Realiza bind sobre IP y puerto.
3. Comienza la escucha mediante listen().
4. El cliente realiza connect().
5. El servidor acepta la conexión mediante accept().
6. Cliente y servidor intercambian mensajes mediante send() y recv().
7. La conexión finaliza mediante close().

---

## Gestión de hilos

Cada cliente conectado genera un hilo independiente.

```python
thread = threading.Thread(
    target=atender_cliente,
    args=(conn, addr)
)

thread.start()
```

Esto permite que varios clientes ejecuten comandos simultáneamente sin bloquear el servidor.

---

## Sistema de autenticación

Al conectarse, el servidor solicita:

- Usuario
- Contraseña

La contraseña es ingresada de forma oculta utilizando:

```python
getpass()
```

Si las credenciales son incorrectas:

- Se informa el error.
- Se cierra la conexión.

---

## Comandos disponibles

### help

Muestra ayuda de comandos.

Ejemplo:

```text
help
```

---

### pwd

Muestra el directorio actual del servidor.

Ejemplo:

```text
pwd
```

---

### ls

Lista archivos y directorios.

Ejemplo:

```text
ls
```

---

### ls ruta

Lista el contenido de una ruta específica.

Ejemplo:

```text
ls /tmp
```

---

### ls -l

Listado detallado.

Ejemplo:

```text
ls -l
```

---

### ls -lh

Listado detallado con tamaños legibles.

Ejemplo:

```text
ls -lh
```

---

### mkdir

Crea un directorio.

Ejemplo:

```text
mkdir pruebas
```

---

### cat

Muestra el contenido de un archivo.

Ejemplo:

```text
cat archivo.txt
```

---

### exit

Finaliza la sesión.

Ejemplo:

```text
exit
```

---

## Ejecución

### Servidor

```bash
python3 proy-1-servidor.py
```

Salida:

```text
[SERVER] Escuchando en 0.0.0.0:65000
```

---

### Cliente

```bash
python3 proy-1-cliente.py
```

Ingreso:

```text
Usuario:
Contraseña:
```

Luego:

```text
shell>
```

---

## Flujo de datos

Cliente
|
| connect()
v
Servidor
|
| login
v
Autenticación
|
| recv()
v
Procesamiento comando
|
| send()
v
Cliente

---

## Tecnologías utilizadas

- Python 3
- Socket TCP
- Threading
- OS
- Datetime
- Getpass
