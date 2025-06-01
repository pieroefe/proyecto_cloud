#!/usr/bin/env python3

import json
import os
import sys

STATE_FILE = os.path.expanduser("~/proyecto/state.json")

def load_state():
    if not os.path.exists(STATE_FILE):
        print("[!] No se encontró el archivo de estado.")
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def draw_lineal(vms):
    result = ""
    for i, vm in enumerate(vms):
        result += f"{vm['name']}"
        if i < len(vms) - 1:
            vlan = vms[i]['vlan']
            result += f" -- vlan{vlan} -- "
    print(result)

def draw_ring(vms):
    result = ""
    n = len(vms)
    for i in range(n):
        vm = vms[i]
        next_vm = vms[(i + 1) % n]
        vlan = vms[i]['vlan']
        result += f"{vm['name']} -- vlan{vlan} --> {next_vm['name']}\n"
    print(result)

def draw_single(vms):
    print(f"{vms[0]['name']} (única VM)")

def draw_topology(slice_name):
    state = load_state()
    if not state or slice_name not in state["slices"]:
        print(f"[!] Slice '{slice_name}' no encontrado en state.json.")
        return

    vms = state["slices"][slice_name].get("vms", [])
    vlans = state["slices"][slice_name].get("vlans", [])

    if len(vms) == 1:
        draw_single(vms)
    elif len(vms) == 2:
        draw_lineal(vms)
    elif len(vms) >= 3:
        # Por defecto se asume tipo "ring" si hay 3 o más
        draw_ring(vms)
    else:
        print("[!] No hay VMs registradas para este slice.")

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 draw_topology.py <slice_name>")
        sys.exit(1)

    slice_name = sys.argv[1]
    print(f"\n🧭 Topología del slice '{slice_name}':\n")
    draw_topology(slice_name)

if __name__ == "__main__":
    main()
