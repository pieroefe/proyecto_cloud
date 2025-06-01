#!/usr/bin/env python3

import sys
import subprocess

def run(cmd, check=True):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def create_vm(vm_name, vlan_id, vnc_port, bridge_name):
    tap_name = f"tap-{vm_name}"
    mac_addr = f"52:54:00:{(int(vlan_id) % 256):02x}:{(vnc_port % 256):02x}:{(abs(hash(vm_name)) % 256):02x}"

    # Crear bridge si no existe
    run(f"ovs-vsctl --may-exist add-br {bridge_name}")

    # Limpieza previa: eliminar tap y puerto OVS si ya existen
    run(f"ovs-vsctl del-port {bridge_name} {tap_name}", check=False)
    run(f"ip link del {tap_name}", check=False)

    # Crear interfaz TAP y agregar al bridge con VLAN tag
    run(f"ip tuntap add {tap_name} mode tap")
    run(f"ip link set {tap_name} up")
    run(f"ovs-vsctl add-port {bridge_name} {tap_name} tag={vlan_id}")

    # Lanzar la VM con QEMU
    run(
        f"qemu-system-x86_64 -enable-kvm -m 512 "
        f"-netdev tap,id=net0,ifname={tap_name},script=no,downscript=no "
        f"-device virtio-net-pci,netdev=net0,mac={mac_addr} "
        f"-drive file=/home/ubuntu/imagenes/debian12-login.qcow2,format=qcow2 "
        f"-vnc :{vnc_port} -daemonize -snapshot"
    )

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python3 create_vm.py <vm_name> <vlan_id> <vnc_port> <bridge_name>")
        sys.exit(1)

    vm_name = sys.argv[1]
    vlan_id = sys.argv[2]
    vnc_port = int(sys.argv[3])
    bridge_name = sys.argv[4]

    create_vm(vm_name, vlan_id, vnc_port, bridge_name)
