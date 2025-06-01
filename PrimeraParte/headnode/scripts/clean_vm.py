#!/usr/bin/env python3

import subprocess
import sys

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return ""

def kill_qemu(vm_name):
    print(f"[+] Buscando proceso QEMU de '{vm_name}'...")
    qemu_list = run("ps aux | grep qemu-system | grep -v grep")
    for line in qemu_list.splitlines():
        if vm_name in line:
            pid = line.split()[1]
            subprocess.call(f"kill {pid}", shell=True)
            print(f"[✓] Proceso QEMU (PID {pid}) eliminado.")
            return True
    print("[!] No se encontró proceso QEMU para esa VM.")
    return False

def delete_tap(vm_name):
    tap_name = f"tap-{vm_name}"
    print(f"[+] Eliminando interfaz TAP '{tap_name}'...")
    result = subprocess.call(f"ip link delete {tap_name}", shell=True)
    if result == 0:
        print(f"[✓] Interfaz TAP '{tap_name}' eliminada.")
    else:
        print("[!] TAP no encontrada o ya eliminada.")

def delete_ovs_port(vm_name):
    print(f"[+] Buscando y eliminando puertos OVS relacionados con '{vm_name}'...")
    bridges = run("ovs-vsctl list-br").splitlines()
    for br in bridges:
        ports = run(f"ovs-vsctl list-ports {br}").splitlines()
        for port in ports:
            if vm_name in port or f"tap-{vm_name}" in port:
                subprocess.call(f"ovs-vsctl del-port {br} {port}", shell=True)
                print(f"[✓] Puerto '{port}' eliminado del bridge '{br}'.")
                return
    print("[!] No se encontraron puertos OVS relacionados.")

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 clean_vm.py <vm_name>")
        sys.exit(1)

    vm_name = sys.argv[1]

    killed = kill_qemu(vm_name)
    delete_ovs_port(vm_name)
    delete_tap(vm_name)

    print(f"\n✅ Limpieza completa de la VM '{vm_name}'.")

if __name__ == "__main__":
    main()
