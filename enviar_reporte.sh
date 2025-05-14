#!/bin/bash

USUARIO=$1
if [ -z "$USUARIO" ]; then
  read -p "Ingrese su nombre de usuario: " USUARIO
fi

read -p "Asunto del reporte: " ASUNTO
echo "Escriba su mensaje (finalice con Ctrl+D):"
MENSAJE=$(cat)

DESTINO="admin@headnode.local"  # Cambia esto por el correo real del administrador

echo "$MENSAJE" | mail -s "$ASUNTO (de $USUARIO)" "$DESTINO"

if [ $? -eq 0 ]; then
  echo "[✔] El reporte fue enviado correctamente al administrador."
else
  echo "[!] Ocurrió un error al enviar el reporte."
fi