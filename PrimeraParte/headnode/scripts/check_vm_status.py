#!/usr/bin/env python3

import json
import subprocess
import os

STATE_FILE = os.path.expanduser("~/proyecto/state.json")

def load_state():
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def check_vm_on_worker(worker, vm_name):
    cmd = f"ssh {worker} \"pgrep -f 'qemu-system.*{vm_name}'\""
    try:
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        return output != ""
    except subprocess.CalledProcessError:
        return False

def main():
    state = load_state()
    slices = state.get("slices", {})

    if not slices:
        print("No hay slices activos.")
        return

    for slice_name, info in slices.items():
        print(f"\n🔹 Slice: {slice_name}")
        for vm in info.get("vms", []):
            name = vm["name"]
            worker = vm["worker"]
            alive = check_vm_on_worker(worker, name)
            status = "🟢 ACTIVA" if alive else "🔴 NO ACTIVA"
            print(f"   - {name} en {worker} → {status}")

if __name__ == "__main__":
    main()
