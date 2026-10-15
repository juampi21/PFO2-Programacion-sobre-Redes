import requests
import sys
import webbrowser
from pathlib import Path

URL_BASE = "http://localhost:5000"

# Usamos Session para mantener las cookies de autenticacion tras el login
sesion = requests.Session()


def registrar_usuario():
    print("\n--- Registro de Usuario ---")
    usuario = input("Ingrese nombre de usuario: ").strip()
    password = input("Ingrese contraseña: ").strip()

    if not usuario or not password:
        print("El usuario y la contraseña no pueden estar vacíos.")
        return

    payload = {
        "usuario": usuario,
        "contraseña": password
    }

    try:
        respuesta = sesion.post(f"{URL_BASE}/registro", json=payload)
        datos = respuesta.json()

        if respuesta.status_code == 201:
            print(f"[OK] {datos.get('mensaje')}")
        else:
            print(f"[ERROR {respuesta.status_code}] {datos.get('error')}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar con el servidor. ¿Está encendido servidor.py?")


usuario_conectado = None


def iniciar_sesion():
    global usuario_conectado
    print("\n--- Inicio de Sesión ---")
    usuario = input("Ingrese su usuario: ").strip()
    password = input("Ingrese su contraseña: ").strip()

    if not usuario or not password:
        print("El usuario y la contraseña no pueden estar vacíos.")
        return

    payload = {
        "usuario": usuario,
        "contraseña": password
    }

    try:
        respuesta = sesion.post(f"{URL_BASE}/login", json=payload)
        datos = respuesta.json()

        if respuesta.status_code == 200:
            usuario_conectado = datos.get("usuario")
            print(f"[OK] {datos.get('mensaje')} - ¡Bienvenido {usuario_conectado}!")
        else:
            print(f"[ERROR {respuesta.status_code}] {datos.get('error')}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar con el servidor. ¿Está encendido servidor.py?")


def consultar_tareas():
    print("\n--- Consultando Tareas (GET /tareas) ---")
    try:
        respuesta = sesion.get(f"{URL_BASE}/tareas")

        if respuesta.status_code == 200:
            print(f"[OK 200] Acceso concedido para: {usuario_conectado or 'Usuario'}")
            print("El servidor devolvió el HTML de bienvenida personalizado.")
            
            # Guardamos el HTML devuelto por la sesión autenticada y lo abrimos de forma segura en Windows
            archivo_html = Path("bienvenida.html")
            archivo_html.write_text(respuesta.text, encoding="utf-8")
            
            print("Abriendo el HTML en el navegador para visualizarlo...")
            webbrowser.open(archivo_html.resolve().as_uri())
            
            input("\nPresione Enter para volver al menú principal...")
        elif respuesta.status_code == 401:
            print("[ERROR 401] Acceso denegado: Primero debés iniciar sesión con la opción 2.")
        else:
            print(f"[RESPUESTA {respuesta.status_code}] Código de estado inesperado.")

    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar con el servidor. ¿Está encendido servidor.py?")


def menu():
    while True:
        print("\n==============================")
        print(" SISTEMA DE GESTIÓN DE TAREAS ")
        print("       Cliente de Consola     ")
        print("==============================")
        print("1. Registrar nuevo usuario")
        print("2. Iniciar sesión")
        print("3. Ver tareas (HTML bienvenida)")
        print("4. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            consultar_tareas()
        elif opcion == "4":
            print("Saliendo del cliente. ¡Hasta luego!")
            sys.exit(0)
        else:
            print("Opción inválida, por favor elija entre 1 y 4.")


if __name__ == "__main__":
    menu()
