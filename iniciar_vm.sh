#!/bin/bash
set -e

# Definir las IPs de los workers y su índice
WORKERS=("10.0.10.2" "10.0.10.3" "10.0.10.4")
ALPINE_ISO="/home/ubuntu/alpine-virt-3.21.3-x86_64.iso"

echo "===== CREACIÓN DE VM ALPINE ====="

# Obtener el nombre de usuario
USER_NAME=$(whoami)

# Solicitar nombre de la VM
read -rp "Nombre de la VM: " VM_NAME

# Formatear el nombre de la VM como 'nombre_de_usuario-nombre_vm'
VM_NAME="${USER_NAME}-${VM_NAME}"

# Mostrar lista de workers
echo "Seleccione el worker donde desea crear la VM:"
for i in "${!WORKERS[@]}"; do
  echo "  [$i] ${WORKERS[$i]}"
done

# Solicitar selección
read -rp "Ingrese el número del worker: " WORKER_INDEX
WORKER="${WORKERS[$WORKER_INDEX]}"

if [[ -z "$WORKER" ]]; then
  echo "❌ Selección inválida. Abortando."
  exit 1
fi

echo "Seleccionado: $WORKER"
echo "Verificando existencia del ISO en el worker..."

# Verificar ISO en el worker, si no está, copiarlo
ssh ubuntu@$WORKER "test -f $ALPINE_ISO" || {
  echo "🔁 ISO no encontrado. Copiando al worker..."
  scp "$ALPINE_ISO" "ubuntu@$WORKER:$ALPINE_ISO"
}

# Crear la VM remotamente
echo "🚀 Creando VM '$VM_NAME' en $WORKER..."

ssh ubuntu@$WORKER " \
  sudo qemu-img create -f qcow2 /var/lib/libvirt/images/$VM_NAME.qcow2 512M && \
  sudo virt-install --name $VM_NAME --ram 128 --vcpus 1 \
  --disk path=/var/lib/libvirt/images/$VM_NAME.qcow2,size=1 \
  --os-variant generic --network bridge=virbr0 \
  --cdrom $ALPINE_ISO --noautoconsole"

echo
echo "✅ VM '$VM_NAME' creada exitosamente en $WORKER"

# Mostrar información útil
echo "===== INFORMACIÓN DE ACCESO ====="
echo "➡️  Usuario por defecto: root"
echo "🔐 Contraseña: (vacía)"
echo "🖥️  Conexión desde el headnode:"
echo "     ssh ubuntu@$WORKER"
echo "     sudo virsh list --all"
echo "     sudo virsh console $VM_NAME"
echo "🛑 Para salir de la consola: Ctrl + ]"