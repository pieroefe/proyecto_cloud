# menu.py - Menú principal del orquestador Silkroad

import os
import json
import subprocess
from datetime import datetime

SLICES_DIR = os.path.expanduser("~/proyecto/slices")
STATE_FILE = os.path.expanduser("~/proyecto/state.json")
LOGS_DIR = os.path.expanduser("~/proyecto/logs")
WORKERS = ["worker1", "worker2", "worker3"]

def run_python(script, args=""):
    os.system(f"python3 scripts/{script} {args}".strip())

def registrar_log(nombre, accion, info):
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f"{nombre}.log")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vlans = info.get("vlans", [])
    vms = info.get("vms", [])

    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] Acción: {accion}\n")
        f.write(f"VLAN(s): {', '.join(map(str, vlans))}\n")
        for vm in vms:
            vm_name = vm.get("name", "sin_nombre")
            worker = vm.get("worker", "no especificado")
            f.write(f"  - {vm_name} en {worker}\n")
        f.write("\n")

def crear_slice(nombre, topologia):
    os.makedirs(SLICES_DIR, exist_ok=True)

    if topologia == "single":
        num_vms = 1
    elif topologia == "lineal":
        num_vms = 2
    elif topologia == "anillo":
        num_vms = 3
    else:
        print("[!] Topología no reconocida.")
        return

    slice_file = os.path.join(SLICES_DIR, f"{nombre}.json")
    vms = {}

    for i in range(num_vms):
        vm_name = f"{nombre}-vm{i+1}"
        vms[vm_name] = {
            "vm_name": vm_name,
            "worker": WORKERS[i % len(WORKERS)]
        }

    slice_data = {
        "nombre": nombre,
        "topologia": topologia,
        "vms": vms
    }

    with open(slice_file, "w") as f:
        json.dump(slice_data, f, indent=2)

    registrar_log(nombre, "CREAR", slice_data)
    run_python("deploy_slice.py", slice_file)

def eliminar_slice():
    if not os.path.exists(STATE_FILE):
        print("[!] No hay slices activos.")
        return

    with open(STATE_FILE, 'r') as f:
        try:
            state = json.load(f)
            slices = state.get("slices", {})
        except json.JSONDecodeError:
            print("[!] Error al leer el archivo state.json.")
            return

    if not slices:
        print("[!] No hay slices activos.")
        return

    nombres_slices = list(slices.keys())

    print("\n=== Slices Activos ===")
    for i, name in enumerate(nombres_slices, 1):
        print(f"{i}) {name}")
    print("0) Cancelar")

    try:
        opcion = int(input("Selecciona un slice para eliminar: ").strip())
    except ValueError:
        print("[!] Entrada no válida.")
        return

    if opcion == 0:
        print("Operación cancelada.")
        return

    if opcion < 1 or opcion > len(nombres_slices):
        print("[!] Selección fuera de rango.")
        return

    nombre = nombres_slices[opcion - 1]
    slice_file = os.path.join(SLICES_DIR, f"{nombre}.json")

    if not os.path.exists(slice_file):
        print(f"[!] Archivo del slice '{nombre}' no encontrado.")
        return

    with open(slice_file, "r") as f:
        slice_data = json.load(f)

    registrar_log(nombre, "ELIMINAR", slice_data)
    run_python("delete_slice.py", slice_file)
    os.remove(slice_file)
    print(f"[\u2713] Slice '{nombre}' eliminado correctamente.")

def ver_recursos_worker():
    for worker in WORKERS:
        print(f"\n== Recursos en {worker} ==")
        os.system(f"ssh {worker} free -h | grep Mem")

def listar_vms_por_worker():
    for worker in WORKERS:
        print(f"\n== VMs en {worker} ==")

        try:
            cmd = f"ssh {worker} ps aux | grep qemu-system | grep -v grep"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()

            if not output.strip():
                print("  (No hay VMs activas)")
                continue

            for line in output.strip().split("\n"):
                vm_name = "desconocido"
                vnc_port = "?"

                if "ifname=tap-" in line:
                    parte = line.split("ifname=tap-")[-1]
                    vm_name = parte.split(",")[0]

                if "-vnc" in line:
                    parte = line.split("-vnc")[-1].strip()
                    vnc_port = parte.split()[0]

                print(f"  {vm_name:<20} | VNC {vnc_port}")
        except Exception as e:
            print(f"  [!] Error en {worker}: {e}")

def listar_slices_activos():
    if not os.path.exists(STATE_FILE):
        print("No hay slices activos.")
        return

    with open(STATE_FILE, 'r') as f:
        try:
            state = json.load(f)
        except json.JSONDecodeError:
            print("[!] Error: El archivo state.json está corrupto o vacío.")
            return

    slices = state.get("slices", {})
    if not slices:
        print("No hay slices activos.")
        return

    print("\n=== Slices Activos ===")
    for slice_name, info in slices.items():
        vms = info.get("vms", [])
        num_vms = len(vms)
        workers = sorted({vm["worker"] for vm in vms if "worker" in vm})

        print(f"\nNombre del slice: {slice_name}")
        print(f"Número de VMs: {num_vms}")
        print(f"Workers involucrados: {', '.join(workers) if workers else 'No especificado'}")
    print("======================\n")

def ver_estado_vms():
    if not os.path.exists(STATE_FILE):
        print("No hay slices activos.")
        return

    with open(STATE_FILE, 'r') as f:
        try:
            state = json.load(f)
        except json.JSONDecodeError:
            print("[!] Error: El archivo state.json está corrupto o vacío.")
            return

    slices = state.get("slices", {})
    if not slices:
        print("No hay slices activos.")
        return

    print("\n=== Estado de VMs Activas ===")
    for slice_name, info in slices.items():
        print(f"\nSlice: {slice_name}")

        vms = info.get("vms", [])
        if not vms:
            print("  No hay VMs registradas.")
            continue

        for vm in vms:
            vm_name = vm.get("name", "sin_nombre")
            worker = vm.get("worker", "desconocido")

            cmd = f"ssh {worker} pgrep -f 'qemu-system.*{vm_name}'"
            result = os.system(cmd + " > /dev/null 2>&1")
            estado = "🟢 Activa" if result == 0 else "🔴 Inactiva"
            print(f"  {vm_name} en {worker}: {estado}")
    print("=============================\n")

def ver_log_slice():
    if not os.path.exists(LOGS_DIR):
        print("No hay logs disponibles.")
        return

    logs = sorted([f for f in os.listdir(LOGS_DIR) if f.endswith(".log")])
    if not logs:
        print("No hay logs disponibles.")
        return

    print("\n=== Logs disponibles ===")
    for i, log in enumerate(logs, 1):
        print(f"{i}) {log}")
    print("0) Cancelar")

    try:
        opcion = int(input("Selecciona un log para ver: ").strip())
    except ValueError:
        print("[!] Entrada no válida.")
        return

    if opcion == 0:
        print("Operación cancelada.")
        return

    if opcion < 1 or opcion > len(logs):
        print("[!] Selección fuera de rango.")
        return

    log_file = os.path.join(LOGS_DIR, logs[opcion - 1])
    print(f"\n=== Contenido de {logs[opcion - 1]} ===")
    with open(log_file, "r") as f:
        print(f.read())
    print("===============================\n")

# Menú principal
while True:
    print("=== Silkroad Orchestrator ===")
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
        nombre = input("Nombre del slice: ").strip()
        crear_slice(nombre, "single")
    elif opcion == "2":
        nombre = input("Nombre del slice: ").strip()
        crear_slice(nombre, "lineal")
    elif opcion == "3":
        nombre = input("Nombre del slice: ").strip()
        crear_slice(nombre, "anillo")
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
        print("[!] Opción no válida. Intenta nuevamente.")
