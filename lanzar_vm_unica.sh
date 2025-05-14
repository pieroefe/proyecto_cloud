
#!/bin/bash

# Definir las direcciones IP de los workers
WORKER1="10.0.10.2"
WORKER2="10.0.10.3"
WORKER3="10.0.10.4"

# Comando para verificar la memoria disponible en cada worker
check_memory() {
    ssh ubuntu@$1 "free -m | grep Mem | awk '{print \$4}'"
}

# Comando para verificar la carga de CPU en cada worker
check_cpu() {
    ssh ubuntu@$1 "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - $1}'"
}

# Obtener memoria disponible en cada worker
mem_worker1=$(check_memory $WORKER1)
mem_worker2=$(check_memory $WORKER2)
mem_worker3=$(check_memory $WORKER3)

# Obtener carga de CPU en cada worker
cpu_worker1=$(check_cpu $WORKER1)
cpu_worker2=$(check_cpu $WORKER2)
cpu_worker3=$(check_cpu $WORKER3)

# Comparar los recursos de cada worker y elegir el mejor
if [ "$mem_worker1" -gt "$mem_worker2" ] && [ "$mem_worker1" -gt "$mem_worker3" ] && [ "$cpu_worker1" -lt "$cpu_worker2" ] && [ "$cpu_worker1" -lt "$cpu_worker3" ]; then
    selected_worker=$WORKER1
elif [ "$mem_worker2" -gt "$mem_worker1" ] && [ "$mem_worker2" -gt "$mem_worker3" ] && [ "$cpu_worker2" -lt "$cpu_worker1" ] && [ "$cpu_worker2" -lt "$cpu_worker3" ]; then
    selected_worker=$WORKER2
else
    selected_worker=$WORKER3
fi

echo "Se seleccionó el worker: $selected_worker"

# Ahora ejecutamos el comando virt-install en el worker seleccionado
virt-install \
  --name ubuntu-vm \
  --memory 512 \
  --vcpus 1 \
  --disk path=/var/lib/libvirt/images/ubuntu-22.04.qcow2,format=qcow2 \
  --disk path=/tmp/my-cloud-init.iso,device=cdrom \
  --os-type linux \
  --os-variant generic \
  --network network=default \
  --graphics none \
  --console pty,target_type=serial \
  --import \
  --connect qemu+ssh://ubuntu@$selected_worker/system