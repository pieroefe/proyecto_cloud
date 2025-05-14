#!/usr/bin/env python3

import subprocess
import os
from pathlib import Path
import random
import string

# Ruta del archivo usuarios.db
USERS_DB = Path("/opt/silkroad/usuarios.db")
USERS_DIR = Path("/home")
MENU_PATH = "/opt/silkroad/menu_usuario.sh"

def leer_usuarios():
    """Leer el archivo usuarios.db y devolver los usuarios"""
    usuarios = {}
    try:
        with open(USERS_DB, "r") as f:
            for linea in f:
                if linea.strip() and not linea.startswith("#"):
                    usuario, rol = linea.strip().split(":")
                    if rol not in usuarios:
                        usuarios[rol] = []
                    usuarios[rol].append(usuario)
    except FileNotFoundError:
        print("[!] El archivo usuarios.db no existe.")
    return usuarios

def generar_contrasena(length=12):
    """Generar una contraseña aleatoria de longitud 'length'"""
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for i in range(length))

def agregar_usuario(usuario, rol):
    """Agregar un nuevo usuario al archivo usuarios.db y al sistema"""
    contrasena = generar_contrasena()  # Generar una contraseña aleatoria

    # Agregar al archivo usuarios.db
    with open(USERS_DB, "a") as f:
        f.write(f"{usuario}:{rol}\n")

    # Crear el usuario en el sistema
    subprocess.run(["sudo", "useradd", "-m", "-s", "/bin/rbash", usuario], check=True)

    # Establecer la contraseña
    subprocess.run(f"echo '{usuario}:{contrasena}' | sudo chpasswd", shell=True, check=True)

    print(f"[✔] Usuario '{usuario}' agregado con el rol '{rol}' y contraseña '{contrasena}'.")

    # Configurar el menú para usuarios con rol 'usuario_general'
    if rol == "usuario_general":
        configurar_menu(usuario)

def eliminar_usuario(usuario):
    """Eliminar un usuario del sistema y del archivo usuarios.db"""
    print(f"[+] Eliminando usuario '{usuario}'...")

    # Verificar si el usuario existe en el sistema antes de intentar eliminarlo
    try:
        subprocess.run(["id", usuario], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"[!] El usuario '{usuario}' no existe en el sistema.")
        return

    # Intentar eliminar procesos activos del usuario (si existen)
    try:
        subprocess.run(["pkill", "-u", usuario], check=True)
    except subprocess.CalledProcessError:
        print(f"[!] No se encontraron procesos activos para el usuario '{usuario}'.")

    # Eliminar el directorio de correo si existe
    correo_dir = f"/var/mail/{usuario}"
    if os.path.exists(correo_dir):
        subprocess.run(["sudo", "rm", "-rf", correo_dir])

    # Eliminar usuario del sistema
    try:
        subprocess.run(["sudo", "userdel", "-r", usuario], check=True)
    except subprocess.CalledProcessError:
        print(f"[!] No se pudo eliminar el usuario '{usuario}' del sistema.")
        return

    # Eliminar de usuarios.db
    with open(USERS_DB, "r") as f:
        lineas = f.readlines()

    with open(USERS_DB, "w") as f:
        for linea in lineas:
            if not linea.startswith(f"{usuario}:"):
                f.write(linea)

    print(f"[✔] Usuario '{usuario}' eliminado exitosamente.")

def validar_usuario(usuario):
    """Verificar si el usuario ya existe en el sistema"""
    usuarios = leer_usuarios()
    for rol in usuarios.values():
        if usuario in rol:
            return True
    return False

def listar_usuarios():
    """Listar todos los usuarios y sus roles"""
    usuarios = leer_usuarios()

    print(f"\n{'Rol':<20} {'Usuarios'}")
    print("-" * 40)

    for rol, usuarios_lista in usuarios.items():
        print(f"{rol:<20} {', '.join(usuarios_lista)}")

def configurar_menu(usuario):
    """Configura el archivo .bash_profile para ejecutar el menú"""
    home = USERS_DIR / usuario
    bash_profile = home / ".bash_profile"
    profile = home / ".profile"

    if not home.exists():
        print(f"[!] El directorio home de {usuario} no existe.")
        return

    # Contenido que queremos agregar
    contenido = f"""
# Ejecutar Silk Road menu al inicio de sesión
export PATH=$HOME/bin:$PATH
{MENU_PATH}
exit
"""

    # Si no existe .bash_profile, lo creamos
    if not bash_profile.exists():
        with open(bash_profile, "w") as f:
            f.write(contenido)
        print(f"[✔] Configurado .bash_profile para {usuario}")

    # Si no existe .profile, lo creamos
    if not profile.exists():
        with open(profile, "w") as f:
            f.write(contenido)
        print(f"[✔] Configurado .profile para {usuario}")

    # Asegurar permisos correctos
    subprocess.run(["chmod", "500", str(bash_profile)])
    subprocess.run(["chmod", "500", str(profile)])
    subprocess.run(["chown", "-R", f"{usuario}:{usuario}", str(home)])

def gestionar():
    """Gestión de usuarios: agregar, eliminar y listar usuarios"""
    while True:
        print("\nOpciones de gestión de usuarios:")
        print("1) Listar usuarios")
        print("2) Agregar usuario")
        print("3) Eliminar usuario")
        print("4) Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            # Listar usuarios
            listar_usuarios()

        elif opcion == "2":
            # Agregar usuario
            usuario = input("\nIngrese el nombre del nuevo usuario: ").strip()
            if not usuario:
                print("[!] El nombre de usuario no puede estar vacío.")
                continue

            if validar_usuario(usuario):
                print(f"[!] El usuario '{usuario}' ya existe.")
                continue

            rol = input("Ingrese el rol del usuario (administrador/usuario_general): ").strip().lower()

            if rol not in ["administrador", "usuario_general"]:
                print("[!] Rol inválido. Debe ser 'administrador' o 'usuario_general'.")
                continue

            agregar_usuario(usuario, rol)

        elif opcion == "3":
            # Eliminar usuario
            usuario_a_eliminar = input("\nIngrese el nombre de usuario a eliminar: ").strip()

            if not usuario_a_eliminar:
                print("[!] El nombre de usuario no puede estar vacío.")
                continue

            if not validar_usuario(usuario_a_eliminar):
                print(f"[!] El usuario '{usuario_a_eliminar}' no existe.")
                continue

            confirmacion = input(f"¿Está seguro de eliminar al usuario '{usuario_a_eliminar}'? (s/n): ").strip().lower()
            if confirmacion == 's':
                eliminar_usuario(usuario_a_eliminar)
            else:
                print("[!] Usuario no eliminado.")

        elif opcion == "4":
            print("Saliendo...")
            break

        else:
            print("[!] Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    gestionar()