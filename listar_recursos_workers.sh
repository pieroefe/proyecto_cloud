#!/bin/bash

# Lista de workers
WORKERS=("worker1" "worker2" "worker3")

echo "============================================="
echo "         Recursos de los Workers"
echo "============================================="

for WORKER in "${WORKERS[@]}"; do
  echo ""
  echo ">>> $WORKER"
  echo "---------------------------------------------"

  ssh "$WORKER" bash <<'EOF'
echo "[+] Hostname: $(hostname)"
echo "[+] Uptime: $(uptime -p)"
echo ""

# Espacio en disco raíz
echo "[+] Espacio en disco (/):"
df -h / | awk 'NR==2 { print "  Total: "$2", Usado: "$3", Libre: "$4", Uso: "$5 }'

# Memoria RAM
echo ""
echo "[+] Memoria RAM:"
free -h | awk '/Mem:/ { print "  Total: "$2", Usado: "$3", Libre: "$4 }'

# Carga de CPU (últimos 1, 5 y 15 min)
echo ""
echo "[+] Carga de CPU:"
uptime | awk -F'load average:' '{ print "  " $2 }'

# VMs activas
echo ""
echo "[+] Número de VMs activas:"
virsh list --state-running --name | grep -v '^$' | wc -l

EOF

  echo "---------------------------------------------"
done

echo ""
echo "============================================="
echo "        Fin del resumen de recursos"
echo "============================================="