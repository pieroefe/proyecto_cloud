#!/bin/bash

# Lista de workers (puedes usar nombres DNS o IPs)
WORKERS=("worker1" "worker2" "worker3")

# Función para mostrar el menú
mostrar_menu() {
  echo "=========================================="
  echo "     Listado de VMs por Worker"
  echo "=========================================="
  echo "1) Ver todas las VMs"
  echo "2) Filtrar por nombre de usuario"
  echo "3) Salir"
  echo "=========================================="
  read -p "Seleccione una opción: " OPCION
}

# Función para listar VMs
listar_vms() {
  local FILTRO="$1"
  for WORKER in "${WORKERS[@]}"; do
    echo ""
    echo ">>> $WORKER"
    echo "------------------------------------------"

    if [ -z "$FILTRO" ]; then
      ssh "$WORKER" 'virsh list --all || echo "  [!] Error: no se pudo ejecutar virsh"'
    else
      ssh "$WORKER" "virsh list --all | grep -i \"$FILTRO\" || echo '  No hay VMs asociadas al usuario $FILTRO'"
    fi
  done
  echo ""
  echo "=========================================="
  echo "       Fin del listado de VMs"
  echo "=========================================="
}

# Lógica principal
while true; do
  mostrar_menu
  case "$OPCION" in
    1)
      listar_vms
      ;;
    2)
      read -p "Ingrese el nombre de usuario para filtrar: " USUARIO
      listar_vms "$USUARIO"
      ;;
    3)
      echo "Saliendo..."
      exit 0
      ;;
    *)
      echo "[!] Opción no válida. Intente nuevamente."
      ;;
  esac
done