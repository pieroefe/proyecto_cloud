#!/usr/bin/env python3

import json
import sys
import os
import subprocess
from utils import logger

STATE_FILE = os.path.expanduser("~/proyecto/state.json")


def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def load_state():
    if not os.path.exists(STATE_FILE):
        print("[!] No se encontró el archivo de estado.")
        sys.exit(1)
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def delete_slice(slice_name):
    state = load_state()
    if slice_name not in state["slices"]:
        print(f"[!] Slice '{slice_name}' no está registrado.")
        return

    slice_data = state["slices"][slice_name]
    vms = slice_data.get("vms", [])
    vlans = slice_data.get("vlans", [])
    bridge_name = f"br-{slice_name}"

    vms_por_worker = {}

    for vm in vms:
        vm_name = vm["name"]
        worker = vm["worker"]
        print(f"[+] Eliminando VM '{vm_name}' en {worker}...")
        ssh_cmd = f"ssh {worker} 'sudo python3 ~/proyecto/scripts/clean_vm.py {vm_name}'"
        run(ssh_cmd)
        logger.log_action(slice_name, f"Eliminada VM {vm_name} de {worker}")
        vms_por_worker.setdefault(worker, 0)
        vms_por_worker[worker] += 1

    for worker in vms_por_worker:
        print(f"[\u2022] Eliminando bridge '{bridge_name}' en {worker}...")
        ssh_cmd = f"ssh {worker} 'sudo ovs-vsctl --if-exists del-br {bridge_name}'"
        run(ssh_cmd)

    state["used_vlans"] = [v for v in state.get("used_vlans", []) if v not in vlans]
    state["used_vnc_ports"] = [p for p in state.get("used_vnc_ports", []) if p not in [vm["vnc"] for vm in vms]]
    del state["slices"][slice_name]
    save_state(state)

    logger.log_action(slice_name, f"Slice eliminado y recursos liberados.")

    # Eliminar archivo .json del slice
    slice_json_path = os.path.expanduser(f"~/proyecto/slices/{slice_name}.json")
    if os.path.exists(slice_json_path):
        os.remove(slice_json_path)
        print(f"[\ud83d\uddd1\ufe0f] Archivo {slice_name}.json eliminado.")

    print(f"\n✅ Slice '{slice_name}' eliminado correctamente.")


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 delete_slice.py <slice_name>")
        sys.exit(1)

    delete_slice(sys.argv[1])


if __name__ == "__main__":
    main()
