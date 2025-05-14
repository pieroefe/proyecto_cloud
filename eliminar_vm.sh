#!/bin/bash

# Uso: eliminar_vm.sh <nombre_usuario>

USUARIO=$1

if [ -z "$USUARIO" ]; then
  read -p "Ingrese su nombre de usuario: " USUARIO
fi

read -p "Ingrese el nombre del worker (ej. worker1, worker2): " WORKER

# Verificar si se puede hacer SSH al worker
if ! ssh "$WORKER" "exit" 2>/dev/null; then
  echo "[!] No se pudo conectar con $WORKER. Verifique el nombre y la conexión."
  exit 1
fi

# Listar VMs del usuario en el worker
echo "[i] Obteniendo lista de VMs para $USUARIO en $WORKER..."
VM_LIST=$(ssh "$WORKER" "virsh list --all | grep ${USUARIO}_ | awk '{print \$2}'")

if [ -z "$VM_LIST" ]; then
  echo "[!] No se encontraron VMs del usuario '$USUARIO' en $WORKER."
  exit 1
fi

echo "VMs disponibles para eliminar:"
echo "$VM_LIST"

read -p "Ingrese el nombre exacto de la VM que desea eliminar: " VM_NAME

# Confirmación
read -p "¿Está seguro de eliminar la VM '$VM_NAME'? (s/n): " CONFIRM
if [[ "$CONFIRM" != "s" ]]; then
  echo "Cancelado."
  exit 0
fi

# Apagar y eliminar la VM
ssh "$WORKER" bash -c "'
if virsh dominfo \"$VM_NAME\" &>/dev/null; then
  virsh destroy \"$VM_NAME\" 2>/dev/null
  virsh undefine \"$VM_NAME\" --remove-all-storage
  echo \"[✔] VM '$VM_NAME' eliminada exitosamente.\"
else
  echo \"[!] La VM '$VM_NAME' no existe.\"
fi
'"