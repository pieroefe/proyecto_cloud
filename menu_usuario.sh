#!/bin/bash

# Captura SIGINT (Ctrl + C) para evitar que el usuario salga del menú
trap 'echo "Interrupción detectada. Reiniciando menú..."; exec $0' SIGINT

while true; do
  clear
  echo "=========================="
  echo "        Silk Road"
  echo "=========================="
  echo "Fecha y hora: $(date)"
  echo ""
  echo "Bienvenido/a, $USER"
  echo ""
  echo "Este es el menú restringido para usuarios generales."
  echo ""
  echo "a) Ver mis VMs"
  echo "b) Lanzar una nueva máquina virtual"
  echo "c) Eliminar una de mis VMs"
  echo "d) Mandar reporte al administrador"
  echo "e) Salir"
  read -p "Opción: " OP

  case $OP in
    a)
      echo "Listando tus VMs..."
    b)
      echo "Lanzando nueva VM..."
    c)
      echo "Eliminando una de tus VMs..."
    d)
      echo "Enviando reporte al administrador..."
    e)
      echo "Saliendo del menú..."
      ;;
    *)
      echo "Opción no válida. Intente nuevamente."
      sleep 2
      ;;
  esac
done