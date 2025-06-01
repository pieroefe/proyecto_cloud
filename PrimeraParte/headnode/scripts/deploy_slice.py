#!/usr/bin/env python3

import json
import sys
import subprocess
from utils import allocator
from utils import logger

def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def main(json_file):
    with open(json_file) as f:
        data = json.load(f)

    slice_name = data["slice_name"]
    topology = data["topology"]
    num_vms = data["num_vms"]
    dhcp_bridge = data["dhcp_bridge"]

    if topology == "lineal":
        num_links = num_vms - 1
    elif topology == "ring":
        num_links = num_vms
    elif topology == "single":
        num_links = 1
    else:
        print(f"[!] Topología no reconocida: {topology}")
        sys.exit(1)

    vlan_ids = allocator.assign_vlan_ids(slice_name, num_links)

    for vlan_id in vlan_ids:
        cidr = f"192.168.{vlan_id}.0/24"
        dhcp_start = f"192.168.{vlan_id}.10"
        dhcp_end = f"192.168.{vlan_id}.100"
        run(f"sudo python3 scripts/ensure_dhcp_vlan.py {vlan_id} {cidr} {dhcp_start} {dhcp_end} {dhcp_bridge}")

    workers = ["worker1", "worker2", "worker3"]
    vm_list = []

    for i in range(num_vms):
        vm_name = allocator.generate_vm_name(slice_name, i)
        vnc_port = allocator.get_free_vnc_port()
        worker = workers[i % len(workers)]
        vlan_id = vlan_ids[i % len(vlan_ids)]
        bridge = f"br-{slice_name}"

        remote_cmd = f"sudo python3 ~/proyecto/scripts/create_vm.py {vm_name} {vlan_id} {vnc_port} {bridge}"
        run(f"ssh {worker} '{remote_cmd}'")

        logger.log_action(slice_name, f"Desplegada VM {vm_name} en {worker} (VLAN {vlan_id}, VNC {vnc_port})")

        vm_list.append({
            "name": vm_name,
            "worker": worker,
            "vlan": vlan_id,
            "vnc": vnc_port
        })

    state = allocator.load_state()
    if slice_name not in state["slices"]:
        state["slices"][slice_name] = {}
    state["slices"][slice_name]["vms"] = vm_list
    allocator.save_state(state)

    print(f"\n✅ Slice '{slice_name}' desplegado con {num_vms} VM(s). Puedes acceder por VNC en los puertos 590X.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 deploy_slice.py <archivo_slice.json>")
        sys.exit(1)

    main(sys.argv[1])
