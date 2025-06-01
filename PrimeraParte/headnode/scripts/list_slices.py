#!/usr/bin/env python3

import json
import os

STATE_FILE = os.path.expanduser("~/proyecto/state.json")

def load_state():
    if not os.path.exists(STATE_FILE):
        print("[!] No se encontró el archivo de estado.")
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def list_slices():
    state = load_state()
    if state is None or "slices" not in state or not state["slices"]:
        print("No hay slices activos.")
        return

    print("🧩 Slices activos:\n")
    for slice_name, info in state["slices"].items():
        print(f"🔹 Slice: {slice_name}")
        vlans = info.get("vlans", [])
        print(f"   VLANs: {', '.join(map(str, vlans)) if vlans else 'N/A'}")

        vms = info.get("vms", [])
        if not vms:
            print("   [!] No se registraron VMs para este slice.")
            continue

        print("   VMs:")
        for vm in vms:
            print(f"     - {vm['name']} (Worker: {vm['worker']}, VLAN: {vm['vlan']}, VNC: {vm['vnc']})")
        print()

def main():
    list_slices()

if __name__ == "__main__":
    main()
