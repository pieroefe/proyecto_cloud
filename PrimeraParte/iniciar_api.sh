import requests
import json

API_URL = "http://10.0.10.99:8000"  # <-- cambia por IP real del headnode

# === LOGIN ===
def login():
    print("=== Iniciar sesión ===")
    user = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()

    response = requests.post(f"{API_URL}/login", json={"user": user, "password": password})
    if response.status_code == 200:
        print(f"[✓] Bienvenido {user}\n")
        return user  # Guardamos el nombre por si se necesita
    else:
        print("[!] Login inválido.")
        exit(1)

# === FUNCIONES ===

def lanzar_topologia(topologia):
    nombre = input("Nombre del slice: ").strip()
    data = {"name": nombre}
    r = requests.post(f"{API_URL}/deploy/{topologia}", json=data)
    print(r.json() if r.ok else r.text)

def eliminar_slice():
    nombre = input("Nombre del slice a eliminar: ").strip()
    r = requests.delete(f"{API_URL}/slice/{nombre}")
    print(r.json() if r.ok else r.text)

def ver_recursos_worker():
    r = requests.get(f"{API_URL}/resources")
    if r.ok:
        for worker, info in r.json().items():
            print(f"\n== {worker} ==")
            for k, v in info.items():
                print(f"{k}: {v}")
    else:
        print(r.text)

def listar_vms_por_worker():
    r = requests.get(f"{API_URL}/vms")
    if r.ok:
        for worker, vms in r.json().items():
            print(f"\n== VMs en {worker} ==")
            for vm in vms:
                print(f"  - {vm}")
    else:
        print(r.text)

def listar_slices_activos():
    r = requests.get(f"{API_URL}/slices")
    if r.ok:
        slices = r.json()
        if not slices:
            print("No hay slices activos.")
            return
        print("\n=== Slices activos ===")
        for s in slices:
            print(f"- {s}")
        print("======================")
    else:
        print(r.text)

def ver_estado_vms():
    nombre = input("Nombre del slice: ").strip()
    r = requests.get(f"{API_URL}/status/{nombre}")
    if r.ok:
        estado = r.json()
        print(f"\n=== Estado de VMs en '{nombre}' ===")
        for vm, est in estado.items():
            simbolo = "🟢" if est == "activo" else "🔴"
            print(f"  {vm}: {simbolo} {est}")
    else:
        print(r.text)

def ver_log_slice():
    nombre = input("Nombre del slice: ").strip()
    r = requests.get(f"{API_URL}/logs/{nombre}")
    if r.ok:
        print(f"\n=== Log de {nombre} ===\n")
        print(r.json()["log"])
        print("=============================\n")
    else:
        print(r.text)

# === MENÚ ===
def menu():
    login()

    while True:
        print("=== Silkroad Remote Orchestrator ===")
        print("1) Lanzar topología SINGLE")
        print("2) Lanzar topología LINEAL")
        print("3) Lanzar topología ANILLO")
        print("4) Eliminar una topología")
        print("5) Ver recursos por worker")
        print("6) Listar VM's por worker")
        print("7) Listar slices activos")
        print("8) Ver estado de VMs")
        print("9) Ver log de un slice")
        print("10) Salir")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            lanzar_topologia("single")
        elif opcion == "2":
            lanzar_topologia("lineal")
        elif opcion == "3":
            lanzar_topologia("anillo")
        elif opcion == "4":
            eliminar_slice()
        elif opcion == "5":
            ver_recursos_worker()
        elif opcion == "6":
            listar_vms_por_worker()
        elif opcion == "7":
            listar_slices_activos()
        elif opcion == "8":
            ver_estado_vms()
        elif opcion == "9":
            ver_log_slice()
        elif opcion == "10":
            print("Saliendo...")
            break
        else:
            print("[!] Opción no válida.")

if __name__ == "__main__":
    menu()
