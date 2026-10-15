# PFO 2: Sistema de gestión de tareas con API y base de datos

**Alumno:** Juan Pablo Pontini  
**Carrera:** Tecnicatura Superior en Desarrollo de Software  
**Materia:** Programación sobre Redes  

---

## Descripción del proyecto

Para este trabajo práctico desarrollé una API REST utilizando **Flask** y persistencia en **SQLite**, incorporando autenticación básica y seguridad mediante el hasheo de contraseñas. Además, implementé un cliente interactivo por consola en Python para realizar las pruebas de los endpoints de manera directa.

### Estructura de archivos
* `servidor.py`: Código del servidor Flask con la lógica de base de datos y los endpoints requeridos.
* `cliente.py`: Cliente de consola interactivo para registrar usuarios, loguearse y consultar tareas.
* `capturas/`: Carpeta con las capturas de pantalla de las pruebas exitosas.
* `README.md`: Documentación con instrucciones de uso, explicación conceptual y guía de pruebas.

---

## Requisitos previos

Tener instalado Python 3 y las librerías necesarias:
```bash
pip install flask requests
```
*(Nota: `sqlite3` y `werkzeug` ya vienen integradas con la instalación estándar de Python y Flask).*

*(Nota de configuración: Para facilitar la ejecución y corrección directa de esta práctica, `secret_key` y `debug=True` se encuentran definidos dentro de `servidor.py`; en un entorno de producción real se gestionarían mediante variables de entorno).*

---

## Cómo ejecutar el proyecto

El proyecto se prueba fácilmente abriendo dos terminales en la carpeta del proyecto:

### 1. Iniciar el Servidor (Terminal 1)
```bash
python servidor.py
```
El servidor creará automáticamente la base de datos `tareas.db` (si no existe) y quedará escuchando peticiones en `http://localhost:5000`.

### 2. Ejecutar el cliente de consola (Terminal 2)
```bash
python cliente.py
```
Se abrirá un menú interactivo con las siguientes opciones:
1. **Registrar nuevo usuario:** Envía una petición `POST /registro` con el usuario y la contraseña ingresados.
2. **Iniciar sesión:** Envía una petición `POST /login`. Si las credenciales son correctas, mantiene la sesión activa en el cliente mediante cookies (`requests.Session`).
3. **Ver tareas:** Realiza un `GET /tareas` utilizando la sesión activa del cliente. Al recibir respuesta exitosa, el cliente guarda el contenido en el archivo local `bienvenida.html` y lo abre automáticamente en el navegador web. *(Aclaración: dado que la cookie de sesión vive en la instancia del cliente de consola, si se intenta ingresar a `http://localhost:5000/tareas` directamente desde el navegador sin haber iniciado sesión allí, el servidor devolverá `401 Unauthorized` — Acceso Denegado).*
4. **Salir.**

---

## Endpoints de la API

* **`POST /registro`**:
  * **Body (JSON):** `{"usuario": "Juampi", "contraseña": "1234"}`
  * **Respuesta:** Código `201 Created` y confirmación de registro. La contraseña se almacena hasheada en SQLite. Si el usuario ya existe, devuelve error `409 Conflict`.

* **`POST /login`**:
  * **Body (JSON):** `{"usuario": "Juampi", "contraseña": "1234"}`
  * **Respuesta:** Código `200 OK` si el usuario existe y el hash coincide; en caso contrario devuelve `401 Unauthorized`. Inicia la sesión del usuario.

* **`GET /tareas`**:
  * **Respuesta:** Código `200 OK`. Devuelve un documento HTML con un mensaje de bienvenida personalizado para el usuario con sesión activa. Si no hay sesión iniciada, deniega el acceso con código `401 Unauthorized`.

---

## Evidencias de pruebas

### 1. Registro de usuario (`POST /registro`)
Se probó el registro de un nuevo usuario (`Juampi`) enviando sus datos desde el cliente de consola:
![Registro exitoso](capturas/Captura%201%20-%20Registro%20exitoso.png)

### 2. Inicio de sesión (`POST /login`)
Se validaron las credenciales contra el hash almacenado en la base de datos SQLite y se obtuvo la confirmación de inicio de sesión:
![Login exitoso](capturas/Captura%202%20-%20Login%20exitoso.png)

### 3. Consulta de tareas y bienvenida HTML (`GET /tareas`)
Se consultó el endpoint protegido con la sesión activa desde el cliente y se visualizó la página de bienvenida personalizada renderizada en el navegador:
![HTML de bienvenida renderizado](capturas/Captura%203%20-%20HTML%20de%20bienvenida%20renderizado.png)

---

## Respuestas Conceptuales

### 1. ¿Por qué hashear contraseñas?
Hashear contraseñas es una práctica fundamental de seguridad porque **nunca se deben almacenar contraseñas en texto plano** en una base de datos. Si el servidor o la base de datos sufrieran una vulneración o filtración de datos, cualquier atacante que acceda al archivo obtendría de forma inmediata las claves reales de todos los usuarios.

Para evitar este riesgo, en este trabajo práctico utilicé una función hash criptográfica a través de la librería `werkzeug.security` (mediante `generate_password_hash`). Las características clave de este enfoque son:
* **Función unidireccional (de un solo sentido):** Una función hash convierte la contraseña en una cadena alfanumérica de longitud fija. A diferencia del cifrado tradicional, el hasheo es irreversible por diseño: no existe una fórmula matemática que permita descifrar o reconstruir la contraseña original a partir del hash generado.
* **Incorporación de Salt (sal aleatoria):** Las librerías modernas de hash añaden automáticamente un valor aleatorio único (*salt*) a cada contraseña antes de procesarla. Esto garantiza que dos usuarios con la misma contraseña tengan hashes totalmente diferentes, neutralizando ataques por tablas precalculadas (*rainbow tables*) o ataques de diccionario.
* **Verificación segura durante el login:** Al momento de autenticarse en el endpoint `/login`, el servidor no necesita desencriptar nada. Simplemente procesa la contraseña enviada por el cliente mediante `check_password_hash` y compara si el hash resultante coincide con el registrado en SQLite. De este modo, la contraseña real nunca se expone en la base de datos.

### 2. Ventajas de usar SQLite en este proyecto
Para el desarrollo y la implementación de este proyecto elegí **SQLite** como motor de base de datos debido a las siguientes ventajas técnicas:
* **Arquitectura Serverless (sin servidor independiente):** A diferencia de motores como MySQL o PostgreSQL, SQLite no requiere la instalación ni ejecución de un servicio o demonio corriendo de fondo en el sistema operativo. La base de datos corre de forma embebida en el mismo proceso de la aplicación Python.
* **Integrada en la biblioteca estándar de Python:** Viene incluida nativamente a través del módulo `sqlite3`, por lo que el proyecto no requiere controladores externos, drivers ODBC ni configuraciones de red complejas para comenzar a funcionar.
* **Portabilidad total:** Toda la base de datos (tablas y registros) se guarda en un único archivo local (`tareas.db`). Esto simplifica el transporte y la entrega del trabajo práctico, ya que el archivo se genera automáticamente al ejecutar el código sin depender de configuraciones previas en el entorno del docente.
* **Cumplimiento ACID y bajo consumo:** A pesar de ser liviana y no consumir memoria de fondo, SQLite cumple con los estándares ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad), garantizando la integridad de las transacciones al registrar usuarios y consultar tareas.