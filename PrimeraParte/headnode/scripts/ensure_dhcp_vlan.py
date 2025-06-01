#!/usr/bin/env python3

import subprocess
import sys
import os

def run(cmd, check=True):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def namespace_exists(ns):
    return os.path.exists(f"/run/netns/{ns}")

def ensure_dhcp_vlan(vlan_id, cidr, dhcp_start, dhcp_end, iface_bridge):
    ns = f"ns-vlan{vlan_id}"
    veth_host = f"veth{vlan_id}"
    veth_ns = f"veth{vlan_id}-ns"
    ip_gw = cidr.split('/')[0]

    # 🔁 Limpieza previa si ya existen namespace o veths
    if namespace_exists(ns):
        print(f"⚠️ Namespace {ns} ya existe. Eliminando...")
        run(f"ip netns delete {ns}", check=False)

    run(f"ip link del {veth_host}", check=False)
    run(f"ovs-vsctl del-port {iface_bridge} {veth_host}", check=False)

    # 🧱 Crear namespace y veth
    run(f"ip netns add {ns}")
    run(f"ip link add {veth_host} type veth peer name {veth_ns}")
    run(f"ip link set {veth_ns} netns {ns}")

    # Activar lado host y agregar al bridge
    run(f"ip link set {veth_host} up")
    run(f"ovs-vsctl add-port {iface_bridge} {veth_host} tag={vlan_id}")

    # Configurar lado namespace
    run(f"ip netns exec {ns} ip link set dev lo up")
    run(f"ip netns exec {ns} ip link set dev {veth_ns} up")
    run(f"ip netns exec {ns} ip address add {ip_gw} dev {veth_ns}")

    # Levantar dnsmasq
    run(
        f"ip netns exec {ns} dnsmasq --interface={veth_ns} "
        f"--bind-interfaces --dhcp-range={dhcp_start},{dhcp_end},255.255.255.0,24h "
        f"--dhcp-option=3,{ip_gw} --no-daemon &"
    )

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Uso: sudo python3 ensure_dhcp_vlan.py <VLAN_ID> <CIDR> <DHCP_START> <DHCP_END> <BRIDGE>")
        sys.exit(1)

    vlan_id = sys.argv[1]
    cidr = sys.argv[2]
    dhcp_start = sys.argv[3]
    dhcp_end = sys.argv[4]
    iface_bridge = sys.argv[5]

    ensure_dhcp_vlan(vlan_id, cidr, dhcp_start, dhcp_end, iface_bridge)
