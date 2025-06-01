#!/bin/bash

# Lista todos los procesos qemu-system-x86_64 relacionados con VMs
ps aux | grep qemu-system-x86_64 | grep -v grep | while read -r line; do
    # Extrae el PID
    pid=$(echo "$line" | awk '{print $2}')

    # Extrae el nombre de la interfaz TAP (busca el argumento ifname=)
    ifname=$(echo "$line" | grep -oP 'ifname=\K[\w\-]+')

    echo "[INFO] Terminando VM PID $pid con interfaz $ifname"

    # Elimina el puerto del OVS (si existe)
    if ovs-vsctl list-ports br-int | grep -q "$ifname"; then
        echo "   > Quitando puerto $ifname del bridge br-int"
        sudo ovs-vsctl del-port br-int "$ifname"
    fi

    # Elimina la interfaz TAP si aún existe
    if ip link show "$ifname" &>/dev/null; then
        echo "   > Eliminando interfaz TAP $ifname"
        sudo ip link delete "$ifname"
    fi

    # Mata el proceso QEMU
    echo "   > Terminando proceso QEMU $pid"
    sudo kill -9 "$pid"
done

echo "[✔] Todas las VMs QEMU activas han sido terminadas."
