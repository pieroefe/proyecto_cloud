#!/bin/bash

# Definir las IPs de los workers
WORKERS=("10.0.10.2" "10.0.10.3" "10.0.10.4")

# Ruta de la imagen ISO de Alpine
ALPINE_ISO="/home/ubuntu/alpine-virt-3.21.3-x86_64.iso"

# Nombre de la VM
VM_NAME="alpine-vm"

# Crear VM en cada worker
for WORKER in "${WORKERS[@]}"; do
  echo "Creando VM en $WORKER..."

  # Ejecutar la creación de la VM usando SSH
  ssh ubuntu@$WORKER " \
    sudo qemu-img create -f qcow2 /var/lib/libvirt/images/$VM_NAME.qcow2 512M && \
    sudo virt-install --name $VM_NAME --ram 128 --vcpus 1 --disk path=/var/lib/libvirt/images/$VM_NAME.qcow2,size=1 \
    --os-variant generic --import --network bridge=virbr0 --cdrom $ALPINE_ISO \
    --noautoconsole"

  echo "VM creada en $WORKER"
done