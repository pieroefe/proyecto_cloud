#!/bin/bash

# Lista de workers
WORKERS=("worker1" "worker2" "worker3")

# Solicitar nombre de usuario
read -p "Ingrese su nombre de usuario para filtrar VMs: " USUARIO
if [ -z "$USUARIO" ]; then
  echo "[!] El nombre de usuario no puede estar vacío."
  exit 1
fi

# Mostrar lista de workers
echo ""
echo "Seleccione el worker donde desea buscar:"
for i in "${!WORKERS[@]}"; do
  echo "$((i+1))) ${WORKERS[$i]}"
done

# Leer selección
read -p "Opción: " OPCION
INDEX=$((OPCION-1))

# Validar selección
if [ "$INDEX" -lt 0 ] || [ "$INDEX" -ge "${#WORKERS[@]}" ]; then
  echo "[!] Opción inválida."
  exit 1
fi

WORKER="${WORKERS[$INDEX]}"
echo ""
echo "Buscando VMs del usuario '$USUARIO' en $WORKER..."
echo "------------------------------------------"

ssh "$WORKER" "virsh list --all | grep -i \"$USUARIO\" || echo '  No hay VMs asociadas al usuario $USUARIO'"

echo ""
echo "=========================================="
echo "         Fin del listado de VMs"
echo "=========================================="