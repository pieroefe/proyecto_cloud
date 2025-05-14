
#!/bin/bash

# Solicitar la cantidad de VMs a crear
read -p "¿Cuántas VMs deseas lanzar? " num_vms

# Verificar que el valor ingresado es un número positivo
if ! [[ "$num_vms" =~ ^[0-9]+$ ]] || [ "$num_vms" -le 0 ]; then
    echo "Por favor, ingresa un número positivo válido."
    exit 1
fi

# Definir la configuración de las VMs (nombre, recursos, etc.)
vm_name_prefix="ubuntu-vm"
memory="512"  # Memoria por VM en MB
vcpus="1"  # CPUs por VM
disk_path="/var/lib/libvirt/images/ubuntu-22.04.qcow2"
cloud_init_iso="/tmp/my-cloud-init.iso"
os_type="linux"
os_variant="generic"
network="network=default"
console="pty,target_type=serial"
connect="qemu+ssh://ubuntu@10.0.10.2/system"

# Función para verificar los recursos disponibles en un worker
check_resources() {
    worker_ip="$1"
    # Usamos 'virsh' para obtener la memoria total y libre, y el número de CPUs disponibles en el worker
    memory_total=$(ssh ubuntu@"$worker_ip" "free -m | awk '/^Mem:/ {print \$2}'")
    memory_free=$(ssh ubuntu@"$worker_ip" "free -m | awk '/^Mem:/ {print \$4}'")
    cpus_total=$(ssh ubuntu@"$worker_ip" "nproc")

    # Validar si hay recursos suficientes para agregar una VM
    if [ "$memory_free" -ge "$memory" ] && [ "$cpus_total" -ge "$vcpus" ]; then
        echo "$worker_ip tiene suficiente memoria y CPUs para agregar una VM."
        return 0  # Recursos suficientes
    else
        echo "$worker_ip no tiene suficientes recursos."
        return 1  # No tiene recursos suficientes
    fi
}

# Función para lanzar una VM en un worker específico
launch_vm() {
    vm_name="$1"
    worker_ip="$2"
    virt-install \
        --name "$vm_name" \
        --memory "$memory" \
        --vcpus "$vcpus" \
        --disk path="$disk_path",format=qcow2 \
        --disk path="$cloud_init_iso",device=cdrom \
        --os-type "$os_type" \
        --os-variant "$os_variant" \
        --network "$network" \
        --graphics none \
        --console "$console" \
        --import \
        --connect "qemu+ssh://ubuntu@$worker_ip/system" &
}

# Lista de workers disponibles
workers=("10.0.10.2" "10.0.10.3" "10.0.10.4")

# Lanzar múltiples VMs distribuidas entre los workers
for i in $(seq 1 "$num_vms"); do
    vm_name="${vm_name_prefix}-${i}"

    # Buscar un worker con recursos suficientes
    for worker_ip in "${workers[@]}"; do
        if check_resources "$worker_ip"; then
            echo "Lanzando VM: $vm_name en el worker $worker_ip"
            launch_vm "$vm_name" "$worker_ip"
            break  # Ya lanzamos la VM, salimos del ciclo de búsqueda de worker
        else
            echo "No se pudo lanzar la VM en el worker $worker_ip. Intentando en otro..."
        fi
    done
done

# Esperar a que todas las instancias de virt-install terminen
wait

echo "Todas las VMs han sido lanzadas exitosamente."