from flask import Flask, request, jsonify, render_template_string, session
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Clave para firmar cookies de sesión (en un entorno productivo se obtendría de os.environ)
app.secret_key = "clave_secreta_pfo2_redes"

# Ruta absoluta a tareas.db en la misma carpeta donde está servidor.py
DB_PATH = Path(__file__).resolve().parent / "tareas.db"


def conectar_bd():
    # Conecta con la base de datos SQLite y devuelve la conexion
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_bd():
    # Crea las tablas necesarias si no existen
    conexion = conectar_bd()
    cursor = conexion.cursor()

    # Tabla de usuarios con la contraseña hasheada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Tabla de tareas para asociar al usuario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            completada INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conexion.commit()
    conexion.close()


# Garantizamos que las tablas existan siempre al cargar el servidor
inicializar_bd()


@app.route("/registro", methods=["POST"])
def registro():
    # Endpoint para registrar un nuevo usuario
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se esperaba un cuerpo en formato JSON"}), 400

    # Obtenemos usuario y contraseña (permitimos 'contraseña' o 'contrasenia')
    usuario = datos.get("usuario")
    password = datos.get("contraseña") or datos.get("contrasenia") or datos.get("password")

    if not usuario or not password:
        return jsonify({"error": "Debe ingresar usuario y contraseña"}), 400

    # Hasheamos la contraseña antes de guardarla en la base de datos
    password_hasheada = generate_password_hash(password)

    conexion = None
    try:
        # Aseguramos que la tabla exista por si se borró tareas.db con el servidor encendido
        inicializar_bd()
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
            (usuario, password_hasheada)
        )
        conexion.commit()

        return jsonify({
            "mensaje": f"Usuario '{usuario}' registrado con éxito"
        }), 201

    except sqlite3.IntegrityError:
        # Ocurre si el nombre de usuario ya existe en la base
        return jsonify({"error": f"El usuario '{usuario}' ya existe"}), 409
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    finally:
        if conexion:
            conexion.close()


@app.route("/login", methods=["POST"])
def login():
    # Endpoint para iniciar sesion y verificar credenciales
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se esperaba un cuerpo en formato JSON"}), 400

    usuario = datos.get("usuario")
    password = datos.get("contraseña") or datos.get("contrasenia") or datos.get("password")

    if not usuario or not password:
        return jsonify({"error": "Debe ingresar usuario y contraseña"}), 400

    inicializar_bd()
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    usuario_db = cursor.fetchone()
    conexion.close()

    # Si el usuario no existe o la contraseña no coincide con el hash
    if not usuario_db or not check_password_hash(usuario_db["password_hash"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Guardamos el usuario en la sesión para permitir el acceso a las tareas
    session["usuario_id"] = usuario_db["id"]
    session["usuario"] = usuario_db["usuario"]

    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "usuario": usuario_db["usuario"]
    }), 200


@app.route("/tareas", methods=["GET"])
def tareas():
    # Endpoint que devuelve un HTML de bienvenida para usuarios autenticados
    usuario_logeado = session.get("usuario")

    # Si no inicio sesion, deniega el acceso como pide la consigna
    if not usuario_logeado:
        html_sin_sesion = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Acceso Denegado</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f6f9; text-align: center; padding-top: 60px; }
                .card { background: white; max-width: 450px; margin: auto; padding: 30px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
                h1 { color: #d9534f; margin-top: 0; }
                p { color: #666; font-size: 16px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Acceso Denegado (401)</h1>
                <p>No tenés una sesión activa. Debés iniciar sesión mediante <code>POST /login</code> para acceder a las tareas.</p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html_sin_sesion), 401

    # Si esta autenticado, muestra el HTML de bienvenida personalizado con su nombre
    html_bienvenida = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Gestión de Tareas - PFO 2</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 40px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; margin-top: 0; }
            .badge { display: inline-block; background-color: #27ae60; color: white; padding: 5px 12px; border-radius: 15px; font-size: 14px; }
            p { color: #555; line-height: 1.6; }
            .info-box { background-color: #eaf2f8; border-left: 4px solid #3498db; padding: 12px 16px; margin: 20px 0; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">Sesión Activa</span>
            <h1>¡Bienvenido/a, {{ usuario }}!</h1>
            <p>Has iniciado sesión correctamente en el <strong>Sistema de Gestión de Tareas</strong> (PFO 2).</p>
            
            <div class="info-box">
                <strong>Estado:</strong> Autenticación validada exitosamente con contraseñas hasheadas en SQLite.
            </div>

            <p>Acceso concedido a las tareas del usuario <strong>{{ usuario }}</strong>.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_bienvenida, usuario=usuario_logeado)


if __name__ == "__main__":
    inicializar_bd()
    print("Iniciando servidor API Flask en http://localhost:5000 ...")
    app.run(host="localhost", port=5000, debug=True, use_reloader=False)
